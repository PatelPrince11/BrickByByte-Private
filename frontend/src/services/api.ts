import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

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

export interface PredictionResponse { prediction: number; }
export interface NeighborhoodResponse { classification: string; score: number; }
export interface SellSpeedResponse { classification: string; }
export interface FeatureImportance { feature: string; importance: number; }

export interface DashboardStats {
  avg_property_value: number;
  avg_roi_potential: number;
  high_investment_areas: number;
  predictions_made: number;
}

export interface ModelPerformance {
  price_r2: number;
  rent_r2: number;
  roi_r2: number;
  neighborhood_accuracy: number;
  sell_speed_accuracy: number;
  average_accuracy: number;
}

export interface MapProperty {
  id: number;
  latitude: number;
  longitude: number;
  price: number;
  investment_score: string;
  median_income: number;
  housing_age: number;
}

export interface MapPropertiesResponse {
  properties: MapProperty[];
  total: number;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 5000, // Global default — fast fallback
});

const handleApiError = (error: any) => {
  if (error.response) {
    console.error("API Error:", error.response.data);
    throw new Error(error.response.data.detail || "API request failed");
  } else if (error.request) {
    console.error("Network Error:", error.request);
    throw new Error(
      `Cannot connect to backend at ${API_BASE_URL}. Please ensure the server is running.`,
    );
  } else {
    console.error("Error:", error.message);
    throw error;
  }
};

// Health check — fail fast
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    await api.get("/", { timeout: 2000 });
    return true;
  } catch (error) {
    return false;
  }
};

// Dashboard stats
export const getDashboardStats = async (): Promise<DashboardStats> => {
  try {
    const response = await api.get("/stats/dashboard", { timeout: 5000 });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// Model performance
export const getModelPerformance = async (): Promise<ModelPerformance> => {
  try {
    const response = await api.get("/stats/model_performance", { timeout: 5000 });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

// Map properties
export const getMapProperties = async (limit?: number): Promise<MapProperty[]> => {
  try {
    const response = await api.get("/map/properties", {
      params: limit ? { limit } : {},
      timeout: 5000,
    });
    return response.data.properties;
  } catch (error) {
    throw error;
  }
};

// Predictions — longer timeout, user is waiting for a result
export const predictPrice = async (features: HouseFeatures): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/price", features, { timeout: 10000 });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictRent = async (features: HouseFeatures): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/rent", features, { timeout: 10000 });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictROI = async (features: HouseFeatures): Promise<PredictionResponse> => {
  try {
    const response = await api.post("/predict/roi", features, { timeout: 10000 });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictNeighborhood = async (features: HouseFeatures): Promise<NeighborhoodResponse> => {
  try {
    const response = await api.post("/predict/neighborhood", features, { timeout: 10000 });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const predictSellSpeed = async (features: HouseFeatures): Promise<SellSpeedResponse> => {
  try {
    const response = await api.post("/predict/sell_speed", features, { timeout: 10000 });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};

export const getFeatureImportance = async (
  modelType: "price" | "rent" | "roi",
): Promise<FeatureImportance[]> => {
  try {
    const response = await api.get(`/predict/feature_importance?model=${modelType}`, { timeout: 5000 });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error;
  }
};
