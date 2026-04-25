import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { type IconComponent } from "@/lib/types";

interface StatCardProps {
  title: string;
  value: string;
  icon: IconComponent;
  trend?: string;
}

export const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  icon: Icon, 
  trend 
}) => {
  return (
    <Card className="bg-card/50 border-border/50 overflow-hidden hover:border-primary/30 transition-all group backdrop-blur-sm rounded-2xl">
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="p-3 rounded-xl bg-secondary text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary transition-colors">
            <Icon weight="duotone" className="w-6 h-6" />
          </div>
          {trend && (
            <span className="text-xs font-mono text-green-500 bg-green-500/10 px-2 py-1 rounded-full border border-green-500/20">
              {trend}
            </span>
          )}
        </div>
        <h3 className="text-muted-foreground text-sm font-medium mb-1">{title}</h3>
        <p className="text-3xl font-bold text-foreground font-sans">{value}</p>
      </CardContent>
    </Card>
  );
};
