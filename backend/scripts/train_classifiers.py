# scripts/train_classifiers.py
import os, warnings
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, balanced_accuracy_score
import joblib
from feature_engineering import add_features

# ---------------- Paths ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "../data/augmented_housing.csv")
models_dir = os.path.join(script_dir, "../models")
os.makedirs(models_dir, exist_ok=True)

RANDOM_STATE = 42

print(f"Loading dataset from: {data_path}")
data = pd.read_csv(data_path)

print("Cleaning data...")
if "total_bedrooms" in data.columns:
    data["total_bedrooms"] = data["total_bedrooms"].fillna(data["total_bedrooms"].median())

print("Applying feature engineering...")
data = add_features(data)

# One-hot encode ocean_proximity
if "ocean_proximity" in data.columns and data["ocean_proximity"].dtype == "object":
    data = pd.get_dummies(data, columns=["ocean_proximity"], drop_first=False)

# Targets
classification_tasks = {
    "neighborhood": "neighborhood_investment",
    "sell_speed": "sell_speed",
}

# Known leaky columns
BASE_DROP = {"monthly_rent","roi","neighborhood_investment","sell_speed","median_house_value"}
POSSIBLE_LEAKY = {"days_on_market","price_bin","roi_bin"}

def leakage_sentinel_drop(X, y, task_name):
    """Drop any single column that perfectly determines y"""
    dropped = []
    ys = y.astype(str)
    for col in X.columns:
        xs = X[col].astype(str)
        m = pd.DataFrame({"x": xs, "y": ys}).drop_duplicates()
        if m.groupby("x")["y"].nunique().max() == 1 and m["x"].nunique() >= ys.nunique():
            warnings.warn(f"[{task_name}] '{col}' perfectly determines the label. Dropping.")
            dropped.append(col)
    return X.drop(columns=dropped) if dropped else X, dropped

for model_name, target_col in classification_tasks.items():
    print(f"\n=== Training {model_name} classifier ===")
    if target_col not in data.columns:
        warnings.warn(f"Missing target '{target_col}', skipping.")
        continue

    y = data[target_col]
    X = data.drop(columns=[c for c in BASE_DROP if c in data.columns])

    # Drop suspicious columns if they exist
    susp = [c for c in POSSIBLE_LEAKY if c in X.columns]
    if susp:
        warnings.warn(f"[{model_name}] Dropping suspicious possibly-leaky columns: {susp}")
        X = X.drop(columns=susp)

    # Deduplicate (X,y) rows
    before = len(X)
    dedup = pd.concat([X, y], axis=1).drop_duplicates()
    X, y = dedup.drop(columns=[target_col]), dedup[target_col]
    if len(X) < before:
        print(f"Deduplicated {before - len(X)} rows.")

    # Single-column leakage sentinel
    X, dropped_cols = leakage_sentinel_drop(X, y, model_name)
    if dropped_cols:
        print(f"[{model_name}] Leakage sentinel dropped: {dropped_cols}")

    print(f"[{model_name}] Class counts:\n{y.value_counts()}\n")

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE
    )

    # Regularized RandomForest
    clf = RandomForestClassifier(
        n_estimators=120,
        max_depth=5,
        min_samples_leaf=25,
        min_samples_split=50,
        max_features=0.3,
        min_impurity_decrease=1e-4,
        bootstrap=True,
        oob_score=True,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    # CV on train only
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(clf, X_train, y_train, cv=skf, scoring="accuracy", n_jobs=-1)
    print(f"{model_name.capitalize()} CV Acc: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # Fit & evaluate
    clf.fit(X_train, y_train)
    if hasattr(clf, "oob_score_"):
        print(f"{model_name.capitalize()} OOB Score: {clf.oob_score_:.4f}")
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    bal = balanced_accuracy_score(y_test, y_pred)
    
    print(f"{model_name.capitalize()} Test Accuracy: {acc:.4f} | Balanced Acc: {bal:.4f}")
    print(f"{model_name.capitalize()} Classification Report:")
    print(classification_report(y_test, y_pred))
    print(f"{model_name.capitalize()} Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # Save model + feature list (NO SCALER for classifiers)
    joblib.dump(clf, os.path.join(models_dir, f"{model_name}_classifier.pkl"))
    joblib.dump(X.columns.tolist(), os.path.join(models_dir, f"{model_name}_feature_columns.pkl"))
    print(f"Saved {model_name}_classifier.pkl and {model_name}_feature_columns.pkl")

print("\n✅ Trained RandomForest classifiers (without scalers)")