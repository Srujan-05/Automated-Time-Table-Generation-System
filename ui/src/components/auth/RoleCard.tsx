import React from "react";
import { motion } from "framer-motion";
import { type IconComponent } from "@/lib/types";
import { cn } from "@/lib/utils";

interface RoleCardProps {
  icon: IconComponent;
  label: string;
  selected: boolean;
  onClick: () => void;
}

export const RoleCard: React.FC<RoleCardProps> = ({ 
  icon: Icon, 
  label, 
  selected, 
  onClick 
}) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        "flex flex-col items-center justify-center p-6 rounded-2xl border-2 transition-all duration-300 w-full",
        selected 
          ? "border-primary bg-primary/10 shadow-[0_0_30px_rgba(var(--primary),0.2)]" 
          : "border-border bg-card/50 hover:border-muted-foreground/30 hover:bg-muted/30"
      )}
    >
      <div className={cn(
        "p-4 rounded-full mb-4",
        selected ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
      )}>
        <Icon weight={selected ? "fill" : "regular"} className="w-8 h-8" />
      </div>
      <span className={cn(
        "font-medium text-lg",
        selected ? "text-foreground" : "text-muted-foreground"
      )}>
        {label}
      </span>
    </motion.button>
  );
};
