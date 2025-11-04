import os
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

# ---------------- Paths ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

# ---------------- Load models ---------------- #
price_model = joblib.load(os.path.join(models_dir, "price_model.pkl"))
scaler = joblib.load(os.path.join(models_dir, "price_scaler.pkl"))
features = joblib.load(os.path.join(models_dir, "price_feature_columns.pkl"))

# ---------------- Sample data ---------------- #
data_dict = {
    "longitude": [-122.23, -122.22],
    "latitude": [37.88, 37.86],
    "housing_median_age": [41.0, 21.0],
    "total_rooms": [880.0, 7099.0],
    "total_bedrooms": [129.0, 1106.0],
    "population": [322.0, 2401.0],
    "households": [126.0, 1138.0],
    "median_income": [8.3252, 8.3014],
    "rooms_per_household": [6.9841, 6.2381],
    "bedrooms_per_room": [0.1466, 0.1558],
    "population_per_household": [2.5556, 2.1098],
    "ocean_proximity_<1H OCEAN": [False, False],
    "ocean_proximity_INLAND": [False, False],
    "ocean_proximity_ISLAND": [False, False],
    "ocean_proximity_NEAR BAY": [True, True],
    "ocean_proximity_NEAR OCEAN": [False, False]
}

df = pd.DataFrame(data_dict)

# ---------------- Convert boolean columns to integers ---------------- #
bool_cols = [col for col in df.columns if col.startswith("ocean_proximity")]
df[bool_cols] = df[bool_cols].astype(int)

# Ensure all feature columns exist
for col in features:
    if col not in df.columns:
        df[col] = 0

# Reorder columns to match training
df = df[features]

# Scale features
X_scaled = scaler.transform(df)

# Predict
predictions = price_model.predict(X_scaled)

# Compare with actual median house prices
actuals = [452600.0, 358500.0]

for i, (pred, act) in enumerate(zip(predictions, actuals), start=1):
    print(f"Property {i}: Predicted Price = {pred}, Actual Price = {act:.2f}")