import React from "react";
import { TimetableMultiCell } from "./TimetableMultiCell";
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
  const getEntries = (day: string, slot: string): TimetableEntry[] => {
    const daySchedule = timetable[day] || [];
    return daySchedule.filter(entry => entry.slot?.toString() === slot);
  };

  const gridTemplate = `60px repeat(${times.length}, 1fr)`;

  return (
    <div className="flex-1 overflow-auto bg-card/30 border border-border rounded-2xl shadow-sm backdrop-blur-sm printable-grid print:bg-white print:shadow-none print:border-none">
      <div style={{ minWidth: Math.max(1500, times.length * 150) + 'px' }} className="print:min-w-0 print:w-full">

        {/* Header */}
        <div 
          className="grid gap-1 mb-2 border-b border-border pt-3 pb-3 sticky top-0 bg-background/80 backdrop-blur z-10 print:pt-0 print:bg-white print:gap-0"
          style={{ gridTemplateColumns: gridTemplate }}
        >
          <div className="text-muted-foreground font-mono text-[10px] uppercase tracking-wider flex items-center justify-center print:text-black">
            SLOT
          </div>
          {times.map(t => (
            <div key={t} className="text-muted-foreground font-mono text-xs text-center font-bold print:text-black print:text-[9px] print:border-l print:border-gray-300">
              {t}
            </div>
          ))}
        </div>

        {/* Body */}
        <div className="space-y-1 print:space-y-0">
          {days.map(day => (
            <div 
              key={day} 
              className="grid gap-1 group print:gap-0 print:border-b print:border-gray-300"
              style={{ gridTemplateColumns: gridTemplate }}
            >
              <div className="flex items-center justify-center font-bold text-muted-foreground text-xs uppercase tracking-tighter py-4 group-hover:text-primary transition-colors border-r border-border/50 print:text-black print:text-[8px] print:py-1 print:border-gray-300">
                {day.substring(0, 3)}
              </div>
              {times.map(time => (
                <TimetableMultiCell 
                  key={`${day}-${time}`} 
                  entries={getEntries(day, time)}
                />
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
