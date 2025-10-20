# scripts/evaluate_models.py

import os
import joblib
import pandas as pd
import sys
import numpy as np
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import cross_val_score, KFold, StratifiedKFold
# Adjust path to import feature_engineering
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))
from feature_engineering import add_features

# ---------------- Paths ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "data/augmented_housing.csv")
models_dir = os.path.join(script_dir, "models")

# ---------------- Load Data ---------------- #
data = pd.read_csv(data_path)
data['total_bedrooms'] = data['total_bedrooms'].fillna(data['total_bedrooms'].median())
data = add_features(data)
data = pd.get_dummies(data, columns=['ocean_proximity'])

# ---------------- Helper Function ---------------- #
def preprocess(df, scaler, feature_columns):
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_columns]
    return scaler.transform(df)

# ---------------- Regression Models ---------------- #
regression_models = {
    'price': 'median_house_value',
    'rent': 'monthly_rent',
    'roi': 'roi'
}

print("\nEvaluating Regression Models:\n")
for model_name, target_col in regression_models.items():
    model = joblib.load(os.path.join(models_dir, f"{model_name}_model.pkl"))
    scaler = joblib.load(os.path.join(models_dir, f"{model_name}_scaler.pkl"))
    features = joblib.load(os.path.join(models_dir, f"{model_name}_feature_columns.pkl"))

    X_scaled = preprocess(data, scaler, features)
    y_true = data[target_col].values
    y_pred = model.predict(X_scaled)

    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    print(f"{model_name.capitalize()} model Test RMSE: {rmse:.4f}")

    # Cross-validation RMSE
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = -cross_val_score(model, X_scaled, y_true, scoring='neg_root_mean_squared_error', cv=kf)
    print(f"{model_name.capitalize()} model 5-Fold CV RMSE: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}\n")

# ---------------- Classification Models ---------------- #
classification_models = {
    'neighborhood': 'neighborhood_investment',
    'sell_speed': 'sell_speed'
}

def preprocess_classification(df, feature_columns):
    """
    Ensure all required feature columns exist in df and reorder.
    Missing columns are filled with 0.
    """
    df_copy = df.copy()
    for col in feature_columns:
        if col not in df_copy.columns:
            df_copy[col] = 0
    return df_copy[feature_columns]

print("\nEvaluating Classification Models:\n")
for model_name, target_col in classification_models.items():
    # Load trained model and feature list
    model = joblib.load(os.path.join(models_dir, f"{model_name}_classifier.pkl"))
    features = joblib.load(os.path.join(models_dir, f"{model_name}_feature_columns.pkl"))

    # Preprocess dataset to match training features
    X_eval = preprocess_classification(data, features)
    y_true = data[target_col].values
    y_pred = model.predict(X_eval)

    # Accuracy
    acc = accuracy_score(y_true, y_pred) * 100
    print(f"{model_name.capitalize()} model Test Accuracy: {acc:.2f}%\n")

    # Cross-validation Accuracy
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_eval, y_true, scoring='accuracy', cv=skf)
    print(f"{model_name.capitalize()} model 5-Fold CV Accuracy: {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%\n")

    # Classification report in percentages
    report = classification_report(y_true, y_pred, output_dict=True)
    print(f"{model_name.capitalize()} Classification Report (%):")
    for cls, metrics in report.items():
        if cls not in ['accuracy', 'macro avg', 'weighted avg']:
            precision = metrics['precision'] * 100
            recall = metrics['recall'] * 100
            f1 = metrics['f1-score'] * 100
            print(f"  {cls}: Precision={precision:.2f}%, Recall={recall:.2f}%, F1={f1:.2f}%")
    print()

    # Confusion matrix as percentages
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_true, y_pred)
    cm_percent = cm / cm.sum(axis=1, keepdims=True) * 100
    print(f"{model_name.capitalize()} Confusion Matrix (% of row total):")
    print(cm_percent)
    print("\n" + "-"*60 + "\n")