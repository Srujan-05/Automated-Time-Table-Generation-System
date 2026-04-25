import React from "react";
import { ClockIcon, BookOpenIcon, UsersIcon, WarningIcon, BellIcon, CheckCircleIcon } from "@phosphor-icons/react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { StatCard } from "@/components/dashboard/StatCard";
import { NotificationItem } from "@/components/dashboard/NotificationItem";
import { RecentChanges } from "@/components/dashboard/RecentChanges";
import { useDashboard } from "@/hooks/useDashboard";
import { Skeleton } from "@/components/ui/skeleton";

const Dashboard: React.FC = () => {
  const { isLoading, user, notifications, recentChanges, stats } = useDashboard();

  if (isLoading) {
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton className="h-96 rounded-2xl" />
          </div>
          <div className="space-y-6">
            <Skeleton className="h-96 rounded-2xl" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold text-foreground tracking-tight mb-2">
            Good Morning, <span className="text-primary">{user.name.split(" ")[0]}</span>
          </h1>
          <p className="text-muted-foreground">Here's what's happening in your campus today.</p>
        </div>
        <div className="flex gap-3">
             <Button variant="outline" size="icon" className="h-12 w-12 rounded-xl">
                <BellIcon className="w-5 h-5" />
             </Button>
             <Button className="h-12 px-6 rounded-xl font-medium">
                Generate Report
             </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Courses" value={stats.totalCourses} icon={BookOpenIcon} trend="+12%" />
        <StatCard title="Active Faculty" value={stats.activeFaculty} icon={UsersIcon} trend="+3" />
        <StatCard title="Weekly Hours" value={stats.weeklyHours} icon={ClockIcon} />
        <StatCard title="Conflicts" value={stats.conflicts} icon={WarningIcon} trend="Perfect" />
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Quick Actions / Recent Activity */}
        <div className="lg:col-span-2 space-y-6">
            <RecentChanges changes={recentChanges} />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <Card className="bg-primary/5 border-primary/20 p-6 rounded-2xl relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                        <WarningIcon size={60} weight="fill" />
                    </div>
                    <h3 className="font-bold text-foreground">Conflict Check</h3>
                    <p className="text-muted-foreground text-sm">Run the GA algorithm to find potential overlaps.</p>
                    <Button variant="destructive" className="w-full h-12 rounded-xl font-medium">Run Check</Button>
                 </Card>
                 <Card className="bg-card border-border p-6 rounded-2xl">
                    <h3 className="font-bold text-foreground">Export Data</h3>
                    <p className="text-muted-foreground text-sm">Download current schedule as PDF or CSV.</p>
                    <Button variant="secondary" className="w-full h-12 rounded-xl font-medium">Export</Button>
                 </Card>
            </div>
        </div>

        {/* Notifications & upcoming */}
        <div className="space-y-6">
             <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                <BellIcon className="text-primary" /> Notifications
            </h2>
            <Card className="bg-card/40 border-border/50 rounded-2xl backdrop-blur-sm p-2">
                <div className="divide-y divide-border/50">
                    {notifications.map((n: any) => (
                        <NotificationItem key={n.id} {...n} />
                    ))}
                </div>
                <Button variant="ghost" className="w-full py-6 text-sm text-muted-foreground hover:text-primary transition-colors rounded-xl">
                    View All Notifications
                </Button>
            </Card>

             <Card className="bg-card border-border p-6 rounded-2xl relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                    <CheckCircleIcon size={100} weight="fill" />
                </div>
                <h3 className="font-bold text-foreground">System Status</h3>
                <div className="flex items-center gap-2 text-green-500">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-sm font-mono">Operational</span>
                </div>
                <p className="text-xs text-muted-foreground">Last backup: 2 hours ago</p>
            </Card>
        </div>

      </div>
    </div>
  );
};


export default Dashboard;
