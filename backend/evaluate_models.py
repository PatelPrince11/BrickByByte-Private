# backend/evaluate_models.py

import os
import joblib
import pandas as pd
import sys
import numpy as np
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold
# Adjust path to import feature_engineering
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
from scripts.feature_engineering import add_features

# ---------------- Paths ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "data/augmented_housing.csv")
models_dir = os.path.join(script_dir, "models")

# ---------------- Load Data ---------------- #
data = pd.read_csv(data_path)
data['total_bedrooms'] = data['total_bedrooms'].fillna(data['total_bedrooms'].median())
data = add_features(data)

# ---------------- Regression Helper ---------------- #
def preprocess_regression(df, feature_columns, scaler):
    """Align features and scale them for regression models"""
    df_copy = df.copy()
    # Add missing columns with 0
    for col in feature_columns:
        if col not in df_copy.columns:
            df_copy[col] = 0
    # Keep only feature columns in the correct order
    df_copy = df_copy[feature_columns]
    return scaler.transform(df_copy)

# ---------------- Regression Models ---------------- #
regression_models = {
    "price": "median_house_value",
    "rent": "monthly_rent",
    "roi": "roi"
}

print("\n=== Regression Model Evaluation ===\n")
for model_name, target_col in regression_models.items():
    model_path = os.path.join(models_dir, f"{model_name}_model.pkl")
    scaler_path = os.path.join(models_dir, f"{model_name}_scaler.pkl")
    features_path = os.path.join(models_dir, f"{model_name}_feature_columns.pkl")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    feature_columns = joblib.load(features_path)

    X_scaled = preprocess_regression(data, feature_columns, scaler)
    y_true = data[target_col].values
    y_pred = model.predict(X_scaled)

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"{model_name.capitalize()} model Test RMSE: {rmse:.2f}")
    print(f"Target range: {y_true.min():,.2f} - {y_true.max():,.2f}")
    print(f"Predicted range: {y_pred.min():,.2f} - {y_pred.max():,.2f}\n")

# ---------------- Classification Helper ---------------- #
def preprocess_classification(df, feature_columns):
    """Align features for classification models"""
    df_copy = df.copy()
    for col in feature_columns:
        if col not in df_copy.columns:
            df_copy[col] = 0
    return df_copy[feature_columns]

# ---------------- Classification Models ---------------- #
classification_models = {
    "neighborhood": "neighborhood_investment",
    "sell_speed": "sell_speed"
}

print("\n=== Classification Model Evaluation ===\n")
for model_name, target_col in classification_models.items():
    model_path = os.path.join(models_dir, f"{model_name}_classifier.pkl")
    features_path = os.path.join(models_dir, f"{model_name}_feature_columns.pkl")

    model = joblib.load(model_path)
    feature_columns = joblib.load(features_path)

    X_eval = preprocess_classification(data, feature_columns)
    y_true = data[target_col].values
    y_pred = model.predict(X_eval)

    acc = accuracy_score(y_true, y_pred) * 100
    print(f"{model_name.capitalize()} model Test Accuracy: {acc:.2f}%")

    # Stratified CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_eval, y_true, scoring="accuracy", cv=skf)
    print(f"{model_name.capitalize()} model 5-Fold CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%\n")

    # Classification report
    report = classification_report(y_true, y_pred, output_dict=True)
    print(f"{model_name.capitalize()} Classification Report (%):")
    for cls, metrics in report.items():
        if cls not in ["accuracy", "macro avg", "weighted avg"]:
            print(
                f"  {cls}: Precision={metrics['precision']*100:.2f}%, "
                f"Recall={metrics['recall']*100:.2f}%, F1={metrics['f1-score']*100:.2f}%"
            )

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    cm_percent = cm / cm.sum(axis=1, keepdims=True) * 100
    print(f"{model_name.capitalize()} Confusion Matrix (% of row total):\n{cm_percent}\n")
    print("-"*60 + "\n")