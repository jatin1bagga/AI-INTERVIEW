Here’s a **professional README.md** tailored for your project (“AI Interview Feedback”) that explains what it does, how to run it locally, and how to deploy on **Google Cloud Run**. It’s written so someone picking up the repo can get going fast.

---

```markdown
# 🎤 AI Interview Feedback

An end-to-end system that analyzes interview answers from **audio** (and optional **video**) to give instant feedback on:

- **Speech-to-Text** transcription (Whisper)
- **Sentiment Analysis** (DistilBERT SST-2)
- **Clarity** (filler word detection)
- **Pace** (words per minute scoring)
- **Confidence** (facial emotion heuristic from video)
- **Overall Score** (combined)

Frontend: a simple HTML dashboard  
Backend: Flask API (Python 3.11)  
Deployment: Docker + Cloud Run (GCP)

---

## 🚀 Features

- Upload an **audio file** (`.wav`, `.mp3`)  
- (Optional) Upload a **video file** (`.mp4`, `.avi`, etc.)  
- See **transcript, sentiment, clarity, pace, confidence, and overall score** in real time  
- Containerized with **Docker** for reproducibility  
- Runs on **Cloud Run** with CPU-only Torch + ffmpeg  

---

## 📂 Project Structure

```

ai-interview-feedback/
├── backend/
│   ├── app.py                # Flask API
│   ├── speech\_analysis.py    # Whisper transcription
│   ├── sentiment\_analysis.py # DistilBERT sentiment
│   ├── feedback.py           # Clarity & pace scoring
│   ├── facial\_analysis.py    # Facial emotion heuristic
│   ├── templates/
│   │   └── index.html        # Frontend dashboard
│   └── requirements.txt
├── Dockerfile
└── README.md

````

---

## ⚙️ Setup (Local)

### 1. Clone & install
```bash
git clone https://github.com/your-username/ai-interview-feedback.git
cd ai-interview-feedback/backend

python -m venv venv
source venv/bin/activate    # or venv\Scripts\activate on Windows

pip install -r requirements.txt
````

### 2. Run locally

```bash
python app.py
```

Visit → [http://127.0.0.1:8080](http://127.0.0.1:8080)

---

## 🐳 Run with Docker (Local)

```bash
# build
docker build -t interview-feedback .

# run
docker run -p 8080:8080 interview-feedback
```

---

## ☁️ Deploy on Google Cloud Run

1. **Enable APIs**

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

2. **Build & push container**

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/interview-feedback
```

3. **Deploy**

```bash
gcloud run deploy interview-feedback \
  --image gcr.io/PROJECT_ID/interview-feedback \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory=4Gi \
  --cpu=2 \
  --timeout=900 \
  --concurrency=1
```

4. **Get URL**

```
Service [interview-feedback] revision deployed to [https://your-service-url.run.app]
```

---

## 🔧 Configuration

* `WHISPER_SIZE`: `tiny | base | small` (default: `base`)
* `UPLOAD_DIR`: override upload folder (default: `/tmp/uploads` for Cloud Run)
* `DEFAULT_CONFIDENCE`: default confidence score if no video (default: `0.5`)

Set via environment variables locally or in Cloud Run.

---

## 📊 Example Output

```json
{
  "transcription": "Thank you for the opportunity...",
  "sentiment": { "label": "POSITIVE", "score": 0.87 },
  "clarity": 0.92,
  "pace": 0.88,
  "confidence": 0.7,
  "overall": 0.84
}
```

---

## 📝 Notes & Limitations

* Whisper is CPU-only by default (Cloud Run doesn’t provide GPUs).
* Facial analysis currently uses **ResNet18 stub**, not a real FER-trained model → heuristic only.
* Best for English speech, short clips (<30 min).
* Cold starts may take \~10s while models load; can prewarm during build.

---

## 📌 Roadmap

* ✅ CPU-only deployment on Cloud Run
* ⏳ Replace ResNet18 with a real **FER model** (e.g. RAF-DB)
* ⏳ Add **real-time streaming** (WebSocket + faster-whisper)
* ⏳ Store & compare sessions in **GCS/Firestore**
* ⏳ Build dashboard with **React**

---

## 🧑‍💻 Authors
Jatin Bagga
Chhavi Tokkhi
