import { useState } from "react";
import { useForm } from "react-hook-form";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import MetricCard from "@/components/MetricCard";
import {
  DollarSign,
  Home,
  TrendingUp,
  MapPin,
  Clock,
  Loader2,
} from "lucide-react";
import type { HouseFeatures } from "@/services/api";
import {
  predictPrice,
  predictRent,
  predictROI,
  predictNeighborhood,
  predictSellSpeed,
} from "@/services/api";

const Predict = () => {
  const { register, handleSubmit, setValue, watch } = useForm<HouseFeatures>();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  const oceanProximity = watch("ocean_proximity");

  const onSubmit = async (data: HouseFeatures) => {
    setLoading(true);
    setResults(null);

    try {
      // Make all predictions in parallel
      const [price, rent, roi, neighborhood, sellSpeed] = await Promise.all([
        predictPrice(data),
        predictRent(data),
        predictROI(data),
        predictNeighborhood(data),
        predictSellSpeed(data),
      ]);

      setResults({
        price: price.prediction,
        rent: rent.prediction,
        roi: roi.prediction,
        neighborhood: neighborhood.classification,
        neighborhoodScore: neighborhood.score,
        sellSpeed: sellSpeed.classification,
      });

      toast({
        title: "Predictions Complete",
        description: "All metrics have been successfully calculated.",
      });
    } catch (error) {
      toast({
        title: "Prediction Failed",
        description:
          "Unable to fetch predictions. Please check your backend connection.",
        variant: "destructive",
      });
      console.error("Prediction error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 animate-fade-in">
        <h1 className="text-4xl font-bold mb-2">Property Predictions</h1>
        <p className="text-muted-foreground">
          Enter property details to get instant AI-powered predictions
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <Card className="p-6 gradient-card border border-border shadow-card animate-slide-up">
          <h2 className="text-2xl font-bold mb-6">Property Details</h2>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="longitude">Longitude</Label>
                <Input
                  id="longitude"
                  type="number"
                  step="any"
                  placeholder="-122.45"
                  {...register("longitude", { required: true, valueAsNumber: true })}
                />
              </div>
              <div>
                <Label htmlFor="latitude">Latitude</Label>
                <Input
                  id="latitude"
                  type="number"
                  step="any"
                  placeholder="37.75"
                  {...register("latitude", { required: true, valueAsNumber: true })}
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="total_rooms">Total Rooms</Label>
                <Input
                  id="total_rooms"
                  type="number"
                  placeholder="8"
                  {...register("total_rooms", { required: true, valueAsNumber: true })}
                />
              </div>
              <div>
                <Label htmlFor="total_bedrooms">Total Bedrooms</Label>
                <Input
                  id="total_bedrooms"
                  type="number"
                  placeholder="3"
                  {...register("total_bedrooms", { required: true, valueAsNumber: true })}
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="population">Population</Label>
                <Input
                  id="population"
                  type="number"
                  placeholder="1500"
                  {...register("population", { required: true, valueAsNumber: true })}
                />
              </div>
              <div>
                <Label htmlFor="households">Households</Label>
                <Input
                  id="households"
                  type="number"
                  placeholder="500"
                  {...register("households", { required: true, valueAsNumber: true })}
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="housing_median_age">Housing Median Age</Label>
                <Input
                  id="housing_median_age"
                  type="number"
                  placeholder="25"
                  {...register("housing_median_age", {
                    required: true,
                    valueAsNumber: true,
                  })}
                />
              </div>
              <div>
                <Label htmlFor="median_income">Median Income</Label>
                <Input
                  id="median_income"
                  type="number"
                  step="any"
                  placeholder="4.5"
                  {...register("median_income", { required: true, valueAsNumber: true })}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="ocean_proximity">Ocean Proximity</Label>
              <Select
                onValueChange={(value) =>
                  setValue("ocean_proximity", value)
                }
                value={oceanProximity}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select proximity to ocean" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="NEAR BAY">Near Bay</SelectItem>
                  <SelectItem value="<1H OCEAN">Less than 1 hour to ocean</SelectItem>
                  <SelectItem value="INLAND">Inland</SelectItem>
                  <SelectItem value="NEAR OCEAN">Near Ocean</SelectItem>
                  <SelectItem value="ISLAND">Island</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="renovation_budget">
                Renovation Budget (Optional)
              </Label>
              <Input
                id="renovation_budget"
                type="number"
                placeholder="50000"
                {...register("renovation_budget", { valueAsNumber: true })}
              />
            </div>

            <Button
              type="submit"
              className="w-full gradient-primary shadow-glow"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Predicting...
                </>
              ) : (
                "Get Predictions"
              )}
            </Button>
          </form>
        </Card>

        {/* Results */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold mb-6 animate-fade-in">
            Prediction Results
          </h2>

          {!results && !loading && (
            <Card className="p-12 gradient-card border border-border text-center">
              <p className="text-muted-foreground">
                Enter property details and click "Get Predictions" to see results
              </p>
            </Card>
          )}

          {results && (
            <>
              <MetricCard
                title="Predicted Sale Price"
                value={`$${results.price.toLocaleString()}`}
                icon={DollarSign}
                variant="success"
              />
              <MetricCard
                title="Predicted Monthly Rent"
                value={`$${results.rent.toLocaleString()}`}
                icon={Home}
                variant="default"
              />
              <MetricCard
                title="Renovation ROI"
                value={`${results.roi.toFixed(1)}%`}
                subtitle="Expected return on investment"
                icon={TrendingUp}
                variant="default"
              />
              <MetricCard
                title="Neighborhood Investment Score"
                value={results.neighborhood}
                subtitle={`Score: ${results.neighborhoodScore.toFixed(2)}`}
                icon={MapPin}
                variant={
                  results.neighborhood === "High" ? "success" : "default"
                }
              />
              <MetricCard
                title="Predicted Sell Speed"
                value={results.sellSpeed}
                icon={Clock}
                variant="default"
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Predict;
