import React from "react";
import type { ReactNode } from "react";
import { useLocation } from "react-router-dom";
import { 
  HouseIcon, 
  CalendarBlankIcon, 
  UserIcon, 
  UploadSimpleIcon, 
  ListBulletsIcon
} from "@phosphor-icons/react";
import { motion, AnimatePresence } from "framer-motion";
import { Sidebar } from "./layout/Sidebar";
import { MobileNavItem } from "./layout/MobileNavItem";
import { ErrorBoundary } from "./common/ErrorBoundary";
type LayoutProps = { 
  children?: ReactNode;
  isDark?: boolean;
  toggleTheme?: () => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
};

const Layout: React.FC<LayoutProps> = ({ children, isDark, toggleTheme, collapsed, setCollapsed }) => {
  const location = useLocation();

  const navItems = [
    { icon: HouseIcon, label: "Dashboard", path: "/dashboard" },
    { icon: CalendarBlankIcon, label: "Timetable", path: "/timetable" },
    { icon: UploadSimpleIcon, label: "Ingestion", path: "/ingestion" },
    { icon: ListBulletsIcon, label: "Preferences", path: "/preferences" },
    { icon: UserIcon, label: "Profile", path: "/profile" },
  ];

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans selection:bg-primary/30">
      
      {/* Desktop Sidebar */}
      <Sidebar 
        collapsed={collapsed} 
        setCollapsed={setCollapsed} 
        isDark={isDark}
        toggleTheme={toggleTheme}
      />

      {/* Main Content */}
      <main className="flex-1 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent pointer-events-none" />
         
         <div className="h-full overflow-y-auto overflow-x-hidden p-4 md:p-8 pb-24 md:pb-8">
            <ErrorBoundary>
              <AnimatePresence mode="wait">
                <motion.div
                  key={location.pathname}
                  initial={{ opacity: 0, y: 20, filter: "blur(10px)" }}
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  exit={{ opacity: 0, y: -20, filter: "blur(10px)" }}
                  transition={{ duration: 0.3 }}
                  className="max-w-7xl mx-auto"
                >
                  {children}
                </motion.div>
              </AnimatePresence>
            </ErrorBoundary>
         </div>
      </main>

      {/* Mobile Bottom Nav */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-sidebar/90 backdrop-blur-xl border-t border-border flex items-center justify-around z-50 px-2">
        {navItems.map((item) => (
            <MobileNavItem 
              key={item.path} 
              {...item} 
              active={location.pathname === item.path} 
            />
        ))}
      </div>

    </div>
  );
};


export default Layout;
