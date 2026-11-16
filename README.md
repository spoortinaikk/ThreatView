
# ThreatView – Tiered Threat Intelligence Dashboard

ThreatView is an affordable threat intelligence dashboard designed to help small and medium-sized businesses (SMBs) monitor malicious indicators, understand emerging threats, and receive alerts relevant to their industry and brand.

## Features

- Aggregates threat intelligence from public feeds.
- Normalizes indicators of compromise (IOCs).
- Stores threat data in PostgreSQL.
- Displays IOC statistics, malware trends, country distribution and threat maps.
- Supports IOC search, filtering and sorting.
- Provides Free and Pro access tiers.
- Sends automated industry and brand-monitoring email alerts.
- Generates downloadable CSV exports and weekly PDF reports for Pro users.
- Runs scheduled feed ingestion using APScheduler.

## Technology Stack

- Backend: Python, FastAPI, SQLAlchemy
- Database: PostgreSQL
- Scheduler: APScheduler
- Frontend: React, Recharts
- Email: SendGrid
- Reports: ReportLab
- Deployment: Docker Compose

## Architecture

1. Feed ingestors retrieve threat intelligence.
2. The normalizer converts source records into a common IOC structure.
3. The ingestion pipeline deduplicates and stores records.
4. Alert rules match new threats against user industries and configured domains.
5. The FastAPI backend provides dashboard, search, export and reporting endpoints.
6. The React frontend presents the threat intelligence dashboard.

## Integrated Threat Intelligence Feeds

| Source | Data |
|---|---|
| AlienVault OTX | IP addresses, domains, URLs, file hashes and pulse metadata |
| OpenPhish | Phishing URLs |
| URLhaus | Malicious and malware-distribution URLs |
| PhishTank | Not integrated; registration/access remains pending |

OpenPhish's public feed does not provide industry metadata. Industry-based matching uses available threat metadata from sources that supply it.

## Scheduled Ingestion

- Ingestion starts when the API application starts.
- APScheduler repeats ingestion every 60 minutes by default.
- The interval can be changed through `INGEST_INTERVAL_MINUTES`.
- Duplicate indicators are prevented using source and indicator value.

## Dashboard

The dashboard provides:

- Threat statistics and severity distribution.
- Country-based threat visualization.
- Malware-family trends from OTX records.
- IOC table with sorting and filtering.
- IOC search.

The country map statistics endpoint currently uses a fixed 30-day period.

## Free and Pro Tiers

| Feature | Free | Pro |
|---|---|---|
| Dashboard and API access | Yes | Yes |
| Data window | Last 24 hours | Selected historical period |
| Historical IOC search | Last 24 hours | Available history |
| CSV export | No | Yes |
| Weekly PDF report | No | Yes |

Authentication uses the `X-API-Key` request header. Users without a valid key are treated as Free users.

### Registration

Register through the API:

`POST /api/register?email=you@example.com&industry=IT&domain=example.com`

The response contains the generated API key. Keep this key private.

### Pro Account Management

Pro access is currently assigned administratively by updating the user's database tier:

```sql
UPDATE users SET tier='pro' WHERE email='you@example.com';
```

Automated Stripe billing is not implemented.

## Automated Email Alerts

ThreatView supports:

- Industry matching against available threat metadata.
- Brand/domain monitoring for configured domains and their subdomains.
- SendGrid email notifications.

If SendGrid is not configured, alerts run in dry-run mode and are logged instead of emailed.

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/register` | Register a user and generate an API key |
| `GET /api/me` | Get account tier and data-window information |
| `GET /api/stats` | Dashboard statistics |
| `GET /api/map-stats` | Country threat statistics |
| `GET /api/trends` | Malware-family trends |
| `GET /api/iocs` | List and sort IOCs |
| `GET /api/search` | Search IOC indicators |
| `GET /api/export.csv` | Pro CSV export |
| `GET /api/report.pdf` | Pro weekly PDF report |

## Setup

### Requirements

- Docker Desktop
- Docker Compose

### Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd threatview
```

Create your environment file:

```bash
cp .env.example .env
```

Configure the required credentials in `.env`.

Build and start the application:

```bash
docker compose up --build -d
```

### Access the Application

- Dashboard: http://localhost:8080
- API documentation: http://localhost:8000/docs

### Environment Variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Database connection |
| `OTX_API_KEY` | AlienVault OTX authentication |
| `URLHAUS_AUTH_KEY` | URLhaus authentication |
| `SENDGRID_API_KEY` | Email delivery |
| `MAIL_FROM` | Verified sender address |
| `INGEST_INTERVAL_MINUTES` | Feed ingestion interval |
| `MAXMIND_DB_PATH` | GeoIP database path |

Never commit `.env` or actual API keys to GitHub.

## Testing and Verification

The following functionality has been tested during development:

- Feed ingestion and IOC normalization.
- Duplicate handling.
- Free and Pro account behavior.
- IOC search and historical data windows.
- Dashboard period filtering.
- Industry and brand-monitoring alert matching.
- SendGrid email delivery.
- Controlled end-to-end feed-to-email ingestion.
- Pro CSV and PDF exports.
- Free-tier export restrictions.

## Known Limitations

- PhishTank integration is pending registration/access.
- OpenPhish's public feed does not include industry metadata.
- Industry alerts depend on available threat metadata.
- Pro tier assignment is administrative; subscription billing is not implemented.
- Production deployment and production email deliverability require separate verification.

## License

Add your chosen project license before public distribution.
