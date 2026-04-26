import { useState, useEffect } from "react";

export const useProfile = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<{
    name: string;
    email: string;
    role: string;
  } | null>(null);

  useEffect(() => {
    const timer = setTimeout(() => {
      const role = localStorage.getItem("userRole") || "student";
      const email = localStorage.getItem("userEmail") || "user@college.edu";
      const name = email.split('@')[0].replace('.', ' ').split(' ').map(s => s.charAt(0).toUpperCase() + s.substring(1)).join(' ');
      
      setUser({
        name,
        email,
        role,
      });
      setIsLoading(false);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  return {
    isLoading,
    user: user || { name: "User", email: "", role: "student" }
  };
};
