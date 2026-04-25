import React from "react";
import { TimetableCell } from "./TimetableCell";
import { type TimetableEntry, type TimetableMap } from "@/lib/types";

interface TimetableGridProps {
  timetable: TimetableMap;
  days: string[];
  times: string[];
}

export const TimetableGrid: React.FC<TimetableGridProps> = ({ 
  timetable, 
  days, 
  times 
}) => {
  const getEntry = (day: string, timeStart: string): TimetableEntry | undefined => {
    const daySchedule = timetable[day] || [];
    return daySchedule.find(entry => entry.time.startsWith(timeStart));
  };

  return (
    <div className="flex-1 overflow-auto bg-card/30 border border-border rounded-2xl p-4 shadow-sm backdrop-blur-sm">
      <div className="min-w-[1000px]">
        {/* Header */}
        <div className="grid grid-cols-[100px_repeat(8,1fr)] gap-2 mb-4 border-b border-border pb-3">
          <div className="text-muted-foreground font-mono text-[10px] uppercase tracking-wider flex items-center justify-center">
            GMT+5:30
          </div>
          {times.map(t => (
            <div key={t} className="text-muted-foreground font-mono text-xs text-center font-medium">
              {t}
            </div>
          ))}
        </div>

        {/* Body */}
        <div className="space-y-1">
          {days.map(day => (
            <div key={day} className="grid grid-cols-[100px_repeat(8,1fr)] gap-2 group">
              <div className="flex items-center justify-center font-bold text-muted-foreground text-xs uppercase tracking-tighter py-4 group-hover:text-primary transition-colors">
                {day.substring(0, 3)}
              </div>
              {times.map(time => (
                <TimetableCell key={`${day}-${time}`} entry={getEntry(day, time)} />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
