
import React, { useState } from "react";
import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { 
  House, 
  CalendarBlank, 
  User, 
  UploadSimple, 
  ListBullets, 
  SignOut, 
  CaretLeft,
  CaretRight
} from "@phosphor-icons/react";
import { motion, AnimatePresence } from "framer-motion";
import type { IconComponent, SidebarItemProps } from "../lib/types";

const SidebarItem: React.FC<SidebarItemProps> = ({ icon: Icon, label, path, active, collapsed }) => (
  <Link to={path} className="w-full">
    <div 
      className={`
        flex items-center gap-3 p-3 my-1 rounded-xl transition-all duration-300 group
        ${active 
          ? "bg-red-500/10 text-red-500 shadow-[0_0_15px_rgba(239,68,68,0.2)] border border-red-500/20" 
          : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50"
        }
      `}
    >
      <Icon weight={active ? "fill" : "regular"} className="w-6 h-6 shrink-0 transition-transform group-hover:scale-110" />
      {!collapsed && (
        <span className="font-sans font-medium whitespace-nowrap overflow-hidden transition-all">
          {label}
        </span>
      )}
      {active && !collapsed && (
        <motion.div 
          layoutId="active-pill" 
          className="ml-auto w-1.5 h-1.5 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444]"
        />
      )}
    </div>
  </Link>
);

type MobileNavItemProps = {
  icon: IconComponent;
  path: string;
  active: boolean;
};

const MobileNavItem: React.FC<MobileNavItemProps> = ({ icon: Icon, path, active }) => (
  <Link to={path} className="flex flex-col items-center justify-center w-full h-full">
     <div 
      className={`
        p-2 rounded-full transition-all duration-300 relative
        ${active ? "text-red-500 bg-red-500/10" : "text-zinc-400"}
      `}
    >
      <Icon weight={active ? "fill" : "regular"} className="w-6 h-6" />
      {active && (
         <motion.div 
          layoutId="mobile-active-glow"
          className="absolute inset-0 rounded-full bg-red-500/20 blur-md"
        />
      )}
    </div>
  </Link>
);

type LayoutProps = { children?: ReactNode };

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState<boolean>(false);
  const location = useLocation();

  const navItems = [
    { icon: House, label: "Dashboard", path: "/dashboard" },
    { icon: CalendarBlank, label: "Timetable", path: "/timetable" },
    { icon: UploadSimple, label: "Ingestion", path: "/ingestion" }, // Admin only usually, but showing all for demo
    { icon: ListBullets, label: "Preferences", path: "/preferences" },
    { icon: User, label: "Profile", path: "/profile" },
  ];

  return (
    <div className="flex h-screen bg-[#09090b] text-zinc-100 overflow-hidden font-sans selection:bg-red-500/30">
      
      {/* Desktop Sidebar */}
      <motion.aside 
        initial={false}
        animate={{ width: collapsed ? 80 : 260 }}
        className="hidden md:flex flex-col border-r border-zinc-800 bg-[#09090b]/95 backdrop-blur-xl h-full relative z-20"
      >
        <div className="p-6 flex items-center justify-between">
          {!collapsed && (
            <motion.div 
              initial={{ opacity: 0 }} 
              animate={{ opacity: 1 }} 
              className="flex items-center gap-2"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center shadow-[0_0_15px_rgba(239,68,68,0.4)]">
                <span className="font-bold text-white">T</span>
              </div>
              <span className="font-bold text-xl tracking-tight">Time<span className="text-red-500">Sync</span></span>
            </motion.div>
          )}
          
          <button 
            onClick={() => setCollapsed(!collapsed)}
            className="p-1.5 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors absolute -right-3 top-7 border border-zinc-700 bg-[#09090b] shadow-xl"
          >
            {collapsed ? <CaretRight size={14} /> : <CaretLeft size={14} />}
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

        <div className="p-4 border-t border-zinc-800">
           <Link to="/">
            <div className={`flex items-center gap-3 p-3 rounded-xl hover:bg-red-500/10 hover:text-red-500 text-zinc-400 transition-colors group cursor-pointer`}>
                <SignOut className="w-6 h-6 shrink-0" />
                {!collapsed && <span className="font-medium">Logout</span>}
            </div>
           </Link>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 relative overflow-hidden bg-[url('/noise.svg')] bg-opacity-20">
         <div className="absolute inset-0 bg-gradient-to-br from-red-500/5 via-transparent to-transparent pointer-events-none" />
         
         <div className="h-full overflow-y-auto overflow-x-hidden p-4 md:p-8 pb-24 md:pb-8">
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
         </div>
      </main>

      {/* Mobile Bottom Nav */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-[#09090b]/90 backdrop-blur-xl border-t border-zinc-800 flex items-center justify-around z-50 px-2">
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
