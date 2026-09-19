"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { api } from "@/lib/api";
import {
  LayoutDashboard,
  Award,
  TrendingDown,
  CheckCircle2,
  BookOpen,
  Sparkles,
  Bot,
  SlidersHorizontal,
  GraduationCap,
  X
} from "lucide-react";
import { useShell } from "./ShellContext";

export default function Sidebar() {
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const { closeSidebar } = useShell();

  useEffect(() => {
    api.getMe().then(setUser).catch(() => setUser(null));
  }, [pathname]);

  // Only hide sidebar on landing/login page
  if (pathname === "/") {
    return null;
  }

  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "AI Skill Gap Analysis", href: "/skill-gaps", icon: TrendingDown },
    { label: "Study Materials & Modules", href: "/recommendations", icon: Sparkles },
    { label: "AI Assessments", href: "/assessments", icon: CheckCircle2 },
    { label: "Upload & RAG Quiz", href: "/materials", icon: BookOpen },
    { label: "Learning Path", href: "/learning-path", icon: GraduationCap },
    { label: "Competency Matrix", href: "/competencies", icon: Award },
    { label: "AI Career & Tech Tutor", href: "/tutor", icon: Bot },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-300 min-h-[calc(100vh-4rem)] flex flex-col p-4 shrink-0">
      {/* Workspace Header with Close Button */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-200">
        <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
          Workspace Navigation
        </div>
        <button
          type="button"
          onClick={closeSidebar}
          title="Close Workspace Sidebar"
          className="p-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 border border-slate-300 flex items-center justify-center cursor-pointer transition"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2 text-xs font-medium border transition ${
                isActive
                  ? "bg-blue-50 text-blue-800 font-bold border-l-4 border-l-blue-600 border-t-slate-200 border-r-slate-200 border-b-slate-200"
                  : "text-slate-700 hover:bg-slate-100 hover:text-slate-900 border-transparent"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-blue-700" : "text-slate-500"}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="pt-4 border-t border-slate-200 my-4">
        <div className="text-[11px] font-bold text-slate-700 uppercase tracking-wider px-1 mb-2">
          Administration
        </div>
        <nav className="space-y-1">
          <Link
            href="/admin"
            className={`flex items-center space-x-3 px-3 py-2 text-xs font-medium border transition ${
              pathname === "/admin"
                ? "bg-slate-100 text-slate-900 font-bold border-l-4 border-l-slate-900 border-slate-200"
                : "text-slate-700 hover:bg-slate-100 hover:text-slate-900 border-transparent"
            }`}
          >
            <SlidersHorizontal className="w-4 h-4 text-slate-600" />
            <span>Org Intelligence Studio</span>
          </Link>
        </nav>
      </div>
    </aside>
  );
}
