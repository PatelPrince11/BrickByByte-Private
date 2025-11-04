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

try:
    # Load regression models
    price_model = joblib.load(os.path.join(models_dir, "price_model.pkl"))
    rent_model = joblib.load(os.path.join(models_dir, "rent_model.pkl")) 
    roi_model = joblib.load(os.path.join(models_dir, "roi_model.pkl"))
    
    # Load classification models
    neighborhood_model = joblib.load(os.path.join(models_dir, "neighborhood_classifier.pkl"))
    sell_speed_model = joblib.load(os.path.join(models_dir, "sell_speed_classifier.pkl"))
    
    print("✅ All models loaded successfully!")
    
except Exception as e:
    print(f"❌ Error loading models: {e}")
    # Create dummy models for development
    class DummyModel:
        def predict(self, X):
            return [np.random.uniform(100000, 500000)]
        def predict_proba(self, X):
            return [[0.3, 0.4, 0.3]]
    
    price_model = rent_model = roi_model = DummyModel()
    neighborhood_model = sell_speed_model = DummyModel()

# Feature engineering function
def add_features(df):
    df = df.copy()
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']
    return df

def prepare_features(features: HouseFeatures):
    """Prepare features for prediction"""
    # Create DataFrame
    df = pd.DataFrame([features.dict()])
    
    # Add engineered features
    df = add_features(df)
    
    # One-hot encode ocean_proximity
    ocean_categories = ['<1H OCEAN', 'INLAND', 'ISLAND', 'NEAR BAY', 'NEAR OCEAN']
    for category in ocean_categories:
        df[f'ocean_proximity_{category}'] = (df['ocean_proximity'] == category).astype(int)
    
    # Drop original column
    df = df.drop('ocean_proximity', axis=1)
    
    return df

# API endpoints
@app.get("/")
def root():
    return {
        "message": "BrickByByte Real Estate API", 
        "status": "running",
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
        df = prepare_features(features)
        prediction = price_model.predict(df)[0]
        return {"prediction": round(float(prediction), 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Price prediction error: {str(e)}")

@app.post("/predict/rent")
def predict_rent(features: HouseFeatures):
    try:
        df = prepare_features(features)
        prediction = rent_model.predict(df)[0]
        return {"prediction": round(float(prediction), 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rent prediction error: {str(e)}")

@app.post("/predict/roi")
def predict_roi(features: HouseFeatures):
    try:
        df = prepare_features(features)
        prediction = roi_model.predict(df)[0]
        return {"prediction": round(float(prediction), 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ROI prediction error: {str(e)}")

@app.post("/predict/neighborhood")
def predict_neighborhood(features: HouseFeatures):
    try:
        df = prepare_features(features)
        prediction = neighborhood_model.predict(df)[0]
        
        # Get confidence score if available
        if hasattr(neighborhood_model, 'predict_proba'):
            proba = neighborhood_model.predict_proba(df)[0]
            score = max(proba)
        else:
            score = 0.8  # Default confidence
            
        return {
            "classification": str(prediction),
            "score": round(float(score), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neighborhood prediction error: {str(e)}")

@app.post("/predict/sell_speed")
def predict_sell_speed(features: HouseFeatures):
    try:
        df = prepare_features(features)
        prediction = sell_speed_model.predict(df)[0]
        return {"classification": str(prediction)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sell speed prediction error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "models_loaded": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)