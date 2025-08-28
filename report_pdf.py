# report_pdf.py
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT

def _pct(x):
    return f"{round(float(x)*100)}%"

def _coaching_suggestions(data: dict) -> list[str]:
    tips = []
    text = data.get("transcription", "") or ""
    words = len(text.split())
    sentiment = (data.get("sentiment") or {}).get("label", "NEUTRAL")
    sscore = float((data.get("sentiment") or {}).get("score", 0))
    clarity = float(data.get("clarity", 0))
    pace = float(data.get("pace", 0))
    conf = float(data.get("confidence", 0))
    overall = float(data.get("overall", 0))
    dur = data.get("duration_sec")  # optional
    wpm = None
    if dur and dur > 0:
        wpm = round(words / (dur/60.0))

    # Clarity
    if clarity < 0.9:
        tips.append("Reduce filler words (um, uh, like). Pause briefly instead of using fillers.")
    # Pace
    if wpm:
        if wpm < 120:
            tips.append(f"Speak a bit faster (current ~{wpm} WPM). Target 130–160 WPM.")
        elif wpm > 180:
            tips.append(f"Slow down slightly (current ~{wpm} WPM). Aim for 130–160 WPM.")
    else:
        if pace < 0.8:
            tips.append("Adjust speaking rate toward the 130–160 WPM range.")
    # Sentiment
    if sentiment == "NEGATIVE" and sscore < 0.5:
        tips.append("Use more positive framing and outcomes when describing experiences.")
    # Confidence
    if conf < 0.6:
        tips.append("Project confidence: steady tone, steady pace, and concise points.")
    # Transcript polish
    if words < 40:
        tips.append("Provide more detail using the STAR method (Situation, Task, Action, Result).")
    if not tips:
        tips.append("Great job! Keep practicing to maintain consistency across answers.")
    return tips

def generate_pdf_report(data: dict, out_path: str):
    """
    data expects keys:
      transcription:str
      sentiment:{label:str, score:float}
      clarity:float  pace:float  confidence:float  overall:float
      duration_sec:float (optional)  username:str (optional)  role:str (optional)
    """
    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            leftMargin=18*mm, rightMargin=18*mm,
                            topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", fontSize=9, leading=12, alignment=TA_LEFT))
    story = []

    username = data.get("username") or "Candidate"
    role = data.get("role") or "Interview Practice"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Title
    story.append(Paragraph(f"<b>AI Interview Feedback Report</b>", styles["Title"]))
    story.append(Paragraph(f"{username} — {role}", styles["Normal"]))
    story.append(Paragraph(f"Generated: {now}", styles["Small"]))
    story.append(Spacer(1, 8))

    # Metrics table
    sent = data.get("sentiment") or {}
    metrics = [
        ["Overall",       _pct(data.get("overall", 0))],
        ["Sentiment",     f'{sent.get("label","").title()} ({_pct(sent.get("score",0))})'],
        ["Clarity",       _pct(data.get("clarity", 0))],
        ["Pace",          _pct(data.get("pace", 0))],
        ["Confidence",    _pct(data.get("confidence", 0))],
    ]
    tbl = Table(metrics, colWidths=[35*mm, 130*mm])
    tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("LEADING", (0,0), (-1,-1), 12),
        ("ALIGN", (1,0), (1,-1), "LEFT"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 10))

    # Suggestions
    tips = _coaching_suggestions(data)
    story.append(Paragraph("<b>Actionable Suggestions</b>", styles["Heading3"]))
    for t in tips:
        story.append(Paragraph(f"• {t}", styles["Normal"]))
    story.append(Spacer(1, 10))

    # Transcript
    story.append(Paragraph("<b>Transcript</b>", styles["Heading3"]))
    transcript = data.get("transcription", "") or ""
    # basic escaping for angle brackets
    transcript = transcript.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    story.append(Paragraph(transcript, styles["Small"]))

    doc.build(story)
    return out_path
