import React from "react";
import { ClockIcon, BookOpenIcon, UsersIcon, WarningIcon, BellIcon, CheckCircleIcon, CalendarBlankIcon, TrendUpIcon, InfoIcon } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { StatCard } from "@/components/dashboard/StatCard";
import { NotificationItem } from "@/components/dashboard/NotificationItem";
import { useDashboard } from "@/hooks/useDashboard";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { Spinner } from "@/components/common/Spinner";
import { motion } from "framer-motion";
import { GASettingsDialog } from "@/components/dashboard/GASettingsDialog";

const Dashboard: React.FC = () => {
  const { 
    isLoading, 
    isGenerating, 
    isSettingsOpen,
    setIsSettingsOpen,
    user, 
    notifications, 
    upcoming, 
    stats, 
    handleRunGA, 
    handleExport, 
    refresh 
  } = useDashboard();

  const isAdmin = user?.role === 'admin';
  const isStudent = user?.role === 'student';

  if (isLoading || !user) {
    return (
      <div className="space-y-8 pb-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-2">
            <Skeleton className="h-12 w-64" />
            <Skeleton className="h-4 w-48" />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-32 rounded-2xl" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-8">
      <GASettingsDialog 
        isOpen={isSettingsOpen} 
        onClose={() => setIsSettingsOpen(false)} 
        onConfirm={handleRunGA}
        isGenerating={isGenerating}
      />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground tracking-tight mb-2">
            Good Morning, <span className="text-primary">{user.name.split(" ")[0]}</span>
          </h1>
          <p className="text-muted-foreground font-medium">
            {isAdmin ? "System Overview" : user.role === 'faculty' ? "Faculty Portal" : "Student Hub"} • Spring 2026
          </p>
        </div>
        <div className="flex gap-3">
             <Button variant="outline" size="icon" className="h-12 w-12 rounded-xl">
                <BellIcon className="w-5 h-5" />
             </Button>
             {isAdmin && (
                <Button className="h-12 px-6 rounded-xl font-medium" onClick={() => refresh()}>
                    Refresh Data
                </Button>
             )}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
            title={stats.primary?.label || "Courses"} 
            value={stats.primary?.value.toString() || "0"} 
            icon={BookOpenIcon} 
        />
        <StatCard 
            title={stats.secondary?.label || "People"} 
            value={stats.secondary?.value.toString() || "0"} 
            icon={isStudent ? TrendUpIcon : UsersIcon} 
        />
        <StatCard 
            title={stats.tertiary?.label || "Facility"} 
            value={stats.tertiary?.value.toString() || "0"} 
            icon={isStudent ? UsersIcon : ClockIcon} 
        />
        <StatCard 
            title={stats.quaternary?.label || "Status"} 
            value={stats.quaternary?.value.toString() || "..." } 
            icon={isStudent ? InfoIcon : WarningIcon} 
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className={cn(isAdmin ? "lg:col-span-2" : "lg:col-span-3", "space-y-6")}>
            <div className="space-y-4">
                <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                    <CalendarBlankIcon className="text-primary" weight="bold" /> 
                    {isStudent ? "Today's Classes" : "Upcoming Sessions"}
                </h2>
                <Card className="bg-card/40 border-border/50 rounded-3xl backdrop-blur-sm overflow-hidden p-2">
                    {upcoming && upcoming.length > 0 ? (
                        <div className={cn("grid gap-2", isAdmin ? "grid-cols-1 md:grid-cols-2" : "grid-cols-1 md:grid-cols-3")}>
                            {upcoming.map((item, i) => (
                                <motion.div 
                                    key={item.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                    className="p-4 rounded-2xl bg-muted/30 border border-border/50 flex items-center justify-between group hover:bg-primary/5 transition-colors cursor-default"
                                >
                                    <div className="min-w-0">
                                        <p className="font-bold text-foreground truncate">{item.course}</p>
                                        <p className="text-xs text-muted-foreground truncate">
                                            {user.role === 'faculty' ? `Group: ${item.group}` : `Prof: ${item.professor}`} • {item.room}
                                        </p>
                                    </div>
                                    <div className="text-right shrink-0">
                                        <p className="text-[10px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded-full border border-primary/20">
                                            Slot {item.slot}
                                        </p>
                                        <p className="text-[10px] font-medium text-muted-foreground mt-1 uppercase">{item.day?.substring(0,3)}</p>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    ) : (
                        <div className="p-12 text-center">
                            <p className="text-muted-foreground">No upcoming classes found.</p>
                        </div>
                    )}
                </Card>
            </div>

            {isAdmin && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card className="bg-primary/5 border-primary/20 p-6 rounded-2xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                            <WarningIcon size={60} weight="fill" />
                        </div>
                        <h3 className="font-bold text-foreground">Algorithm Engine</h3>
                        <p className="text-muted-foreground text-sm">Update the master schedule using the GA optimizer.</p>
                        <Button 
                            variant="destructive" 
                            className="w-full h-12 rounded-xl font-medium mt-4"
                            onClick={() => setIsSettingsOpen(true)}
                            disabled={isGenerating}
                        >
                            {isGenerating ? <Spinner className="mr-2" /> : null}
                            {isGenerating ? "Optimizing..." : "Run GA Algorithm"}
                        </Button>
                    </Card>
                    <Card className="bg-card border-border p-6 rounded-2xl">
                        <h3 className="font-bold text-foreground">Export Timetable</h3>
                        <p className="text-muted-foreground text-sm">Download the current schedule in CSV format.</p>
                        <Button 
                            variant="secondary" 
                            className="w-full h-12 rounded-xl font-medium mt-4"
                            onClick={handleExport}
                        >
                            Export CSV
                        </Button>
                    </Card>
                </div>
            )}
        </div>

        {isAdmin && (
            <div className="space-y-6">
                <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                    <BellIcon className="text-primary" /> Notifications
                </h2>
                <Card className="bg-card/40 border-border/50 rounded-2xl backdrop-blur-sm p-2">
                    <div className="divide-y divide-border/50">
                        {notifications.map((n) => (
                            <NotificationItem key={n.id} {...n} />
                        ))}
                    </div>
                </Card>
            </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
