
import React from "react";
import { mockData } from "../lib/mockData";
import { DownloadSimple, CalendarPlus, Funnel } from "@phosphor-icons/react";
import { motion } from "framer-motion";
import type { TimetableCellProps, TimetableEntry, TimetableMap } from "../lib/types";

const TimetableCell: React.FC<TimetableCellProps> = ({ entry }) => {
    if (!entry) return <div className="h-24 bg-zinc-900/20 border border-zinc-800/50 rounded-xl m-1" />;

    return (
        <motion.div 
            whileHover={{ scale: 1.05, zIndex: 10 }}
            className="h-24 bg-gradient-to-br from-zinc-800 to-zinc-900 border-l-4 border-red-500 rounded-r-xl p-2 m-1 shadow-lg cursor-pointer group relative overflow-hidden"
        >
            <div className="absolute top-0 right-0 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="w-2 h-2 bg-green-500 rounded-full" />
            </div>
            <p className="font-bold text-white text-sm truncate">{entry.course}</p>
            <p className="text-xs text-zinc-400 truncate">{entry.room}</p>
            <div className="mt-2 flex items-center gap-1">
                 <span className="text-[10px] bg-red-500/10 text-red-500 px-1.5 py-0.5 rounded border border-red-500/20 font-mono">{entry.time.split(" - ")[0]}</span>
            </div>
        </motion.div>
    );
};

const Timetable = () => {
  const timetable = mockData.timetable as TimetableMap;
  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const times = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"];

  // Helper to find entry for a specific time slot
  const getEntry = (day: string, timeStart: string): TimetableEntry | undefined => {
      const daySchedule = timetable[day] || [];
      return daySchedule.find(entry => entry.time.startsWith(timeStart));
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
           <h1 className="text-3xl font-bold text-white tracking-tight">Master Schedule</h1>
           <p className="text-zinc-400 text-sm">Viewing as <span className="text-white font-bold">Admin</span> • Spring 2026</p>
        </div>
        <div className="flex gap-2">
            <button className="p-2 rounded-lg bg-zinc-900 text-zinc-400 hover:text-white border border-zinc-800"><Funnel /></button>
            <button className="flex items-center gap-2 px-4 py-2 bg-zinc-900 text-white rounded-lg border border-zinc-800 hover:bg-zinc-800 text-sm font-medium"><CalendarPlus /> Google Cal</button>
            <button className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium shadow-lg shadow-red-500/20"><DownloadSimple /> Export PDF</button>
        </div>
      </div>

      <div className="flex-1 overflow-auto bg-[#0f0f0f] border border-zinc-800 rounded-2xl p-4 shadow-2xl">
        <div className="min-w-[1000px]">
             {/* Header */}
             <div className="grid grid-cols-[100px_repeat(8,1fr)] gap-2 mb-4 border-b border-zinc-800 pb-2">
                <div className="text-zinc-500 font-mono text-xs">GMT+5:30</div>
                {times.map(t => (
                    <div key={t} className="text-zinc-500 font-mono text-xs text-center">{t}</div>
                ))}
             </div>

             {/* Body */}
             <div className="space-y-2">
                {days.map(day => (
                    <div key={day} className="grid grid-cols-[100px_repeat(8,1fr)] gap-2">
                        <div className="py-8 font-bold text-zinc-400 text-sm writing-mode-vertical">{day}</div>
                        {times.map(time => (
                            <TimetableCell key={`${day}-${time}`} entry={getEntry(day, time)} />
                        ))}
                    </div>
                ))}
             </div>
        </div>
      </div>
    </div>
  );
};

export default Timetable;
