# ThreatView – Tiered Threat Intelligence Dashboard

ThreatView is an affordable threat intelligence dashboard designed to help small and medium-sized businesses (SMBs) monitor malicious indicators, understand emerging cyber threats, and receive alerts relevant to their industry and brand.

## Features

- Aggregates threat intelligence from public feeds.
- Normalizes Indicators of Compromise (IOCs) into a common format.
- Stores threat data in PostgreSQL.
- Displays IOC statistics, malware trends, country distribution, and threat maps.
- Supports IOC search, filtering, and sorting.
- Provides Free and Pro access tiers.
- Sends automated industry and brand-monitoring email alerts.
- Generates downloadable CSV exports and weekly PDF reports for Pro users.
- Runs scheduled threat-feed ingestion using APScheduler.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Scheduler | APScheduler |
| Frontend | React, Recharts |
| Email notifications | SendGrid |
| PDF reports | ReportLab |
| Containerization | Docker, Docker Compose |

## Architecture

1. **Feed ingestion:** Feed ingestors retrieve threat intelligence from supported public sources.
2. **Normalization:** The normalizer converts source records into a common IOC structure.
3. **Storage:** The ingestion pipeline deduplicates and stores records in PostgreSQL.
4. **Alert processing:** Alert rules match new threats against user industries and configured domains.
5. **API:** FastAPI provides dashboard, search, export, registration, and reporting endpoints.
6. **Frontend:** The React application presents threat intelligence through an interactive dashboard.

## Integrated Threat Intelligence Feeds

| Source | Data |
|---|---|
| AlienVault OTX | IP addresses, domains, URLs, file hashes, and pulse metadata |
| OpenPhish | Phishing URLs |
| URLhaus | Malicious and malware-distribution URLs |
| PhishTank | Not integrated; registration and access remain pending |

OpenPhish's public feed does not provide industry metadata. Industry-based matching therefore depends on metadata available from supported sources.

## Scheduled Ingestion

- Ingestion starts when the API application starts.
- APScheduler repeats ingestion every 60 minutes by default.
- The interval can be configured using `INGEST_INTERVAL_MINUTES`.
- Duplicate indicators are prevented using source and indicator-value checks.

## Dashboard

The dashboard provides:

- Threat statistics and severity distribution.
- Country-based threat visualization.
- Malware-family trends from available OTX records.
- IOC table with sorting and filtering.
- IOC search.

**Note:** The country map statistics endpoint currently uses a fixed 30-day period, independently of the dashboard's selected data window.

## Free and Pro Tiers

| Feature | Free | Pro |
|---|---|---|
| Dashboard and API access | Yes | Yes |
| Data window | Last 24 hours | Selectable historical period |
| Historical IOC search | Last 24 hours | Available history |
| CSV export | No | Yes |
| Weekly PDF report | No | Yes |

Authentication uses the `X-API-Key` request header. Requests without a valid API key are treated as Free-tier requests.

### Registration

Users can register through the API:

```http
POST /api/register?email=you@example.com&industry=IT&domain=example.com
```

A successful registration returns a generated API key. Users should store this key securely and include it in subsequent API requests using the `X-API-Key` header.

### Pro Account Management

Pro access is currently assigned administratively by updating the user's database tier:

```sql
UPDATE users SET tier='pro' WHERE email='you@example.com';
```

Automated subscription billing through Stripe is not implemented.

## Automated Email Alerts

ThreatView supports:

- Industry matching against available threat metadata.
- Brand and domain monitoring for configured domains and their subdomains.
- SendGrid email notifications.

If SendGrid is not configured, alerts run in dry-run mode and are logged rather than emailed. Email delivery also requires a verified sender identity in SendGrid.

## API Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/register` | Register a user and generate an API key |
| `GET /api/me` | Get account tier and data-window information |
| `GET /api/stats` | Retrieve dashboard statistics |
| `GET /api/map-stats` | Retrieve country threat statistics |
| `GET /api/trends` | Retrieve malware-family trends |
| `GET /api/iocs` | List and sort IOCs |
| `GET /api/search` | Search IOC indicators |
| `GET /api/export.csv` | Export IOCs as CSV (Pro) |
| `GET /api/report.pdf` | Generate a weekly PDF report (Pro) |

For request parameters and response schemas, see the interactive FastAPI documentation at `/docs`.

## Setup

### Requirements

- Docker Desktop
- Docker Compose
- Git

### Installation

Clone the repository:

```bash
git clone https://github.com/spoortinaikk/ThreatView.git
cd ThreatView
```

Create your environment file:

```bash
cp .env.example .env
```

On Windows PowerShell, you can use:

```powershell
Copy-Item .env.example .env
```

Configure the required credentials and database settings in `.env`. Do not use example or placeholder credentials for a real deployment.

Build and start the application:

```bash
docker compose up --build -d
```

To inspect running containers:

```bash
docker compose ps
```

To view application logs:

```bash
docker compose logs -f
```

### Access the Application

- **Dashboard:** http://localhost:8080
- **API documentation:** http://localhost:8000/docs

### Environment Variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL database connection |
| `POSTGRES_PASSWORD` | PostgreSQL database password |
| `OTX_API_KEY` | AlienVault OTX authentication |
| `URLHAUS_AUTH_KEY` | URLhaus authentication, if required by the configured integration |
| `SENDGRID_API_KEY` | SendGrid email delivery |
| `MAIL_FROM` | Verified sender email address |
| `INGEST_INTERVAL_MINUTES` | Feed ingestion interval |
| `MAXMIND_DB_PATH` | Path to the GeoLite2 country database |

The exact required values depend on the project's Docker Compose and application configuration. Refer to `.env.example` for the environment variables used by the current project version.

### GeoLite2 Country Database Setup

ThreatView uses the MaxMind GeoLite2 Country database for IP geolocation.

1. Create a MaxMind account.
2. Obtain the GeoLite2 Country database from MaxMind under its applicable terms.
3. Download the database in MMDB format.
4. Place the file in the project's configured GeoIP directory. The current development layout uses:

```text
data/
└── geoip/
    └── GeoLite2-Country.mmdb
```

5. Configure `MAXMIND_DB_PATH` to point to the database file, using the path expected by the application and Docker configuration.

The database is not included in the GitHub repository. Each deployment must obtain and configure its own copy.

**Security:** Never commit `.env`, actual API keys, database passwords, or private credentials to GitHub.

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

These results reflect development testing. Production deployment, security, and production email deliverability require separate verification.

## Known Limitations

- PhishTank integration is pending registration and access.
- OpenPhish's public feed does not include industry metadata.
- Industry alerts depend on available threat metadata.
- Pro tier assignment is administrative; subscription billing is not implemented.
- The country map endpoint currently uses a fixed 30-day period.
- Production deployment and production email deliverability require separate verification.

## License

No open-source license has been specified yet. Select and add an appropriate license before distributing the project publicly. Until then, do not assume that the repository grants others permission to reuse or redistribute the code.
