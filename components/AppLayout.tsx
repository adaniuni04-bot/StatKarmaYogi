"use client";

import React from "react";
import { usePathname } from "next/navigation";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";
import { ShellProvider, useShell } from "./ShellContext";

function ShellInner({ children }: { children: React.ReactNode }) {
  const { isSidebarOpen } = useShell();
  const pathname = usePathname();
  const isLanding = pathname === "/";

  return (
    <div className="min-h-screen bg-white text-slate-900">
      <Navbar />
      <div className="flex min-h-[calc(100vh-4rem)]">
        {!isLanding && isSidebarOpen && <Sidebar />}
        <main className={`flex-1 p-4 sm:p-6 md:p-8 overflow-y-auto transition-all ${!isLanding && isSidebarOpen ? "max-w-7xl mx-auto" : "w-full max-w-full px-4 sm:px-6 md:px-12"}`}>
          {children}
        </main>
      </div>
    </div>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <ShellProvider>
      <ShellInner>{children}</ShellInner>
    </ShellProvider>
  );
}
