import axios from "axios";

// Backend API configuration
// TODO: Replace with your actual backend URL
const API_BASE_URL = "http://127.0.0.1:8000"; // Update this to your FastAPI backend URL

export interface HouseFeatures {
  longitude: number;
  latitude: number;
  housing_median_age: number;
  total_rooms: number;
  total_bedrooms: number;
  population: number;
  households: number;
  median_income: number;
  ocean_proximity: string;
  renovation_budget?: number;
}

export interface PredictionResponse {
  prediction: number;
  confidence?: number;
}

export interface NeighborhoodResponse {
  classification: string;
  score: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const predictPrice = async (
  features: HouseFeatures
): Promise<PredictionResponse> => {
  const response = await api.post("/predict/price", features);
  return response.data;
};

export const predictRent = async (
  features: HouseFeatures
): Promise<PredictionResponse> => {
  const response = await api.post("/predict/rent", features);
  return response.data;
};

export const predictROI = async (
  features: HouseFeatures
): Promise<PredictionResponse> => {
  const response = await api.post("/predict/roi", features);
  return response.data;
};

export const predictNeighborhood = async (
  features: HouseFeatures
): Promise<NeighborhoodResponse> => {
  const response = await api.post("/predict/neighborhood", features);
  return response.data;
};

export const predictSellSpeed = async (
  features: HouseFeatures
): Promise<{ classification: string }> => {
  const response = await api.post("/predict/sell_speed", features);
  return response.data;
};

export const getFeatureImportance = async (
  modelType: "price" | "rent" | "roi"
): Promise<FeatureImportance[]> => {
  const response = await api.get(
    `/predict/feature_importance?model=${modelType}`
  );
  return response.data;
};
