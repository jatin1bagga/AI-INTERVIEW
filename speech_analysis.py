# speech_analysis.py  — fast, production-friendly
from faster_whisper import WhisperModel
import torch, os

from faster_whisper import WhisperModel

WHISPER_SIZE = "base"
DEVICE = "cpu"   # or "cuda" if you have NVIDIA GPU
COMPUTE_TYPE = "int8"   # safe on CPU, avoids float16 issue

_model = WhisperModel(WHISPER_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

def transcribe_audio(audio_path: str) -> str:
    """
    Fast transcription using faster-whisper with VAD to skip silence.
    """
    try:
        segments, info = _model.transcribe(
            audio_path,
            language="en",
            vad_filter=True,                        # trims silence; big speed win
            vad_parameters={"min_speech_duration_ms": 300},
            without_timestamps=True,                # faster string assembly
            beam_size=1,                            # greedy = fastest
            temperature=0                           # deterministic
        )
        return " ".join(seg.text for seg in segments).strip()
    except Exception as e:
        return f"Error during transcription: {e}"
