# scripts/feature_engineering.py
# Description: This script contains functions for feature engineering on the housing dataset.
import pandas as pd

def add_features(df):
    """
    Adds new engineered features to improve model performance.
    """
    df = df.copy()
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']
    return df