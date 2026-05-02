import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { type TimetableEntry, type TimetableMap } from "@/lib/types";

export const useTimetable = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState<{
    timetable: TimetableMap;
    days: string[];
    times: string[];
  } | null>(null);
  
  // Advanced Multi-Faceted Filters
  const [filters, setFilters] = useState({
    group: "",
    year: "",
    professor: "",
    room: "",
    course: ""
  });

  const [filterOptions, setFilterOptions] = useState<{
    rooms: string[];
    courses: string[];
    professors: string[];
    years: string[];
    batches: string[];
  }>({ rooms: [], courses: [], professors: [], years: [], batches: [] });

  const fetchFilterOptions = useCallback(async () => {
    try {
        const [rooms, courses, professors, groups] = await Promise.all([
            api.timetable.listRooms(),
            api.timetable.listCourses(),
            api.timetable.listProfessors(),
            api.timetable.listGroups()
        ]);
        
        // Categorize groups: if they start with "Year" they are years, otherwise batches
        const years = groups.filter(g => g.startsWith("Year")).map(g => g.replace("Year ", ""));
        const batches = groups.filter(g => !g.startsWith("Year"));

        setFilterOptions({ rooms, courses, professors, years, batches });
    } catch (err) {
        console.error("Failed to fetch filter options", err);
    }
  }, []);

  const updateFilter = (key: keyof typeof filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({ group: "", year: "", professor: "", room: "", course: "" });
  };

  const fetchTimetable = useCallback(async () => {
    setIsLoading(true);
    try {
      // Build query string from active filters
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const entries = await api.timetable.fetchSchedule(params.toString());
      
      const timetable: TimetableMap = {};
      let maxSlot = 0;

      entries.forEach((e: TimetableEntry) => {
          const day = e.day || "Monday";
          if (!timetable[day]) timetable[day] = [];
          timetable[day].push(e);
          if (e.slot > maxSlot) maxSlot = e.slot;
      });

      // Dynamic slot count based on data (min 10)
      const slotCount = Math.max(10, maxSlot);

      setData({
        timetable,
        days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        times: Array.from({ length: slotCount }, (_, i) => `${i + 1}`)
      });
    } catch (err) {
      console.error("Timetable fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  const handlePrint = () => window.print();

  const handleExportCalendar = () => {
    if (!data?.timetable) return;
    
    let icsContent = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//ATGS//Timetable//EN\n";
    
    // Day mapping for ICS
    const dayMap: Record<string, string> = {
      "Monday": "MO", "Tuesday": "TU", "Wednesday": "WE", "Thursday": "TH", "Friday": "FR"
    };

    Object.entries(data.timetable).forEach(([day, entries]) => {
      entries.forEach(e => {
        const startHour = 8 + e.slot; // Rough estimate: classes start at 9AM (slot 1)
        const dateStr = new Date().toISOString().split('T')[0].replace(/-/g, '');
        
        icsContent += "BEGIN:VEVENT\n";
        icsContent += `SUMMARY:${e.course} (${e.type})\n`;
        icsContent += `DESCRIPTION:Prof: ${e.professor}, Group: ${e.group}\n`;
        icsContent += `LOCATION:${e.room}\n`;
        icsContent += `RRULE:FREQ=WEEKLY;BYDAY=${dayMap[day] || 'MO'}\n`;
        // Dummy times for the event
        icsContent += `DTSTART:${dateStr}T${startHour.toString().padStart(2, '0')}0000\n`;
        icsContent += `DTEND:${dateStr}T${(startHour + 1).toString().padStart(2, '0')}0000\n`;
        icsContent += "END:VEVENT\n";
      });
    });

    icsContent += "END:VCALENDAR";

    const blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `timetable_calendar_${new Date().toISOString().split('T')[0]}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  useEffect(() => {
    fetchTimetable();
  }, [fetchTimetable]);

  useEffect(() => {
    fetchFilterOptions();
  }, [fetchFilterOptions]);

  return {
    isLoading,
    ...data,
    filters,
    filterOptions,
    updateFilter,
    clearFilters,
    handlePrint,
    handleExportCalendar,
    refresh: fetchTimetable
  };
};
