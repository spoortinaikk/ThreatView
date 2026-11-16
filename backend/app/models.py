import datetime as dt, secrets
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Index, JSON
from .db import Base

def now(): return dt.datetime.utcnow()

class Threat(Base):
    """Unified ThreatModel: every feed is normalized into this schema."""
    __tablename__ = "threats"
    id = Column(Integer, primary_key=True)
    source = Column(String(32), nullable=False)
    ioc_type = Column(String(16), nullable=False)      # ip | domain | url | hash
    value = Column(String(2048), nullable=False)
    country = Column(String(2))
    malware_family = Column(String(64))
    industry = Column(String(64))
    severity = Column(Integer, default=2)               # 1 low .. 3 high
    first_seen = Column(DateTime, default=now, index=True)
    raw = Column(JSON)
    __table_args__ = (UniqueConstraint("source", "value", name="uq_src_val"),
                      Index("ix_value", "value"), Index("ix_type_seen", "ioc_type", "first_seen"))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    tier = Column(String(8), default="free")            # free | pro
    industry = Column(String(64))
    domain = Column(String(255))
    api_key = Column(String(64), unique=True, default=lambda: secrets.token_urlsafe(24))
