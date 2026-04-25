import React from "react";
import { CheckCircleIcon } from "@phosphor-icons/react";
import { motion } from "framer-motion";
import { TimeSlot } from "@/components/preferences/TimeSlot";
import { ConstraintSettings } from "@/components/preferences/ConstraintSettings";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { usePreferences } from "@/hooks/usePreferences";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/common/Spinner";
import { useConstraints } from "@/hooks/useConstraints";

const Preferences: React.FC = () => {
  const { isLoading, isSubmitting, preferences, togglePreference, submitPreferences, days, times } = usePreferences();
  const constraintProps = useConstraints();

  if (isLoading) {
    return (
        <div className="space-y-8 max-w-5xl mx-auto pb-12">
            <div className="flex justify-between items-center">
                <Skeleton className="h-12 w-64" />
                <Skeleton className="h-12 w-48" />
            </div>
            <Skeleton className="h-96 rounded-3xl" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Skeleton className="h-64 rounded-2xl" />
                <Skeleton className="h-64 rounded-2xl" />
            </div>
        </div>
    );
  }

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight mb-2">Faculty Preferences</h1>
          <p className="text-muted-foreground">Select your preferred teaching slots. We try to accommodate 80% of requests.</p>
        </div>
        <Button 
          onClick={submitPreferences}
          disabled={isSubmitting}
          className="h-12 px-6 rounded-xl font-bold shadow-lg shadow-primary/20 flex items-center gap-2"
        >
          {isSubmitting ? <Spinner /> : <CheckCircleIcon weight="fill" size={20} />}
          Submit Preferences
        </Button>
      </div>

      <Card className="bg-sidebar/50 border-border rounded-3xl p-6 md:p-8 overflow-x-auto backdrop-blur-sm">
        <div className="min-w-[800px]">
            <div 
              className="grid gap-4 mb-6" 
              style={{ gridTemplateColumns: `100px repeat(${times.length}, 1fr)` }}
            >
                <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider flex items-end pb-1 px-2">
                  Day / Time
                </div>
                {times.map(t => (
                  <div key={t} className="text-center text-xs font-mono font-bold text-muted-foreground border-b border-border pb-2">
                    {t}
                  </div>
                ))}
            </div>

            <div className="space-y-4">
                {days.map((day, idx) => (
                    <motion.div 
                        key={day} 
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="grid gap-4 items-center group"
                        style={{ gridTemplateColumns: `100px repeat(${times.length}, 1fr)` }}
                    >
                        <div className="font-bold text-muted-foreground group-hover:text-primary transition-colors px-2">
                          {day}
                        </div>
                        {times.map(time => (
                            <TimeSlot 
                                key={`${day}-${time}`} 
                                time={time} 
                                selected={preferences[`${day}-${time}`]} 
                                unavailable={day === "Wednesday" && time === "14:00"}
                                onClick={() => togglePreference(day, time)}
                            />
                        ))}
                    </motion.div>
                ))}
            </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
         <ConstraintSettings {...constraintProps} />
      </div>
    </div>
  );
};


export default Preferences;
