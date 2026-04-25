import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { FileCsvIcon } from "@phosphor-icons/react";

interface IngestionCardProps {
  type: string;
  description: string;
}

export const IngestionCard: React.FC<IngestionCardProps> = ({ type, description }) => {
  return (
    <Card className="bg-card/40 border-border/50 p-6 rounded-2xl hover:border-primary/30 transition-all cursor-pointer group">
      <CardContent className="p-0">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-foreground">{type} CSV</h3>
          <FileCsvIcon className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors" />
        </div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
};

