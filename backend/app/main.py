
import csv
import io
import datetime as dt

from fastapi import FastAPI, Depends, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import func, or_

from .db import Session, Base, engine
from .models import Threat, User
from .normalize import clean_malware_family
from . import scheduler
from .reports import weekly_pdf


Base.metadata.create_all(engine)

app = FastAPI(title="ThreatView API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def _s():
    scheduler.start()


def db():
    with Session() as s:
        yield s


def user(x_api_key: str = Header(None), s=Depends(db)):
    if not x_api_key:
        return None

    return s.query(User).filter(User.api_key == x_api_key).first()


def pro(u):
    return bool(u and u.tier == "pro")


def window(q, u, days):
    """Free users see 24 hours; Pro users see the selected period."""
    if pro(u):
        return q.filter(
            Threat.first_seen >=
            dt.datetime.utcnow() - dt.timedelta(days=max(1, days))
        )

    return q.filter(
        Threat.first_seen >=
        dt.datetime.utcnow() - dt.timedelta(hours=24)
    )


def row(t):
    return {
        "id": t.id,
        "source": t.source,
        "type": t.ioc_type,
        "value": t.value,
        "country": t.country,
        "malware": t.malware_family,
        "industry": t.industry,
        "severity": t.severity,
        "seen": t.first_seen.isoformat()
    }


# REGISTRATION
@app.post("/api/register")
def register(
    email: str,
    industry: str = None,
    domain: str = None,
    s=Depends(db)
):
    u = s.query(User).filter(User.email == email).first()

    if not u:
        u = User(
            email=email,
            industry=industry,
            domain=domain,
            tier="free"
        )
        s.add(u)
    else:
        u.industry = industry or u.industry
        u.domain = domain or u.domain

    s.commit()
    s.refresh(u)

    return {
        "api_key": u.api_key,
        "tier": u.tier
    }


# ACCOUNT DETAILS
@app.get("/api/me")
def me(u=Depends(user)):
    return {
        "tier": u.tier if u else "free",
        "window_days": None if pro(u) else 1
    }


# DASHBOARD STATISTICS
@app.get("/api/stats")
def stats(days: int = 1, u=Depends(user), s=Depends(db)):
    q = window(s.query(Threat), u, days)

    by = lambda col, n=10: [
        {"name": a or "unknown", "count": c}
        for a, c in q.with_entities(col, func.count())
        .group_by(col)
        .order_by(func.count().desc())
        .limit(n)
    ]

    severity_counts = {
        "high": q.filter(Threat.severity == 3).count(),
        "medium": q.filter(Threat.severity == 2).count(),
        "low": q.filter(Threat.severity == 1).count()
    }

    country_rows = q.with_entities(
        Threat.country,
        Threat.severity,
        func.count()
    ).group_by(
        Threat.country,
        Threat.severity
    ).all()

    country_summary = {}

    for country, severity, count in country_rows:
        name = country or "unknown"

        if name not in country_summary:
            country_summary[name] = {
                "name": name,
                "count": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }

        country_summary[name]["count"] += count

        if severity == 3:
            country_summary[name]["high"] += count
        elif severity == 2:
            country_summary[name]["medium"] += count
        elif severity == 1:
            country_summary[name]["low"] += count

    countries = sorted(
        country_summary.values(),
        key=lambda item: item["count"],
        reverse=True
    )[:10]

    return {
        "total": q.count(),
        "high": severity_counts["high"],
        "medium": severity_counts["medium"],
        "low": severity_counts["low"],
        "countries": countries,
        "malware": by(Threat.malware_family),
        "types": by(Threat.ioc_type),
        "last_ingest": (
            q.with_entities(func.max(Threat.first_seen)).scalar()
            or dt.datetime.min
        ).isoformat()
    }


# MAP COUNTRY STATISTICS (30 days)
@app.get("/api/map-stats")
def map_stats(s=Depends(db)):
    since = dt.datetime.utcnow() - dt.timedelta(days=30)

    rows = (
        s.query(Threat.country, Threat.severity, func.count())
        .filter(
            Threat.first_seen >= since,
            Threat.country.isnot(None),
            Threat.country.notin_(["UN", "XX", "ZZ", "UK"])
        )
        .group_by(Threat.country, Threat.severity)
        .all()
    )

    summary = {}

    for country, severity, count in rows:
        if country not in summary:
            summary[country] = {
                "name": country,
                "count": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            }

        summary[country]["count"] += count

        if severity == 3:
            summary[country]["high"] += count
        elif severity == 2:
            summary[country]["medium"] += count
        elif severity == 1:
            summary[country]["low"] += count

    return {
        "period_days": 30,
        "countries": sorted(
            summary.values(),
            key=lambda item: item["count"],
            reverse=True
        )
    }



# MALWARE TRENDS
@app.get("/api/trends")
def trends(days: int = 7, u=Depends(user), s=Depends(db)):
    # Keep the existing Free/Pro date-window restrictions.
    # OTX is the source used for malware-family trends.
    q = window(
        s.query(Threat),
        u,
        days,
    ).filter(
        Threat.source == "otx"
    )

    day = func.date(Threat.first_seen)

    rows = q.with_entities(
        day,
        Threat.malware_family,
        func.count(),
    ).filter(
        Threat.malware_family.isnot(None),
        Threat.malware_family != "",
    ).group_by(
        day,
        Threat.malware_family,
    ).all()

    trends_data = []

    for date, family, count in rows:
        clean_family = clean_malware_family(family)

        if not clean_family:
            continue

        trends_data.append({
            "day": str(date),
            "family": clean_family,
            "count": count,
        })

    return trends_data


# IOC TABLE
@app.get("/api/iocs")
def iocs(
    sort: str = "first_seen",
    order: str = "desc",
    type: str = None,
    limit: int = Query(100, le=500),
    days: int = 1,
    u=Depends(user),
    s=Depends(db)
):
    col = getattr(
        Threat,
        sort if sort in (
            "first_seen",
            "severity",
            "value",
            "source",
            "ioc_type"
        ) else "first_seen"
    )

    q = window(s.query(Threat), u, days)

    if type:
        q = q.filter(Threat.ioc_type == type)

    return [
        row(t)
        for t in q.order_by(
            col.desc() if order == "desc" else col.asc()
        ).limit(limit)
    ]


# IOC SEARCH
@app.get("/api/search")
def search(q: str, u=Depends(user), s=Depends(db)):
    qq = window(
        s.query(Threat),
        u,
        3650
    ).filter(
        or_(
            Threat.value == q,
            Threat.value.like(f"%{q}%") if len(q) > 3 else False
        )
    )

    hits = [
        row(t)
        for t in qq.order_by(
            Threat.first_seen.desc()
        ).limit(50)
    ]

    return {
        "query": q,
        "found": bool(hits),
        "hits": hits,
        "scope": "all history" if pro(u) else "last 24h"
    }


# CSV EXPORT
@app.get("/api/export.csv")
def export(days: int = 30, u=Depends(user), s=Depends(db)):
    if not pro(u):
        raise HTTPException(
            402,
            "CSV export requires the Pro plan"
        )

    out = io.StringIO()
    w = csv.writer(out)

    w.writerow([
        "seen",
        "type",
        "value",
        "source",
        "malware",
        "country",
        "severity"
    ])

    for t in window(
        s.query(Threat),
        u,
        days
    ).limit(50000):
        w.writerow([
            t.first_seen,
            t.ioc_type,
            t.value,
            t.source,
            t.malware_family,
            t.country,
            t.severity
        ])

    return Response(
        out.getvalue(),
        media_type="text/csv"
    )


# WEEKLY PDF REPORT

# WEEKLY PDF REPORT
@app.get("/api/report.pdf")
def report(u=Depends(user), s=Depends(db)):
    if not pro(u):
        raise HTTPException(
            402,
            "PDF report requires the Pro plan"
        )

    return Response(
        weekly_pdf(s),
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=weekly-threat-landscape.pdf"
        }
    )
