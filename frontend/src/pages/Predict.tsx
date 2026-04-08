import { useState, useEffect } from "react";
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
  FlaskConical,
} from "lucide-react";
import type { HouseFeatures } from "@/services/api";
import {
  predictPrice,
  predictRent,
  predictROI,
  predictNeighborhood,
  predictSellSpeed,
  checkBackendHealth,
} from "@/services/api";

const DEFAULT_INPUTS: HouseFeatures = {
  longitude: -122,
  latitude: 37.75,
  housing_median_age: 25,
  total_rooms: 8,
  total_bedrooms: 3,
  population: 1500,
  households: 500,
  median_income: 4.5,
  ocean_proximity: "INLAND",
  renovation_budget: 50000,
};

const FALLBACK_RESULTS = {
  price: 342500,
  rent: 1850,
  roi: 18.4,
  neighborhood: "Medium",
  neighborhoodScore: 0.74,
  sellSpeed: "Moderate",
  isSample: true,
};

const Predict = () => {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<HouseFeatures>({ defaultValues: DEFAULT_INPUTS });

  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  const oceanProximity = watch("ocean_proximity");

  // On mount: check backend and immediately show fallback if offline
  useEffect(() => {
    const init = async () => {
      const healthy = await checkBackendHealth();
      setBackendOnline(healthy);
      if (!healthy) {
        setResults(FALLBACK_RESULTS);
      }
    };
    init();
  }, []);

  const onSubmit = async (data: HouseFeatures) => {
    setLoading(true);
    setResults(null);

    try {
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
        isSample: false,
      });

      toast({
        title: "Predictions Complete",
        description: "All metrics have been successfully calculated.",
      });
    } catch (error) {
      console.error("Prediction error:", error);
      setResults(FALLBACK_RESULTS);
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
            {/* Coordinates */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="longitude">Longitude</Label>
                <Input
                  id="longitude"
                  type="number"
                  step="any"
                  className={errors.longitude ? "border-destructive" : ""}
                  {...register("longitude", {
                    required: "Required",
                    valueAsNumber: true,
                    min: { value: -180, message: "Min −180" },
                    max: { value: 180, message: "Max 180" },
                  })}
                />
                {errors.longitude && (
                  <p className="text-xs text-destructive mt-1">{errors.longitude.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="latitude">Latitude</Label>
                <Input
                  id="latitude"
                  type="number"
                  step="any"
                  className={errors.latitude ? "border-destructive" : ""}
                  {...register("latitude", {
                    required: "Required",
                    valueAsNumber: true,
                    min: { value: -90, message: "Min −90" },
                    max: { value: 90, message: "Max 90" },
                  })}
                />
                {errors.latitude && (
                  <p className="text-xs text-destructive mt-1">{errors.latitude.message}</p>
                )}
              </div>
            </div>

            {/* Rooms */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="total_rooms">Total Rooms</Label>
                <Input
                  id="total_rooms"
                  type="number"
                  className={errors.total_rooms ? "border-destructive" : ""}
                  {...register("total_rooms", {
                    required: "Required",
                    valueAsNumber: true,
                    min: { value: 1, message: "Must be ≥ 1" },
                  })}
                />
                {errors.total_rooms && (
                  <p className="text-xs text-destructive mt-1">{errors.total_rooms.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="total_bedrooms">Total Bedrooms</Label>
                <Input
                  id="total_bedrooms"
                  type="number"
                  className={errors.total_bedrooms ? "border-destructive" : ""}
                  {...register("total_bedrooms", {
                    required: "Required",
                    valueAsNumber: true,
                    min: { value: 1, message: "Must be ≥ 1" },
                  })}
                />
                {errors.total_bedrooms && (
                  <p className="text-xs text-destructive mt-1">{errors.total_bedrooms.message}</p>
                )}
              </div>
            </div>

            {/* Population & Households */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="population">Population</Label>
                <Input
                  id="population"
                  type="number"
                  className={errors.population ? "border-destructive" : ""}
                  {...register("population", {
                    required: "Required",
                    valueAsNumber: true,
                    min: { value: 1, message: "Must be ≥ 1" },
                  })}
                />
                {errors.population && (
                  <p className="text-xs text-destructive mt-1">{errors.population.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="households">Households</Label>
                <Input
                  id="households"
                  type="number"
                  className={errors.households ? "border-destructive" : ""}
                  {...register("households", {
                    required: "Required",
                    valueAsNumber: true,
                    min: { value: 1, message: "Must be ≥ 1" },
                  })}
                />
                {errors.households && (
                  <p className="text-xs text-destructive mt-1">{errors.households.message}</p>
                )}
              </div>
            </div>

            {/* Age & Income */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="housing_median_age">Housing Median Age</Label>
                <Input
                  id="housing_median_age"
                  type="number"
                  className={errors.housing_median_age ? "border-destructive" : ""}
                  {...register("housing_median_age", {
                    required: "Required",
                    valueAsNumber: true,
                    min: { value: 1, message: "Must be ≥ 1" },
                    max: { value: 52, message: "Max 52" },
                  })}
                />
                {errors.housing_median_age && (
                  <p className="text-xs text-destructive mt-1">{errors.housing_median_age.message}</p>
                )}
              </div>
              <div>
                <Label htmlFor="median_income">
                  Median Income{" "}
                  <span className="text-xs text-muted-foreground">(scaled 0.5–15)</span>
                </Label>
                <Input
                  id="median_income"
                  type="number"
                  step="any"
                  className={errors.median_income ? "border-destructive" : ""}
                  {...register("median_income", {
                    required: "Required",
                    valueAsNumber: true,
                    min: { value: 0.5, message: "Min 0.5" },
                    max: { value: 15, message: "Max 15" },
                  })}
                />
                {errors.median_income && (
                  <p className="text-xs text-destructive mt-1">{errors.median_income.message}</p>
                )}
              </div>
            </div>

            {/* Ocean Proximity */}
            <div>
              <Label htmlFor="ocean_proximity">Ocean Proximity</Label>
              <Select
                onValueChange={(value) =>
                  setValue("ocean_proximity", value, { shouldValidate: true })
                }
                value={oceanProximity}
              >
                <SelectTrigger className={errors.ocean_proximity ? "border-destructive" : ""}>
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
              <input
                type="hidden"
                {...register("ocean_proximity", { required: "Select an option" })}
              />
              {errors.ocean_proximity && (
                <p className="text-xs text-destructive mt-1">{errors.ocean_proximity.message}</p>
              )}
            </div>

            {/* Renovation Budget */}
            <div>
              <Label htmlFor="renovation_budget">
                Renovation Budget{" "}
                <span className="text-xs text-muted-foreground">(Optional)</span>
              </Label>
              <Input
                id="renovation_budget"
                type="number"
                className={errors.renovation_budget ? "border-destructive" : ""}
                {...register("renovation_budget", {
                  setValueAs: (v) =>
                    v === "" || v === null || isNaN(Number(v)) ? 0 : Number(v),
                  min: { value: 0, message: "Can't be negative" },
                })}
              />
              {errors.renovation_budget && (
                <p className="text-xs text-destructive mt-1">{errors.renovation_budget.message}</p>
              )}
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
          <h2 className="text-2xl font-bold mb-2 animate-fade-in">Prediction Results</h2>

          {/* Sample data disclaimer */}
          {results?.isSample && (
            <div className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 dark:bg-amber-950/20 dark:border-amber-800 px-4 py-3 text-sm text-amber-800 dark:text-amber-300">
              <FlaskConical className="w-4 h-4 mt-0.5 shrink-0" />
              <span>
                <strong>Sample prediction</strong> — backend is offline. Values shown are
                illustrative only and not based on your inputs.
              </span>
            </div>
          )}

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
                value={`$${Math.round(results.price).toLocaleString()}`}
                icon={DollarSign}
                variant="success"
              />
              <MetricCard
                title="Predicted Monthly Rent"
                value={`$${Math.round(results.rent).toLocaleString()}`}
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
                subtitle={`Confidence: ${(results.neighborhoodScore * 100).toFixed(0)}%`}
                icon={MapPin}
                variant={results.neighborhood === "High" ? "success" : "default"}
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