import { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: "up" | "down" | "neutral";
  variant?: "default" | "success" | "warning" | "destructive";
  loading?: boolean;
}

const MetricCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend = "neutral",
  variant = "default",
  loading = false,
}: MetricCardProps) => {
  const variantStyles = {
    default: "border-border",
    success: "border-success/50 shadow-glow",
    warning: "border-warning/50",
    destructive: "border-destructive/50",
  };

  const trendColors = {
    up: "text-success",
    down: "text-destructive",
    neutral: "text-muted-foreground",
  };

  return (
    <Card
      className={`bg-card border-2 ${variantStyles[variant]} transition-smooth hover:scale-105 hover:shadow-card p-6 animate-slide-up shadow-subtle`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground font-medium mb-2">
            {title}
          </p>
          {loading ? (
            <div className="h-8 w-32 bg-muted animate-pulse rounded" />
          ) : (
            <h3 className="text-3xl font-bold text-foreground mb-1">{value}</h3>
          )}
          {subtitle && (
            <p className={`text-sm ${trendColors[trend]} font-medium`}>
              {subtitle}
            </p>
          )}
        </div>
        <div className="p-3 rounded-xl gradient-primary shadow-glow">
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </Card>
  );
};

export default MetricCard;
