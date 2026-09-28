import json
import unittest
from unittest.mock import patch

from src.checkout.handler import checkout


class FakeTable:
    def __init__(self):
        self.items = []

    def put_item(self, Item, ConditionExpression=None):
        self.items.append(Item)
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}


class FakeContext:
    aws_request_id = "local-test-request-001"


def make_event(method, path, body=None):
    return {
        "httpMethod": method,
        "path": path,
        "body": json.dumps(body) if body is not None else None,
        "requestContext": {"requestId": "local-api-request-001"},
    }


class CheckoutHandlerTests(unittest.TestCase):
    def setUp(self):
        self.context = FakeContext()
        self.table = FakeTable()

    def test_health_check(self):
        result = checkout(
            make_event("GET", "/health"),
            self.context,
            self.table,
        )
        self.assertEqual(result["statusCode"], 200)
        self.assertEqual(json.loads(result["body"])["status"], "healthy")
        self.assertEqual(len(self.table.items), 0)

    def test_successful_checkout_persists_order(self):
        result = checkout(
            make_event(
                "POST",
                "/checkout",
                {
                    "customerId": "customer-001",
                    "items": [{"sku": "item-001", "quantity": 1}],
                    "amount": 49.99,
                },
            ),
            self.context,
            self.table,
        )
        body = json.loads(result["body"])
        self.assertEqual(result["statusCode"], 201)
        self.assertEqual(body["status"], "PLACED")
        self.assertEqual(len(self.table.items), 1)
        self.assertEqual(self.table.items[0]["customerId"], "customer-001")

    def test_invalid_json_returns_400(self):
        event = make_event("POST", "/checkout")
        event["body"] = "{invalid-json"
        result = checkout(event, self.context, self.table)
        self.assertEqual(result["statusCode"], 400)
        self.assertEqual(len(self.table.items), 0)

    def test_missing_fields_returns_400(self):
        result = checkout(
            make_event("POST", "/checkout", {"customerId": "customer-001"}),
            self.context,
            self.table,
        )
        self.assertEqual(result["statusCode"], 400)
        self.assertEqual(len(self.table.items), 0)

    def test_unknown_route_returns_404(self):
        result = checkout(
            make_event("GET", "/unknown"),
            self.context,
            self.table,
        )
        self.assertEqual(result["statusCode"], 404)

    def test_simulated_error_returns_500(self):
        result = checkout(
            make_event("POST", "/checkout", {"simulate_error": True}),
            self.context,
            self.table,
        )
        self.assertEqual(result["statusCode"], 500)
        self.assertEqual(len(self.table.items), 0)

    def test_simulated_delay_is_bounded(self):
        with patch("src.checkout.handler.time.sleep") as sleep_mock:
            result = checkout(
                make_event(
                    "POST",
                    "/checkout",
                    {
                        "customerId": "customer-001",
                        "items": [{"sku": "item-001", "quantity": 1}],
                        "amount": 10,
                        "simulate_delay": True,
                        "delay_seconds": 3,
                    },
                ),
                self.context,
                self.table,
            )
        self.assertEqual(result["statusCode"], 201)
        sleep_mock.assert_called_once_with(3.0)


if __name__ == "__main__":
    unittest.main()
