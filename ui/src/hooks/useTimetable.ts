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
  const [filter, setFilter] = useState<string>("");

  const fetchTimetable = useCallback(async (params?: string) => {
    setIsLoading(true);
    try {
      const entries = await api.timetable.get(params);
      
      const timetable: TimetableMap = {};
      entries.forEach((e: TimetableEntry) => {
          const day = e.day || "Monday";
          if (!timetable[day]) timetable[day] = [];
          timetable[day].push({
              id: e.id,
              course: e.course,
              professor: e.professor,
              room: e.room,
              type: e.type,
              group: e.group,
              day: e.day,
              slot: e.slot
          });
      });

      setData({
        timetable,
        days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        times: Array.from({ length: 10 }, (_, i) => `${i + 1}`)
      });
    } catch (err) {
      console.error("Timetable fetch error:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handlePrint = () => {
    window.print();
  };

  const handleExportCalendar = () => {
    if (!data?.timetable) return;

    const now = new Date();
    const nextMonday = new Date();
    nextMonday.setDate(now.getDate() + (1 + 7 - now.getDay()) % 7);
    nextMonday.setHours(0, 0, 0, 0);

    let icsContent = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PROID:-//MU//Timetable//EN",
      "CALSCALE:GREGORIAN",
      "METHOD:PUBLISH"
    ].join("\n");

    const dayOffsets: Record<string, number> = {
      "Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4
    };

    const getSlotTime = (slot: number) => {
        const startHour = 8 + slot; 
        return { start: startHour, end: startHour + 1 };
    };

    Object.entries(data.timetable).forEach(([day, entries]) => {
      const offset = dayOffsets[day] || 0;
      const eventDate = new Date(nextMonday);
      eventDate.setDate(nextMonday.getDate() + offset);

      entries.forEach(entry => {
        if (!entry.slot) return;
        
        const { start, end } = getSlotTime(entry.slot);
        
        const startDate = new Date(eventDate);
        startDate.setHours(start, 0, 0);
        
        const endDate = new Date(eventDate);
        endDate.setHours(end, 0, 0);

        const formatDate = (date: Date) => {
          return date.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
        };

        icsContent += "\n" + [
          "BEGIN:VEVENT",
          `SUMMARY:${entry.course} (${entry.type})`,
          `DTSTART:${formatDate(startDate)}`,
          `DTEND:${formatDate(endDate)}`,
          `DESCRIPTION:Professor: ${entry.professor}\\nGroup: ${entry.group}\\nRoom: ${entry.room}`,
          `LOCATION:${entry.room}`,
          "END:VEVENT"
        ].join("\n");
      });
    });

    icsContent += "\nEND:VCALENDAR";

    const blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8" });
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.setAttribute("download", `timetable_${filter || 'master'}.ics`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  useEffect(() => {
    const params = filter ? `group=${filter}` : undefined;
    fetchTimetable(params);
  }, [filter, fetchTimetable]);

  return {
    isLoading,
    ...data,
    filter,
    setFilter,
    handlePrint,
    handleExportCalendar,
    refresh: () => fetchTimetable(filter ? `group=${filter}` : undefined)
  };
};
