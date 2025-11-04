import pandas as pd
import numpy as np
import joblib
import os
from sklearn.metrics import mean_squared_error

script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "data/augmented_housing.csv")
models_dir = os.path.join(script_dir, "models")

print("=== COMPREHENSIVE MODEL DIAGNOSTIC ===")

# Load data
data = pd.read_csv(data_path)
print(f"Data shape: {data.shape}")

# Test each model
models_to_test = [
    ("price", "median_house_value"),
    ("rent", "monthly_rent"), 
    ("roi", "roi")
]

for model_name, target_col in models_to_test:
    print(f"\n{'='*50}")
    print(f"Testing {model_name} model")
    print(f"{'='*50}")
    
    try:
        # Load model components
        model = joblib.load(os.path.join(models_dir, f"{model_name}_model.pkl"))
        scaler = joblib.load(os.path.join(models_dir, f"{model_name}_scaler.pkl"))
        features = joblib.load(os.path.join(models_dir, f"{model_name}_feature_columns.pkl"))
        
        print(f"✅ Model loaded: {type(model)}")
        print(f"✅ Scaler loaded: {type(scaler)}")
        print(f"✅ Features: {len(features)} columns")
        
        # Prepare test data
        X_test = data[features]
        y_true = data[target_col]
        
        # Scale features
        X_scaled = scaler.transform(X_test)
        
        # Make predictions
        y_pred = model.predict(X_scaled)
        
        # Calculate metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        
        print(f"Target stats - Min: {y_true.min():.2f}, Max: {y_true.max():.2f}, Mean: {y_true.mean():.2f}")
        print(f"Prediction stats - Min: {y_pred.min():.2f}, Max: {y_pred.max():.2f}, Mean: {y_pred.mean():.2f}")
        print(f"RMSE: {rmse:.2f}")
        
        # Test single prediction
        single_pred = model.predict(X_scaled[:1])[0]
        print(f"Single test prediction: {single_pred:.2f} vs actual: {y_true.iloc[0]:.2f}")
        
        # Check for constant predictions
        unique_preds = np.unique(y_pred)
        if len(unique_preds) < 10:
            print(f"⚠️  Warning: Only {len(unique_preds)} unique predictions (might be predicting constant values)")
            print(f"Unique values: {unique_preds}")
            
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")

# Test classification models
print(f"\n{'='*50}")
print("Testing Classification Models")
print(f"{'='*50}")

classification_models = ["neighborhood", "sell_speed"]
for model_name in classification_models:
    try:
        model = joblib.load(os.path.join(models_dir, f"{model_name}_classifier.pkl"))
        features = joblib.load(os.path.join(models_dir, f"{model_name}_feature_columns.pkl"))
        
        print(f"\n{model_name} classifier:")
        print(f"Model: {type(model)}")
        print(f"Features: {len(features)}")
        
        # Test prediction
        test_input = {feature: 0 for feature in features}
        # Set some basic values
        for col in ['longitude', 'latitude', 'total_rooms', 'median_income']:
            if col in test_input:
                test_input[col] = data[col].mean()
        
        df_test = pd.DataFrame([test_input])[features]
        prediction = model.predict(df_test)[0]
        print(f"Test prediction: {prediction}")
        
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")