# 🏡 BrickByByte – Real Estate Insights Platform

## **Project Overview**

ML-powered real estate intelligence platform. The platform predicts property sale prices, rental estimates, ROI from renovations, neighborhood investment scores, and expected sell speed from housing characteristics using XGBoost and scikit-learn. It also visualizes neighborhood clusters on a map to help users identify high-potential areas.

**Live demo:** https://brick-by-byte-private.vercel.app

---

## Features

- 💰 **Price prediction** — XGBoost regression estimating median house value
- 💸 **Rent estimation** — Separate model trained on derived monthly rental values
- 🏗️ **ROI analysis** — Renovation return on investment prediction
- 🏘️ **Neighborhood scoring** — Classification into High / Medium / Low investment tiers
- ⏳ **Sell speed prediction** — Estimated time-to-sell classification
- 🗺️ **Interactive map & Clustering** — 100 sampled properties with investment score overlays and popup details
- **Model insights** — Live feature importance charts per model with real R² scores

---

## Stack

| Layer      | Technology                                          |
| ---------- | --------------------------------------------------- |
| Frontend   | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Backend    | FastAPI, Python 3.11, Uvicorn                       |
| ML         | XGBoost, scikit-learn, pandas, joblib               |
| Maps       | React Leaflet                                       |
| Deployment | Vercel (frontend), Render (backend)                 |

---

## Architecture

```
Browser → Vercel (React/Vite)
              │
              │  HTTPS + JSON  (CORS allowlisted)
              ▼
         Render (FastAPI)
              │
              ├── /predict/*  ──►  XGBoost / sklearn .pkl models
              ├── /stats/*    ──►  augmented_housing.csv
              └── /map/*      ──►  augmented_housing.csv
```

All five models are loaded at startup from serialized `.pkl` files. Each prediction request runs preprocessing (feature engineering + one-hot encoding) then inference — no database involved.

---

## Models

Trained on the California Housing dataset, augmented with engineered features:

| Engineered Feature         | Formula                        |
| -------------------------- | ------------------------------ |
| `rooms_per_household`      | `total_rooms / households`     |
| `bedrooms_per_room`        | `total_bedrooms / total_rooms` |
| `population_per_household` | `population / households`      |

Ocean proximity is one-hot encoded across 5 categories.

| Model        | Algorithm  | Type       | Target                    |
| ------------ | ---------- | ---------- | ------------------------- |
| Price        | XGBoost    | Regressor  | `median_house_value`      |
| Rent         | XGBoost    | Regressor  | `monthly_rent` (derived)  |
| ROI          | XGBoost    | Regressor  | `roi` (derived)           |
| Neighborhood | Classifier | Classifier | `neighborhood_investment` |
| Sell Speed   | Classifier | Classifier | `sell_speed`              |

Regression models use a StandardScaler fitted on training data. Classification models use raw engineered features.

---

## Local Development

**Backend**

```bash
cd backend
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
ALLOWED_ORIGINS=http://localhost:5173 uvicorn brickbybyte_api_backend:app --reload
```

**Frontend**

```bash
cd frontend
npm install
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

Open: http://localhost:5173

---

## Deployment

| Service | Purpose  | Config                                                                                                                                    |
| ------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Render  | Backend  | Build: `pip install -r backend/requirements.txt` · Start: `cd backend && uvicorn brickbybyte_api_backend:app --host 0.0.0.0 --port $PORT` |
| Vercel  | Frontend | Root: `frontend` · Framework: Vite · Build: `npm run build`                                                                               |

**Environment variables:**

| Variable            | Where  | Value                                               |
| ------------------- | ------ | --------------------------------------------------- |
| `ALLOWED_ORIGINS`   | Render | `https://your-app.vercel.app,http://localhost:5173` |
| `VITE_API_BASE_URL` | Vercel | `https://your-api.onrender.com`                     |

---

## API Endpoints

| Method | Endpoint                                  | Description                           |
| ------ | ----------------------------------------- | ------------------------------------- |
| GET    | `/`                                       | Health check                          |
| POST   | `/predict/price`                          | Predict sale price                    |
| POST   | `/predict/rent`                           | Predict monthly rent                  |
| POST   | `/predict/roi`                            | Predict renovation ROI                |
| POST   | `/predict/neighborhood`                   | Classify neighborhood investment tier |
| POST   | `/predict/sell_speed`                     | Classify sell speed                   |
| GET    | `/predict/feature_importance?model=price` | Feature importances                   |
| GET    | `/stats/dashboard`                        | Aggregate dataset statistics          |
| GET    | `/stats/model_performance`                | Real R² and accuracy scores           |
| GET    | `/map/properties?limit=100`               | Sampled properties for map            |

**Predict request body:**

```json
{
  "longitude": -122.45,
  "latitude": 37.75,
  "housing_median_age": 25,
  "total_rooms": 8,
  "total_bedrooms": 3,
  "population": 1500,
  "households": 500,
  "median_income": 4.5,
  "ocean_proximity": "<1H OCEAN",
  "renovation_budget": 50000
}
```

---

## Known Limitations

- **Render cold starts** — Free tier spins down after 15 min idle. First request after inactivity takes ~30s to wake.
- **California-only training data** — Predictions outside California are unreliable; the model has no knowledge of other housing markets.
- **Derived targets** — `monthly_rent` and `roi` are engineered from the dataset, not ground-truth observed values.
- **No held-out test set persisted** — Model performance metrics are computed on the full training dataset, which overstates true generalization performance.
- **Static map sample** — Map always shows the same 100 properties (fixed `random_state=42`), not a live data feed.
