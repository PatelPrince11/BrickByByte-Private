# test_brickbybyte_api_combined.py
import requests

BASE_URL = "http://127.0.0.1:8000"

# Sample input matching your FastAPI schema
sample_data = {
    "longitude": -122.23,
    "latitude": 37.88,
    "housing_median_age": 41,
    "total_rooms": 880,
    "total_bedrooms": 129,
    "population": 322,
    "households": 126,
    "median_income": 8.3252,
    "ocean_proximity": "NEAR BAY",
    "renovation_budget": 0.05
}

def safe_post(endpoint, payload, label):
    try:
        resp = requests.post(endpoint, json=payload)
        print(f"\nStatus code: {resp.status_code}")
        if resp.status_code == 200:
            print(f"{label}: {resp.json()}")
        else:
            print(f"{label} - Raw response: {resp.text}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"{label} - JSON Decode Error:", e)
    except Exception as e:
        print(f"{label} - Error:", e)

def safe_get(endpoint, label):
    try:
        resp = requests.get(endpoint)
        print(f"\nStatus code: {resp.status_code}")
        if resp.status_code == 200:
            print(f"{label}: {resp.json()}")
        else:
            print(f"{label} - Raw response: {resp.text}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"{label} - JSON Decode Error:", e)
    except Exception as e:
        print(f"{label} - Error:", e)

if __name__ == "__main__":
    safe_post(f"{BASE_URL}/predict/price", sample_data, "🏠 House Price Prediction")
    safe_post(f"{BASE_URL}/predict/rent", sample_data, "💰 Monthly Rent Prediction")
    safe_post(f"{BASE_URL}/predict/roi", sample_data, "📈 Estimated ROI")
    safe_post(f"{BASE_URL}/predict/neighborhood", sample_data, "🏘️ Neighborhood Investment")
    safe_post(f"{BASE_URL}/predict/sell_speed", sample_data, "⚡ Sell Speed Prediction")
    safe_get(f"{BASE_URL}/predict/feature_importance", "🔑 Feature Importance")
