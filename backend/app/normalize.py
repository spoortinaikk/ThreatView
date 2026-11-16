
"""Normalize threat intelligence feeds and classify indicator severity."""

import ipaddress
import os
import re

import geoip2.database
from geoip2.errors import AddressNotFoundError

from .config import MAXMIND_DB_PATH


FIELD_MAP = {
    "value": ["indicator", "url", "src_ip", "origin_address", "ioc"],
    "malware_family": ["malware_family", "malware", "family"],
    "country": ["country", "targeted_country", "targeted_countries", "geo"],
    "industry": ["industry", "industries", "sector"],
}

INVALID_FAMILIES = {
    "unknown",
    "phishing",
    "malware",
    "malware_download",
    "elf",
    "zip",
    "sh",
    "exe",
    "ps1",
    "dll",
    "trojan",
    "malicious",
    "psirt",
    "github",
    "cowrie",
    "honeypot",
    "iot",
    "connectwise",
    "screenconnect",
    "fleetdeck",
    "datto",
    "simplehelp",
    "jumpcloud",
    "n-able",
    "ultraviewer",
}

HIGH_RISK_TERMS = (
    "ransomware",
    "stealer",
    "keylogger",
    "rootkit",
    "backdoor",
    "botnet",
    "spyware",
    "remote access trojan",
)

MEDIUM_RISK_TERMS = (
    "phishing",
    "malware",
    "malware_download",
    "trojan",
    "loader",
    "exploit",
    "malicious",
)


def clean_malware_family(value):
    """Return a plausible single malware-family label, or None."""
    if not value:
        return None

    if isinstance(value, dict):
        value = value.get("display_name") or value.get("name")

    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value:
        return None

    normalized = value.lower()

    # Reject long pulse/article headlines.
    if len(value) > 30:
        return None

    # Reject combined tags, file types, and other metadata.
    if "," in value or ";" in value or "\n" in value:
        return None

    if normalized in INVALID_FAMILIES:
        return None

    # Reject IP addresses written with hyphens instead of dots.
    if re.fullmatch(r"\d{1,3}(?:-\d{1,3}){3}", value):
        return None

    return value


def lookup_ip_country(value):
    """Return the ISO country code for a public IP address."""
    try:
        ip = ipaddress.ip_address(value)

        if not ip.is_global:
            return None

        if not os.path.exists(MAXMIND_DB_PATH):
            return None

        with geoip2.database.Reader(MAXMIND_DB_PATH) as reader:
            response = reader.country(str(ip))
            return response.country.iso_code

    except (ValueError, AddressNotFoundError, OSError):
        return None


def pick(rec, key):
    """Get a field from a feed record using known field aliases."""
    for alias in FIELD_MAP[key]:
        value = rec.get(alias)

        if isinstance(value, list):
            value = next(
                (item for item in value if item),
                None,
            )

        if value:
            return value

    return None


def normalize_country(value):
    """Convert country names to ISO codes and reject unknown placeholders."""
    if not value:
        return None

    value = str(value).strip()

    invalid_values = {
        "UN",
        "XX",
        "ZZ",
        "UNKNOWN",
        "N/A",
        "NULL",
        "NONE",
    }

    if value.upper() in invalid_values:
        return None

    if len(value) == 2 and value.isalpha():
        return value.upper()

    country_codes = {
        "united states": "US",
        "usa": "US",
        "united kingdom": "GB",
        "uk": "GB",
        "india": "IN",
        "russia": "RU",
        "china": "CN",
        "germany": "DE",
        "france": "FR",
        "canada": "CA",
        "australia": "AU",
        "japan": "JP",
        "brazil": "BR",
    }

    return country_codes.get(value.lower())


def ioc_type(value):
    """Identify an indicator as an IP, hash, URL, or domain."""
    value = value.strip()

    try:
        ipaddress.ip_address(value)
        return "ip"
    except ValueError:
        pass

    if re.fullmatch(
        r"[a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64}",
        value,
    ):
        return "hash"

    if value.startswith(("http://", "https://")):
        return "url"

    return "domain"


def classify_severity(rec, malware, default=2):
    """Return 3=High, 2=Medium, or 1=Low."""
    explicit = rec.get("severity", rec.get("risk_level"))

    if isinstance(explicit, (int, float)) and explicit in (1, 2, 3):
        return int(explicit)

    if isinstance(explicit, str):
        levels = {
            "low": 1,
            "medium": 2,
            "moderate": 2,
            "high": 3,
            "critical": 3,
        }

        if explicit.strip().lower() in levels:
            return levels[explicit.strip().lower()]

    evidence = " ".join(
        str(value)
        for value in (
            malware,
            rec.get("threat"),
            rec.get("name"),
            rec.get("description"),
        )
        if value
    ).lower()

    if any(term in evidence for term in HIGH_RISK_TERMS):
        return 3

    if any(term in evidence for term in MEDIUM_RISK_TERMS):
        return 2

    return default


def normalize(source, rec, severity=2):
    """Normalize one feed record into the unified ThreatView format."""
    value = pick(rec, "value")

    if not value:
        return None

    value = str(value).strip()

    if not value:
        return None

    raw_malware = pick(rec, "malware_family")
    malware = clean_malware_family(raw_malware)

    industry = pick(rec, "industry")
    country = normalize_country(pick(rec, "country"))

    indicator_type = ioc_type(value)

    # Use GeoLite2 only for IP indicators without a valid feed country.
    if not country and indicator_type == "ip":
        country = lookup_ip_country(value)

    return {
        "source": source,
        "ioc_type": indicator_type,
        "value": value[:2048],
        "country": country,
        "malware_family": malware,
        "industry": str(industry)[:64] if industry else None,
        "severity": classify_severity(rec, raw_malware, severity),
        "raw": rec,
    }
