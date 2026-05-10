import json
import time
from collections import deque, Counter
from typing import Any, Dict

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

bundle = joblib.load("rf_unsw_multiclass.pkl")

model = bundle["model"]
feature_encoder = bundle["feature_encoder"]
label_encoder = bundle["label_encoder"]
feature_columns = bundle["feature_columns"]
cat_cols = bundle["cat_cols"]

app = FastAPI(title="Victim IDS API")

HISTORY_FILE = "victim_prediction_history.jsonl"
history = deque(maxlen=1000)

class FeatureRow(BaseModel):
    features: Dict[str, Any]

def log_history(entry: dict) -> None:
    history.append(entry)
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def predict_from_features(features: dict):
    X = pd.DataFrame([features])

    for col in cat_cols:
        if col not in X.columns:
            X[col] = "missing"
        X[col] = X[col].astype(str).fillna("missing")

    X[cat_cols] = feature_encoder.transform(X[cat_cols])

    for col in feature_columns:
        if col not in X.columns:
            X[col] = 0

    X = X[feature_columns]

    pred_idx = model.predict(X)[0]
    pred = label_encoder.inverse_transform([pred_idx])[0]
    probs = model.predict_proba(X)[0]

    top = sorted(
        zip(label_encoder.classes_, probs),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    confidence = float(max(probs))
    return pred, confidence, top

@app.post("/predict")
def predict(row: FeatureRow):
    pred, confidence, top = predict_from_features(row.features)

    entry = {
        "timestamp": time.time(),
        "prediction": pred,
        "confidence": confidence,
        "top3": [{"class": c, "prob": float(p)} for c, p in top],
        "features": row.features
    }
    log_history(entry)

    print("\n" + "=" * 60)
    print("RECEIVED PROFILE")
    print("PREDICTION:", pred)
    print("CONFIDENCE:", f"{confidence:.4f}")
    print("TOP 3:", ", ".join(f"{c}={p:.4f}" for c, p in top))
    print("=" * 60)

    return {
        "prediction": pred,
        "confidence": confidence,
        "top3": [{"class": c, "prob": float(p)} for c, p in top]
    }

@app.get("/history")
def get_history(limit: int = 100):
    items = list(history)[-limit:]
    return {"items": items}

@app.get("/stats")
def get_stats():
    items = list(history)
    counts = Counter(x["prediction"] for x in items)
    latest = items[-1] if items else None
    return {
        "total": len(items),
        "counts": dict(counts),
        "latest": latest
    }
