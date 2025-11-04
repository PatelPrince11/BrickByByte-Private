import requests
import json
import pandas as pd
import joblib
import os

# Load the models and feature columns directly to compare
models_dir = "models"

print("=== LOADING MODEL COMPONENTS ===")
price_features = joblib.load(os.path.join(models_dir, "price_feature_columns.pkl"))
rent_features = joblib.load(os.path.join(models_dir, "rent_feature_columns.pkl")) 
roi_features = joblib.load(os.path.join(models_dir, "roi_feature_columns.pkl"))

print(f"Price features ({len(price_features)}): {price_features}")
print(f"Rent features ({len(rent_features)}): {rent_features}")
print(f"ROI features ({len(roi_features)}): {roi_features}")

# Test data that should give good predictions
test_data = {
    "longitude": -122.23,
    "latitude": 37.88,
    "housing_median_age": 25,
    "total_rooms": 1500,
    "total_bedrooms": 300,
    "population": 800,
    "households": 300,
    "median_income": 4.0,
    "ocean_proximity": "NEAR BAY"
}

print(f"\n=== TEST DATA ===")
print(json.dumps(test_data, indent=2))

# Test API
BASE_URL = "http://127.0.0.1:8000"

print(f"\n=== API RESPONSES ===")
endpoints = ["price", "rent", "roi"]

for endpoint in endpoints:
    try:
        response = requests.post(
            f"{BASE_URL}/predict/{endpoint}",
            json=test_data,
            timeout=10
        )
        
        print(f"\n{endpoint.upper()}:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"API Prediction: {result}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Failed: {e}")

# Now test the models directly with the same data
print(f"\n=== DIRECT MODEL PREDICTIONS ===")

def test_model_directly(model_name, features_list, test_data):
    """Test model directly without API"""
    try:
        model = joblib.load(os.path.join(models_dir, f"{model_name}_model.pkl"))
        scaler = joblib.load(os.path.join(models_dir, f"{model_name}_scaler.pkl"))
        
        # Create DataFrame and preprocess exactly like training
        df = pd.DataFrame([test_data])
        
        # Feature engineering
        df['rooms_per_household'] = df['total_rooms'] / df['households']
        df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
        df['population_per_household'] = df['population'] / df['households']
        
        # One-hot encode ocean_proximity
        ocean_categories = ['<1H OCEAN', 'INLAND', 'ISLAND', 'NEAR BAY', 'NEAR OCEAN']
        for category in ocean_categories:
            col_name = f'ocean_proximity_{category}'
            df[col_name] = (df['ocean_proximity'] == category).astype(int)
        
        df = df.drop('ocean_proximity', axis=1)
        
        # Ensure all columns exist
        for col in features_list:
            if col not in df.columns:
                df[col] = 0
        
        df = df[features_list]
        
        # Scale and predict
        X_scaled = scaler.transform(df)
        prediction = model.predict(X_scaled)[0]
        
        return prediction, df.columns.tolist()
        
    except Exception as e:
        return f"Error: {e}", []

# Test each model directly
for model_name, features in [("price", price_features), ("rent", rent_features), ("roi", roi_features)]:
    print(f"\n{model_name.upper()} DIRECT TEST:")
    prediction, used_cols = test_model_directly(model_name, features, test_data)
    print(f"Direct prediction: {prediction}")
    print(f"Used {len(used_cols)} columns")
    print(f"First 10 columns: {used_cols[:10]}")