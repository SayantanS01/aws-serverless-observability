# API Gateway Access Logging Test

Date: 2026-09-28
Region: ap-south-1
API: ecommerce-observability-dev-http-api
Stage: $default
Route: GET /health
Log group: /aws/apigateway/ecommerce-observability-dev-http-api-access

## Test summary

- API Gateway access logging configured and deployed.
- JSON-formatted access logs successfully delivered to CloudWatch.
- Four GET /health requests verified through CloudWatch Logs Insights.
- All four requests returned HTTP 200.
- All four had no integration errors.
- Logs Insights query status: Complete.
- Records matched: 4.
- Records scanned: 4.
- Bytes scanned: 1,051.

## Observed response latencies

| Request | HTTP status | Latency |
|---|---:|---:|
| 1 | 200 | 225 ms |
| 2 | 200 | 37 ms |
| 3 | 200 | 24 ms |
| 4 | 200 | 16 ms |

Average observed latency: 75.5 ms.

Note: This is a small health-check sample and is not a load or
performance benchmark.

## Logs Insights query

    fields @timestamp, requestId, httpMethod, routeKey,
           status, responseLatency, integrationError
    | sort @timestamp desc
    | limit 50

## Result

PASS — API Gateway access logging and Logs Insights query
were verified for the four observed requests.
