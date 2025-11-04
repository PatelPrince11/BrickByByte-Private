import os
import pandas as pd
import numpy as np

print("Fixing data generation with proper one-hot encoding...")

# Load original housing data - FIXED PATH
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "data/housing.csv")  # Changed from ../data/housing.csv

print(f"Looking for data at: {data_path}")
print(f"File exists: {os.path.exists(data_path)}")

if not os.path.exists(data_path):
    print("❌ housing.csv not found! Please make sure it exists in backend/data/")
    exit(1)

housing_df = pd.read_csv(data_path)
print(f"✅ Loaded data: {housing_df.shape}")

# Clean data
housing_df['total_bedrooms'] = housing_df['total_bedrooms'].fillna(housing_df['total_bedrooms'].median())

# Feature engineering
def add_features(df):
    df = df.copy()
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']
    return df

housing_df = add_features(housing_df)

# Generate realistic additional data
np.random.seed(42)

# Rent calculation
base_rent_ratio = np.random.uniform(0.001, 0.003, len(housing_df))
location_rent_multiplier = {
    'NEAR BAY': 1.8, 'NEAR OCEAN': 1.6, '<1H OCEAN': 1.4, 'ISLAND': 1.3, 'INLAND': 1.0
}
rent_multiplier = housing_df['ocean_proximity'].map(location_rent_multiplier)
housing_df['monthly_rent'] = housing_df['median_house_value'] * base_rent_ratio * rent_multiplier
housing_df['monthly_rent'] += np.random.normal(0, 200, len(housing_df))
housing_df['monthly_rent'] = housing_df['monthly_rent'].clip(500, 10000)

# ROI calculation (as percentage)
base_roi = (housing_df['monthly_rent'] * 12 / housing_df['median_house_value']) * 100
location_appreciation = {
    'NEAR BAY': 8, 'NEAR OCEAN': 6, '<1H OCEAN': 4, 'ISLAND': 3, 'INLAND': 1
}
appreciation = housing_df['ocean_proximity'].map(location_appreciation)
housing_df['roi'] = base_roi + appreciation + np.random.normal(0, 2, len(housing_df))
housing_df['roi'] = housing_df['roi'].clip(2, 25)

# Classification targets
conditions = [
    (housing_df['median_income'] > 7) & (housing_df['roi'] > 15),
    (housing_df['median_income'] > 5) & (housing_df['roi'] > 10),
    (housing_df['roi'] <= 10)
]
choices = ['High', 'Medium', 'Low']
housing_df['neighborhood_investment'] = np.select(conditions, choices, default='Medium')

speed_conditions = [
    (housing_df['median_income'] > 6) & (housing_df['roi'] > 12),
    (housing_df['median_income'] > 4) & (housing_df['roi'] > 8),
    (housing_df['roi'] <= 8)
]
speed_choices = ['Fast', 'Medium', 'Slow']
housing_df['sell_speed'] = np.select(speed_conditions, speed_choices, default='Medium')

# CRITICAL: Apply one-hot encoding to ocean_proximity
print("Applying one-hot encoding to ocean_proximity...")
housing_df = pd.get_dummies(housing_df, columns=['ocean_proximity'], prefix='ocean_proximity')

# Save the fixed dataset
output_path = os.path.join(script_dir, "data/augmented_housing.csv")  # Fixed path
housing_df.to_csv(output_path, index=False)

print(f"✅ Fixed dataset saved to {output_path}")
print(f"Final dataset shape: {housing_df.shape}")
print(f"Total columns: {len(housing_df.columns)}")

# Show ocean_proximity columns
ocean_cols = [col for col in housing_df.columns if 'ocean_proximity' in col]
print(f"Ocean proximity columns: {ocean_cols}")

print("\n=== DATA SUMMARY ===")
print(f"Housing Prices: ${housing_df['median_house_value'].min():,.0f} - ${housing_df['median_house_value'].max():,.0f}")
print(f"Monthly Rent: ${housing_df['monthly_rent'].min():,.0f} - ${housing_df['monthly_rent'].max():,.0f}")
print(f"ROI: {housing_df['roi'].min():.1f}% - {housing_df['roi'].max():.1f}%")