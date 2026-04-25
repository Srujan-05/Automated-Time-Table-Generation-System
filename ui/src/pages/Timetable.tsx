import { DownloadSimpleIcon, CalendarPlusIcon, FunnelIcon } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { TimetableGrid } from "@/components/timetable/TimetableGrid";
import { type TimetableMap } from "@/lib/types";
import { useTimetable } from "@/hooks/useTimetable";
import { Skeleton } from "@/components/ui/skeleton";

const Timetable = () => {
  const { isLoading, timetable, days, times } = useTimetable();
  const userRole = localStorage.getItem("userRole") || "student";

  if (isLoading) {
    return (
        <div className="space-y-6 h-full flex flex-col pb-8">
            <div className="flex justify-between items-center">
                <Skeleton className="h-12 w-64" />
                <div className="flex gap-2">
                    <Skeleton className="h-12 w-12" />
                    <Skeleton className="h-12 w-32" />
                    <Skeleton className="h-12 w-32" />
                </div>
            </div>
            <Skeleton className="flex-1 rounded-2xl" />
        </div>
    );
  }

  return (
    <div className="space-y-6 h-full flex flex-col pb-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
           <h1 className="text-3xl font-bold text-foreground tracking-tight">Master Schedule</h1>
           <p className="text-muted-foreground text-sm">
             Viewing as <span className="text-primary font-bold capitalize">{userRole}</span> • Spring 2026
           </p>
        </div>
        <div className="flex gap-2">
            <Button variant="outline" size="icon" className="rounded-xl h-12 px-6">
              <FunnelIcon size={18} />
            </Button>
            <Button variant="secondary" className="h-12 px-6 rounded-xl gap-2 font-medium">
              <CalendarPlusIcon size={18} /> Google Cal
            </Button>
            <Button className="h-12 px-6 rounded-xl gap-2 font-medium shadow-lg shadow-primary/20">
              <DownloadSimpleIcon size={18} /> Export PDF
            </Button>
        </div>
      </div>

      <TimetableGrid 
        timetable={timetable as TimetableMap} 
        days={days || []} 
        times={times || []} 
      />
    </div>
  );
};


export default Timetable;
