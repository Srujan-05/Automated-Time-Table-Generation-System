import React from "react";
import { 
  DownloadSimpleIcon, 
  CalendarBlankIcon, 
  FunnelIcon, 
  XIcon, 
  UserIcon, 
  BookIcon, 
  GraduationCapIcon,
  MapPinIcon
} from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { TimetableGrid } from "@/components/timetable/TimetableGrid";
import { ContinuousTimetableGrid } from "@/components/timetable/ContinuousTimetableGrid";
import { type TimetableMap } from "@/lib/types";
import { useTimetable } from "@/hooks/useTimetable";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from "@/components/ui/select";

const Timetable = () => {
  const { 
    isLoading, 
    timetable, 
    days, 
    times, 
    filters, 
    filterOptions,
    updateFilter,
    clearFilters,
    handlePrint, 
    handleExportCalendar 
  } = useTimetable();
  
  const userRole = (localStorage.getItem("userRole") || "student").toLowerCase();
  const isAdmin = userRole === "admin";

  if (isLoading && !timetable) {
    return (
        <div className="space-y-6 h-full flex flex-col pb-8">
            <Skeleton className="h-12 w-64" />
            <Skeleton className="flex-1 rounded-2xl" />
        </div>
    );
  }

  return (
    <div className="space-y-6 h-full flex flex-col pb-8">
      {/* Header & Main Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
           <h1 className="text-3xl font-bold text-foreground tracking-tight">
             {isAdmin ? "Master Schedule" : "My Schedule"}
           </h1>
           <p className="text-muted-foreground text-sm">
             Spring 2026 Academic Calendar
           </p>
        </div>
        <div className="flex gap-2">
            <Button variant="outline" onClick={handleExportCalendar} className="h-11 rounded-xl gap-2 hidden md:flex">
              <CalendarBlankIcon size={18} /> Export
            </Button>
            <Button onClick={handlePrint} className="h-11 rounded-xl gap-2 shadow-lg shadow-primary/10">
              <DownloadSimpleIcon size={18} /> PDF
            </Button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 p-4 bg-card/50 border border-border/50 rounded-2xl backdrop-blur-sm print:hidden">
        {/* Year Filter */}
        <Select 
            value={filters.year || "all"} 
            onValueChange={(val) => updateFilter('year', val === "all" ? "" : val)}
        >
            <SelectTrigger className="h-10 w-full rounded-xl bg-background border-border/50">
                <div className="flex items-center gap-2">
                    <GraduationCapIcon className="text-muted-foreground size-4" />
                    <SelectValue placeholder="All Years" />
                </div>
            </SelectTrigger>
            <SelectContent className="rounded-xl">
                <SelectItem value="all">All Years</SelectItem>
                {filterOptions.years.map(y => (
                    <SelectItem key={y} value={y}>{y}{y.length === 1 ? "th Year" : ""}</SelectItem>
                ))}
            </SelectContent>
        </Select>

        {/* Batch Filter */}
        <Select 
            value={filters.group || "all"} 
            onValueChange={(val) => {
                updateFilter('group', val === "all" ? "" : val);
            }}
        >
            <SelectTrigger className="h-10 w-full rounded-xl bg-background border-border/50">
                <div className="flex items-center gap-2">
                    <FunnelIcon className="text-muted-foreground size-4" />
                    <SelectValue placeholder="Select Batch" />
                </div>
            </SelectTrigger>
            <SelectContent className="rounded-xl max-h-[300px]">
                <SelectItem value="all">All Batches</SelectItem>
                {filterOptions.batches.map(b => (
                    <SelectItem key={b} value={b}>{b}</SelectItem>
                ))}
            </SelectContent>
        </Select>

        {/* Professor Filter */}
        <Select 
            value={filters.professor || "all"} 
            onValueChange={(val) => updateFilter('professor', val === "all" ? "" : val)}
        >
            <SelectTrigger className="h-10 w-full rounded-xl bg-background border-border/50">
                <div className="flex items-center gap-2">
                    <UserIcon className="text-muted-foreground size-4" />
                    <SelectValue placeholder="Filter by Professor" />
                </div>
            </SelectTrigger>
            <SelectContent className="rounded-xl max-h-[300px]">
                <SelectItem value="all">All Professors</SelectItem>
                {filterOptions.professors.map(p => (
                    <SelectItem key={p} value={p}>{p}</SelectItem>
                ))}
            </SelectContent>
        </Select>

        {/* Subject Filter */}
        <Select 
            value={filters.course || "all"} 
            onValueChange={(val) => updateFilter('course', val === "all" ? "" : val)}
        >
            <SelectTrigger className="h-10 w-full rounded-xl bg-background border-border/50">
                <div className="flex items-center gap-2">
                    <BookIcon className="text-muted-foreground size-4" />
                    <SelectValue placeholder="Filter by Subject" />
                </div>
            </SelectTrigger>
            <SelectContent className="rounded-xl max-h-[300px]">
                <SelectItem value="all">All Subjects</SelectItem>
                {filterOptions.courses.map(c => (
                    <SelectItem key={c} value={c}>{c}</SelectItem>
                ))}
            </SelectContent>
        </Select>

        {/* Room Filter */}
        <Select 
            value={filters.room || "all"} 
            onValueChange={(val) => updateFilter('room', val === "all" ? "" : val)}
        >
            <SelectTrigger className="h-10 w-full rounded-xl bg-background border-border/50">
                <div className="flex items-center gap-2">
                    <MapPinIcon className="text-muted-foreground size-4" />
                    <SelectValue placeholder="Filter by Room" />
                </div>
            </SelectTrigger>
            <SelectContent className="rounded-xl max-h-[300px]">
                <SelectItem value="all">All Rooms</SelectItem>
                {filterOptions.rooms.map(r => (
                    <SelectItem key={r} value={r}>{r}</SelectItem>
                ))}
            </SelectContent>
        </Select>

        {(filters.group || filters.year || filters.professor || filters.course || filters.room) && (
            <Button variant="ghost" size="sm" onClick={clearFilters} className="h-10 rounded-xl text-primary font-bold lg:col-start-5">
                <XIcon className="mr-2" /> Clear All
            </Button>
        )}
      </div>

      {/* Grid Container */}
      <div className="flex-1 relative min-h-[500px]">
        {isLoading && (
            <div className="absolute inset-0 bg-background/50 backdrop-blur-[2px] z-50 flex items-center justify-center rounded-2xl">
                <div className="bg-card p-4 rounded-2xl shadow-xl border border-border flex items-center gap-3 animate-bounce">
                    <span className="text-sm font-bold text-primary">Updating Schedule...</span>
                </div>
            </div>
        )}
        {filters.group ? (
          <ContinuousTimetableGrid 
            timetable={timetable as TimetableMap} 
            days={days || []} 
            times={times || []} 
          />
        ) : (
          <TimetableGrid 
            timetable={timetable as TimetableMap} 
            days={days || []} 
            times={times || []} 
          />
        )}
      </div>
    </div>
  );
};

export default Timetable;
