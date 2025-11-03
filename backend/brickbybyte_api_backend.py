# brickbybyte_api_backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import os

# ---------------- Setup ---------------- #
app = FastAPI(title="BrickByByte Housing API", version="1.0")

# CORS Configuration - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # Vite dev server
        "http://localhost:5173",  # Alternative Vite port
        "http://localhost:3000",  # React alternative
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Load models and feature columns ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

# Regression models
price_model = joblib.load(os.path.join(models_dir, "price_model.pkl"))
price_scaler = joblib.load(os.path.join(models_dir, "price_scaler.pkl"))
price_features = joblib.load(os.path.join(models_dir, "price_feature_columns.pkl"))

rent_model = joblib.load(os.path.join(models_dir, "rent_model.pkl"))
rent_scaler = joblib.load(os.path.join(models_dir, "rent_scaler.pkl"))
rent_features = joblib.load(os.path.join(models_dir, "rent_feature_columns.pkl"))

roi_model = joblib.load(os.path.join(models_dir, "roi_model.pkl"))
roi_scaler = joblib.load(os.path.join(models_dir, "roi_scaler.pkl"))
roi_features = joblib.load(os.path.join(models_dir, "roi_feature_columns.pkl"))

# Classification models (no scaler needed - they were trained on raw features)
neighborhood_model = joblib.load(os.path.join(models_dir, "neighborhood_classifier.pkl"))
neighborhood_features = joblib.load(os.path.join(models_dir, "neighborhood_feature_columns.pkl"))

sell_speed_model = joblib.load(os.path.join(models_dir, "sell_speed_classifier.pkl"))
sell_speed_features = joblib.load(os.path.join(models_dir, "sell_speed_feature_columns.pkl"))

# ---------------- Input Schema ---------------- #
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
    renovation_budget: float = 0.0

# ---------------- Feature Processing ---------------- #
def preprocess_input(input_data: HouseFeatures, feature_columns, use_scaler=None):
    """
    Process input features and prepare for model prediction.
    """
    df = pd.DataFrame([input_data.dict()])

    # Feature engineering
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']

    # One-hot encode ocean_proximity
    ocean_mapping = {
        '<1H OCEAN': 'ocean_proximity_<1H OCEAN',
        'INLAND': 'ocean_proximity_INLAND',
        'ISLAND': 'ocean_proximity_ISLAND',
        'NEAR BAY': 'ocean_proximity_NEAR BAY',
        'NEAR OCEAN': 'ocean_proximity_NEAR OCEAN'
    }
    
    # Initialize all ocean proximity columns to 0
    for col in feature_columns:
        if col.startswith('ocean_proximity_'):
            df[col] = 0
    
    # Set the correct one to 1
    if input_data.ocean_proximity in ocean_mapping:
        col_name = ocean_mapping[input_data.ocean_proximity]
        if col_name in feature_columns:
            df[col_name] = 1
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid ocean_proximity. Must be one of: {list(ocean_mapping.keys())}"
        )

    # Ensure all required columns exist
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    
    # Reorder to match training
    df = df[feature_columns]

    # Apply scaling if provided
    if use_scaler is not None:
        return use_scaler.transform(df)
    return df.values

# ---------------- API Endpoints ---------------- #
@app.get("/")
def root():
    return {
        "message": "BrickByByte Housing API",
        "version": "1.0",
        "endpoints": [
            "/predict/price",
            "/predict/rent", 
            "/predict/roi",
            "/predict/neighborhood",
            "/predict/sell_speed",
            "/predict/feature_importance"
        ]
    }

@app.post("/predict/price")
def predict_price(features: HouseFeatures):
    """Predict house price"""
    try:
        X = preprocess_input(features, price_features, price_scaler)
        prediction = float(price_model.predict(X)[0])
        return {"prediction": round(prediction, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/rent")
def predict_rent(features: HouseFeatures):
    """Predict monthly rent"""
    try:
        X = preprocess_input(features, rent_features, rent_scaler)
        prediction = float(rent_model.predict(X)[0])
        return {"prediction": round(prediction, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/roi")
def predict_roi(features: HouseFeatures):
    """Predict return on investment"""
    try:
        X = preprocess_input(features, roi_features, roi_scaler)
        prediction = float(roi_model.predict(X)[0])
        return {"prediction": round(prediction, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/neighborhood")
def predict_neighborhood(features: HouseFeatures):
    """Predict neighborhood investment score"""
    try:
        X = preprocess_input(features, neighborhood_features, use_scaler=None)
        classification = neighborhood_model.predict(X)[0]
        
        # Get probability scores if available
        if hasattr(neighborhood_model, 'predict_proba'):
            proba = neighborhood_model.predict_proba(X)[0]
            score = float(max(proba))
        else:
            score = 1.0
        
        return {
            "classification": classification,
            "score": round(score, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/sell_speed")
def predict_sell_speed(features: HouseFeatures):
    """Predict how fast property will sell"""
    try:
        X = preprocess_input(features, sell_speed_features, use_scaler=None)
        classification = sell_speed_model.predict(X)[0]
        return {"classification": classification}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/feature_importance")
def get_feature_importance(model: str = "price"):
    """Get feature importance for specified model"""
    try:
        importance_data = []
        
        if model == "price":
            if hasattr(price_model, "feature_importances_"):
                importances = price_model.feature_importances_
                for feat, imp in zip(price_features, importances):
                    importance_data.append({
                        "feature": feat,
                        "importance": float(imp)
                    })
        elif model == "rent":
            if hasattr(rent_model, "feature_importances_"):
                importances = rent_model.feature_importances_
                for feat, imp in zip(rent_features, importances):
                    importance_data.append({
                        "feature": feat,
                        "importance": float(imp)
                    })
        elif model == "roi":
            if hasattr(roi_model, "feature_importances_"):
                importances = roi_model.feature_importances_
                for feat, imp in zip(roi_features, importances):
                    importance_data.append({
                        "feature": feat,
                        "importance": float(imp)
                    })
        
        # Sort by importance descending
        importance_data.sort(key=lambda x: x["importance"], reverse=True)
        return importance_data[:10]  # Return top 10
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)