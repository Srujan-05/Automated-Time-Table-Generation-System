import React from "react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ClockIcon } from "@phosphor-icons/react";
import { cn } from "@/lib/utils";

interface Change {
  id: number;
  course: string;
  faculty: string;
  time: string;
  status: string;
}

interface RecentChangesProps {
  changes: Change[];
}

export const RecentChanges: React.FC<RecentChangesProps> = ({ changes }) => {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
        <ClockIcon className="text-primary" /> Recent Schedule Changes
      </h2>
      <Card className="bg-card/40 border-border/50 rounded-2xl backdrop-blur-sm overflow-hidden">
        <div className="p-4 border-b border-border/50 grid grid-cols-4 text-sm font-medium text-muted-foreground">
          <span>Course</span>
          <span>Faculty</span>
          <span>New Time</span>
          <span>Status</span>
        </div>
        <div className="divide-y divide-border/50">
          {changes.map((change, i) => (
            <motion.div 
              key={change.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="p-4 grid grid-cols-4 items-center hover:bg-muted/50 transition-colors cursor-pointer group"
            >
              <span className="font-mono text-foreground group-hover:text-primary transition-colors font-medium">
                {change.course}
              </span>
              <span className="text-muted-foreground">{change.faculty}</span>
              <span className="text-muted-foreground">{change.time}</span>
              <div className="w-fit">
                <Badge 
                  variant={change.status === "Approved" ? "default" : "outline"}
                  className={cn(
                    "font-mono text-[10px]",
                    change.status === "Approved" ? "bg-green-500/10 text-green-500 hover:bg-green-500/20 border-green-500/20" : ""
                  )}
                >
                  {change.status}
                </Badge>
              </div>
            </motion.div>
          ))}
        </div>
      </Card>
    </div>
  );
};
