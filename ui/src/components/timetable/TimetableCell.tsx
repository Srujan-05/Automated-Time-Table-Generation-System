import React from "react";
import { motion } from "framer-motion";
import { type TimetableEntry } from "@/lib/types";

interface TimetableCellProps {
  entry?: TimetableEntry;
}

export const TimetableCell: React.FC<TimetableCellProps> = ({ entry }) => {
  if (!entry) {
    return (
      <div className="h-28 bg-muted/20 border border-border/50 rounded-xl m-1 transition-colors hover:bg-muted/30" />
    );
  }

  return (
    <motion.div 
      whileHover={{ scale: 1.02, zIndex: 10 }}
      className="h-28 bg-card border border-border/50 border-l-4 border-l-primary rounded-r-xl p-3 m-1 shadow-sm cursor-pointer group relative overflow-hidden flex flex-col justify-between hover:shadow-md transition-shadow"
    >
      <div className="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
      </div>
      
      <div className="min-w-0">
        <p className="font-bold text-foreground text-sm truncate group-hover:text-primary transition-colors">
          {entry.course}
        </p>
        <p className="text-xs text-muted-foreground truncate mt-0.5">
          {entry.room} • {entry.faculty.split(" ").pop()}
        </p>
      </div>

      <div className="flex items-center gap-2">
        <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded border border-primary/20 font-mono font-medium">
          {entry.time.split(" - ")[0]}
        </span>
        {entry.batch && (
          <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded font-mono">
            {entry.batch}
          </span>
        )}
      </div>
    </motion.div>
  );
};
