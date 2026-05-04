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
        const [roomsData, courses, professors, groups] = await Promise.all([
            api.timetable.listRooms(true), // Request detailed room info
            api.timetable.listCourses(),
            api.timetable.listProfessors(),
            api.timetable.listGroups()
        ]);
        
        // Handle rooms: either array of strings or array of room objects
        const rooms = Array.isArray(roomsData)
          ? roomsData.map(r => typeof r === 'string' ? r : r.name || '')
          : [];
        
        // Categorize groups more accurately
        // Check for common year indicators: "Year", numbers, or levels like "1st", "2nd"
        const years: string[] = [];
        const batches: string[] = [];
        
        groups.forEach((g: string) => {
          const lowerG = g.toLowerCase();
          // Check if group is a year: contains "year", "1st", "2nd", "3rd", "4th", or just digits
          if (lowerG.includes("year") || /^\d+$/.test(g) || /st|nd|rd|th/.test(lowerG)) {
            years.push(g);
          } else {
            batches.push(g);
          }
        });

        setFilterOptions({ rooms, courses, professors, years, batches });
    } catch (err) {
        console.error("Failed to fetch filter options", err);
        // Fallback to empty options on error
        setFilterOptions({ rooms: [], courses: [], professors: [], years: [], batches: [] });
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

      // Sort entries by day and slot for proper rendering
      const sortedEntries = [...entries].sort((a, b) => {
        const dayOrder = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
        const dayA = dayOrder.indexOf(a.day || "Monday");
        const dayB = dayOrder.indexOf(b.day || "Monday");
        if (dayA !== dayB) return dayA - dayB;
        return (a.slot || 0) - (b.slot || 0);
      });

      // Store ALL entries per slot (enabling multi-class display)
      sortedEntries.forEach((e: TimetableEntry) => {
          const day = e.day || "Monday";
          if (!timetable[day]) timetable[day] = [];
          timetable[day].push(e);
          if (e.slot && e.slot > maxSlot) maxSlot = e.slot;
      });

      // Dynamic slot count based on actual data (no minimum)
      const slotCount = maxSlot > 0 ? maxSlot : 1;  // At least 1 slot if data exists

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
    timetable: data?.timetable,
    days: data?.days,
    times: data?.times,
    filters,
    filterOptions,
    updateFilter,
    clearFilters,
    handlePrint,
    handleExportCalendar,
    refresh: fetchTimetable
  };
};
