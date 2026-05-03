import React from "react";
import { type TimetableEntry, type TimetableMap } from "@/lib/types";
import { TimetableMultiCell } from "./TimetableMultiCell";

interface ContinuousTimetableGridProps {
  timetable: TimetableMap;
  days: string[];
  times: string[];
}

interface RenderedEntry {
  entry: TimetableEntry;
  rowSpan: number;
  isStart: boolean;
}

export const ContinuousTimetableGrid: React.FC<ContinuousTimetableGridProps> = ({ 
  timetable, 
  days, 
  times 
}) => {
  // Track which entries have been rendered to handle merged cells
  const renderedEntries = new Map<string, number>();

  // Helper to check if entry is continuous (same course, same time slot range)
  const getContinuousSpan = (day: string, slot: number, entryId: number): number => {
    const daySchedule = timetable[day] || [];
    const entry = daySchedule.find(e => e.slot === slot && e.id === entryId);
    if (!entry) return 1;

    let span = 1;
    // Look ahead for same entry in consecutive slots
    for (let nextSlot = slot + 1; nextSlot <= times.length; nextSlot++) {
      const nextEntry = daySchedule.find(e => e.slot === nextSlot && e.id === entryId);
      if (nextEntry && nextEntry.course === entry.course && nextEntry.room === entry.room) {
        span++;
      } else {
        break;
      }
    }
    return span;
  };

  const gridTemplate = `60px repeat(${times.length}, 1fr)`;
  const timeIndex: Record<string, number> = {};
  times.forEach((t, idx) => {
    timeIndex[t] = idx + 1; // 1-indexed for grid positioning
  });

  return (
    <div className="flex-1 overflow-auto bg-card/30 border border-border rounded-2xl shadow-sm backdrop-blur-sm printable-grid">
      <div style={{ minWidth: Math.max(1500, times.length * 150) + 'px' }} className="print:min-w-0 print:w-full">

        {/* Header */}
        <div 
          className="grid gap-1 mb-2 border-b border-border pt-3 pb-3 sticky top-0 bg-background/80 backdrop-blur z-10"
          style={{ gridTemplateColumns: gridTemplate }}
        >
          <div className="text-muted-foreground font-mono text-[10px] uppercase tracking-wider flex items-center justify-center">
            SLOT
          </div>
          {times.map(t => (
            <div key={t} className="text-muted-foreground font-mono text-xs text-center font-bold">
              {t}
            </div>
          ))}
        </div>

        {/* Body with merged cells for continuous classes */}
        <div className="space-y-1">
          {days.map(day => {
            const daySchedule = timetable[day] || [];
            const renderedInDay = new Set<number>(); // Track what we've rendered in this day

            return (
              <div 
                key={day} 
                className="grid gap-1 group"
                style={{ gridTemplateColumns: gridTemplate }}
              >
                <div className="flex items-center justify-center font-bold text-muted-foreground text-xs uppercase tracking-tighter py-4 border-r border-border/50">
                  {day.substring(0, 3)}
                </div>

                {/* Grid cells for each time slot */}
                {times.map((time, slotIndex) => {
                  const slot = parseInt(time);
                  const entriesInSlot = daySchedule.filter(e => e.slot === slot);

                  return (
                    <div key={`${day}-${time}`} className="contents">
                      {entriesInSlot.map((entry, idx) => {
                        // Skip if already rendered as part of a merged cell
                        if (renderedInDay.has(entry.id || idx)) {
                          return null;
                        }

                        const span = getContinuousSpan(day, slot, entry.id || idx);
                        if (span > 1) {
                          renderedInDay.add(entry.id || idx);

                          return (
                            <div
                              key={`${day}-${slot}-${entry.id}-merged`}
                              style={{
                                gridColumn: `${slotIndex + 2} / span ${span}`,
                                gridRow: "auto"
                              }}
                              className="m-1"
                            >
                              <MergedCell entry={entry} />
                            </div>
                          );
                        }

                        return (
                          <div
                            key={`${day}-${slot}-${entry.id}`}
                            className="m-1"
                          >
                            <TimetableMultiCell entries={[entry]} />
                          </div>
                        );
                      })}

                      {/* Empty cell if no entries */}
                      {entriesInSlot.length === 0 && (
                        <div className="h-28 bg-muted/20 border border-border/50 rounded-xl m-1 transition-colors hover:bg-muted/30" />
                      )}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// Component for merged cell displaying continuous classes
const MergedCell: React.FC<{ entry: TimetableEntry }> = ({ entry }) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  return (
    <div 
      onClick={() => setIsExpanded(!isExpanded)}
      className="h-full min-h-28 bg-gradient-to-br from-primary/10 to-primary/5 border-2 border-primary/30 rounded-xl p-3 shadow-md cursor-pointer group hover:shadow-lg hover:border-primary/50 transition-all flex flex-col justify-between"
    >
      <div>
        <p className="font-bold text-foreground text-sm group-hover:text-primary transition-colors">
          {entry.course}
        </p>
        <p className="text-[10px] text-muted-foreground mt-0.5">
          {entry.room} • {entry.professor?.split(" ").pop() || "N/A"}
        </p>
      </div>

      <div className="flex items-center gap-2 mt-auto flex-wrap">
        <span className="text-[10px] bg-primary/20 text-primary px-2 py-0.5 rounded border border-primary/30 font-mono font-medium">
          {entry.type.substring(0, 3).toUpperCase()}
        </span>
        {entry.group && (
          <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded font-mono">
            {entry.group}
          </span>
        )}
      </div>

      <div className="text-[8px] text-primary/60 font-semibold mt-1">
        ↔ Continuous Block
      </div>
    </div>
  );
};
