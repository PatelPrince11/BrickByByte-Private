import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { Card } from "@/components/ui/card";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { Button } from "@/components/ui/button";
import { Layers, Loader2 } from "lucide-react";
import { getMapProperties, type MapProperty } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

// Fix for default markers in Leaflet with Vite
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

// Custom marker icons for different property types
const createCustomIcon = (color: string) => {
  return L.divIcon({
    className: "custom-marker",
    html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.3);"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

const highValueIcon = createCustomIcon("#10b981");
const mediumValueIcon = createCustomIcon("#0A21C0");
const lowValueIcon = createCustomIcon("#ef4444");

const MapView = () => {
  const { toast } = useToast();
  const [mapType, setMapType] = useState<"street" | "satellite">("street");
  const [properties, setProperties] = useState<MapProperty[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProperties();
  }, []);

const loadProperties = async () => {
  try {
    setLoading(true);
    const data = await getMapProperties(100); // Load 100 properties
    setProperties(data); // data is already MapProperty[]
  } catch (error) {
    console.error("Failed to load properties:", error);
    toast({
      title: "Failed to Load Properties",
      description: "Please check your backend connection.",
      variant: "destructive",
    });
  } finally {
    setLoading(false);
  }
};
  const getMarkerIcon = (investmentScore: string) => {
    switch (investmentScore) {
      case "High":
        return highValueIcon;
      case "Medium":
        return mediumValueIcon;
      default:
        return lowValueIcon;
    }
  };

  const highInvestmentCount = properties.filter(
    (p) => p.investment_score === "High"
  ).length;

  const avgPropertyValue =
    properties.length > 0
      ? properties.reduce((sum, p) => sum + p.price, 0) / properties.length
      : 0;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-4xl font-bold mb-2">Interactive Map View</h1>
        <p className="text-muted-foreground">
          Explore properties and neighborhoods with investment insights
        </p>
      </div>

      <Card className="p-4 gradient-card border border-border shadow-card overflow-hidden animate-slide-up">
        <div className="mb-4 flex justify-between items-center">
          <div className="flex gap-2">
            <div className="flex items-center gap-2 text-sm">
              <div className="w-3 h-3 rounded-full bg-success" />
              <span>High Investment</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="w-3 h-3 rounded-full bg-primary" />
              <span>Medium Investment</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <div className="w-3 h-3 rounded-full bg-destructive" />
              <span>Low Investment</span>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              setMapType(mapType === "street" ? "satellite" : "street")
            }
          >
            <Layers className="w-4 h-4 mr-2" />
            {mapType === "street" ? "Satellite" : "Street"} View
          </Button>
        </div>

        {loading ? (
          <div className="h-[600px] rounded-lg border border-border flex items-center justify-center bg-muted">
            <div className="text-center">
              <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-4" />
              <p className="text-muted-foreground">Loading properties...</p>
            </div>
          </div>
        ) : properties.length === 0 ? (
          <div className="h-[600px] rounded-lg border border-border flex items-center justify-center bg-muted">
            <p className="text-muted-foreground">No properties found</p>
          </div>
        ) : (
          <div className="h-[600px] rounded-lg overflow-hidden border border-border">
            <MapContainer
              center={[
                properties[0]?.latitude || 37.0,
                properties[0]?.longitude || -120.0,
              ]}
              zoom={6}
              style={{ height: "100%", width: "100%" }}
              className="z-0"
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url={
                  mapType === "street"
                    ? "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    : "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                }
              />

              {properties.map((property) => (
                <Marker
                  key={property.id}
                  position={[property.latitude, property.longitude]}
                  icon={getMarkerIcon(property.investment_score)}
                >
                  <Popup>
                    <div className="p-2">
                      <h3 className="font-bold text-lg mb-1">
                        Property #{property.id}
                      </h3>
                      <p className="text-sm mb-1">
                        <strong>Price:</strong> $
                        {property.price.toLocaleString()}
                      </p>
                      <p className="text-sm mb-1">
                        <strong>Median Income:</strong> $
                        {(property.median_income * 10000).toLocaleString()}
                      </p>
                      <p className="text-sm mb-1">
                        <strong>Age:</strong> {property.housing_age} years
                      </p>
                      <p className="text-sm">
                        <strong>Investment Score:</strong>{" "}
                        <span
                          className={
                            property.investment_score === "High"
                              ? "text-success font-bold"
                              : property.investment_score === "Medium"
                              ? "text-primary font-bold"
                              : "text-destructive font-bold"
                          }
                        >
                          {property.investment_score}
                        </span>
                      </p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        )}
      </Card>

      <div className="mt-8 grid md:grid-cols-3 gap-6">
        <Card className="p-6 gradient-card border border-border transition-smooth hover:shadow-card">
          <h3 className="text-lg font-bold mb-2">Total Properties</h3>
          <p className="text-3xl font-bold text-primary">
            {properties.length}
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Currently displayed on map
          </p>
        </Card>

        <Card className="p-6 gradient-card border border-border transition-smooth hover:shadow-card">
          <h3 className="text-lg font-bold mb-2">High Investment Areas</h3>
          <p className="text-3xl font-bold text-success">
            {highInvestmentCount}
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Prime investment opportunities
          </p>
        </Card>

        <Card className="p-6 gradient-card border border-border transition-smooth hover:shadow-card">
          <h3 className="text-lg font-bold mb-2">Avg Property Value</h3>
          <p className="text-3xl font-bold text-accent">
            ${Math.round(avgPropertyValue).toLocaleString()}
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Across all locations
          </p>
        </Card>
      </div>
    </div>
  );
};

export default MapView;