# api/app.py
# Description: Flask API for house price prediction and related models.
from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
from scripts.feature_engineering import add_features

app = Flask(__name__)

# Load models and scaler
price_model = joblib.load("../models/price_model.pkl")
rent_model = joblib.load("../models/rent_model.pkl")
roi_model = joblib.load("../models/roi_model.pkl")
neighborhood_clf = joblib.load("../models/neighborhood_classifier.pkl")
sell_speed_clf = joblib.load("../models/sell_speed_classifier.pkl")
scaler = joblib.load("../models/scaler.pkl")
feature_columns = joblib.load("../models/feature_columns.pkl")  # Ordered columns

# Ocean proximity mapping
OCEAN_CATEGORIES = ['<1H OCEAN', 'INLAND', 'ISLAND', 'NEAR BAY', 'NEAR OCEAN']

def prepare_input(input_dict):
    """
    Converts input JSON to scaled numpy array for prediction.
    """
    df = pd.DataFrame([input_dict])
    df = add_features(df)

    # One-hot encode ocean_proximity
    for category in OCEAN_CATEGORIES:
        df[f'ocean_proximity_{category}'] = int(df['ocean_proximity'][0] == category)
    df = df.drop('ocean_proximity', axis=1)

    # Ensure all columns exist
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    # Reorder columns
    df = df[feature_columns]

    # Scale numerical features
    X = scaler.transform(df)
    return X

# ---------------- API Endpoints ---------------- #

@app.route("/predict/price", methods=["POST"])
def predict_price():
    data = request.json
    X = prepare_input(data)
    price = price_model.predict(X)[0]
    return jsonify({"predicted_price": round(price, 2)})

@app.route("/predict/rent", methods=["POST"])
def predict_rent():
    data = request.json
    X = prepare_input(data)
    rent = rent_model.predict(X)[0]
    return jsonify({"predicted_rent": round(rent, 2)})

@app.route("/predict/roi", methods=["POST"])
def predict_roi():
    data = request.json
    X = prepare_input(data)
    roi = roi_model.predict(X)[0]
    return jsonify({"predicted_roi": round(roi, 2)})

@app.route("/predict/neighborhood", methods=["POST"])
def predict_neighborhood():
    data = request.json
    X = prepare_input(data)
    pred = neighborhood_clf.predict(X)[0]
    return jsonify({"neighborhood_investment": pred})

@app.route("/predict/sell_speed", methods=["POST"])
def predict_sell_speed():
    data = request.json
    X = prepare_input(data)
    pred = sell_speed_clf.predict(X)[0]
    return jsonify({"sell_speed": pred})

@app.route("/predict/feature_importance", methods=["GET"])
def feature_importance():
    # For demonstration, use price model feature importance if available
    if hasattr(price_model, "coef_"):
        importance = dict(zip(feature_columns, price_model.coef_.tolist()))
    else:
        importance = "Feature importance not available for this model."
    return jsonify({"feature_importance": importance})

# Run app
if __name__ == "__main__":
    app.run(debug=True)
