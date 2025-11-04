import requests
import json

# Test the API endpoint directly
test_data = {
    "longitude": -122.23,
    "latitude": 37.88, 
    "housing_median_age": 25,
    "total_rooms": 1500,
    "total_bedrooms": 300,
    "population": 800,
    "households": 300,
    "median_income": 4.0,
    "ocean_proximity": "NEAR BAY"
}

BASE_URL = "http://127.0.0.1:8000"

print("Testing API endpoints...")

endpoints = ["price", "rent", "roi", "neighborhood", "sell_speed"]

for endpoint in endpoints:
    try:
        response = requests.post(
            f"{BASE_URL}/predict/{endpoint}",
            json=test_data,
            timeout=10
        )
        
        print(f"\n=== {endpoint.upper()} ===")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result}")
            
            if endpoint == "roi":
                roi_value = result['prediction']
                print(f"ROI as decimal: {roi_value}")
                print(f"ROI as percentage: {roi_value * 100:.2f}%")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Failed: {e}")