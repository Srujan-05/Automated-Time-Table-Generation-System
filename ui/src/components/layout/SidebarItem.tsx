import React from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { type SidebarItemProps } from "@/lib/types";
import { cn } from "@/lib/utils";

export const SidebarItem: React.FC<SidebarItemProps> = ({ 
  icon: Icon, 
  label, 
  path, 
  active, 
  collapsed 
}) => {
  return (
    <Link to={path} className="w-full">
      <div 
        className={cn(
          "flex items-center gap-3 p-3 my-1 rounded-xl transition-all duration-300 group border border-transparent",
          active 
            ? "bg-primary/10 text-primary border-primary/20" 
            : "text-muted-foreground hover:text-foreground hover:bg-card/50"
        )}
      >
        <Icon 
          weight={active ? "fill" : "regular"} 
          className="w-6 h-6 shrink-0 transition-transform group-hover:scale-110" 
        />
        {!collapsed && (
          <span className="font-medium whitespace-nowrap overflow-hidden transition-all">
            {label}
          </span>
        )}
        {active && !collapsed && (
          <motion.div 
            layoutId="active-pill" 
            className="ml-auto w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_var(--color-primary)]"
          />
        )}
      </div>
    </Link>
  );
};
