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
  timeout: 30000, // 30 second timeout for ML predictions
});

// Error handler
const handleApiError = (error: any) => {
  if (error.response) {
    console.error("API Error:", error.response.data);
    throw new Error(error.response.data.detail || "API request failed");
  } else if (error.request) {
    console.error("Network Error:", error.request);
    throw new Error("Cannot connect to backend. Please ensure the server is running at http://127.0.0.1:8000");
  } else {
    console.error("Error:", error.message);
    throw error;
  }
};

// API functions with better error handling
export const predictPrice = async (features: HouseFeatures): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/price", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictRent = async (features: HouseFeatures): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/rent", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictROI = async (features: HouseFeatures): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/roi", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictNeighborhood = async (features: HouseFeatures): Promise<NeighborhoodResponse> => {
  try {
    const response = await api.post("/predict/neighborhood", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictSellSpeed = async (features: HouseFeatures): Promise<SellSpeedResponse> => {
  try {
    const response = await api.post("/predict/sell_speed", features);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// Mock feature importance for now
export const getFeatureImportance = async (modelType: "price" | "rent" | "roi"): Promise<FeatureImportance[]> => {
  // Return mock data since this endpoint isn't implemented yet
  const mockData: FeatureImportance[] = [
    { feature: "median_income", importance: 0.42 },
    { feature: "ocean_proximity", importance: 0.18 },
    { feature: "total_rooms", importance: 0.15 },
    { feature: "latitude", importance: 0.12 },
    { feature: "housing_median_age", importance: 0.08 },
    { feature: "population", importance: 0.05 },
  ];
  
  return new Promise((resolve) => {
    setTimeout(() => resolve(mockData), 500);
  });
};

// Health check endpoint
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    await api.get("/health");
    return true;
  } catch (error) {
    console.error("Backend health check failed:", error);
    return false;
  }
};