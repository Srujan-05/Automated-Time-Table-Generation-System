import { useState, useEffect } from "react";
import { mockData } from "@/lib/mockData";
import { type TimetableMap } from "@/lib/types";

export const useTimetable = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState<{
    timetable: TimetableMap;
    days: string[];
    times: string[];
  } | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setData({
        timetable: mockData.timetable as TimetableMap,
        days: mockData.days,
        times: mockData.times
      });
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return {
    isLoading,
    ...data
  };
};
