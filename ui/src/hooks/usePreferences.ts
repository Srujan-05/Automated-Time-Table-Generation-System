import { useState, useEffect } from "react";
import { mockData } from "@/lib/mockData";
import { toast } from "sonner";

export const usePreferences = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [preferences, setPreferences] = useState<Record<string, boolean>>({});
  const [data, setData] = useState<{ days: string[], times: string[] } | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      setData({
        days: mockData.days,
        times: mockData.times
      });
      setIsLoading(false);
    }, 1000);
    return () => clearTimeout(timer);
  }, []);

  const togglePreference = (day: string, time: string) => {
    const key = `${day}-${time}`;
    setPreferences(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const submitPreferences = () => {
    setIsSubmitting(true);
    setTimeout(() => {
      toast.success("Preferences submitted successfully");
      setIsSubmitting(false);
    }, 1500);
  };

  return {
    isLoading,
    isSubmitting,
    preferences,
    togglePreference,
    submitPreferences,
    days: data?.days || [],
    times: data?.times || []
  };
};
