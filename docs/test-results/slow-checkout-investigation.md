# Slow Checkout Investigation

Date: 2026-09-28
Region: ap-south-1
Function: ecommerce-observability-dev-checkout
Table: ecommerce-observability-dev-orders

## Investigation

A checkout invocation was identified with a Lambda duration of
3107.68 ms. CloudWatch Logs Insights was used to correlate the
Lambda REPORT record with structured application events using
the request ID.

## Correlated evidence

- Request ID: dbfa01e0-a3c8-4098-8bcd-a53ae01b5702
- Route: POST /checkout
- Application event: checkout_succeeded
- Application duration: 3092.41 ms
- Lambda duration: 3107.68 ms
- Billed duration: 3108 ms
- Maximum memory used: 94 MB
- Configured memory: 256 MB
- Order ID: e48c78f7-4b89-4b2c-8d95-cadced57b327
- Amount: 49.99
- Order status: PLACED
- Test customer: observability-test-customer
- Test SKU: TEST-001
- Quantity: 1

## DynamoDB verification

The order was retrieved successfully using DynamoDB GetItem.
The persisted request ID matched the Lambda invocation request ID.
The order status was PLACED and the amount was 49.99.

## Result

PASS: The slow checkout was correlated across application logs,
Lambda execution records, and the persisted DynamoDB order.

The cause of the delay is not conclusively established by the
available logs. No explicit delay-start event was observed.

## Follow-up

- Verify the request payload or simulation configuration to
  determine whether the controlled delay was enabled.
- Configure and test CloudWatch alarms for elevated duration.
- Measure alert delivery time and document the result.
