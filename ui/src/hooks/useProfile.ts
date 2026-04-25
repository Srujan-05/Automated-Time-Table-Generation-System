import { useState, useEffect } from "react";
import { mockData } from "@/lib/mockData";

export const useProfile = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      const role = localStorage.getItem("userRole") || "student";
      setUser(mockData.users[role as keyof typeof mockData.users]);
      setIsLoading(false);
    }, 800);

    return () => clearTimeout(timer);
  }, []);

  return {
    isLoading,
    user
  };
};
