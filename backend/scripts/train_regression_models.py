# scripts/train_regression_models.py
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
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

# ---------------- Convert Boolean Columns to Integers ---------------- #
bool_cols = [col for col in data.columns if col.startswith("ocean_proximity")]
data[bool_cols] = data[bool_cols].astype(int)

# ---------------- Function to Train One Model ---------------- #
def train_xgb_regression(target_col, model_name):
    print(f"\n{'='*60}")
    print(f"Training {model_name} model for target: {target_col}")
    print(f"{'='*60}")

    # Define ALL target columns (never use these as features)
    ALL_TARGETS = ['monthly_rent', 'roi', 'neighborhood_investment', 'sell_speed', 'median_house_value']
    
    # Verify target exists
    if target_col not in data.columns:
        raise ValueError(f"Target column '{target_col}' not found in data!")
    
    # Drop ALL target columns from features (including the one we're predicting)
    X = data.drop(columns=ALL_TARGETS, errors='ignore')
    y = data[target_col]
    
    print(f"\nDataset Info:")
    print(f"  Features shape: {X.shape}")
    print(f"  Target shape: {y.shape}")
    print(f"  Target range: [{y.min():.2f}, {y.max():.2f}]")
    print(f"  Target mean: {y.mean():.2f}")
    print(f"  Feature columns: {X.columns.tolist()[:5]}... (showing first 5)")

    # Save feature columns
    joblib.dump(X.columns.tolist(), os.path.join(models_dir, f"{model_name}_feature_columns.pkl"))
    print(f"  Saved feature columns: {len(X.columns.tolist())} features")

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, os.path.join(models_dir, f"{model_name}_scaler.pkl"))
    print(f"  Fitted and saved StandardScaler")

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    print(f"\nTrain/Test Split:")
    print(f"  Training samples: {len(X_train)}")
    print(f"  Testing samples: {len(X_test)}")

    # Initialize XGBRegressor with better hyperparameters
    xgb_model = XGBRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        max_depth=8,  # Increased from 6
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        objective='reg:squarederror',
        random_state=42,
        n_jobs=-1
    )

    # Fit model with early stopping
    print(f"\nTraining XGBoost model...")
    try:
        xgb_model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            early_stopping_rounds=50,
            verbose=False
        )
    except TypeError:
        try:
            import xgboost as xgb
            xgb_model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                callbacks=[xgb.callback.EarlyStopping(rounds=50, save_best=True)],
                verbose=False
            )
        except Exception:
            print("  Warning: early stopping not supported - fitting without it.")
            xgb_model.fit(X_train, y_train)

    # Predict & evaluate
    y_pred_train = xgb_model.predict(X_train)
    y_pred_test = xgb_model.predict(X_test)
    
    rmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train))
    rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)

    # Cross-validation RMSE
    cv_scores = cross_val_score(
        xgb_model, X_scaled, y, cv=5, scoring='neg_root_mean_squared_error', n_jobs=-1
    )
    cv_rmse = -np.mean(cv_scores)
    cv_std = np.std(cv_scores)

    # Print results
    print(f"\n{'='*60}")
    print(f"MODEL PERFORMANCE - {model_name.upper()}")
    print(f"{'='*60}")
    print(f"Training RMSE:   ${rmse_train:,.2f}")
    print(f"Test RMSE:       ${rmse_test:,.2f}")
    print(f"Training R²:     {r2_train:.4f}")
    print(f"Test R²:         {r2_test:.4f}")
    print(f"CV RMSE (5-fold): ${cv_rmse:,.2f} ± ${cv_std:,.2f}")
    
    # Show sample predictions
    print(f"\nSample Predictions (first 5 test samples):")
    for i in range(min(5, len(y_test))):
        print(f"  Actual: ${y_test.iloc[i]:,.2f}  |  Predicted: ${y_pred_test[i]:,.2f}")

    # Save model
    joblib.dump(xgb_model, os.path.join(models_dir, f"{model_name}_model.pkl"))
    print(f"\n✓ Saved {model_name} model, scaler, and feature columns.")
    print(f"{'='*60}\n")

# ---------------- Train All Models ---------------- #
train_xgb_regression("median_house_value", "price")
train_xgb_regression("monthly_rent", "rent")
train_xgb_regression("roi", "roi")

print("\n" + "="*60)
print("ALL REGRESSION MODELS TRAINED SUCCESSFULLY!")
print("="*60)
print("\nNext steps:")
print("1. Run 'python evaluate_models.py' to verify model performance")
print("2. Restart your FastAPI backend server")
print("3. Test predictions from the frontend")