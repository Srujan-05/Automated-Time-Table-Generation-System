import { useState } from "react";

export const useSidebar = () => {
  const [collapsed, setCollapsed] = useState<boolean>(false);

  const toggleSidebar = () => setCollapsed(!collapsed);

  return {
    collapsed,
    setCollapsed,
    toggleSidebar
  };
};
