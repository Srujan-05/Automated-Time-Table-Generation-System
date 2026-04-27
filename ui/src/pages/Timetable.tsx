import { DownloadSimpleIcon, CalendarBlankIcon, FunnelIcon, XIcon } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { TimetableGrid } from "@/components/timetable/TimetableGrid";
import { type TimetableMap } from "@/lib/types";
import { useTimetable } from "@/hooks/useTimetable";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuLabel,
  DropdownMenuSeparator
} from "@/components/ui/dropdown-menu";

const Timetable = () => {
  const { 
    isLoading, 
    timetable, 
    days, 
    times, 
    filter, 
    setFilter, 
    handlePrint, 
    handleExportCalendar 
  } = useTimetable();
  
  const userRole = (localStorage.getItem("userRole") || "student").toLowerCase();
  const isAdmin = userRole === "admin";

  const studentGroups = ["CS1", "CS2", "AI1", "AI2", "ECE", "ECM", "BT", "CE", "ME"];

  if (isLoading && !timetable) {
    return (
        <div className="space-y-6 h-full flex flex-col pb-8">
            <div className="flex justify-between items-center">
                <Skeleton className="h-12 w-64" />
                <div className="flex gap-2">
                    <Skeleton className="h-12 w-32" />
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
           <h1 className="text-3xl font-bold text-foreground tracking-tight">
             {isAdmin ? "Master Schedule" : "My Schedule"}
           </h1>
           <p className="text-muted-foreground text-sm">
             Viewing as <span className="text-primary font-bold capitalize">{userRole}</span> • Spring 2026
             {isAdmin && filter && <span className="ml-2 inline-flex items-center gap-1 bg-primary/10 text-primary px-2 py-0.5 rounded-full text-xs font-bold">
                Filtered: {filter}
                <button onClick={() => setFilter("")} className="hover:text-foreground">
                    <XIcon size={12} weight="bold" />
                </button>
             </span>}
           </p>
        </div>
        <div className="flex gap-2">
            {isAdmin && (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant={filter ? "default" : "outline"} className="h-12 px-6 rounded-xl gap-2 font-medium">
                            <FunnelIcon size={18} /> {filter || "Filter"}
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-56 rounded-xl">
                        <DropdownMenuLabel>Filter by Group</DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem onClick={() => setFilter("")} className="rounded-lg">
                            All Groups
                        </DropdownMenuItem>
                        {studentGroups.map(group => (
                            <DropdownMenuItem key={group} onClick={() => setFilter(group)} className="rounded-lg">
                                {group}
                            </DropdownMenuItem>
                        ))}
                    </DropdownMenuContent>
                </DropdownMenu>
            )}

            <Button 
                variant="secondary" 
                onClick={handleExportCalendar}
                className="h-12 px-6 rounded-xl gap-2 font-medium"
            >
              <CalendarBlankIcon size={18} weight="bold" /> Export Calendar
            </Button>
            <Button 
                onClick={handlePrint}
                className="h-12 px-6 rounded-xl gap-2 font-medium shadow-lg shadow-primary/20"
            >
              <DownloadSimpleIcon size={18} /> Export PDF
            </Button>
        </div>
      </div>

      <div className="flex-1 relative">
        {isLoading && (
            <div className="absolute inset-0 bg-background/50 backdrop-blur-[2px] z-50 flex items-center justify-center rounded-2xl">
                <div className="bg-card p-4 rounded-2xl shadow-xl border border-border flex items-center gap-3">
                    <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    <span className="text-sm font-medium">Updating Schedule...</span>
                </div>
            </div>
        )}
        <TimetableGrid 
            timetable={timetable as TimetableMap} 
            days={days || []} 
            times={times || []} 
        />
      </div>
    </div>
  );
};

export default Timetable;
