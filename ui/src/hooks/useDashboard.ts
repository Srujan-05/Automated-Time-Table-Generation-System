import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { type NotificationItem, type RecentChange, type TimetableEntry, type DashboardStats, type BackendActivity } from "@/lib/types";

export const useDashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [data, setData] = useState<{
    user: { name: string; role: string };
    notifications: NotificationItem[];
    recentChanges: RecentChange[];
    upcoming: TimetableEntry[];
    stats: DashboardStats;
  } | null>(null);

  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);
    try {
      const role = localStorage.getItem("userRole") || "STUDENT";
      const email = localStorage.getItem("userEmail") || "user@college.edu";
      const name = email.split('@')[0].replace('.', ' ').split(' ').map(s => s.charAt(0).toUpperCase() + s.substring(1)).join(' ');
      
      const stats: DashboardStats = await api.timetable.getStats();

      const backendActivities = stats.activities || [];
      const backendUpcoming = stats.upcoming || [];
      
      const notifications: NotificationItem[] = backendActivities
        .filter(a => a.category === 'NOTIFICATION')
        .map(a => ({
            id: a.id,
            title: a.title,
            message: a.message,
            time: new Date(a.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }));

      const recentChanges: RecentChange[] = backendActivities
        .filter(a => a.category === 'CHANGE')
        .map(a => ({
            id: a.id,
            course: a.title.split(' ').slice(-1)[0],
            faculty: "System",
            time: new Date(a.time).toLocaleDateString([], { month: 'short', day: 'numeric' }),
            status: "Approved"
        }));

      setData({
        user: { name, role: role.toLowerCase() },
        notifications: notifications.length > 0 ? notifications : [
            { id: 0, title: "Connected", message: "Live system data loaded successfully.", time: "Just now" }
        ],
        recentChanges,
        upcoming: backendUpcoming,
        stats: stats
      });
    } catch (err) {
      console.error("Dashboard data fetch error:", err);
      const role = localStorage.getItem("userRole")?.toLowerCase() || "student";
      setData({
        user: { name: "User", role },
        notifications: [],
        recentChanges: [],
        upcoming: [],
        stats: {
            active_schedule: false,
            requirements: 0,
            professors: 0,
            primary: { label: "Schedule", value: "Offline" },
            secondary: { label: "Server", value: "Error" },
            tertiary: { label: "Data", value: "None" },
            quaternary: { label: "Status", value: "Retrying..." }
        }
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRunGA = async () => {
    setIsGenerating(true);
    try {
        const res = await api.timetable.generate();
        toast.success(`Schedule generated! Fitness: ${res.fitness.toFixed(2)}`);
        fetchDashboardData();
    } catch (err) {
        toast.error((err as Error).message || "Generation failed");
    } finally {
        setIsGenerating(false);
    }
  };

  const handleExport = () => {
    toast.info("Preparing export...");
    setTimeout(() => {
        const link = document.createElement('a');
        link.href = "http://localhost:5000/instance/timetable.db";
        link.download = "timetable_backup.db";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }, 1500);
  };

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return {
    isLoading,
    isGenerating,
    user: data?.user,
    notifications: data?.notifications || [],
    recentChanges: data?.recentChanges || [],
    upcoming: data?.upcoming || [],
    stats: data?.stats || {
        active_schedule: false,
        requirements: 0,
        professors: 0,
        primary: { label: "Courses", value: "0" },
        secondary: { label: "Status", value: "..." },
        tertiary: { label: "Updates", value: "..." },
        quaternary: { label: "System", value: "..." }
    },
    handleRunGA,
    handleExport,
    refresh: fetchDashboardData
  };
};
