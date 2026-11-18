
"""One function per feed; each returns raw dict records."""

import httpx

from ..config import OTX_API_KEY, URLHAUS_AUTH_KEY

T = 30


def openphish():
    """Fetch URLs from the public OpenPhish feed."""
    url = (
        "https://raw.githubusercontent.com/"
        "openphish/public_feed/refs/heads/main/feed.txt"
    )

    response = httpx.get(
        url,
        timeout=T,
        follow_redirects=True,
    )
    response.raise_for_status()

    urls = [
        line.strip()
        for line in response.text.splitlines()
        if line.strip().startswith(("http://", "https://"))
    ]

    return [{"url": url} for url in urls[:1000]]


def phishunt():
    """Fetch suspicious phishing URLs from the public Phishunt feed."""
    url = "https://phishunt.io/feed.txt"

    response = httpx.get(url, timeout=T, follow_redirects=True)
    response.raise_for_status()

    urls = [
        line.strip()
        for line in response.text.splitlines()
        if line.strip().startswith(("http://", "https://"))
    ]

    return [{"url": item} for item in urls[:1000]]


def urlhaus():
    """Fetch recent URLhaus indicators without treating tags as families."""
    if not URLHAUS_AUTH_KEY:
        print("URLhaus skipped: Auth-Key not configured")
        return []

    response = httpx.get(
        "https://urlhaus-api.abuse.ch/v1/urls/recent/",
        headers={"Auth-Key": URLHAUS_AUTH_KEY},
        timeout=T,
    )
    response.raise_for_status()

    data = response.json()

    if data.get("query_status") != "ok":
        print("URLhaus response:", data.get("query_status"))
        return []

    return [
        {
            "url": item.get("url"),
            "threat": item.get("threat", "malware_download"),
            "malware_family": None,
        }
        for item in data.get("urls", [])
        if item.get("url")
    ]


def otx():
    """Fetch OTX indicators and their reported malware-family names."""
    if not OTX_API_KEY:
        print("OTX skipped: API key not configured")
        return []

    response = httpx.get(
        "https://otx.alienvault.com/api/v1/pulses/subscribed?limit=30",
        headers={"X-OTX-API-KEY": OTX_API_KEY},
        timeout=T,
    )
    response.raise_for_status()

    out = []

    for pulse in response.json().get("results", []):
        families = pulse.get("malware_families") or []
        family = families[0] if families else None

        if isinstance(family, dict):
            family = (
                family.get("display_name")
                or family.get("name")
            )

        if isinstance(family, str):
            family = family.strip() or None
        else:
            family = None

        for indicator in pulse.get("indicators", []):
            value = indicator.get("indicator")

            if not value:
                continue

            out.append({
                "indicator": value,
                "malware_family": family,
                "targeted_country": pulse.get("targeted_countries"),
                "industries": pulse.get("industries"),
            })

    return out


FEEDS = {
    "openphish": (openphish, 2),
    "phishunt": (phishunt, 2),
    "urlhaus": (urlhaus, 2),
    "otx": (otx, 2),
}

