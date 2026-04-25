import { useState, useEffect } from "react";
import { mockData } from "@/lib/mockData";

export const useDashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      const role = localStorage.getItem("userRole") || "student";
      const user = mockData.users[role as keyof typeof mockData.users];
      setData({
        user,
        notifications: mockData.notifications,
        recentChanges: mockData.recentChanges,
        stats: mockData.stats
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
