import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///threatview.db")
OTX_API_KEY = os.getenv("OTX_API_KEY", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
MAIL_FROM = os.getenv("MAIL_FROM", "alerts@threatview.example")
INGEST_INTERVAL_MINUTES = int(os.getenv("INGEST_INTERVAL_MINUTES", "60"))
URLHAUS_AUTH_KEY = os.getenv("URLHAUS_AUTH_KEY", "")
MAXMIND_DB_PATH = os.getenv(
    "MAXMIND_DB_PATH",
    
    "/data/geoip/GeoLite2-Country.mmdb"
)