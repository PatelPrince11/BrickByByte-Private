# backend/predict_models.py

import os
import pandas as pd
import joblib
from scripts.feature_engineering import add_features

# ---------------- Paths ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

# ---------------- Load Models ---------------- #
def load_model(model_name):
    model = joblib.load(os.path.join(models_dir, f"{model_name}_model.pkl"))
    scaler = joblib.load(os.path.join(models_dir, f"{model_name}_scaler.pkl"))
    features = joblib.load(os.path.join(models_dir, f"{model_name}_feature_columns.pkl"))
    return model, scaler, features

price_model, price_scaler, price_features = load_model("price")
rent_model, rent_scaler, rent_features = load_model("rent")
roi_model, roi_scaler, roi_features = load_model("roi")

# ---------------- Preprocessing Function ---------------- #
def preprocess_input(data_dict, features, scaler):
    """
    Converts raw input dictionary to model-ready scaled DataFrame.
    """
    df = pd.DataFrame(data_dict)
    
    # Feature engineering
    df = add_features(df)
    
    # Ensure all features exist
    for col in features:
        if col not in df.columns:
            df[col] = 0
    
    # Convert booleans to int
    for col in df.select_dtypes('bool').columns:
        df[col] = df[col].astype(int)
    
    # Reorder columns
    df = df[features]
    
    # Scale
    X_scaled = scaler.transform(df)
    
    return X_scaled

# ---------------- Predict Function ---------------- #
def predict_all(data_dict):
    """
    Returns dictionary of predictions for all regression models
    """
    results = {}

    # Price
    X_price = preprocess_input(data_dict, price_features, price_scaler)
    results['price'] = price_model.predict(X_price).tolist()

    # Rent
    X_rent = preprocess_input(data_dict, rent_features, rent_scaler)
    results['rent'] = rent_model.predict(X_rent).tolist()

    # ROI
    X_roi = preprocess_input(data_dict, roi_features, roi_scaler)
    results['roi'] = roi_model.predict(X_roi).tolist()

    return results

# ---------------- Test Script ---------------- #
if __name__ == "__main__":
    sample_data = {
        "longitude": [-122.23, -122.22],
        "latitude": [37.88, 37.86],
        "housing_median_age": [41.0, 21.0],
        "total_rooms": [880.0, 7099.0],
        "total_bedrooms": [129.0, 1106.0],
        "population": [322.0, 2401.0],
        "households": [126.0, 1138.0],
        "median_income": [8.3252, 8.3014],
        "ocean_proximity_<1H OCEAN": [0, 0],
        "ocean_proximity_INLAND": [0, 0],
        "ocean_proximity_ISLAND": [0, 0],
        "ocean_proximity_NEAR BAY": [1, 1],
        "ocean_proximity_NEAR OCEAN": [0, 0]
    }

    predictions = predict_all(sample_data)

    for i in range(len(sample_data["longitude"])):
        print(f"Property {i+1}:")
        print(f"  Predicted Price: {predictions['price'][i]:.2f}")
        print(f"  Predicted Rent: {predictions['rent'][i]:.2f}")
        print(f"  Predicted ROI: {predictions['roi'][i]:.2f}")
        print()