from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import joblib
import numpy as np
import pandas as pd
import os

# Initialize FastAPI app
app = FastAPI(title="BrickByByte API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request validation
class HouseFeatures(BaseModel):
    longitude: float
    latitude: float
    housing_median_age: float
    total_rooms: float
    total_bedrooms: float
    population: float
    households: float
    median_income: float
    ocean_proximity: str
    renovation_budget: Optional[float] = 0

# Load models
models_dir = os.path.join(os.path.dirname(__file__), "models")

# Initialize variables
price_model = rent_model = roi_model = None
neighborhood_model = sell_speed_model = None
price_scaler = rent_scaler = roi_scaler = None
price_features = rent_features = roi_features = []
neighborhood_features = sell_speed_features = []

def load_models():
    """Load all ML models and their components"""
    global price_model, rent_model, roi_model, neighborhood_model, sell_speed_model
    global price_scaler, rent_scaler, roi_scaler
    global price_features, rent_features, roi_features, neighborhood_features, sell_speed_features
    
    try:
        # Load regression models
        price_model = joblib.load(os.path.join(models_dir, "price_model.pkl"))
        price_scaler = joblib.load(os.path.join(models_dir, "price_scaler.pkl"))
        price_features = joblib.load(os.path.join(models_dir, "price_feature_columns.pkl"))
        
        rent_model = joblib.load(os.path.join(models_dir, "rent_model.pkl"))
        rent_scaler = joblib.load(os.path.join(models_dir, "rent_scaler.pkl"))
        rent_features = joblib.load(os.path.join(models_dir, "rent_feature_columns.pkl"))
        
        roi_model = joblib.load(os.path.join(models_dir, "roi_model.pkl"))
        roi_scaler = joblib.load(os.path.join(models_dir, "roi_scaler.pkl"))
        roi_features = joblib.load(os.path.join(models_dir, "roi_feature_columns.pkl"))
        
        # Load classification models
        neighborhood_model = joblib.load(os.path.join(models_dir, "neighborhood_classifier.pkl"))
        neighborhood_features = joblib.load(os.path.join(models_dir, "neighborhood_feature_columns.pkl"))
        
        sell_speed_model = joblib.load(os.path.join(models_dir, "sell_speed_classifier.pkl"))
        sell_speed_features = joblib.load(os.path.join(models_dir, "sell_speed_feature_columns.pkl"))
        
        print("✅ All models loaded successfully!")
        print(f"Price features: {len(price_features)} columns")
        print(f"Rent features: {len(rent_features)} columns") 
        print(f"ROI features: {len(roi_features)} columns")
        print(f"Neighborhood features: {len(neighborhood_features)} columns")
        print(f"Sell speed features: {len(sell_speed_features)} columns")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        print("Using fallback dummy models...")
        return False

# Load models on startup
models_loaded = load_models()

def prepare_features_for_model(features: HouseFeatures, feature_columns, scaler=None):
    """Prepare features for a specific model using the same preprocessing as training"""
    # Create DataFrame from input
    input_data = features.dict()
    
    # Remove renovation_budget if not in model features
    if 'renovation_budget' in input_data and 'renovation_budget' not in feature_columns:
        del input_data['renovation_budget']
    
    df = pd.DataFrame([input_data])
    
    # Apply the same feature engineering as in training
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']
    
    # CRITICAL: One-hot encode ocean_proximity (same as training)
    ocean_categories = ['<1H OCEAN', 'INLAND', 'ISLAND', 'NEAR BAY', 'NEAR OCEAN']
    for category in ocean_categories:
        col_name = f'ocean_proximity_{category}'
        df[col_name] = (df['ocean_proximity'] == category).astype(int)
    
    # Drop original ocean_proximity column
    df = df.drop('ocean_proximity', axis=1)
    
    # Debug: Show what columns we have vs what model expects
    print(f"Input columns after processing: {len(df.columns)}")
    print(f"Model expects: {len(feature_columns)} columns")
    
    # Check for missing columns
    missing_cols = [col for col in feature_columns if col not in df.columns]
    if missing_cols:
        print(f"⚠️  Missing columns: {missing_cols}")
    
    # Ensure all required columns exist and in correct order
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0  # Add missing columns with default value
    
    # Reorder columns to match training exactly
    df = df[feature_columns]
    
    # Debug: Show first few columns to verify order
    print(f"First 10 columns for model: {list(df.columns)[:10]}")
    
    # Apply scaling if scaler is provided (for regression models)
    if scaler is not None:
        X_scaled = scaler.transform(df)
        print(f"Input shape after scaling: {X_scaled.shape}")
        return X_scaled
    else:
        print(f"Input shape: {df.values.shape}")
        return df.values

# Fallback dummy model class
class DummyModel:
    def predict(self, X):
        return [np.random.uniform(100000, 500000)]
    def predict_proba(self, X):
        return [[0.3, 0.4, 0.3]]

# API endpoints
@app.get("/")
def root():
    return {
        "message": "BrickByByte Real Estate API", 
        "status": "running",
        "models_loaded": models_loaded,
        "endpoints": {
            "price_prediction": "/predict/price",
            "rent_prediction": "/predict/rent",
            "roi_prediction": "/predict/roi", 
            "neighborhood_insights": "/predict/neighborhood",
            "sell_speed": "/predict/sell_speed"
        }
    }

@app.post("/predict/price")
def predict_price(features: HouseFeatures):
    try:
        if not models_loaded or price_model is None:
            return {"prediction": 350000.0}
        
        print(f"\n=== PRICE PREDICTION ===")
        X = prepare_features_for_model(features, price_features, price_scaler)
        prediction = price_model.predict(X)[0]
        print(f"Raw prediction: {prediction}")
        print(f"Final prediction: ${prediction:,.2f}")
        return {"prediction": round(float(prediction), 2)}
    except Exception as e:
        print(f"Price prediction error: {e}")
        return {"prediction": 350000.0}

@app.post("/predict/rent")
def predict_rent(features: HouseFeatures):
    try:
        if not models_loaded or rent_model is None:
            return {"prediction": 2500.0}
        
        print(f"\n=== RENT PREDICTION ===")
        X = prepare_features_for_model(features, rent_features, rent_scaler)
        prediction = rent_model.predict(X)[0]
        print(f"Raw prediction: {prediction}")
        print(f"Final prediction: ${prediction:,.2f}")
        return {"prediction": round(float(prediction), 2)}
    except Exception as e:
        print(f"Rent prediction error: {e}")
        return {"prediction": 2500.0}

@app.post("/predict/roi")
def predict_roi(features: HouseFeatures):
    try:
        if not models_loaded or roi_model is None:
            return {"prediction": 12.5}
        
        print(f"\n=== ROI PREDICTION ===")
        X = prepare_features_for_model(features, roi_features, roi_scaler)
        prediction = roi_model.predict(X)[0]
        print(f"Raw prediction: {prediction}")
        print(f"Final prediction: {prediction:.2f}%")
        
        # ROI is already percentage in the model output
        roi_value = max(2.0, min(25.0, float(prediction)))
        return {"prediction": round(roi_value, 2)}
    except Exception as e:
        print(f"ROI prediction error: {e}")
        return {"prediction": 12.5}

@app.post("/predict/neighborhood")
def predict_neighborhood(features: HouseFeatures):
    try:
        if not models_loaded or neighborhood_model is None:
            return {"classification": "Medium", "score": 0.8}
        
        print(f"\n=== NEIGHBORHOOD PREDICTION ===")
        X = prepare_features_for_model(features, neighborhood_features)
        prediction = neighborhood_model.predict(X)[0]
        
        # Get confidence score if available
        if hasattr(neighborhood_model, 'predict_proba'):
            proba = neighborhood_model.predict_proba(X)[0]
            score = max(proba)
        else:
            score = 0.8
        
        print(f"Prediction: {prediction}, Score: {score:.2f}")
        return {
            "classification": str(prediction),
            "score": round(float(score), 2)
        }
    except Exception as e:
        print(f"Neighborhood prediction error: {e}")
        return {"classification": "Medium", "score": 0.8}

@app.post("/predict/sell_speed")
def predict_sell_speed(features: HouseFeatures):
    try:
        if not models_loaded or sell_speed_model is None:
            return {"classification": "Medium"}
        
        print(f"\n=== SELL SPEED PREDICTION ===")
        X = prepare_features_for_model(features, sell_speed_features)
        prediction = sell_speed_model.predict(X)[0]
        print(f"Prediction: {prediction}")
        return {"classification": str(prediction)}
    except Exception as e:
        print(f"Sell speed prediction error: {e}")
        return {"classification": "Medium"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "models_loaded": models_loaded}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)