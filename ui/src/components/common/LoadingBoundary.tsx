import React from "react";
import { cn } from "@/lib/utils";

interface LoadingBoundaryProps {
  className?: string;
  text?: string;
}

export const LoadingBoundary: React.FC<LoadingBoundaryProps> = ({ 
  className, 
  text = "Loading..." 
}) => {
  return (
    <div className={cn("flex flex-col items-center justify-center min-h-[200px] space-y-4", className)}>
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 border-4 border-primary/20 rounded-full" />
        <div className="absolute inset-0 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
      {text && <p className="text-sm font-medium text-muted-foreground animate-pulse">{text}</p>}
    </div>
  );
};
