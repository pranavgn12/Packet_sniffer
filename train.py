import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OrdinalEncoder, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# -----------------------------
# Load data
# -----------------------------
train_path = "UNSW_NB15_training-set.csv"
test_path = "UNSW_NB15_testing-set.csv"

train_df = pd.read_csv(train_path)
test_df = pd.read_csv(test_path)

# -----------------------------
# Target and feature columns
# -----------------------------
target_col = "attack_cat"

# Drop leakage / unwanted columns
drop_cols = ["id", "label", target_col]

X_train = train_df.drop(columns=drop_cols)
y_train = train_df[target_col].astype(str)

X_test = test_df.drop(columns=drop_cols)
y_test = test_df[target_col].astype(str)

# -----------------------------
# Categorical columns
# -----------------------------
cat_cols = ["proto", "service", "state"]

# Fill missing values before encoding
for col in cat_cols:
    X_train[col] = X_train[col].astype(str).fillna("missing")
    X_test[col] = X_test[col].astype(str).fillna("missing")

# -----------------------------
# Encode features
# -----------------------------
feature_encoder = OrdinalEncoder(
    handle_unknown="use_encoded_value",
    unknown_value=-1
)

X_train[cat_cols] = feature_encoder.fit_transform(X_train[cat_cols])
X_test[cat_cols] = feature_encoder.transform(X_test[cat_cols])

# -----------------------------
# Encode target
# -----------------------------
label_encoder = LabelEncoder()
y_train_enc = label_encoder.fit_transform(y_train)
y_test_enc = label_encoder.transform(y_test)

# -----------------------------
# Train Random Forest
# -----------------------------
rf = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)

rf.fit(X_train, y_train_enc)

# -----------------------------
# Evaluate
# -----------------------------
y_pred = rf.predict(X_test)

print("Accuracy:", accuracy_score(y_test_enc, y_pred))
print("\nClassification Report:\n")
print(classification_report(
    y_test_enc,
    y_pred,
    target_names=label_encoder.classes_
))

print("\nConfusion Matrix:\n")
print(confusion_matrix(y_test_enc, y_pred))

# -----------------------------
# Save model + encoders + feature order
# -----------------------------
bundle = {
    "model": rf,
    "feature_encoder": feature_encoder,
    "label_encoder": label_encoder,
    "feature_columns": X_train.columns.tolist(),
    "cat_cols": cat_cols
}

joblib.dump(bundle, "rf_unsw_multiclass.pkl")
print("\nSaved to rf_unsw_multiclass.pkl")
