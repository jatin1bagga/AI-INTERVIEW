from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Load pre-trained model and tokenizer (small & fast)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

def sentiment_score(text: str) -> dict:
    """
    Returns positivity score of input text.
    Output: {"label": "POSITIVE"/"NEGATIVE", "score": float 0-1}
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model(**inputs)
    probs = F.softmax(outputs.logits, dim=-1)
    
    # 0 = NEGATIVE, 1 = POSITIVE
    label = "POSITIVE" if torch.argmax(probs) == 1 else "NEGATIVE"
    score = probs[0][1].item()  # probability of POSITIVE
    return {"label": label, "score": round(score, 2)}
