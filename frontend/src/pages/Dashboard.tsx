import { useEffect, useState } from "react";
import { DollarSign, TrendingUp, MapPin, BarChart3, Home } from "lucide-react";
import MetricCard from "@/components/MetricCard";
import FeatureCard from "@/components/FeatureCard";
import { getDashboardStats, type DashboardStats } from "@/services/api";
import { useToast } from "@/hooks/use-toast";

const Dashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const data = await getDashboardStats();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch dashboard stats:", error);
        toast({
          title: "Failed to Load Statistics",
          description: "Unable to fetch dashboard data. Check backend connection.",
          variant: "destructive",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [toast]);

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 gradient-hero">
        <div className="container mx-auto max-w-6xl">
          <div className="max-w-4xl animate-fade-in">
            <h1 className="text-7xl md:text-8xl font-bold text-foreground mb-8 leading-tight">
              Real Estate
              <br />
              <span className="bg-gradient-accent bg-clip-text text-transparent">
                Intelligence
              </span>
            </h1>
            <p className="text-2xl md:text-3xl text-foreground/80 mb-6 font-light">
              Data-driven insights for smarter property investments
            </p>
            <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
              Leverage advanced machine learning models to predict property prices, analyze ROI,
              and discover high-potential investment opportunities
            </p>
          </div>
        </div>
      </section>

      {/* Metrics Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Avg Property Value"
            value={
              loading
                ? "Loading..."
                : stats
                ? `$${Math.round(stats.avg_property_value).toLocaleString()}`
                : "N/A"
            }
            subtitle={
              stats
                ? "From dataset analysis"
                : "Unable to load data"
            }
            icon={DollarSign}
            trend={stats ? "up" : "neutral"}
            variant="success"
          />
          <MetricCard
            title="Avg ROI Potential"
            value={
              loading
                ? "Loading..."
                : stats
                ? `${stats.avg_roi_potential.toFixed(1)}%`
                : "N/A"
            }
            subtitle="For renovation investments"
            icon={TrendingUp}
            trend={stats ? "up" : "neutral"}
            variant="default"
          />
          <MetricCard
            title="High Investment Areas"
            value={
              loading
                ? "Loading..."
                : stats
                ? stats.high_investment_areas.toString()
                : "N/A"
            }
            subtitle="Neighborhoods analyzed"
            icon={MapPin}
            trend="neutral"
            variant="default"
          />
          <MetricCard
            title="Predictions Made"
            value={
              loading
                ? "Loading..."
                : stats
                ? stats.predictions_made.toLocaleString()
                : "N/A"
            }
            subtitle="Total dataset records"
            icon={BarChart3}
            trend={stats ? "up" : "neutral"}
            variant="default"
          />
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20 bg-secondary/20">
        <div className="text-center mb-16">
          <h2 className="text-5xl md:text-6xl font-bold text-foreground mb-6">
            Powerful Analytics
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to make informed real estate investment decisions
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <FeatureCard
            title="Price Predictions"
            description="Accurate property value estimates using advanced regression models trained on thousands of data points"
            icon={DollarSign}
            accentColor="hsl(228 92% 39%)"
            route="/price-prediction"
          />

          <FeatureCard
            title="ROI Analysis"
            description="Calculate renovation returns and investment opportunities with machine learning insights"
            icon={TrendingUp}
            accentColor="hsl(142 76% 36%)"
            route="/roi-analysis"
          />

          <FeatureCard
            title="Neighborhood Insights"
            description="Investment scores and sell-speed predictions by area to find the perfect location"
            icon={Home}
            accentColor="hsl(180 100% 50%)"
            route="/neighborhood-insights"
          />
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
