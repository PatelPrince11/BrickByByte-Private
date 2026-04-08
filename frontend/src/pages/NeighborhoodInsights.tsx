import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MapPin, TrendingUp, Clock, Star, FlaskConical } from "lucide-react";
import { predictNeighborhood, predictSellSpeed, checkBackendHealth } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const FALLBACK_RESULTS = {
  neighborhoodScore: { classification: "Medium", score: 0.74 },
  sellSpeed: { classification: "Moderate" },
};

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

const NeighborhoodInsights = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [neighborhoodScore, setNeighborhoodScore] = useState<{ classification: string; score: number } | null>(null);
  const [sellSpeed, setSellSpeed] = useState<{ classification: string } | null>(null);
  const [isSample, setIsSample] = useState(false);
  const [formData, setFormData] = useState(DEFAULT_FORM);

  useEffect(() => {
    const init = async () => {
      const healthy = await checkBackendHealth();
      if (!healthy) {
        setNeighborhoodScore(FALLBACK_RESULTS.neighborhoodScore);
        setSellSpeed(FALLBACK_RESULTS.sellSpeed);
        setIsSample(true);
      }
    };
    init();
  }, []);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      const data = {
        longitude: parseFloat(formData.longitude),
        latitude: parseFloat(formData.latitude),
        housing_median_age: parseFloat(formData.housing_median_age),
        total_rooms: parseFloat(formData.total_rooms),
        total_bedrooms: parseFloat(formData.total_bedrooms),
        population: parseFloat(formData.population),
        households: parseFloat(formData.households),
        median_income: parseFloat(formData.median_income),
        ocean_proximity: formData.ocean_proximity,
      };

      const [neighborhood, speed] = await Promise.all([
        predictNeighborhood(data),
        predictSellSpeed(data),
      ]);

      setNeighborhoodScore(neighborhood);
      setSellSpeed(speed);
      setIsSample(false);
      toast({
        title: "Analysis Complete",
        description: "Neighborhood insights have been generated.",
      });
    } catch (error) {
      setNeighborhoodScore(FALLBACK_RESULTS.neighborhoodScore);
      setSellSpeed(FALLBACK_RESULTS.sellSpeed);
      setIsSample(true);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: string) => {
    switch (score.toLowerCase()) {
      case "high":   return { bg: "bg-success/10", text: "text-success", border: "border-success/30" };
      case "medium": return { bg: "bg-warning/10", text: "text-warning", border: "border-warning/30" };
      case "low":    return { bg: "bg-destructive/10", text: "text-destructive", border: "border-destructive/30" };
      default:       return { bg: "bg-muted", text: "text-muted-foreground", border: "border-border" };
    }
  };

  const getSpeedColor = (speed: string) => {
    switch (speed.toLowerCase()) {
      case "fast":     return { bg: "bg-success/10", text: "text-success", border: "border-success/30" };
      case "moderate": return { bg: "bg-warning/10", text: "text-warning", border: "border-warning/30" };
      case "medium":   return { bg: "bg-warning/10", text: "text-warning", border: "border-warning/30" };
      case "slow":     return { bg: "bg-destructive/10", text: "text-destructive", border: "border-destructive/30" };
      default:         return { bg: "bg-muted", text: "text-muted-foreground", border: "border-border" };
    }
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-16 px-4">
      <div className="container mx-auto max-w-6xl">
        <div className="mb-12 text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-foreground mb-4">
            Neighborhood Insights
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Investment scores and sell-speed predictions by area
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Input Form */}
          <Card className="shadow-card border-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="w-6 h-6 text-primary" />
                Location Details
              </CardTitle>
              <CardDescription>
                Enter neighborhood information to get investment insights
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

              <Button onClick={handleAnalyze} disabled={loading} className="w-full" size="lg">
                {loading ? "Analyzing..." : "Analyze Neighborhood"}
              </Button>
            </CardContent>
          </Card>

          {/* Results */}
          <div className="space-y-6">
            {isSample && (
              <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800 px-4 py-3 text-sm text-amber-800 dark:text-amber-300">
                <FlaskConical className="w-4 h-4 mt-0.5 shrink-0" />
                <span>
                  <strong>Demo mode</strong> — backend is offline. Values shown are illustrative only.
                </span>
              </div>
            )}

            <Card className={`shadow-card border-2 ${neighborhoodScore ? getScoreColor(neighborhoodScore.classification).border : "border-border"}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-6 h-6 text-primary" />
                  Investment Score
                </CardTitle>
              </CardHeader>
              <CardContent>
                {neighborhoodScore ? (
                  <div className="text-center space-y-4">
                    <div className={`inline-flex items-center gap-3 px-6 py-3 rounded-2xl ${getScoreColor(neighborhoodScore.classification).bg} border-2 ${getScoreColor(neighborhoodScore.classification).border}`}>
                      <TrendingUp className={`w-8 h-8 ${getScoreColor(neighborhoodScore.classification).text}`} />
                      <span className={`text-3xl font-bold ${getScoreColor(neighborhoodScore.classification).text}`}>
                        {neighborhoodScore.classification.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-muted-foreground">Neighborhood investment potential</p>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Star className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
                    <p className="text-muted-foreground">Enter location details to see investment score</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className={`shadow-card border-2 ${sellSpeed ? getSpeedColor(sellSpeed.classification).border : "border-border"}`}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-6 h-6 text-primary" />
                  Sell Speed Prediction
                </CardTitle>
              </CardHeader>
              <CardContent>
                {sellSpeed ? (
                  <div className="text-center space-y-4">
                    <div className={`inline-flex items-center gap-3 px-6 py-3 rounded-2xl ${getSpeedColor(sellSpeed.classification).bg} border-2 ${getSpeedColor(sellSpeed.classification).border}`}>
                      <Clock className={`w-8 h-8 ${getSpeedColor(sellSpeed.classification).text}`} />
                      <span className={`text-3xl font-bold ${getSpeedColor(sellSpeed.classification).text}`}>
                        {sellSpeed.classification.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-muted-foreground">Expected time to sell</p>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Clock className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
                    <p className="text-muted-foreground">Analyze to see sell speed prediction</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="shadow-subtle border-2">
              <CardHeader>
                <CardTitle>Understanding the Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm text-muted-foreground">
                <div>
                  <strong className="text-foreground">Investment Score:</strong>
                  <p>Evaluates neighborhood growth potential based on income trends, demographics, and property characteristics.</p>
                </div>
                <div>
                  <strong className="text-foreground">Sell Speed:</strong>
                  <p>Predicts how quickly properties typically sell in this area based on market demand and location factors.</p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NeighborhoodInsights;