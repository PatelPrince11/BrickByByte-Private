# 🏡 BrickByByte – Real Estate Insights Platform

## **Project Overview**
**BrickByByte** is an advanced real estate analytics platform that helps home buyers, sellers, and real estate agents make data-driven decisions. The platform predicts property sale prices, rental estimates, ROI from renovations, neighborhood investment scores, and expected sell speed. It also visualizes neighborhood clusters on a map to help users identify high-potential areas.  

### **Key Features**
- 💰 **Price Prediction:** Estimate the current market value of a property.  
- 💸 **Rental Price Estimation:** Predict monthly rental value.  
- 🏗️ **Renovation ROI:** Estimate the return on investment from upgrades like adding a bedroom or renovating the kitchen.  
- 🏘️ **Neighborhood Investment Score:** Classify neighborhoods based on potential growth and investment appeal.  
- ⏳ **Sell-Within-30-Days Classification:** Predict how fast a property is likely to sell.  
- 🗺️ **Interactive Map & Clustering:** Visualize neighborhoods, highlight investment potential, and explore geographic trends.  
- 📊 **Feature Importance Dashboard:** Understand which factors impact property value and rent most.  
- 🌌 **Dark-Themed UI:** Professional, modern, and user-friendly interface.

---

## **Tech Stack**
- **Backend:** Python, FastAPI, Scikit-learn, XGBoost, Pandas, Joblib  
- **Frontend:** React.js, React Router, Axios, Leaflet.js / Mapbox, Recharts / Chart.js  
- **Data:** `augmented_housing.csv` (processed dataset with engineered features)  
- **Other:** Node.js / npm, Docker (optional for deployment)  

---

## **Installation & Setup**

### **Clone the Repository**
```bash
git clone https://github.com/yourusername/brickbybyte.git
cd brickbybyte
```

### **Backend Setup**
```bash
cd backend
python -m venv ml_env
source ml_env/bin/activate    # Linux/Mac
ml_env\Scripts\activate       # Windows
pip install -r requirements.txt
```

### **Run Backend API**
```bash
uvicorn brickbybyte_api_backend:app --reload
```

### **Frontend Setup**
```bash
cd frontend
npm install
npm start
```

> **Note:** Update backend URL in frontend config if the backend is not running on `localhost:8000`.

---

## **Usage**
1. Open the website at `http://localhost:3000/`.  
2. Use the **Prediction Form** to enter property details.  
3. View predicted metrics: Price, Rent, ROI, Neighborhood Score, and Sell-Speed.  
4. Explore the **Neighborhood Map** for clustered property insights.  
5. Check the **Feature Importance Dashboard** to understand which features influence predictions the most.

---

## **File Structure**
```
brickbybyte/
│
├── backend/
│   ├── brickbybyte_api_backend.py      # FastAPI backend
│   ├── scripts/
│   │   ├── train_classifiers.py        # Train ML classification models
│   │   ├── evaluate_models.py          # Evaluate regression/classification models
│   │   └── feature_engineering.py      # Feature engineering logic
│   ├── models/                         # Trained ML models and scalers
│   └── data/augmented_housing.csv      # Dataset with engineered features
│
├── frontend/
│   ├── src/
│   │   ├── components/                  # React components (forms, charts, map)
│   │   ├── pages/                       # Page-level React components (Dashboard, Map, Reports)
│   │   ├── services/                    # API service calls
│   │   └── App.js                        # Root React component
│   └── package.json                     # Frontend dependencies
│
└── README.md                             # This file
```

---

## **API Endpoints (FastAPI)**

**POST `/predict/price`**  
- Returns predicted sale price of a property.

**POST `/predict/rent`**  
- Returns predicted monthly rent.

**POST `/predict/roi`**  
- Returns predicted ROI from renovation budget.

**POST `/predict/neighborhood`**  
- Returns neighborhood investment score.

**POST `/predict/sell_speed`**  
- Returns sell-speed classification.

**GET `/predict/feature_importance`**  
- Returns feature importance for regression models.

**Example JSON Payload:**
```json
{
  "longitude": -122.23,
  "latitude": 37.88,
  "housing_median_age": 41,
  "total_rooms": 880,
  "total_bedrooms": 129,
  "population": 322,
  "households": 126,
  "median_income": 8.3252,
  "ocean_proximity": "NEAR BAY",
  "renovation_budget": 5000
}
```

---

## **Color Palette**
- **Obsidian:** `#141619` – background  
- **Gunmetal:** `#2C2E3A` – cards / panels  
- **Deep Navy:** `#050A44` – headers / accents  
- **Cobalt Blue:** `#0A21C0` – buttons / highlights / map markers  
- **Silver Grey:** `#B3B4BD` – text / labels  

---

## **Future Improvements**
- Time-series 1-year price forecasting  
- Multi-target prediction: Price + Rent simultaneously  
- Advanced map filters (ROI, Sell-Speed, Price Range)  
- Export / share reports as PDF or CSV  
- Authentication for real estate agents  

---

## **References / Credits**
- Zillow / Kaggle housing datasets  
- Scikit-learn / XGBoost  
- React.js / Leaflet.js / Chart.js  

---

## **License**
This project is MIT licensed – see the [LICENSE](LICENSE) file for details.
