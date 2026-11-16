
import logging

from sqlalchemy.exc import IntegrityError

from ..db import Session, Base, engine
from ..models import Threat
from ..normalize import normalize
from ..alerts import dispatch_alerts
from .feeds import FEEDS


logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ingest")


def ingest_all():
    Base.metadata.create_all(engine)

    new = []

    for name, (fn, sev) in FEEDS.items():
        log.info("Starting feed: %s", name)

        try:
            records = fn()
        except Exception as e:
            log.warning("Feed %s failed: %s", name, e)
            continue

        inserted = 0

        with Session() as s:
            known = {
                value
                for (value,) in s.query(Threat.value).filter(
                    Threat.source == name
                )
            }

            for rec in records:
                t = normalize(name, rec, sev)

                if t and t["value"] not in known:
                    known.add(t["value"])
                    obj = Threat(**t)
                    s.add(obj)
                    new.append(obj)
                    inserted += 1

            try:
                s.commit()
            except IntegrityError:
                s.rollback()
                log.exception("Database integrity error for feed: %s", name)

        log.info(
            "Feed %s processed: %d fetched, %d inserted",
            name,
            len(records),
            inserted
        )

    try:
        dispatch_alerts(new)
    except Exception:
        log.exception("Alert dispatch failed")

    log.info(
        "Ingestion complete. New records inserted: %d",
        len(new)
    )

    return len(new)
