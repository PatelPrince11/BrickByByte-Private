import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navigation from "./components/Navigation";
import Dashboard from "./pages/Dashboard";
import Predict from "./pages/Predict";
import MapView from "./pages/MapView";
import Insights from "./pages/Insights";
import PricePrediction from "./pages/PricePrediction";
import ROIAnalysis from "./pages/ROIAnalysis";
import NeighborhoodInsights from "./pages/NeighborhoodInsights";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Navigation />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/predict" element={<Predict />} />
          <Route path="/map" element={<MapView />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/price-prediction" element={<PricePrediction />} />
          <Route path="/roi-analysis" element={<ROIAnalysis />} />
          <Route path="/neighborhood-insights" element={<NeighborhoodInsights />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
