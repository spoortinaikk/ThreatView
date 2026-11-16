
"""Backfill missing IP country values using the local GeoLite2 database."""

from .db import Session
from .models import Threat
from .normalize import lookup_ip_country, normalize_country


def backfill_geoip():
    checked = 0
    updated = 0
    unmatched = 0

    with Session() as session:
        records = (
            session.query(Threat)
            .filter(Threat.ioc_type == "ip")
            .all()
        )

        for record in records:
            # Preserve valid country codes already stored.
            if normalize_country(record.country):
                continue

            checked += 1
            country = lookup_ip_country(record.value)

            if country:
                record.country = country
                updated += 1
            else:
                unmatched += 1

        session.commit()

    print(f"IP records checked: {checked}")
    print(f"Country values updated: {updated}")
    print(f"No GeoIP match: {unmatched}")


if __name__ == "__main__":
    backfill_geoip()
