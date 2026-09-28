# Lambda Execution Error Alert Test

## Objective

Verify that a genuine unhandled Lambda execution error increments
the Lambda Errors metric, triggers the CloudWatch alarm, and sends
an email notification through SNS.

## Test environment

- AWS Region: ap-south-1
- Lambda: ecommerce-observability-dev-checkout
- Alarm: ecommerce-observability-dev-lambda-errors
- SNS topic: ecommerce-observability-dev-alerts
- Alarm threshold: Errors Sum >= 1
- Evaluation period: 60 seconds
- Missing data: notBreaching

## Test method

A synthetic checkout request was sent to the development API
with `simulate_delay=true` and `delay_seconds="invalid"`.

The invalid delay value caused an unhandled ValueError during
float conversion in the checkout handler.

No production customer data was used.

## Observed results

- API response: HTTP 500
- Exception: ValueError converting 'invalid' to float
- Error location: handler.py, line 117
- Lambda Errors metric:
  - 1 error at 15:11 IST
  - 1 error at 15:12 IST
- CloudWatch alarm transition: OK -> ALARM
- Alarm transition time: 2026-09-28 15:12:23.715 IST
- SNS action: Successfully executed
- Email notification: Received in Gmail
- Approximate request-to-alarm interval: 14 seconds

## Outcome

PASS — The genuine Lambda execution error was recorded in
CloudWatch, triggered the configured alarm, and resulted in
an SNS email notification.

The observed alarm transition was within the project's
two-minute detection target. This is a measured result from
this test, not a guarantee of future alert latency.

## Evidence

- CloudWatch Lambda Errors metric datapoints
- CloudWatch alarm state history
- CloudWatch alarm action history
- Lambda error logs
- Gmail alarm notification screenshot

## Security and cleanup

The test used a development-only error-inducing request.
Disable or remove test controls before production use.
Review API authentication, access restrictions, AWS costs,
and resource cleanup before publishing the project.
