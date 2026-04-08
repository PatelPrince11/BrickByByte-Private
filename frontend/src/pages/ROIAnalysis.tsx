import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { TrendingUp, DollarSign, Calculator, Lightbulb, FlaskConical } from "lucide-react";
import { predictROI, checkBackendHealth } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const FALLBACK_PREDICTION = 18.4;

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
  renovation_budget: "50000",
};

const ROIAnalysis = () => {
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
      const result = await predictROI({
        longitude: parseFloat(formData.longitude),
        latitude: parseFloat(formData.latitude),
        housing_median_age: parseFloat(formData.housing_median_age),
        total_rooms: parseFloat(formData.total_rooms),
        total_bedrooms: parseFloat(formData.total_bedrooms),
        population: parseFloat(formData.population),
        households: parseFloat(formData.households),
        median_income: parseFloat(formData.median_income),
        ocean_proximity: formData.ocean_proximity,
        renovation_budget: parseFloat(formData.renovation_budget),
      });
      setPrediction(result.prediction);
      setIsSample(false);
      toast({
        title: "ROI Calculated",
        description: "Your investment return has been estimated.",
      });
    } catch (error) {
      setPrediction(FALLBACK_PREDICTION);
      setIsSample(true);
    } finally {
      setLoading(false);
    }
  };

  const getROICategory = (roi: number) => {
    if (roi >= 15) return "high";
    if (roi >= 8) return "medium";
    return "low";
  };

  const getROICategoryColor = (category: string) => {
    switch (category) {
      case "high":   return "text-success";
      case "medium": return "text-warning";
      case "low":    return "text-destructive";
      default:       return "text-muted-foreground";
    }
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-16 px-4">
      <div className="container mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-4">ROI Analysis</h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Calculate renovation returns and investment opportunities
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Input Form */}
          <Card className="shadow-card border-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-6 h-6 text-primary" />
                Investment Details
              </CardTitle>
              <CardDescription>
                Enter property and renovation details to calculate ROI
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
                <Label htmlFor="renovation_budget">Renovation Budget ($)</Label>
                <Input id="renovation_budget" type="number"
                  value={formData.renovation_budget}
                  onChange={(e) => setFormData({ ...formData, renovation_budget: e.target.value })}
                />
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
                {loading ? "Calculating ROI..." : "Calculate ROI"}
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

            <Card className="shadow-card border-2 border-success/20 bg-gradient-to-br from-success/5 to-accent/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-6 h-6 text-success" />
                  Return on Investment
                </CardTitle>
              </CardHeader>
              <CardContent>
                {prediction !== null ? (
                  <div className="text-center space-y-4">
                    <div>
                      <p className="text-5xl font-bold text-success mb-2">
                        {prediction.toFixed(2)}%
                      </p>
                      <p className="text-muted-foreground">Expected return</p>
                    </div>
                    <div className={`inline-block px-4 py-2 rounded-full border-2 ${getROICategoryColor(getROICategory(prediction))} font-semibold`}>
                      {getROICategory(prediction).toUpperCase()} ROI
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <DollarSign className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
                    <p className="text-muted-foreground">Enter investment details to calculate ROI</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="shadow-subtle border-2">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-accent" />
                  ROI Insights
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-muted-foreground">
                <p>• <strong>High ROI (15%+):</strong> Excellent investment opportunity with strong returns</p>
                <p>• <strong>Medium ROI (8-15%):</strong> Good investment with moderate returns</p>
                <p>• <strong>Low ROI (&lt;8%):</strong> Consider other investment options</p>
                <p className="pt-2 text-xs">
                  Our models analyze renovation costs, property appreciation potential, and neighborhood growth trends to provide accurate ROI predictions.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ROIAnalysis;