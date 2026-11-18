# ThreatView – Threat Intelligence Feed Documentation

ThreatView integrates four threat intelligence feeds to collect, normalize, and store Indicators of Compromise (IOCs). These indicators help identify potentially malicious IP addresses, domains, URLs, and file hashes.

## Integrated Threat Intelligence Feeds

| Feed | Data collected | Authentication | Schedule |
|---|---|---|---|
| AlienVault OTX | IPs, domains, URLs, file hashes, and pulse metadata | `OTX_API_KEY` | Every 60 minutes |
| OpenPhish | Public phishing URL feed | Not required | Every 60 minutes |
| URLhaus | Malicious and malware-distribution URLs | `URLHAUS_AUTH_KEY` | Every 60 minutes |
| Phishunt | Public phishing URL feed | Not required | Every 60 minutes |

## Feed Details

### 1. AlienVault OTX

- Source: https://otx.alienvault.com/
- Authentication: `OTX_API_KEY`
- Retrieves subscribed threat intelligence pulses.
- Extracts indicators such as IP addresses, domains, URLs, and file hashes.
- Uses available pulse metadata for malware families, targeted countries, and industries.

The metadata available depends on the individual pulse.

### 2. OpenPhish

- Source: https://openphish.com/
- Public feed: https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt
- Authentication: Not required for the public feed.
- Provides publicly available phishing URLs.
- The public feed does not provide industry or malware-family metadata.

ThreatView retrieves the public feed and processes its URL records into the common IOC structure.

### 3. URLhaus

- Source: https://urlhaus.abuse.ch/
- Authentication: `URLHAUS_AUTH_KEY`
- Retrieves recent malicious URLs.
- Provides threat classifications such as `malware_download`.
- Malware classification does not necessarily identify a specific malware family.

URLhaus data is used to identify URLs associated with malware distribution and related malicious activity.

### 4. Phishunt

- Source: https://phishunt.io/
- Public feed: https://phishunt.io/feed.txt
- Authentication: Not required for the tested public feed.
- Provides publicly available phishing URLs.
- ThreatView retrieves URL records and converts them into its common IOC structure.

**Integration verification:**
- Phishunt successfully returned HTTP 200 during testing.
- 904 phishing URL records were fetched.
- 904 Phishunt records were verified in the ThreatView database.

Phishunt is an active feed in the current ingestion pipeline.

## Ingestion Workflow

1. The API application starts and initializes the scheduled ingestion process.
2. APScheduler triggers the configured feed ingestion jobs.
3. Each feed connector retrieves available threat records.
4. The normalizer converts records into the common Threat database model.
5. Duplicate records are checked using the source and indicator value.
6. New records are stored in PostgreSQL.
7. Newly inserted records are passed to the alert dispatcher.
8. The dashboard API makes the stored threat information available to the frontend.

## Data Normalization

ThreatView converts records from different feed formats into a common structure.

Depending on the source data, normalized records can contain:

- Indicator value
- IOC type
- Threat source
- Severity
- Malware family or classification
- Country information
- First-seen timestamp
- Available threat metadata

Not every feed provides every field. Missing metadata is handled according to the application's normalization logic.

## Configuration

Configure the following variables in the root `.env` file:

```env
OTX_API_KEY=your_otx_api_key
URLHAUS_AUTH_KEY=your_urlhaus_auth_key
INGEST_INTERVAL_MINUTES=60
```

Optional email configuration:

```env
SENDGRID_API_KEY=your_sendgrid_api_key
MAIL_FROM=your_verified_sender_address
```

The database password is configured separately:

```env
POSTGRES_PASSWORD=your_secure_password
```

Never publish actual API keys, passwords, or other credentials.

## Scheduling

The default ingestion interval is 60 minutes.

The interval can be changed using `INGEST_INTERVAL_MINUTES` in the root `.env` file.

For example:

```env
INGEST_INTERVAL_MINUTES=30
```

This configures ingestion to run every 30 minutes, subject to the scheduler configuration and successful application startup.

## Error Handling and Reliability

- Feed connectors handle retrieval and processing errors independently.
- A failure in one feed should not prevent other configured feeds from being processed.
- HTTP and feed-processing errors are logged for troubleshooting.
- Duplicate indicators are prevented using source and indicator-value checks.
- Feed availability and external service response codes can affect ingestion results.

## Limitations

- OpenPhish and Phishunt public feed records do not provide industry metadata.
- Industry alerts depend on metadata supplied by the relevant feed.
- URLhaus threat classifications do not always identify a specific malware family.
- External feed availability and authentication requirements may change.
- Feed records may contain incomplete or inconsistent metadata.

## Security Considerations

- Store API keys and credentials in the root `.env` file.
- Do not commit `.env` to the public Git repository.
- Use secure credentials for database access.
- Follow the usage terms and rate limits of each external feed provider.