"use client";

import React, { createContext, useContext, useState, useEffect } from "react";

interface ShellContextType {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  openSidebar: () => void;
  closeSidebar: () => void;
}

const ShellContext = createContext<ShellContextType>({
  isSidebarOpen: true,
  toggleSidebar: () => {},
  openSidebar: () => {},
  closeSidebar: () => {},
});

export function ShellProvider({ children }: { children: React.ReactNode }) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Initialize from localStorage if available
  useEffect(() => {
    const saved = localStorage.getItem("stat_sidebar_open");
    if (saved !== null) {
      setIsSidebarOpen(saved === "true");
    }
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen((prev) => {
      const next = !prev;
      localStorage.setItem("stat_sidebar_open", String(next));
      return next;
    });
  };

  const openSidebar = () => {
    setIsSidebarOpen(true);
    localStorage.setItem("stat_sidebar_open", "true");
  };

  const closeSidebar = () => {
    setIsSidebarOpen(false);
    localStorage.setItem("stat_sidebar_open", "false");
  };

  return (
    <ShellContext.Provider
      value={{
        isSidebarOpen,
        toggleSidebar,
        openSidebar,
        closeSidebar,
      }}
    >
      {children}
    </ShellContext.Provider>
  );
}

export function useShell() {
  return useContext(ShellContext);
}