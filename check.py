import pandas as pd

data = pd.read_csv("data/augmented_housing.csv")

print("Neighborhood Investment Class Distribution:")
print(data['neighborhood_investment'].value_counts())

print("\nSell Speed Class Distribution:")
print(data['sell_speed'].value_counts())