import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def log_event(level, event, **fields):
    """Write one structured JSON log record."""
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "event": event,
        **fields,
    }
    getattr(logger, level.lower())(
        json.dumps(record, default=str, separators=(",", ":"))
    )


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Cache-Control": "no-store",
        },
        "body": json.dumps(body, default=str),
    }


def get_path(event):
    return (
        event.get("rawPath")
        or event.get("path")
        or event.get("resource")
        or "/"
    )


def get_method(event):
    return (
        event.get("requestContext", {})
        .get("http", {})
        .get("method")
        or event.get("httpMethod")
        or "GET"
    ).upper()


def get_request_id(event, context):
    return (
        getattr(context, "aws_request_id", None)
        or event.get("requestContext", {}).get("requestId")
        or str(uuid.uuid4())
    )


def parse_body(event):
    body = event.get("body")
    if isinstance(body, dict):
        return body
    if not isinstance(body, str) or not body:
        return {}
    if event.get("isBase64Encoded"):
        raise ValueError("Base64-encoded request bodies are not supported")
    parsed = json.loads(body)
    if not isinstance(parsed, dict):
        raise ValueError("Request body must be a JSON object")
    return parsed


def checkout(event, context, table=None):
    started = time.monotonic()
    request_id = get_request_id(event, context)
    path = get_path(event)
    method = get_method(event)

    log_event(
        "info",
        "request_received",
        request_id=request_id,
        method=method,
        path=path,
    )

    if method == "GET" and path.rstrip("/") == "/health":
        log_event(
            "info",
            "health_check_succeeded",
            request_id=request_id,
            duration_ms=round((time.monotonic() - started) * 1000, 2),
        )
        return response(200, {"status": "healthy", "requestId": request_id})

    if method != "POST" or path.rstrip("/") != "/checkout":
        return response(404, {"message": "Route not found", "requestId": request_id})

    try:
        payload = parse_body(event)
    except (ValueError, json.JSONDecodeError) as exc:
        log_event(
            "warning",
            "request_validation_failed",
            request_id=request_id,
            reason=str(exc),
        )
        return response(400, {"message": "Invalid JSON request body", "requestId": request_id})

    # Development-only observability test controls.
    if payload.get("simulate_delay"):
        delay_seconds = min(max(float(payload.get("delay_seconds", 3)), 0), 5)
        time.sleep(delay_seconds)

    if payload.get("simulate_error"):
        log_event(
            "error",
            "simulated_checkout_failure",
            request_id=request_id,
            failure_type="controlled_test_error",
        )
        return response(
            500,
            {"message": "Simulated checkout failure", "requestId": request_id},
        )

    customer_id = payload.get("customerId")
    items = payload.get("items")
    amount = payload.get("amount")

    if (
        not isinstance(customer_id, str)
        or not customer_id.strip()
        or not isinstance(items, list)
        or not items
        or amount is None
    ):
        return response(
            400,
            {
                "message": "customerId, non-empty items, and amount are required",
                "requestId": request_id,
            },
        )

    try:
        amount_decimal = Decimal(str(amount))
        if not amount_decimal.is_finite() or amount_decimal <= 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError, TypeError):
        return response(
            400,
            {"message": "amount must be a positive number", "requestId": request_id},
        )

    order_id = str(uuid.uuid4())
    order = {
        "orderId": order_id,
        "customerId": customer_id.strip(),
        "items": items,
        "amount": amount_decimal,
        "status": "PLACED",
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "requestId": request_id,
    }

    try:
        if table is None:
            import boto3

            table_name = os.environ["ORDERS_TABLE"]
            table = boto3.resource("dynamodb").Table(table_name)

        table.put_item(
            Item=order,
            ConditionExpression="attribute_not_exists(orderId)",
        )

        duration_ms = round((time.monotonic() - started) * 1000, 2)
        log_event(
            "info",
            "checkout_succeeded",
            request_id=request_id,
            order_id=order_id,
            amount=str(amount_decimal),
            duration_ms=duration_ms,
        )
        return response(
            201,
            {
                "message": "Order placed",
                "orderId": order_id,
                "status": "PLACED",
                "requestId": request_id,
            },
        )

    except Exception:
        duration_ms = round((time.monotonic() - started) * 1000, 2)
        log_event(
            "exception",
            "checkout_persistence_failed",
            request_id=request_id,
            duration_ms=duration_ms,
        )
        return response(
            500,
            {"message": "Unable to place order", "requestId": request_id},
        )


def lambda_handler(event, context):
    return checkout(event, context)
