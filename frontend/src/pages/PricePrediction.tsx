import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DollarSign, TrendingUp, MapPin, Home, FlaskConical } from "lucide-react";
import { predictPrice, checkBackendHealth } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const FALLBACK_PREDICTION = 342500;

const DEFAULT_FORM = {
  longitude: "-122.23",
  latitude: "37.88",
  housing_median_age: "35",
  total_rooms: "2000",
  total_bedrooms: "400",
  population: "1500",
  households: "500",
  median_income: "3.5",
  ocean_proximity: "NEAR BAY",
};

const PricePrediction = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [isSample, setIsSample] = useState(false);
  const [formData, setFormData] = useState(DEFAULT_FORM);

  useEffect(() => {
    const init = async () => {
      const healthy = await checkBackendHealth();
      if (!healthy) {
        setPrediction(FALLBACK_PREDICTION);
        setIsSample(true);
      }
    };
    init();
  }, []);

  const handlePredict = async () => {
    setLoading(true);
    try {
      const result = await predictPrice({
        longitude: parseFloat(formData.longitude),
        latitude: parseFloat(formData.latitude),
        housing_median_age: parseFloat(formData.housing_median_age),
        total_rooms: parseFloat(formData.total_rooms),
        total_bedrooms: parseFloat(formData.total_bedrooms),
        population: parseFloat(formData.population),
        households: parseFloat(formData.households),
        median_income: parseFloat(formData.median_income),
        ocean_proximity: formData.ocean_proximity,
      });
      setPrediction(result.prediction);
      setIsSample(false);
      toast({
        title: "Prediction Complete",
        description: "Property value has been estimated successfully.",
      });
    } catch (error) {
      setPrediction(FALLBACK_PREDICTION);
      setIsSample(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-16 px-4">
      <div className="container mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-4">
            Price Predictions
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Accurate property value estimates using advanced regression models
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Input Form */}
          <Card className="shadow-card border-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Home className="w-6 h-6 text-primary" />
                Property Details
              </CardTitle>
              <CardDescription>
                Enter property information to get an accurate price prediction
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="longitude">Longitude</Label>
                  <Input id="longitude" type="number" step="0.000001"
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="latitude">Latitude</Label>
                  <Input id="latitude" type="number" step="0.000001"
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="median_income">Median Income (in $10,000s)</Label>
                <Input id="median_income" type="number" step="0.01"
                  value={formData.median_income}
                  onChange={(e) => setFormData({ ...formData, median_income: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="total_rooms">Total Rooms</Label>
                  <Input id="total_rooms" type="number"
                    value={formData.total_rooms}
                    onChange={(e) => setFormData({ ...formData, total_rooms: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="total_bedrooms">Total Bedrooms</Label>
                  <Input id="total_bedrooms" type="number"
                    value={formData.total_bedrooms}
                    onChange={(e) => setFormData({ ...formData, total_bedrooms: e.target.value })}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="population">Population</Label>
                  <Input id="population" type="number"
                    value={formData.population}
                    onChange={(e) => setFormData({ ...formData, population: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="households">Households</Label>
                  <Input id="households" type="number"
                    value={formData.households}
                    onChange={(e) => setFormData({ ...formData, households: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="housing_median_age">Housing Median Age</Label>
                <Input id="housing_median_age" type="number"
                  value={formData.housing_median_age}
                  onChange={(e) => setFormData({ ...formData, housing_median_age: e.target.value })}
                />
              </div>

              <div>
                <Label htmlFor="ocean_proximity">Ocean Proximity</Label>
                <Select value={formData.ocean_proximity} onValueChange={(value) => setFormData({ ...formData, ocean_proximity: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select proximity" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="<1H OCEAN">{"< 1H OCEAN"}</SelectItem>
                    <SelectItem value="INLAND">INLAND</SelectItem>
                    <SelectItem value="NEAR OCEAN">NEAR OCEAN</SelectItem>
                    <SelectItem value="NEAR BAY">NEAR BAY</SelectItem>
                    <SelectItem value="ISLAND">ISLAND</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <Button onClick={handlePredict} disabled={loading} className="w-full" size="lg">
                {loading ? "Calculating..." : "Get Price Prediction"}
              </Button>
            </CardContent>
          </Card>

          {/* Results */}
          <div className="space-y-6">
            {isSample && (
              <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800 px-4 py-3 text-sm text-amber-800 dark:text-amber-300">
                <FlaskConical className="w-4 h-4 mt-0.5 shrink-0" />
                <span>
                  <strong>Demo mode</strong> — backend is offline. Value shown is illustrative only.
                </span>
              </div>
            )}

            <Card className="shadow-card border-2 border-primary/20 bg-gradient-to-br from-primary/5 to-accent/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="w-6 h-6 text-primary" />
                  Predicted Property Value
                </CardTitle>
              </CardHeader>
              <CardContent>
                {prediction !== null ? (
                  <div className="text-center">
                    <p className="text-5xl font-bold text-primary mb-2">
                      ${Math.round(prediction).toLocaleString()}
                    </p>
                    <p className="text-muted-foreground">Estimated market value</p>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <TrendingUp className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
                    <p className="text-muted-foreground">Enter property details to see prediction</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="shadow-subtle border-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-accent" />
                  How It Works
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-muted-foreground">
                <p>• Our advanced regression models analyze historical property data and market trends</p>
                <p>• Location factors including proximity to ocean and geographic coordinates</p>
                <p>• Property characteristics like size, age, and bedroom count</p>
                <p>• Neighborhood demographics and median income levels</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricePrediction;