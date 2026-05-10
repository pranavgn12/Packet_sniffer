import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict

bundle = joblib.load("rf_unsw_multiclass.pkl")

model = bundle["model"]
feature_encoder = bundle["feature_encoder"]
label_encoder = bundle["label_encoder"]
feature_columns = bundle["feature_columns"]
cat_cols = bundle["cat_cols"]

app = FastAPI()

class FeatureRow(BaseModel):
    features: Dict[str, Any]

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

    return pred, top

@app.post("/predict")
def predict(row: FeatureRow):
    pred, top = predict_from_features(row.features)

    print("\n" + "=" * 60)
    print("RECEIVED PROFILE")
    print("PREDICTION:", pred)
    print("TOP 3:", ", ".join(f"{c}={p:.4f}" for c, p in top))
    print("=" * 60)

    return {
        "prediction": pred,
        "top3": [{"class": c, "prob": float(p)} for c, p in top]
    }
