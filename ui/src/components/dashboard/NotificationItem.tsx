import React from "react";
import { type NotificationItem as NotificationType } from "@/lib/types";

export const NotificationItem: React.FC<NotificationType> = ({ 
  title, 
  message, 
  time 
}) => {
  return (
    <div className="flex gap-4 p-4 rounded-xl hover:bg-muted/50 transition-colors border-b border-border/50 last:border-0">
      <div className="mt-1 shrink-0">
        <div className="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_var(--color-primary)]" />
      </div>
      <div className="min-w-0">
        <h4 className="text-foreground font-medium text-sm truncate">{title}</h4>
        <p className="text-muted-foreground text-sm mt-0.5 line-clamp-1">{message}</p>
        <span className="text-xs text-muted-foreground/50 font-mono mt-2 block">{time}</span>
      </div>
    </div>
  );
};
