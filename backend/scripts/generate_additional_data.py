# scripts/generate_additional_data.py

import os
import pandas as pd
import numpy as np

# ---------------- Step 1: Load housing.csv ---------------- #
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, "../data/housing.csv")

print("Loading housing.csv ...")
housing_df = pd.read_csv(data_path)

# ---------------- Step 2: Clean Data ---------------- #
print("Cleaning data ...")
housing_df['total_bedrooms'] = housing_df['total_bedrooms'].fillna(housing_df['total_bedrooms'].median())

# ---------------- Step 3: Feature Engineering ---------------- #
print("Applying feature engineering ...")
from feature_engineering import add_features
housing_df = add_features(housing_df)

# ---------------- Step 4: Generate Rent Data ---------------- #
# Approximate rent as 0.003 * median_house_value + some noise
np.random.seed(42)
housing_df['monthly_rent'] = housing_df['median_house_value'] * 0.003 + np.random.normal(0, 100, len(housing_df))

# ---------------- Step 5: Generate ROI Data ---------------- #
# Approximate ROI as (monthly_rent * 12 / median_house_value) + renovation_factor
housing_df['renovation_factor'] = np.random.uniform(-0.05, 0.2, len(housing_df))  # random % change
housing_df['roi'] = (housing_df['monthly_rent'] * 12 / housing_df['median_house_value']) + housing_df['renovation_factor']

# ---------------- Step 6: Generate Neighborhood Investment ---------------- #
# Assign "High", "Medium", "Low" randomly based on median_income
conditions = [
    (housing_df['median_income'] > 7),
    (housing_df['median_income'] > 4) & (housing_df['median_income'] <= 7),
    (housing_df['median_income'] <= 4)
]
choices = ['High', 'Medium', 'Low']
housing_df['neighborhood_investment'] = np.select(conditions, choices, default='Unknown')

# ---------------- Step 7: Generate Sell Speed ---------------- #
# Assign "Fast" if median_income > 6 else "Slow"
housing_df['sell_speed'] = np.where(housing_df['median_income'] > 6, 'Fast', 'Slow')

# ---------------- Step 8: Save to CSV ---------------- #
output_path = os.path.join(script_dir, "../data/augmented_housing.csv")
housing_df.to_csv(output_path, index=False)
print(f"Augmented dataset saved to {output_path}")
