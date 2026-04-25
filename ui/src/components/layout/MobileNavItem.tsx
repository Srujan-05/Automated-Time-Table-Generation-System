import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { type IconComponent } from "@/lib/types";
import { cn } from "@/lib/utils";

interface MobileNavItemProps {
  icon: IconComponent;
  path: string;
  active: boolean;
}

export const MobileNavItem: React.FC<MobileNavItemProps> = ({ 
  icon: Icon, 
  path, 
  active 
}) => {
  return (
    <Link to={path} className="flex flex-col items-center justify-center w-full h-full relative">
      <div 
        className={cn(
          "p-2 rounded-full transition-all duration-300 relative",
          active ? "text-primary bg-primary/10" : "text-muted-foreground"
        )}
      >
        <Icon weight={active ? "fill" : "regular"} className="w-6 h-6" />
        {active && (
          <motion.div 
            layoutId="mobile-active-glow"
            className="absolute inset-0 rounded-full bg-primary/20 blur-md"
          />
        )}
      </div>
    </Link>
  );
};
