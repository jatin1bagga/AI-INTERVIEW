from flask import Flask, request, jsonify, render_template, send_file
from pathlib import Path
import os
import soundfile as sf

from feedback import clarity_score, pace_score
from speech_analysis import transcribe_audio
from sentiment_analysis import sentiment_score
from facial_analysis import video_confidence_score

from report_pdf import generate_pdf_report  # NEW

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

REPORTS_DIR = Path("reports")               # NEW
REPORTS_DIR.mkdir(exist_ok=True)            # NEW

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No audio file uploaded (field name: file)"}), 400

    audio_f = request.files["file"]
    if not audio_f.filename:
        return jsonify({"error": "Empty audio filename"}), 400

    audio_path = UPLOAD_FOLDER / audio_f.filename
    audio_f.save(str(audio_path))

    # Optional video
    video_path = None
    if "video" in request.files and request.files["video"].filename:
        video_f = request.files["video"]
        video_path = UPLOAD_FOLDER / video_f.filename
        video_f.save(str(video_path))

    # Transcribe
    text = transcribe_audio(str(audio_path))

    # Sentiment
    sentiment = sentiment_score(text)

    # Fast duration
    try:
        info = sf.info(str(audio_path))
        duration_sec = (info.frames / float(info.samplerate)) if info.samplerate else 60.0
    except Exception:
        duration_sec = 60.0

    # Clarity & Pace
    clarity = clarity_score(text)
    pace = pace_score(text, duration_sec)

    # Confidence (video optional)
    confidence = video_confidence_score(str(video_path)) if video_path else 0.5

    overall = round((clarity + pace + sentiment["score"] + confidence) / 4, 2)

    return jsonify({
        "transcription": text,
        "sentiment": sentiment,
        "clarity": clarity,
        "pace": pace,
        "confidence": confidence,
        "overall": overall,
        "duration_sec": round(duration_sec, 2)  # <-- NEW for PDF WPM
    })

@app.route("/api/report", methods=["POST"])  # NEW
def make_report():
    """
    POST JSON with keys from /api/analyze response (+ optional username, role).
    Returns a PDF file.
    """
    data = request.get_json(force=True, silent=True) or {}
    required = ["transcription", "sentiment", "clarity", "pace", "confidence", "overall"]
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    username = (data.get("username") or "candidate").replace(" ", "_")
    out_path = REPORTS_DIR / f"report_{username}.pdf"
    generate_pdf_report(data, str(out_path))
    return send_file(str(out_path), as_attachment=True,
                     download_name=out_path.name, mimetype="application/pdf")

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
