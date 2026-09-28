"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { api, getToken, removeToken } from "@/lib/api";
import { User, LogOut, Menu, X } from "lucide-react";
import { useShell } from "./ShellContext";

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const [hasToken, setHasToken] = useState(false);
  const { isSidebarOpen, toggleSidebar } = useShell();

  const isAppRoute = pathname !== "/";

  const loadUser = async () => {
    const token = getToken();
    setHasToken(!!token);
    if (token) {
      try {
        const u = await api.getMe();
        setUser(u);
      } catch {
        // Keep hasToken true if token exists
        setUser(null);
      }
    } else {
      setUser(null);
    }
  };

  useEffect(() => {
    loadUser();

    const handleAuthChange = () => {
      loadUser();
    };

    window.addEventListener("stat_auth_change", handleAuthChange);
    window.addEventListener("storage", handleAuthChange);

    return () => {
      window.removeEventListener("stat_auth_change", handleAuthChange);
      window.removeEventListener("storage", handleAuthChange);
    };
  }, [pathname]);

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch {
      // ignore
    }
    removeToken();
    setUser(null);
    setHasToken(false);
    router.push("/");
    router.refresh();
  };

  const initials = user
    ? `${user.first_name?.[0] || ""}${user.last_name?.[0] || ""}`.toUpperCase()
    : "SK";

  return (
    <header className="bg-white border-b border-slate-300 sticky top-0 z-50">
      <div className="w-full px-4 sm:px-6">
        <div className="flex justify-between items-center h-16">
          {/* Left section: Workspace Toggle Button + Brand */}
          <div className="flex items-center space-x-3">
            {isAppRoute && (
              <button
                type="button"
                onClick={toggleSidebar}
                title={isSidebarOpen ? "Hide Workspace Sidebar" : "Show Workspace Sidebar"}
                className="px-3 py-1.5 border border-slate-400 bg-slate-100 hover:bg-slate-200 text-slate-900 font-bold text-xs flex items-center space-x-2 cursor-pointer transition select-none shadow-xs"
              >
                {isSidebarOpen ? (
                  <>
                    <X className="w-4 h-4 text-slate-800" />
                    <span className="hidden sm:inline">Close Menu</span>
                  </>
                ) : (
                  <>
                    <Menu className="w-4 h-4 text-slate-800" />
                    <span className="hidden sm:inline">Workspace Menu</span>
                  </>
                )}
              </button>
            )}

            <Link href={hasToken ? "/dashboard" : "/"} className="flex items-center space-x-2.5">
              <div className="w-8 h-8 bg-blue-600 border border-blue-700 flex items-center justify-center text-white font-bold text-sm">
                SK
              </div>
              <div>
                <div className="text-base font-bold text-slate-900 leading-tight flex items-center space-x-2">
                  <span>StatKarmaYogi</span>
                  <span className="bg-slate-100 text-slate-700 text-[10px] font-semibold px-1.5 py-0.5 border border-slate-300">
                    Platform
                  </span>
                </div>
                <div className="text-[11px] text-slate-500 font-medium">
                  AI-Powered Competency & Learning System
                </div>
              </div>
            </Link>
          </div>

          {/* Right Navigation & User Session */}
          <div className="flex items-center space-x-4">
            {hasToken || user ? (
              <div className="flex items-center space-x-3 pl-3 border-l border-slate-300">
                <div className="w-8 h-8 bg-slate-800 text-white flex items-center justify-center text-xs font-bold border border-slate-900">
                  {initials || <User className="w-4 h-4" />}
                </div>
                <div className="text-left hidden md:block">
                  <div className="text-xs font-bold text-slate-900">
                    {user ? `${user.first_name} ${user.last_name}` : "Active User"}
                  </div>
                  <div className="text-[11px] text-slate-600 truncate max-w-[200px]">
                    {user?.position || user?.designation_name || "Professional"}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleLogout}
                  title="Sign Out"
                  className="px-2.5 py-1.5 border border-slate-300 hover:border-red-400 text-slate-600 hover:text-red-600 hover:bg-red-50 text-xs font-medium transition cursor-pointer flex items-center space-x-1"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </div>
            ) : (
              !isAppRoute ? (
                <div className="text-xs font-semibold text-slate-600">
                  Authentication Portal
                </div>
              ) : (
                <Link
                  href="/"
                  className="px-3 py-1.5 bg-blue-600 text-white font-semibold text-xs border border-blue-700 hover:bg-blue-700"
                >
                  Sign In
                </Link>
              )
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
