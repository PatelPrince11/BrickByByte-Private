import os
import joblib
import pandas as pd
import numpy as np

# ---------------- Sample Properties ---------------- #
sample_properties = [
    {"longitude": -122.23, "latitude": 37.88, "housing_median_age": 41, "total_rooms": 880,
     "total_bedrooms": 129, "population": 322, "households": 126, "median_income": 8.3,
     "ocean_proximity": "NEAR BAY", "renovation_budget": 5000},
    {"longitude": -118.15, "latitude": 34.15, "housing_median_age": 25, "total_rooms": 1500,
     "total_bedrooms": 300, "population": 600, "households": 280, "median_income": 5.5,
     "ocean_proximity": "INLAND", "renovation_budget": 10000},
    {"longitude": -121.90, "latitude": 36.77, "housing_median_age": 30, "total_rooms": 2000,
     "total_bedrooms": 400, "population": 800, "households": 380, "median_income": 6.8,
     "ocean_proximity": "<1H OCEAN", "renovation_budget": 15000},
    {"longitude": -119.70, "latitude": 36.33, "housing_median_age": 15, "total_rooms": 1200,
     "total_bedrooms": 250, "population": 450, "households": 220, "median_income": 4.5,
     "ocean_proximity": "ISLAND", "renovation_budget": 7000},
    {"longitude": -123.05, "latitude": 38.10, "housing_median_age": 50, "total_rooms": 800,
     "total_bedrooms": 100, "population": 200, "households": 90, "median_income": 9.2,
     "ocean_proximity": "NEAR OCEAN", "renovation_budget": 20000}
]

df = pd.DataFrame(sample_properties)

# ---------------- Paths ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

# ---------------- Feature Engineering ---------------- #
def add_features(df):
    df = df.copy()
    df['total_bedrooms'] = df['total_bedrooms'].fillna(df['total_bedrooms'].median())
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']
    return df

df = add_features(df)

# Apply one-hot encoding for ocean_proximity
df = pd.get_dummies(df, columns=['ocean_proximity'])

# ---------------- Helper Function ---------------- #
def preprocess(df, scaler, feature_columns):
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
    return scaler.transform(df[feature_columns])

# ---------------- Regression Predictions ---------------- #
regression_models = {
    'price': 'median_house_value',
    'rent': 'monthly_rent',
    'roi': 'roi'
}

print("\n=== Regression Predictions ===\n")
for model_name in regression_models.keys():
    model_path = os.path.join(models_dir, f"{model_name}_model.pkl")
    scaler_path = os.path.join(models_dir, f"{model_name}_scaler.pkl")
    features_path = os.path.join(models_dir, f"{model_name}_feature_columns.pkl")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    feature_columns = joblib.load(features_path)

    X_scaled = preprocess(df, scaler, feature_columns)
    y_pred = model.predict(X_scaled)

    print(f"{model_name.capitalize()} Predictions:")
    for i, val in enumerate(y_pred):
        print(f"  Property {i+1}: {val:,.2f}")
    print()

# ---------------- Classification Predictions ---------------- #
classification_models = {
    'neighborhood': 'neighborhood_investment',
    'sell_speed': 'sell_speed'
}

def preprocess_classification(df, feature_columns):
    df_copy = df.copy()
    for col in feature_columns:
        if col not in df_copy.columns:
            df_copy[col] = 0
    return df_copy[feature_columns]

print("\n=== Classification Predictions ===\n")
for model_name, target_col in classification_models.items():
    model_path = os.path.join(models_dir, f"{model_name}_classifier.pkl")
    features_path = os.path.join(models_dir, f"{model_name}_feature_columns.pkl")

    model = joblib.load(model_path)
    feature_columns = joblib.load(features_path)

    X_eval = preprocess_classification(df, feature_columns)
    y_pred = model.predict(X_eval)

    print(f"{model_name.capitalize()} Predictions:")
    for i, val in enumerate(y_pred):
        print(f"  Property {i+1}: {val}")
    print()