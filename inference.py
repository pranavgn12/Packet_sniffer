import pandas as pd
import joblib

bundle = joblib.load("rf_unsw_multiclass.pkl")

model = bundle["model"]
feature_encoder = bundle["feature_encoder"]
label_encoder = bundle["label_encoder"]
feature_columns = bundle["feature_columns"]
cat_cols = bundle["cat_cols"]

# -----------------------------
# Load test dataset
# -----------------------------
df = pd.read_csv("UNSW_NB15_testing-set.csv")

# Pick one real row
row = df.iloc[0]

# Save ground truth
ground_truth = row["attack_cat"]

# Remove non-feature columns
X = row.drop(labels=["id", "label", "attack_cat"])

# Convert to DataFrame
X = pd.DataFrame([X])

# Encode categorical columns
for col in cat_cols:
    X[col] = X[col].astype(str).fillna("missing")

X[cat_cols] = feature_encoder.transform(X[cat_cols])

# Ensure correct column order
X = X[feature_columns]

# Predict
pred_idx = model.predict(X)[0]
prediction = label_encoder.inverse_transform([pred_idx])[0]

# Probabilities
probs = model.predict_proba(X)[0]

print("\nGround Truth :", ground_truth)
print("Prediction   :", prediction)

print("\nClass Probabilities:\n")

for cls, prob in sorted(
    zip(label_encoder.classes_, probs),
    key=lambda x: x[1],
    reverse=True
):
    print(f"{cls:15} {prob:.4f}")
