import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { type TimetableEntry } from "@/lib/types";
import { 
    Dialog, 
    DialogContent, 
    DialogHeader, 
    DialogTitle, 
    DialogTrigger,
    DialogDescription
} from "@/components/ui/dialog";
import { ClockIcon, UserIcon, MapPinIcon, UsersIcon, BookIcon } from "@phosphor-icons/react";

interface TimetableMultiCellProps {
  entries?: TimetableEntry[];
}

export const TimetableMultiCell: React.FC<TimetableMultiCellProps> = ({ entries = [] }) => {
  const [selectedEntry, setSelectedEntry] = useState<TimetableEntry | null>(null);

  if (entries.length === 0) {
    return (
      <div className="h-28 bg-muted/20 border border-border/50 rounded-xl m-1 transition-colors hover:bg-muted/30" />
    );
  }

  // If only one entry, show as before
  if (entries.length === 1) {
    const entry = entries[0];
    return (
      <Dialog>
        <DialogTrigger asChild>
          <motion.div 
            whileHover={{ scale: 1.02, zIndex: 10 }}
            className="h-28 bg-card border rounded-xl p-3 m-1 shadow-sm cursor-pointer group relative overflow-hidden flex flex-col justify-between hover:shadow-md transition-shadow"
          >
            <div className="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="w-1.5 h-1.5 bg-primary rounded-full animate-pulse" />
            </div>
            
            <div className="min-w-0">
              <p className="font-bold text-foreground text-sm truncate group-hover:text-primary transition-colors">
                {entry.course}
              </p>
              <p className="text-[10px] text-muted-foreground truncate mt-0.5">
                {entry.room} • {entry.professor?.split(" ").pop() || "N/A"}
              </p>
            </div>

            <div className="flex items-center gap-2 mt-auto flex-wrap">
              <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded border border-primary/20 font-mono font-medium truncate">
                {entry.type.substring(0, 3).toUpperCase()}
              </span>
              {entry.group && (
                <span className="text-[10px] bg-muted text-muted-foreground px-2 py-0.5 rounded font-mono truncate">
                  {entry.group}
                </span>
              )}
            </div>
          </motion.div>
        </DialogTrigger>
        
        <DialogContent className="sm:max-w-[425px] rounded-3xl border-border bg-card">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold flex items-center gap-2">
              <BookIcon className="text-primary" weight="fill" />
              Session Details
            </DialogTitle>
          </DialogHeader>
          {renderEntryDetails(entry)}
        </DialogContent>
      </Dialog>
    );
  }

  // Multiple entries: show stacked list with expandable preview
  return (
    <div className="h-28 bg-card border rounded-xl p-2 m-1 shadow-sm cursor-pointer group relative overflow-hidden flex flex-col hover:shadow-md transition-shadow border-blue-300/50 bg-blue-50/50">
      <div className="text-[9px] font-bold text-blue-600 mb-1 uppercase tracking-tight">
        {entries.length} Classes
      </div>
      
      <div className="flex-1 overflow-hidden space-y-0.5">
        {entries.slice(0, 2).map((entry, idx) => (
          <Dialog key={entry.id}>
            <DialogTrigger asChild>
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-muted/60 rounded p-1.5 cursor-pointer hover:bg-muted transition-colors"
              >
                <p className="font-semibold text-foreground text-[9px] truncate">
                  {entry.course}
                </p>
                <p className="text-[8px] text-muted-foreground truncate">
                  {entry.room} • {entry.professor?.split(" ").pop() || "N/A"}
                </p>
              </motion.div>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px] rounded-3xl border-border bg-card">
              <DialogHeader>
                <DialogTitle className="text-2xl font-bold flex items-center gap-2">
                  <BookIcon className="text-primary" weight="fill" />
                  Session Details
                </DialogTitle>
              </DialogHeader>
              {renderEntryDetails(entry)}
            </DialogContent>
          </Dialog>
        ))}
      </div>

      {entries.length > 2 && (
        <div className="text-[8px] text-blue-600 font-bold mt-auto">
          +{entries.length - 2} more
        </div>
      )}
    </div>
  );
};

function renderEntryDetails(entry: TimetableEntry) {
  return (
    <div className="grid gap-6 py-4">
      <div className="space-y-4">
        <div className="flex items-center gap-4 p-3 rounded-2xl bg-muted/30 border border-border/50">
          <div className="p-2 bg-background rounded-xl text-primary border border-border/50">
            <BookIcon size={20} weight="bold" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Course</p>
            <p className="font-bold text-foreground">{entry.course}</p>
          </div>
        </div>

        <div className="flex items-center gap-4 p-3 rounded-2xl bg-muted/30 border border-border/50">
          <div className="p-2 bg-background rounded-xl text-primary border border-border/50">
            <UserIcon size={20} weight="bold" />
          </div>
          <div>
            <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Professor</p>
            <p className="font-bold text-foreground">{entry.professor}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
            <div className="flex items-center gap-4 p-3 rounded-2xl bg-muted/30 border border-border/50">
                <div className="p-2 bg-background rounded-xl text-primary border border-border/50">
                    <MapPinIcon size={20} weight="bold" />
                </div>
                <div>
                    <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Room</p>
                    <p className="font-bold text-foreground">{entry.room}</p>
                </div>
            </div>
            <div className="flex items-center gap-4 p-3 rounded-2xl bg-muted/30 border border-border/50">
                <div className="p-2 bg-background rounded-xl text-primary border border-border/50">
                    <UsersIcon size={20} weight="bold" />
                </div>
                <div>
                    <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Group</p>
                    <p className="font-bold text-foreground">{entry.group}</p>
                </div>
            </div>
        </div>

        <div className="flex items-center gap-4 p-3 rounded-2xl bg-muted/30 border border-border/50">
          <div className="p-2 bg-background rounded-xl text-primary border border-border/50">
            <ClockIcon size={20} weight="bold" />
          </div>
          <div className="flex-1 flex justify-between items-center">
            <div>
                <p className="text-[10px] uppercase font-bold text-muted-foreground tracking-widest">Schedule</p>
                <p className="font-bold text-foreground">{entry.day}, Slot {entry.slot}</p>
            </div>
            <div className="bg-primary/10 text-primary text-[10px] font-bold px-3 py-1 rounded-full border border-primary/20 uppercase">
                {entry.type}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
