import axios from "axios";

// Backend API configuration
const API_BASE_URL = "http://127.0.0.1:8000";

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
}

export interface NeighborhoodResponse {
  classification: string;
  score: number;
}

export interface SellSpeedResponse {
  classification: string;
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
  timeout: 10000, // 10 second timeout
});

// Error handler
const handleApiError = (error: any) => {
  if (error.response) {
    // Server responded with error
    console.error("API Error:", error.response.data);
    throw new Error(error.response.data.detail || "API request failed");
  } else if (error.request) {
    // Request made but no response
    console.error("Network Error:", error.request);
    throw new Error("Cannot connect to backend. Please ensure the server is running at http://127.0.0.1:8000");
  } else {
    // Something else happened
    console.error("Error:", error.message);
    throw error;
  }
};

export const predictPrice = async (
  features: HouseFeatures
): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/price", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictRent = async (
  features: HouseFeatures
): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/rent", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictROI = async (
  features: HouseFeatures
): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/roi", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictNeighborhood = async (
  features: HouseFeatures
): Promise<NeighborhoodResponse> => {
  try {
    const response = await api.post("/predict/neighborhood", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictSellSpeed = async (
  features: HouseFeatures
): Promise<SellSpeedResponse> => {
  try {
    const response = await api.post("/predict/sell_speed", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getFeatureImportance = async (
  modelType: "price" | "rent" | "roi"
): Promise<FeatureImportance[]> => {
  try {
    const response = await api.get(
      `/predict/feature_importance?model=${modelType}`
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// Health check endpoint
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    await api.get("/");
    return true;
  } catch (error) {
    return false;
  }
};