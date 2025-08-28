import re

# List of common filler words
FILLERS = ["um", "uh", "like", "you know", "so", "actually", "basically"]

def clarity_score(transcript: str) -> float:
    """
    Returns clarity score (0-1) based on filler words.
    More filler words → lower score.
    """
    words = transcript.lower().split()
    filler_count = sum(words.count(f) for f in FILLERS)
    total_words = max(len(words), 1)
    score = 1 - (filler_count / total_words)  # higher is better
    return round(score, 2)

def pace_score(transcript: str, duration_sec: float) -> float:
    """
    Returns normalized speaking rate score (0-1).
    Ideal speaking rate ~130-160 WPM.
    """
    words = len(transcript.split())
    wpm = words / (duration_sec / 60)
    
    if wpm < 100:
        score = wpm / 130  # too slow
    elif wpm > 180:
        score = 180 / wpm  # too fast
    else:
        score = 1.0  # ideal range

    return round(min(score,1.0),2)
