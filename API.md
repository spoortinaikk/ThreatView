# ThreatView – API Documentation

## 1. Overview

ThreatView provides a REST API for accessing threat intelligence data collected from supported public threat feeds.

The API is built using FastAPI and provides endpoints for:

- User registration and authentication.
- Dashboard statistics.
- Country-based threat statistics.
- Malware trends.
- IOC listing, filtering, and sorting.
- IOC searching.
- CSV exports for Pro users.
- Weekly PDF reports for Pro users.

## 2. Base URL

For local development:

```text
http://localhost:8000
```

API documentation (Swagger UI):

```text
http://localhost:8000/docs
```

## 3. Authentication

ThreatView uses API-key authentication.

Authenticated requests must include the following HTTP header:

```http
X-API-Key: YOUR_API_KEY
```

Example:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/me
```

Requests without a valid API key are treated as Free-tier requests.

Keep API keys private. Do not publish them in source code or public repositories.

## 4. User Registration

### Register a new user

**Endpoint:**

```http
POST /api/register
```

**Parameters:**

| Parameter | Description |
|---|---|
| `email` | User's email address |
| `industry` | User's industry |
| `domain` | User's organization domain |

Example:

```bash
curl -X POST \
"http://localhost:8000/api/register?email=user@example.com&industry=IT&domain=example.com"
```

A successful registration returns a generated API key.

Store the returned API key securely. It is used to authenticate subsequent requests.

## 5. Account Information

### Get account details

**Endpoint:**

```http
GET /api/me
```

Returns information about the authenticated user's account tier and data-window access.

Example:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  http://localhost:8000/api/me
```

## 6. Dashboard Statistics

### Get threat statistics

**Endpoint:**

```http
GET /api/stats
```

**Query parameter:**

| Parameter | Description |
|---|---|
| `days` | Number of days of historical data to retrieve, subject to account permissions |

Example:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
"http://localhost:8000/api/stats?days=1"
```

The response provides dashboard statistics such as:

- Total IOC count.
- Top countries.
- Malware-family statistics.
- IOC type distribution.
- Latest ingestion timestamp.

### Get country threat statistics

**Endpoint:**

```http
GET /api/map-stats
```

Provides country-level threat statistics used by the dashboard threat map.

The current implementation uses a fixed 30-day period.

Example:

```bash
curl http://localhost:8000/api/map-stats
```

### Get malware trends

**Endpoint:**

```http
GET /api/trends
```

**Query parameter:**

| Parameter | Description |
|---|---|
| `days` | Historical period, subject to account permissions |

Example:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
"http://localhost:8000/api/trends?days=7"
```

## 7. IOC Management

### List Indicators of Compromise

**Endpoint:**

```http
GET /api/iocs
```

**Query parameters:**

| Parameter | Description |
|---|---|
| `days` | Historical data window |
| `sort` | Field used to sort the results |
| `order` | Sort direction: `asc` or `desc` |
| `limit` | Maximum number of records returned |

Example:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
"http://localhost:8000/api/iocs?days=1&sort=first_seen&order=desc&limit=50"
```

### Search IOCs

**Endpoint:**

```http
GET /api/search
```

**Query parameter:**

| Parameter | Description |
|---|---|
| `q` | IOC indicator or search term |

Example:

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
"http://localhost:8000/api/search?q=example.com"
```

The endpoint returns matching threat information according to the application's search implementation and the user's access permissions.

## 8. CSV Export

### Export threat intelligence data

**Endpoint:**

```http
GET /api/export.csv
```

This endpoint is available to Pro users.

Example:

```bash
curl -H "X-API-Key: YOUR_PRO_API_KEY" \
-o threatview-export.csv \
http://localhost:8000/api/export.csv
```

The response provides a downloadable CSV export.

## 9. Weekly PDF Report

### Generate a weekly report

**Endpoint:**

```http
GET /api/report.pdf
```

This endpoint is available to Pro users.

Example:

```bash
curl -H "X-API-Key: YOUR_PRO_API_KEY" \
-o threatview-report.pdf \
http://localhost:8000/api/report.pdf
```

The response provides a downloadable PDF report generated using ReportLab.

## 10. Free and Pro Access

ThreatView implements two access tiers.

| Feature | Free | Pro |
|---|---|---|
| Dashboard statistics | Yes | Yes |
| IOC listing | Yes | Yes |
| IOC search | Last 24 hours | Available history |
| Historical data window | 24 hours | Selectable period |
| CSV export | No | Yes |
| Weekly PDF report | No | Yes |

Free users are restricted to the most recent 24 hours of data.

Pro users can access historical periods according to the configured application permissions.

Pro access is currently assigned administratively. Automated subscription billing is not implemented.

## 11. Common HTTP Status Codes

| Status code | Meaning |
|---|---|
| `200 OK` | Request completed successfully |
| `400 Bad Request` | Invalid request or parameters |
| `403 Forbidden` | Access to the requested feature is restricted |
| `404 Not Found` | Requested endpoint or resource was not found |
| `422 Unprocessable Entity` | Request validation failed |
| `500 Internal Server Error` | Unexpected server-side error |

Actual responses depend on the endpoint and application implementation.

## 12. API Testing

The API can be tested using:

- FastAPI Swagger UI at `http://localhost:8000/docs`.
- PowerShell `Invoke-RestMethod`.
- cURL.
- Postman.

Swagger UI provides an interactive interface for viewing available endpoints, entering parameters, and executing requests.

## 13. Security Recommendations

- Keep API keys private.
- Never commit credentials or `.env` files to GitHub.
- Use strong database passwords.
- Configure HTTPS for public deployments.
- Restrict access to administrative database operations.
- Use verified sender identities for SendGrid email delivery.

## 14. Known Limitations

- PhishTank integration is pending registration and access.
- Pro account assignment is administrative.
- Automated subscription billing is not implemented.
- Country map statistics currently use a fixed 30-day period.
- Historical data access depends on the user's account tier and available stored records.

## 15. Additional Resources

- ThreatView repository: https://github.com/spoortinaikk/ThreatView
- Interactive API documentation: http://localhost:8000/docs
- AlienVault OTX: https://otx.alienvault.com/
- OpenPhish: https://openphish.com/
- URLhaus: https://urlhaus.abuse.ch/
