from apscheduler.schedulers.background import BackgroundScheduler
from .config import INGEST_INTERVAL_MINUTES
from .ingestors.run import ingest_all


def start():
    sch = BackgroundScheduler(timezone="UTC")

    sch.add_job(
        ingest_all,
        "interval",
        minutes=INGEST_INTERVAL_MINUTES,
        id="ingest",
        next_run_time=__import__("datetime").datetime.utcnow(),
        max_instances=1
    )

    sch.start()

    print(
        "ThreatView scheduler started. Next run:",
        sch.get_job("ingest").next_run_time,
        flush=True
    )

    return sch