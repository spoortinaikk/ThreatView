
# ThreatView – Threat Intelligence Feed Documentation

ThreatView currently integrates three threat intelligence sources.

## Integrated Feeds

| Feed | Data collected | Authentication | Schedule |
|---|---|---|---|
| AlienVault OTX | IPs, domains, URLs, file hashes and pulse metadata | `OTX_API_KEY` | Every 60 minutes |
| OpenPhish | Public phishing URL feed | Not required | Every 60 minutes |
| URLhaus | Malicious and malware-distribution URLs | `URLHAUS_AUTH_KEY` required by current implementation | Every 60 minutes |
| PhishTank | Not integrated | Registration and application access pending | Not scheduled |

## Feed Details

### 1. AlienVault OTX

- Source: https://otx.alienvault.com/
- Authentication: `OTX_API_KEY`
- Retrieves subscribed threat intelligence pulses.
- Extracts indicators such as IP addresses, domains, URLs and file hashes.
- Uses available pulse metadata for malware family, targeted countries and industries.

### 2. OpenPhish

- Source: https://openphish.com/
- Public feed: https://raw.githubusercontent.com/openphish/public_feed/refs/heads/main/feed.txt
- Authentication: Not required for the public feed.
- Provides phishing URLs.
- The public feed does not provide industry or malware-family metadata.

### 3. URLhaus

- Source: https://urlhaus.abuse.ch/
- Authentication: `URLHAUS_AUTH_KEY`
- Retrieves recent malicious URLs.
- Provides threat classification such as `malware_download`.
- Malware classification is not necessarily the same as a specific malware-family name.

### 4. PhishTank

- Source: https://phishtank.org/
- Integration status: Pending.
- Registration/application access has not yet been completed.
- No PhishTank data is currently ingested by ThreatView.

## Ingestion Workflow

1. The scheduler starts when the API application starts.
2. Each configured feed function retrieves available records.
3. The normalizer converts records into the common Threat model.
4. Duplicate records are checked using source and indicator value.
5. New records are stored in PostgreSQL.
6. Newly inserted records are passed to the alert dispatcher.

## Configuration

Configure these variables in the root `.env` file:

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

Never publish actual API keys or credentials.

## Scheduling

The default ingestion interval is 60 minutes.

Change `INGEST_INTERVAL_MINUTES` in `.env` to configure a different interval.

## Limitations

- PhishTank is not yet integrated.
- OpenPhish public feed records do not include industry metadata.
- Industry alerts depend on metadata supplied by the relevant feed.
- URLhaus threat classifications do not always identify a specific malware family.
