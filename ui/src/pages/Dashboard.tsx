
import { mockData } from "../lib/mockData";
import { Clock, BookOpen, Users, Warning, Bell } from "@phosphor-icons/react";
import { motion } from "framer-motion";
import type {NotificationItem as NotificationType, StatCardProps } from "../lib/types";

const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, trend }) => (
  <div className="bg-zinc-900/50 border border-zinc-800/50 p-6 rounded-2xl hover:border-red-500/30 transition-all group backdrop-blur-sm">
    <div className="flex items-start justify-between mb-4">
      <div className="p-3 rounded-xl bg-zinc-800/50 text-zinc-400 group-hover:bg-red-500/10 group-hover:text-red-500 transition-colors">
        <Icon weight="duotone" className="w-6 h-6" />
      </div>
      {trend && (
        <span className="text-xs font-mono text-green-500 bg-green-500/10 px-2 py-1 rounded-full">
          {trend}
        </span>
      )}
    </div>
    <h3 className="text-zinc-500 text-sm font-medium mb-1">{title}</h3>
    <p className="text-3xl font-bold text-white font-sans">{value}</p>
  </div>
);

type NotificationItemProps = NotificationType;

const NotificationItem: React.FC<NotificationItemProps> = ({ title, message, time }) => (
  <div className="flex gap-4 p-4 rounded-xl hover:bg-zinc-800/30 transition-colors border-b border-zinc-800/50 last:border-0">
    <div className="mt-1">
      <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444]" />
    </div>
    <div>
      <h4 className="text-zinc-200 font-medium text-sm">{title}</h4>
      <p className="text-zinc-500 text-sm mt-0.5 line-clamp-1">{message}</p>
      <span className="text-xs text-zinc-600 font-mono mt-2 block">{time}</span>
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  const { users, notifications } = mockData;
  const user = users.admin; // Simulating Admin view

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-2">
            Good Morning, <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-red-600">{user.name}</span>
          </h1>
          <p className="text-zinc-400">Here's what's happening in your campus today.</p>
        </div>
        <div className="flex gap-3">
             <button className="p-3 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-700 transition-all">
                <Bell className="w-5 h-5" />
             </button>
             <button className="px-6 py-3 rounded-xl bg-white text-black font-bold hover:bg-zinc-200 transition-colors shadow-lg shadow-white/5">
                Generate Report
             </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Courses" value="124" icon={BookOpen} trend="+12%" />
        <StatCard title="Active Faculty" value="48" icon={Users} trend="+3" />
        <StatCard title="Weekly Hours" value="1,240" icon={Clock} />
        <StatCard title="Conflicts" value="0" icon={Warning} trend="Perfect" />
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Quick Actions / Recent Activity */}
        <div className="lg:col-span-2 space-y-6">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Clock className="text-red-500" /> Recent Schedule Changes
            </h2>
            <div className="bg-zinc-900/40 border border-zinc-800/50 rounded-2xl backdrop-blur-sm overflow-hidden">
                <div className="p-4 border-b border-zinc-800/50 grid grid-cols-4 text-sm font-medium text-zinc-500">
                    <span>Course</span>
                    <span>Faculty</span>
                    <span>New Time</span>
                    <span>Status</span>
                </div>
                {[1,2,3].map((_, i) => (
                    <motion.div 
                        key={i}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-4 border-b border-zinc-800/50 grid grid-cols-4 items-center hover:bg-white/5 transition-colors cursor-pointer group"
                    >
                        <span className="font-mono text-white group-hover:text-red-400 transition-colors">CS10{i+1}</span>
                        <span className="text-zinc-400">Dr. Smith</span>
                        <span className="text-zinc-400">Mon, 10:00 AM</span>
                        <span className="inline-flex w-fit px-2 py-1 rounded-md bg-green-500/10 text-green-500 text-xs font-mono border border-green-500/20">Approved</span>
                    </motion.div>
                ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <div className="bg-gradient-to-br from-red-500/10 to-transparent border border-red-500/20 p-6 rounded-2xl">
                    <h3 className="font-bold text-white mb-2">Conflict Check</h3>
                    <p className="text-zinc-400 text-sm mb-4">Run the GA algorithm to find potential overlaps.</p>
                    <button className="w-full py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium">Run Check</button>
                 </div>
                 <div className="bg-zinc-900/40 border border-zinc-800/50 p-6 rounded-2xl">
                    <h3 className="font-bold text-white mb-2">Export Data</h3>
                    <p className="text-zinc-400 text-sm mb-4">Download current schedule as PDF or CSV.</p>
                    <button className="w-full py-2 bg-zinc-800 text-white rounded-lg hover:bg-zinc-700 transition-colors font-medium">Export</button>
                 </div>
            </div>
        </div>

        {/* Notifications & upcoming */}
        <div className="space-y-6">
             <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Bell className="text-red-500" /> Notifications
            </h2>
            <div className="bg-zinc-900/40 border border-zinc-800/50 rounded-2xl backdrop-blur-sm p-2">
                {notifications.map((n) => (
                    <NotificationItem key={n.id} {...n} />
                ))}
                <button className="w-full py-3 text-sm text-zinc-500 hover:text-white transition-colors">
                    View All Notifications
                </button>
            </div>

             <div className="bg-[#0f0f0f] border border-zinc-800 p-6 rounded-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Warning size={100} weight="fill" />
                </div>
                <h3 className="font-bold text-white mb-1">System Status</h3>
                <div className="flex items-center gap-2 text-green-500 mb-4">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                    <span className="text-sm font-mono">Operational</span>
                </div>
                <p className="text-xs text-zinc-500">Last backup: 2 hours ago</p>
            </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
