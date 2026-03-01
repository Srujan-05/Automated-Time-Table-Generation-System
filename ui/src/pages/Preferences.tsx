
import React, { useState } from "react";
import { CheckCircle } from "@phosphor-icons/react";
import { motion } from "framer-motion";
import type { TimeSlotProps } from "@/lib/types";

const TimeSlot: React.FC<TimeSlotProps> = ({ time, selected, unavailable, onClick }) => (
  <button
    onClick={onClick}
    disabled={unavailable}
    className={`
      px-4 py-3 rounded-xl border text-sm font-medium transition-all duration-200 w-full
      ${unavailable 
        ? "bg-zinc-900/50 border-zinc-800 text-zinc-600 cursor-not-allowed decoration-slice line-through" 
        : selected 
            ? "bg-red-500 text-white border-red-600 shadow-lg shadow-red-500/20" 
            : "bg-zinc-900 border-zinc-800 text-zinc-300 hover:border-red-500/50 hover:text-white"
      }
    `}
  >
    {time}
  </button>
);

const Preferences: React.FC = () => {
  const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
  const times = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00"];
  
  const [preferences, setPreferences] = useState<Record<string, boolean>>({}); // { "Mon-09:00": true }
  
  const togglePreference = (day: string, time: string) => {
    const key = `${day}-${time}`;
    setPreferences(prev => ({
        ...prev,
        [key]: !prev[key]
    }));
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Faculty Preferences</h1>
          <p className="text-zinc-400">Select your preferred teaching slots. We try to accommodate 80% of requests.</p>
        </div>
        <button className="px-6 py-3 bg-white text-black font-bold rounded-xl hover:bg-zinc-200 transition-colors shadow-lg shadow-white/5 flex items-center gap-2">
            <CheckCircle weight="fill" className="text-green-600" />
            Submit Preferences
        </button>
      </div>

      <div className="bg-[#0f0f0f] border border-zinc-800 rounded-3xl p-6 md:p-8 overflow-x-auto">
        <div className="min-w-[600px]">
            <div className="grid grid-cols-[100px_repeat(7,1fr)] gap-4 mb-4">
                <div className="text-xs font-bold text-zinc-500 uppercase tracking-wider self-end pb-2">Day / Time</div>
                {times.map(t => (
                    <div key={t} className="text-center text-xs font-mono text-zinc-500 pb-2">{t}</div>
                ))}
            </div>

            <div className="space-y-4">
                {days.map(day => (
                    <motion.div 
                        key={day} 
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="grid grid-cols-[100px_repeat(7,1fr)] gap-4 items-center"
                    >
                        <div className="font-bold text-zinc-300">{day}</div>
                        {times.map(time => (
                            <TimeSlot 
                                key={`${day}-${time}`} 
                                time={time} 
                                selected={preferences[`${day}-${time}`]} 
                                unavailable={day === "Wed" && time === "14:00"} // Mock unavailable
                                onClick={() => togglePreference(day, time)}
                            />
                        ))}
                    </motion.div>
                ))}
            </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
         <div className="bg-zinc-900/40 border border-zinc-800 p-6 rounded-2xl">
            <h3 className="font-bold text-white mb-4">Constraint Settings</h3>
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <span className="text-zinc-400 text-sm">Max consecutive hours</span>
                    <select className="bg-zinc-950 border border-zinc-800 text-white rounded-lg px-3 py-1 text-sm focus:border-red-500 outline-none">
                        <option>2 Hours</option>
                        <option>3 Hours</option>
                        <option>4 Hours</option>
                    </select>
                </div>
                 <div className="flex items-center justify-between">
                    <span className="text-zinc-400 text-sm">Preferred Room Type</span>
                    <select className="bg-zinc-950 border border-zinc-800 text-white rounded-lg px-3 py-1 text-sm focus:border-red-500 outline-none">
                        <option>Lecture Hall</option>
                        <option>Smart Lab</option>
                    </select>
                </div>
            </div>
         </div>
      </div>
    </div>
  );
};

export default Preferences;
