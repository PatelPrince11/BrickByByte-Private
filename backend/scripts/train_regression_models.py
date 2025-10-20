# scripts/train_regression_models.py

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
from feature_engineering import add_features

# ---------------- Paths ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "../data/augmented_housing.csv")
models_dir = os.path.join(script_dir, "../models")
os.makedirs(models_dir, exist_ok=True)

# ---------------- Load Data ---------------- #
print("Loading augmented_housing.csv ...")
data = pd.read_csv(data_path)

# ---------------- Clean Data ---------------- #
data['total_bedrooms'] = data['total_bedrooms'].fillna(data['total_bedrooms'].median())

# ---------------- Feature Engineering ---------------- #
data = add_features(data)
data = pd.get_dummies(data, columns=['ocean_proximity'])

# ---------------- Function to Train One Model ---------------- #
def train_xgb_regression(target_col, model_name):
    print(f"\nTraining {model_name} model...")

    # Drop other targets
    drop_cols = ['monthly_rent', 'roi', 'neighborhood_investment', 'sell_speed', 'median_house_value']
    drop_cols.remove(target_col)
    X = data.drop(drop_cols, axis=1)
    y = data[target_col]

    # Save feature columns
    joblib.dump(X.columns.tolist(), os.path.join(models_dir, f"{model_name}_feature_columns.pkl"))

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, os.path.join(models_dir, f"{model_name}_scaler.pkl"))

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    # Initialize XGBRegressor
    xgb_model = XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=6,
        objective='reg:squarederror',
        random_state=42
    )

    # Fit model with early stopping
    try:
        xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=50,
            verbose=False
        )
    except TypeError:
        # Newer xgboost uses callback-based early stopping
        try:
            import xgboost as xgb
            xgb_model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                callbacks=[xgb.callback.EarlyStopping(rounds=50, save_best=True)],
                verbose=False
            )
        except Exception:
            # Fallback: fit without early stopping
            print("Warning: early stopping not supported by this xgboost build — fitting without it.")
            xgb_model.fit(X_train, y_train)

    # Predict & evaluate
    y_pred = xgb_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    # Cross-validation RMSE
    cv_scores = cross_val_score(
        xgb_model, X_scaled, y, cv=5, scoring='neg_root_mean_squared_error'
    )
    cv_rmse = -np.mean(cv_scores)

    print(f"{model_name.capitalize()} Cross-Validation RMSE: {cv_rmse:.4f}")
    print(f"{model_name.capitalize()} Test Set RMSE: {rmse:.4f}")

    # Save model
    joblib.dump(xgb_model, os.path.join(models_dir, f"{model_name}_model.pkl"))
    print(f"Saved {model_name} model, scaler, and feature columns.")

# ---------------- Train All Models ---------------- #
train_xgb_regression("median_house_value", "price")
train_xgb_regression("monthly_rent", "rent")
train_xgb_regression("roi", "roi")

print("\nAll regression models trained, evaluated, and saved successfully!")
