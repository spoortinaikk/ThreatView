# ThreatView – Testing and Verification Documentation

## 1. Introduction

This document describes the testing and verification performed during the development of ThreatView, a tiered threat intelligence dashboard.

Testing focuses on feed ingestion, IOC processing, API functionality, user access control, dashboard behavior, email notifications, and report generation.

## 2. Testing Environment

| Component | Configuration |
|---|---|
| Operating System | Windows |
| Containers | Docker Desktop |
| Backend | Python, FastAPI |
| Frontend | React |
| Database | PostgreSQL |
| API Testing | FastAPI Swagger UI, PowerShell |
| Email Service | SendGrid |

## 3. Functional Testing

The following test cases describe the expected behavior and the verification status recorded during development.

### 3.1 Threat Feed Ingestion

| Test Case | Expected Result | Development Status |
|---|---|---|
| AlienVault OTX ingestion | Retrieve and process available threat indicators | Tested |
| OpenPhish ingestion | Retrieve public phishing URLs | Tested |
| URLhaus ingestion | Retrieve and process malicious URLs | Tested |
| PhishTank ingestion | Retrieve phishing indicators | Not tested; integration pending |
| Scheduled ingestion | Execute feed jobs at the configured interval | Implemented; final schedule verification pending |

### 3.2 IOC Processing

| Test Case | Expected Result | Development Status |
|---|---|---|
| IOC normalization | Convert source records into a common structure | Tested |
| Duplicate handling | Avoid inserting duplicate indicators | Tested |
| IOC storage | Save processed records in PostgreSQL | Tested |
| IOC retrieval | Return stored indicators through the API | Tested |

### 3.3 API Testing

| Endpoint | Expected Behavior | Development Status |
|---|---|---|
| `POST /api/register` | Register a user and generate an API key | Implemented |
| `GET /api/me` | Return account information | Tested |
| `GET /api/stats` | Return dashboard statistics | Tested |
| `GET /api/map-stats` | Return country threat statistics | Tested |
| `GET /api/trends` | Return malware trend data | Tested |
| `GET /api/iocs` | Return IOC records | Tested |
| `GET /api/search` | Search threat indicators | Tested |
| `GET /api/export.csv` | Generate CSV export for Pro users | Tested |
| `GET /api/report.pdf` | Generate weekly PDF report for Pro users | Tested |

### 3.4 Free and Pro Access Testing

| Test Case | Expected Result | Development Status |
|---|---|---|
| Free user authentication | Apply Free-tier permissions | Tested |
| Pro user authentication | Apply Pro-tier permissions | Tested |
| Free historical data access | Restrict access to the last 24 hours | Tested |
| Pro historical data access | Allow configured historical periods | Tested |
| Free CSV export | Deny access | Tested |
| Pro CSV export | Allow access | Tested |
| Free PDF report | Deny access | Tested |
| Pro PDF report | Allow access | Tested |

Pro access is currently assigned administratively. Automated subscription billing is not implemented.

### 3.5 Dashboard Testing

| Test Case | Expected Result | Development Status |
|---|---|---|
| Dashboard statistics | Display threat statistics | Tested |
| Country visualization | Display country-level threat information | Tested |
| Malware trends | Display available malware-family trends | Tested |
| IOC table | Display threat indicators | Tested |
| Sorting and filtering | Update IOC results based on selected options | Tested |
| Historical period selection | Update data according to account permissions | Tested |
| High-severity map markers | Display high-severity countries correctly | Final verification pending |

### 3.6 Email Alert Testing

| Test Case | Expected Result | Development Status |
|---|---|---|
| Industry matching | Match available threat metadata against user industry | Tested |
| Brand/domain monitoring | Match configured domains against new indicators | Tested |
| SendGrid integration | Submit email notifications through SendGrid | Tested |
| Controlled end-to-end test | Process a controlled feed record and trigger alert handling | Tested |

A controlled end-to-end ingestion test successfully processed a test indicator and received a successful SendGrid response. Email delivery and inbox placement should be checked separately in the target deployment.

### 3.7 Report Generation

| Test Case | Expected Result | Development Status |
|---|---|---|
| CSV export | Generate downloadable IOC data | Tested |
| Weekly PDF report | Generate a PDF report | Tested |
| Free-tier export restriction | Restrict CSV and PDF exports | Tested |

## 4. Integration Testing

A controlled end-to-end test was performed using a temporary test feed record.

The test verified the following workflow:

1. A controlled test indicator was submitted.
2. The ingestion pipeline processed the indicator.
3. The indicator was normalized.
4. The database stored the new record.
5. Alert processing was triggered.
6. SendGrid returned a successful submission response.

This test demonstrated the integration between ingestion, database storage, alert processing, and email submission.

## 5. API Testing Tools

The following tools were used during development:

- FastAPI Swagger UI: `http://localhost:8000/docs`
- PowerShell `Invoke-RestMethod`
- Docker Compose logs
- Browser-based dashboard testing

Example API request:

```powershell
Invoke-RestMethod "http://localhost:8000/api/stats?days=1"
```

Example authenticated request:

```powershell
Invoke-RestMethod "http://localhost:8000/api/me" -Headers @{
    "X-API-Key" = "YOUR_API_KEY"
}
```

Use an actual test API key when running authenticated tests. Do not publish real credentials.

## 6. Known Testing Limitations

- PhishTank testing is pending because integration and registration are incomplete.
- Production deployment has not yet been verified.
- Production email deliverability requires separate testing.
- High-severity map marker behavior requires final visual verification.
- Testing results reflect development-environment verification, not a formal independent security audit.

## 7. Conclusion

Development testing has covered the main ThreatView functionality, including threat-feed ingestion, IOC processing, API access, tier-based restrictions, dashboard data, email alert handling, and report generation.

Further verification is required before production deployment, particularly for the pending PhishTank integration, final dashboard checks, and production configuration.
