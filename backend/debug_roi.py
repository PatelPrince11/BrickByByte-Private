import pandas as pd
import numpy as np
import joblib
import os

# Get the correct path to the data file
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "data/augmented_housing.csv")

print(f"Looking for data at: {data_path}")
print(f"File exists: {os.path.exists(data_path)}")

if not os.path.exists(data_path):
    print("❌ Data file not found! Please run generate_additional_data.py first")
    exit(1)

# Load the training data
data = pd.read_csv(data_path)

print("=== ROI DATA ANALYSIS ===")
print(f"Dataset shape: {data.shape}")
print(f"Columns: {list(data.columns)}")

if 'roi' not in data.columns:
    print("❌ ROI column not found in dataset!")
    print("Available columns:", list(data.columns))
    exit(1)

print(f"\nROI column statistics:")
print(f"Min ROI: {data['roi'].min():.4f}")
print(f"Max ROI: {data['roi'].max():.4f}")
print(f"Mean ROI: {data['roi'].mean():.4f}")
print(f"Median ROI: {data['roi'].median():.4f}")
print(f"ROI value counts:")
print(data['roi'].value_counts().head(10))

print(f"\nNumber of zero ROI values: {(data['roi'] == 0).sum()}")
print(f"Percentage of zero ROI: {(data['roi'] == 0).mean() * 100:.2f}%")

# Check the ROI calculation
print(f"\n=== ROI CALCULATION CHECK ===")
sample = data.iloc[0]
print(f"Sample property:")
print(f"  Price: ${sample['median_house_value']:,.2f}")
if 'monthly_rent' in data.columns:
    print(f"  Monthly Rent: ${sample['monthly_rent']:,.2f}")
    print(f"  Annual Rent: ${sample['monthly_rent'] * 12:,.2f}")
print(f"  ROI: {sample['roi']:.4f}")

if 'monthly_rent' in data.columns and 'median_house_value' in data.columns:
    calculated_roi = (sample['monthly_rent'] * 12 / sample['median_house_value'])
    print(f"  Calculated ROI (rent*12/price): {calculated_roi:.4f}")

# Load and test the ROI model
try:
    models_dir = os.path.join(script_dir, "models")
    roi_model_path = os.path.join(models_dir, "roi_model.pkl")
    roi_features_path = os.path.join(models_dir, "roi_feature_columns.pkl")
    
    print(f"\n=== ROI MODEL INFO ===")
    print(f"Model file exists: {os.path.exists(roi_model_path)}")
    print(f"Features file exists: {os.path.exists(roi_features_path)}")
    
    if os.path.exists(roi_model_path) and os.path.exists(roi_features_path):
        roi_model = joblib.load(roi_model_path)
        roi_features = joblib.load(roi_features_path)
        
        print(f"Model type: {type(roi_model)}")
        print(f"Number of features: {len(roi_features)}")
        print(f"First 10 features: {roi_features[:10]}")
        
        # Test prediction
        test_input = {feature: 0 for feature in roi_features}
        
        # Set some realistic values
        if 'longitude' in test_input: test_input['longitude'] = -122.23
        if 'latitude' in test_input: test_input['latitude'] = 37.88
        if 'housing_median_age' in test_input: test_input['housing_median_age'] = 25
        if 'total_rooms' in test_input: test_input['total_rooms'] = 1500
        if 'total_bedrooms' in test_input: test_input['total_bedrooms'] = 300
        if 'population' in test_input: test_input['population'] = 800
        if 'households' in test_input: test_input['households'] = 300
        if 'median_income' in test_input: test_input['median_income'] = 4.0
        
        # Set ocean proximity
        for col in test_input:
            if col.startswith('ocean_proximity_'):
                if 'NEAR BAY' in col:
                    test_input[col] = 1
                else:
                    test_input[col] = 0
        
        df_test = pd.DataFrame([test_input])
        df_test = df_test[roi_features]
        
        prediction = roi_model.predict(df_test)[0]
        print(f"Test prediction: {prediction:.4f}")
    else:
        print("❌ Model files not found! Please train models first.")
        
except Exception as e:
    print(f"Error loading model: {e}")