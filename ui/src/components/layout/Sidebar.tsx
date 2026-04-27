import React from "react";
import { motion } from "framer-motion";
import { 
  HouseIcon, 
  CalendarBlankIcon, 
  UserIcon, 
  UploadSimpleIcon, 
  ListBulletsIcon, 
  SignOutIcon, 
  CaretLeftIcon,
  CaretRightIcon,
  SunIcon,
  MoonIcon
} from "@phosphor-icons/react";
import { Link, useLocation } from "react-router-dom";
import { SidebarItem } from "./SidebarItem";
import { Logo } from "../common/Logo";

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  isDark?: boolean;
  toggleTheme?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  collapsed, 
  setCollapsed,
  isDark,
  toggleTheme
}) => {
  const location = useLocation();

  const userRole = localStorage.getItem("userRole") || "student";

  const navItems = [
    { icon: HouseIcon, label: "Dashboard", path: "/dashboard" },
    { icon: CalendarBlankIcon, label: "Timetable", path: "/timetable" },
    { icon: UploadSimpleIcon, label: "Ingestion", path: "/ingestion", roles: ["admin"] },
    { icon: ListBulletsIcon, label: "Preferences", path: "/preferences", roles: ["admin", "faculty"] },
    { icon: UserIcon, label: "Profile", path: "/profile" },
  ].filter(item => !item.roles || item.roles.includes(userRole));

  return (
    <motion.aside 
      initial={false}
      animate={{ width: collapsed ? 80 : 260 }}
      className="hidden md:flex flex-col border-r border-border bg-sidebar/95 text-sidebar-foreground backdrop-blur-xl h-full relative z-20"
    >
      <div className="p-6 flex items-center justify-between">
        <Logo collapsed={collapsed} />
        
        <button 
          onClick={() => setCollapsed(!collapsed)}
          className="cursor-pointer p-1.5 rounded-lg hover:bg-card text-muted-foreground hover:text-foreground transition-colors absolute -right-3 top-16 border border-border bg-sidebar shadow-xl"
        >
          {collapsed ? <CaretRightIcon size={14} /> : <CaretLeftIcon size={14} />}
        </button>
      </div>

      <nav className="flex-1 px-4 py-4 space-y-2">
        {navItems.map((item) => (
          <SidebarItem 
            key={item.path} 
            {...item} 
            active={location.pathname === item.path} 
            collapsed={collapsed}
          />
        ))}
      </nav>

      <div className="p-4 border-t border-border/50 space-y-2">
        <div 
          onClick={toggleTheme}
          className="flex items-center gap-3 p-3 rounded-xl hover:bg-primary/10 hover:text-primary text-muted-foreground transition-colors group cursor-pointer"
        >
          {isDark ? (
            <SunIcon className="w-6 h-6 shrink-0" />
          ) : (
            <MoonIcon className="w-6 h-6 shrink-0" />
          )}
          {!collapsed && <span className="font-medium">{isDark ? "Light Mode" : "Dark Mode"}</span>}
        </div>

        <Link to="/">
          <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-destructive/10 hover:text-destructive text-muted-foreground transition-colors group cursor-pointer">
            <SignOutIcon className="w-6 h-6 shrink-0" />
            {!collapsed && <span className="font-medium">Logout</span>}
          </div>
        </Link>
      </div>
    </motion.aside>
  );
};
