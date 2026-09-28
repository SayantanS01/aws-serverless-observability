# Serverless E-Commerce Observability

An AWS serverless checkout microservice demonstrating end-to-end
observability with CloudWatch, AWS X-Ray, SNS, and DynamoDB.

## Architecture

API Gateway HTTP API
        |
        v
AWS Lambda (Python 3.12)
        |
        v
Amazon DynamoDB

Observability:
- CloudWatch Logs: structured application logs and API access logs
- CloudWatch Metrics: API Gateway and Lambda metrics
- CloudWatch Logs Insights: request investigation and troubleshooting
- AWS X-Ray: Lambda tracing
- CloudWatch Dashboard: service health and performance
- CloudWatch Alarms + Amazon SNS: email notifications

## Features

- GET /health health-check endpoint
- POST /checkout order creation endpoint
- DynamoDB persistence for checkout orders
- Structured JSON application log events
- API Gateway access logging
- Lambda tracing with AWS X-Ray
- CloudWatch dashboard and metric alarms
- SNS email notifications for alarm state changes
- Development-only delay and error simulation controls

## Repository Structure

- src/checkout/handler.py: Lambda application
- tests/test_handler.py: automated unit tests
- infrastructure/: IAM policies, dashboard configuration,
  API access-log settings, and deployment ZIP
- docs/test-results/: observability test evidence
- requirements.txt: Python dependencies

## Observability Test Evidence

The test reports in docs/test-results/ document:

- API Gateway access-log verification
- Slow checkout investigation using logs and metrics
- Lambda execution-error alert testing

The Lambda error test produced an HTTP 500 response from an
unhandled ValueError. CloudWatch recorded Lambda Errors metric
datapoints, the alarm transitioned to ALARM, and its SNS action
successfully executed. The notification was confirmed in Gmail.

The measured alarm transition was within the project's
two-minute detection target for that test. This is an observed
test result, not a guarantee of future alert latency.

## Local Tests

Run the unit tests from the repository root:

    python3 -m unittest discover -s tests -v

## AWS Environment

The development deployment used:

- Region: ap-south-1
- Lambda runtime: Python 3.12
- API: API Gateway HTTP API
- Database: DynamoDB on-demand table
- Logs and metrics: Amazon CloudWatch
- Tracing: AWS X-Ray
- Notifications: Amazon SNS email subscription

The deployed resources are environment-specific. Review and
update the resource names, account-specific ARNs, and region
before reusing the infrastructure configuration.

## Security Notes

This is a development and portfolio project, not a production
checkout service.

The development API was unauthenticated. Do not send real
customer information or payment data to it.

Before production use:
- Add authentication and authorization.
- Restrict access and configure throttling.
- Remove or securely disable test simulation controls.
- Review IAM permissions and resource policies.
- Add payment-provider integration and appropriate safeguards.
- Configure monitoring, retention, and incident procedures.
- Review AWS costs and clean up unused resources.

## Cost and Cleanup

The project uses AWS managed services that may incur charges.
Review current AWS pricing and the resources deployed in your
account before running or leaving the environment active.

Delete development resources when testing is complete, after
saving any screenshots and evidence needed for the portfolio.
