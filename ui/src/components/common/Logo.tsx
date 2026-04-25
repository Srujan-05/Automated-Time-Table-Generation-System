import React from "react";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  collapsed?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ className, collapsed = false }) => {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center shrink-0">
        <span className="font-bold text-primary-foreground">T</span>
      </div>
      {!collapsed && (
        <span className="font-bold text-xl tracking-tight text-foreground">
          Time<span className="text-primary">Sync</span>
        </span>
      )}
    </div>
  );
};
