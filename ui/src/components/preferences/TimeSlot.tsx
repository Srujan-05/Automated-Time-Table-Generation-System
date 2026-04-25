import React from "react";
import { cn } from "@/lib/utils";

interface TimeSlotProps {
  time: string;
  selected: boolean | undefined;
  unavailable?: boolean;
  onClick: () => void;
}

export const TimeSlot: React.FC<TimeSlotProps> = ({ 
  time, 
  selected, 
  unavailable, 
  onClick 
}) => {
  return (
    <button
      onClick={onClick}
      disabled={unavailable}
      className={cn(
        "px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200 w-full",
        unavailable 
          ? "bg-muted/50 border-border text-muted-foreground/30 cursor-not-allowed line-through" 
          : selected 
            ? "bg-primary text-primary-foreground border-primary shadow-lg shadow-primary/20" 
            : "bg-card border-border text-muted-foreground hover:border-primary/50 hover:text-foreground"
      )}
    >
      {time}
    </button>
  );
};
