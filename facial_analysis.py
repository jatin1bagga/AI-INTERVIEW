# facial_analysis.py  — SPEED OPTIMIZED
import os
import torch
import cv2
import numpy as np
import torchvision.transforms as transforms
from torchvision.models import resnet18
from PIL import Image
from pathlib import Path

# --- Speed knobs (env overridable) ---
FRAME_STRIDE = int(os.getenv("FA_FRAME_STRIDE", "10"))   # analyze every Nth frame
TARGET_WIDTH = int(os.getenv("FA_TARGET_WIDTH", "320"))  # downscale width (px)
MAX_FACES     = int(os.getenv("FA_MAX_FACES", "1"))      # analyze first K faces per frame

# Optional: reduce OpenCV threading overhead on some CPUs
try:
    cv2.setNumThreads(int(os.getenv("OPENCV_NUM_THREADS", "1")))
except Exception:
    pass

# --- Model (still a placeholder for real FER) ---
device = "cuda" if torch.cuda.is_available() else "cpu"
model = resnet18(num_classes=7).to(device).eval()

transform = transforms.Compose([
    transforms.Resize((48, 48)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3),
])

EMOTION_MAP = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"]

# Reuse the cascade (don’t re-create per frame)
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def _is_video(path: str) -> bool:
    return Path(path).suffix.lower() in {".mp4", ".mov", ".avi", ".mkv", ".webm"}

def video_confidence_score(video_path: str) -> float:
    """
    Fast-ish heuristic "confidence" from facial emotion.
    NOTE: resnet18 here is NOT trained for FER; replace with a fine-tuned FER model for real use.
    Returns a float in [0,1].
    """
    if not _is_video(video_path):
        return 0.0

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0.0

    scores = []
    frame_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1

            # Skip frames to reduce compute
            if frame_idx % FRAME_STRIDE != 0:
                continue

            # Downscale to TARGET_WIDTH (keep aspect ratio)
            h, w = frame.shape[:2]
            if w > TARGET_WIDTH:
                scale = TARGET_WIDTH / float(w)
                frame = cv2.resize(
                    frame, (TARGET_WIDTH, int(h * scale)), interpolation=cv2.INTER_AREA
                )

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            # Process at most MAX_FACES faces per sampled frame
            for (x, y, fw, fh) in faces[:MAX_FACES]:
                face = gray[y:y+fh, x:x+fw]
                face = Image.fromarray(face)
                face = transform(face).unsqueeze(0).to(device)

                with torch.no_grad():
                    logits = model(face)
                    pred = int(torch.argmax(logits, dim=1).item()) % len(EMOTION_MAP)
                emotion = EMOTION_MAP[pred]

                # Heuristic mapping → confidence
                if emotion in ("Happy", "Neutral"):
                    scores.append(1.0)
                elif emotion in ("Sad", "Surprise"):
                    scores.append(0.7)
                else:
                    scores.append(0.5)
    finally:
        cap.release()

    return round(float(np.mean(scores)), 2) if scores else 0.0
