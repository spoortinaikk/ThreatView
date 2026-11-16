import io, datetime as dt
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from sqlalchemy import func
from .models import Threat

def weekly_pdf(s):
    since = dt.datetime.utcnow() - dt.timedelta(days=7)
    q = s.query(Threat).filter(Threat.first_seen >= since)
    st = getSampleStyleSheet(); buf = io.BytesIO()
    def table(rows, head):
        t = Table([head] + rows, hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
                               ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                               ("GRID", (0, 0), (-1, -1), .25, colors.grey)])); return t
    fam = q.with_entities(Threat.malware_family, func.count()).group_by(Threat.malware_family).order_by(func.count().desc()).limit(8).all()
    typ = q.with_entities(Threat.ioc_type, func.count()).group_by(Threat.ioc_type).all()
    top = q.filter(Threat.severity == 3).order_by(Threat.first_seen.desc()).limit(10).all()
    doc = [Paragraph("Weekly Threat Landscape", st["Title"]),
           Paragraph(f"Period: last 7 days to {dt.date.today()} · {q.count()} indicators", st["Normal"]), Spacer(1, 12),
           Paragraph("Top malware families", st["Heading2"]), table([[f or "unknown", n] for f, n in fam], ["Family", "Count"]),
           Paragraph("Indicators by type", st["Heading2"]), table([[a, b] for a, b in typ], ["Type", "Count"]),
           Paragraph("Highest-severity indicators to block", st["Heading2"]),
           table([[t.ioc_type, t.value[:70], t.source] for t in top], ["Type", "Value", "Source"])]
    SimpleDocTemplate(buf, pagesize=A4).build(doc); return buf.getvalue()
