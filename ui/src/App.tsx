import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Auth from "./pages/Auth";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Timetable from "./pages/Timetable";
import Preferences from "./pages/Preferences";
import DataIngestion from "./pages/DataIngestion";
import { useTheme } from "./hooks/useTheme";
import { useSidebar } from "./hooks/useSidebar";
import { Toaster } from "@/components/ui/sonner";

const ProtectedRoute = ({ children, roles }: { children: React.ReactNode, roles?: string[] }) => {
  const userRole = localStorage.getItem("userRole");
  if (!userRole) return <Navigate to="/" replace />;
  if (roles && !roles.includes(userRole)) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

export function App() {
  const { isDark, toggleTheme } = useTheme();
  const sidebarProps = useSidebar();

return (
    <div className="App bg-background text-foreground min-h-screen">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Auth />} />
          <Route path="/dashboard" element={<ProtectedRoute><Layout isDark={isDark} toggleTheme={toggleTheme} {...sidebarProps}><Dashboard /></Layout></ProtectedRoute>} />
          <Route path="/ingestion" element={<ProtectedRoute roles={["admin"]}><Layout isDark={isDark} toggleTheme={toggleTheme} {...sidebarProps}><DataIngestion /></Layout></ProtectedRoute>} />
          <Route path="/preferences" element={<ProtectedRoute roles={["admin", "faculty"]}><Layout isDark={isDark} toggleTheme={toggleTheme} {...sidebarProps}><Preferences /></Layout></ProtectedRoute>} />
          <Route path="/timetable" element={<ProtectedRoute><Layout isDark={isDark} toggleTheme={toggleTheme} {...sidebarProps}><Timetable /></Layout></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Layout isDark={isDark} toggleTheme={toggleTheme} {...sidebarProps}><Profile /></Layout></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </div>
  );
}

export default App;
