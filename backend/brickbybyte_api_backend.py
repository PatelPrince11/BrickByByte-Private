# brickbybyte_api_backend.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import os

# ---------------- Setup ---------------- #
app = FastAPI(title="BrickByByte Housing API", version="1.0")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Load models, scalers, and feature columns ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

# ---------------- Load Models ---------------- #
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

# Classification models
neighborhood_model = joblib.load(os.path.join(models_dir, "neighborhood_classifier.pkl"))
neighborhood_scaler = joblib.load(os.path.join(models_dir, "neighborhood_scaler.pkl"))
neighborhood_features = joblib.load(os.path.join(models_dir, "neighborhood_feature_columns.pkl"))

sell_speed_model = joblib.load(os.path.join(models_dir, "sell_speed_classifier.pkl"))
sell_speed_scaler = joblib.load(os.path.join(models_dir, "sell_speed_scaler.pkl"))
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
    renovation_budget: float = 0.0  # optional, for ROI

# ---------------- Feature Processing ---------------- #
def preprocess_input(input: HouseFeatures, scaler, feature_columns):
    df = pd.DataFrame([input.dict()])

    # Feature engineering
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']

    # One-hot encode ocean_proximity
    ocean_cols = [col for col in feature_columns if "ocean_proximity_" in col]
    for col in ocean_cols:
        df[col] = 0
    mapping = {
        '<1H OCEAN':'ocean_proximity_<1H OCEAN',
        'INLAND':'ocean_proximity_INLAND',
        'ISLAND':'ocean_proximity_ISLAND',
        'NEAR BAY':'ocean_proximity_NEAR BAY',
        'NEAR OCEAN':'ocean_proximity_NEAR OCEAN'
    }
    if input.ocean_proximity not in mapping:
        raise HTTPException(status_code=400, detail="Invalid ocean_proximity value")
    df[mapping[input.ocean_proximity]] = 1

    # Reorder columns and add missing features
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_columns]

    # Scale features
    X_scaled = scaler.transform(df)
    return X_scaled

# ---------------- API Endpoints ---------------- #
@app.post("/predict/price")
def predict_price(features: HouseFeatures):
    X = preprocess_input(features, price_scaler, price_features)
    price = price_model.predict(X)[0]
    return {"predicted_price": float(price)}

@app.post("/predict/rent")
def predict_rent(features: HouseFeatures):
    X = preprocess_input(features, rent_scaler, rent_features)
    rent = rent_model.predict(X)[0]
    return {"predicted_rent": float(rent)}

@app.post("/predict/roi")
def predict_roi(features: HouseFeatures):
    X = preprocess_input(features, roi_scaler, roi_features)
    roi = roi_model.predict(X)[0]
    return {"predicted_roi": float(roi)}

@app.post("/predict/neighborhood")
def predict_neighborhood(features: HouseFeatures):
    X = preprocess_input(features, neighborhood_scaler, neighborhood_features)
    neighborhood = neighborhood_model.predict(X)[0]
    return {"neighborhood_investment": neighborhood}

@app.post("/predict/sell_speed")
def predict_sell_speed_(features: HouseFeatures):
    X = preprocess_input(features, sell_speed_scaler, sell_speed_features)
    speed = sell_speed_model.predict(X)[0]
    return {"sell_speed": speed}

@app.get("/predict/feature_importance")
def get_feature_importance():
    importance = {}
    if hasattr(price_model, "coef_"):
        importance['price_model'] = dict(zip(price_features, price_model.coef_.tolist()))
    if hasattr(rent_model, "coef_"):
        importance['rent_model'] = dict(zip(rent_features, rent_model.coef_.tolist()))
    return importance
