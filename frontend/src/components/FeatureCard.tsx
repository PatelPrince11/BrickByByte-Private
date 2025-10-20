import { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";

interface FeatureCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  accentColor: string;
  route: string;
}

const FeatureCard = ({ title, description, icon: Icon, accentColor, route }: FeatureCardProps) => {
  const navigate = useNavigate();

  return (
    <Card className="group relative overflow-hidden bg-card border-2 border-border hover:border-primary transition-smooth p-8 shadow-subtle hover:shadow-card">
      {/* Accent decoration */}
      <div 
        className="absolute top-0 right-0 w-32 h-32 opacity-10 transition-smooth group-hover:opacity-20"
        style={{ 
          background: `radial-gradient(circle, ${accentColor} 0%, transparent 70%)` 
        }}
      />
      
      <div className="relative z-10">
        <div className="mb-6 inline-block p-4 rounded-2xl bg-primary/5 group-hover:bg-primary/10 transition-smooth">
          <Icon className="w-10 h-10 text-primary" />
        </div>
        
        <h3 className="text-2xl font-bold text-foreground mb-3 group-hover:text-primary transition-smooth">
          {title}
        </h3>
        
        <p className="text-muted-foreground mb-6 leading-relaxed">
          {description}
        </p>
        
        <Button 
          onClick={() => navigate(route)}
          variant="outline"
          className="group/btn font-semibold"
        >
          Explore Feature
          <span className="ml-2 transition-transform group-hover/btn:translate-x-1">→</span>
        </Button>
      </div>
      
      {/* Bottom accent line */}
      <div 
        className="absolute bottom-0 left-0 h-1 w-0 group-hover:w-full transition-all duration-500"
        style={{ backgroundColor: accentColor }}
      />
    </Card>
  );
};

export default FeatureCard;
