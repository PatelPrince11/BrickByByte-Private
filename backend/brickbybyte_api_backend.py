# brickbybyte_api_backend.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- Setup ---------------- #
app = FastAPI(title="BrickByByte Housing API", version="1.0")

# CORS Configuration - Allow frontend to connect
import os

# CORS Configuration - Allow frontend to connect
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:5173,http://127.0.0.1:8080"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
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
            "/predict/feature_importance",
            "/stats/dashboard"
        ]
    }

@app.get("/stats/dashboard")
def get_dashboard_stats():
    """Get dashboard statistics from the dataset"""
    try:
        # Load the dataset
        data_path = os.path.join(script_dir, "data/augmented_housing.csv")
        df = pd.read_csv(data_path)
        
        # Calculate statistics
        avg_property_value = float(df['median_house_value'].mean())
        avg_roi = float(df['roi'].mean())  # Convert to percentage
        
        # Count high investment neighborhoods
        high_investment_count = int((df['neighborhood_investment'] == 'High').sum())
        
        # For predictions count, we'll use total number of records
        total_properties = len(df)
        
        return {
            "avg_property_value": round(avg_property_value, 2),
            "avg_roi_potential": round(avg_roi, 2),
            "high_investment_areas": high_investment_count,
            "predictions_made": total_properties
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats/model_performance")
def get_model_performance():
    try:
        from sklearn.metrics import r2_score, accuracy_score

        data_path = os.path.join(script_dir, "data/augmented_housing.csv")
        df = pd.read_csv(data_path)

        # Feature engineering (same as training pipeline)
        df['rooms_per_household'] = df['total_rooms'] / df['households']
        df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
        df['population_per_household'] = df['population'] / df['households']

        # DO NOT re-encode ocean_proximity — already encoded in augmented CSV

        def calc_r2(model, scaler, feature_cols, target_col):
            X = pd.DataFrame(0, index=df.index, columns=feature_cols)
            for col in feature_cols:
                if col in df.columns:
                    X[col] = df[col]
            X_scaled = scaler.transform(X)
            y_pred = model.predict(X_scaled)
            return float(round(r2_score(df[target_col].values, y_pred), 4))

        def calc_accuracy(model, feature_cols, target_col):
            X = pd.DataFrame(0, index=df.index, columns=feature_cols)
            for col in feature_cols:
                if col in df.columns:
                    X[col] = df[col]
            y_pred = model.predict(X)
            return float(round(accuracy_score(df[target_col].values, y_pred), 4))

        price_r2 = calc_r2(price_model, price_scaler, price_features, 'median_house_value')
        rent_r2 = calc_r2(rent_model, rent_scaler, rent_features, 'monthly_rent')
        roi_r2 = calc_r2(roi_model, roi_scaler, roi_features, 'roi')
        neighborhood_acc = calc_accuracy(neighborhood_model, neighborhood_features, 'neighborhood_investment')
        sell_speed_acc = calc_accuracy(sell_speed_model, sell_speed_features, 'sell_speed')

        average = round((price_r2 + rent_r2 + roi_r2 + neighborhood_acc + sell_speed_acc) / 5, 4)

        return {
            "price_r2": price_r2,
            "rent_r2": rent_r2,
            "roi_r2": roi_r2,
            "neighborhood_accuracy": neighborhood_acc,
            "sell_speed_accuracy": sell_speed_acc,
            "average_accuracy": average
        }
    except Exception as e:
        logger.error(f"Model performance calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/map/properties")
def get_map_properties(limit: int = 100):
    """Get property data for map visualization"""
    try:
        # Load the dataset
        data_path = os.path.join(script_dir, "data/augmented_housing.csv")
        df = pd.read_csv(data_path)
        
        # Sample properties for map display
        df_sample = df.sample(n=min(limit, len(df)), random_state=42)
        
        properties = []
        for idx, row in df_sample.iterrows():
            properties.append({
                "id": int(idx),
                "latitude": float(row['latitude']),
                "longitude": float(row['longitude']),
                "price": float(row['median_house_value']),
                "investment_score": row['neighborhood_investment'],
                "median_income": float(row['median_income']),
                "housing_age": float(row['housing_median_age'])
            })
        
        return {"properties": properties, "total": len(properties)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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