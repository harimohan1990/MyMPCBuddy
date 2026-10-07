"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Inbox,
  Sparkles,
  Calendar,
  Layers,
  ShieldCheck,
  FileText,
  Radio,
  Lock,
  Search,
  RefreshCw,
  Zap,
  CheckCircle2,
  ChevronRight,
  LogOut,
  User,
  ExternalLink,
} from "lucide-react";
import { apiFetch, getAuthToken, clearAuthToken } from "@/lib/api";

interface ShellProps {
  children: React.ReactNode;
}

export function Shell({ children }: ShellProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [syncing, setSyncing] = useState(false);
  const [currentUser, setCurrentUser] = useState<{ full_name?: string; email?: string } | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  // If on login or oauth callback page, render without full application shell
  const isAuthPage = pathname.startsWith("/login") || pathname.startsWith("/oauth");

  useEffect(() => {
    async function fetchUser() {
      const token = getAuthToken();
      if (!token && !isAuthPage) {
        // Not logged in, but we allow demo browsing or redirect
      }
      try {
        const user = await apiFetch<any>("/api/v1/auth/me");
        if (user) {
          setCurrentUser(user);
        }
      } catch (err) {
        // Fallback demo user
        setCurrentUser({ full_name: "Hari Mohan", email: "hari.mohan@gmail.com" });
      }
    }
    fetchUser();
  }, [pathname, isAuthPage]);

  const handleGlobalSync = async () => {
    try {
      setSyncing(true);
      setSyncMessage("Synchronizing 4 providers...");
      await apiFetch("/api/v1/notifications/sync", { method: "POST" });
      setSyncMessage("All feeds updated!");
      setTimeout(() => setSyncMessage(null), 3000);
      // Trigger soft reload or event
      window.dispatchEvent(new CustomEvent("mcp:sync-complete"));
    } catch (err) {
      setSyncMessage("Sync error");
      setTimeout(() => setSyncMessage(null), 3000);
    } finally {
      setSyncing(false);
    }
  };

  const handleSignOut = () => {
    clearAuthToken();
    router.push("/login");
  };

  if (isAuthPage) {
    return <main className="min-h-screen bg-[#080c16]">{children}</main>;
  }

  const navItems = [
    { label: "Executive Dashboard", href: "/dashboard", icon: LayoutDashboard, tag: "Daily" },
    { label: "Unified Inbox", href: "/inbox", icon: Inbox, badge: "5", tag: "Live" },
    { label: "AI Copilot Assistant", href: "/assistant", icon: Sparkles, highlight: true },
    { label: "Smart Calendar", href: "/calendar", icon: Calendar },
    { label: "Connected Accounts", href: "/providers", icon: Layers, badge: "4 Active" },
    { label: "Privacy & Encryption", href: "/privacy", icon: ShieldCheck },
    { label: "Security & Audit Logs", href: "/audit", icon: FileText },
  ];

  return (
    <div className="flex h-screen w-full bg-[#080c16] text-slate-100 overflow-hidden font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/[0.08] bg-[#0c1322]/95 backdrop-blur-xl flex flex-col justify-between shrink-0 z-20">
        <div>
          {/* Brand Emblem */}
          <div className="p-4 border-b border-white/[0.07]">
            <Link href="/dashboard" className="flex items-center space-x-3 group">
              <div className="relative">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/30 group-hover:shadow-blue-500/50 transition-all duration-300">
                  <Zap className="w-5 h-5 text-white fill-white/20" />
                </div>
                <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full status-ring-pulse border-2 border-[#0c1322]" />
              </div>
              <div>
                <h1 className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
                  Personal MCP
                  <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                    HUB
                  </span>
                </h1>
                <p className="text-[11px] text-slate-400 font-medium">Unified Intelligence OS</p>
              </div>
            </Link>
          </div>

          {/* Quick Action Pill */}
          <div className="p-3">
            <Link
              href="/assistant"
              className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-gradient-to-r from-blue-600/20 via-indigo-600/20 to-purple-600/20 hover:from-blue-600/30 hover:via-indigo-600/30 hover:to-purple-600/30 border border-blue-500/30 text-blue-300 text-xs font-semibold shadow-sm transition-all group"
            >
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-cyan-400 group-hover:rotate-12 transition-transform" />
                <span>Ask AI Copilot</span>
              </div>
              <span className="text-[10px] font-mono bg-blue-500/30 text-blue-200 px-1.5 py-0.5 rounded border border-blue-400/30">
                ⌘J
              </span>
            </Link>
          </div>

          {/* Nav Links */}
          <div className="px-3 py-1">
            <p className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Workspace Feeds
            </p>
            <nav className="space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`relative flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all group ${
                      isActive
                        ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold shadow-md shadow-blue-600/25"
                        : "text-slate-400 hover:text-slate-100 hover:bg-white/[0.05]"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon
                        className={`w-4 h-4 shrink-0 transition-transform group-hover:scale-110 ${
                          isActive
                            ? "text-white"
                            : item.highlight
                            ? "text-cyan-400"
                            : "text-slate-400 group-hover:text-slate-200"
                        }`}
                      />
                      <span>{item.label}</span>
                    </div>

                    <div className="flex items-center space-x-1.5">
                      {item.badge && (
                        <span
                          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                            isActive
                              ? "bg-white/20 text-white"
                              : "bg-slate-800 text-slate-300 border border-white/5"
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </div>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>

        {/* User Card & Security Status */}
        <div className="p-3 border-t border-white/[0.08] space-y-2 bg-[#090e1a]/80">
          {/* Security Badge */}
          <div className="p-2.5 rounded-xl bg-slate-900/90 border border-white/[0.06] flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="text-[11px] font-medium text-slate-300">AES-256-GCM Active</span>
            </div>
            <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
              Zero-Trust
            </span>
          </div>

          {/* User Account Info */}
          <div className="p-2 rounded-xl flex items-center justify-between hover:bg-white/[0.04] transition-colors group">
            <div className="flex items-center space-x-2.5 overflow-hidden">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center font-bold text-xs text-white shrink-0 shadow-sm">
                {currentUser?.full_name?.slice(0, 2).toUpperCase() || "HM"}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-semibold text-slate-200 truncate">
                  {currentUser?.full_name || "Hari Mohan"}
                </p>
                <p className="text-[10px] text-slate-400 truncate">
                  {currentUser?.email || "hari.mohan@gmail.com"}
                </p>
              </div>
            </div>

            <button
              onClick={handleSignOut}
              className="p-1.5 text-slate-400 hover:text-red-400 rounded-lg hover:bg-red-500/10 transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Top Header Bar */}
        <header className="h-14 border-b border-white/[0.08] bg-[#0c1322]/80 backdrop-blur-xl px-6 flex items-center justify-between shrink-0 z-10">
          {/* Breadcrumb / Context */}
          <div className="flex items-center space-x-3 text-xs">
            <div className="flex items-center space-x-2 text-slate-400">
              <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="font-medium text-slate-300">MCP Protocol Bus</span>
            </div>
            <span className="text-slate-600">•</span>
            <span className="text-slate-400 hidden sm:inline">
              Gmail • Teams • WhatsApp • Calendar • GitHub
            </span>
          </div>

          {/* Header Controls */}
          <div className="flex items-center space-x-3">
            {/* Sync Status Toast/Indicator */}
            {syncMessage && (
              <span className="text-xs text-cyan-300 bg-cyan-500/10 border border-cyan-500/20 px-2.5 py-1 rounded-full animate-fade-in flex items-center space-x-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                <span>{syncMessage}</span>
              </span>
            )}

            {/* Sync Feeds Button */}
            <button
              onClick={handleGlobalSync}
              disabled={syncing}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/[0.08] text-xs font-semibold text-slate-300 transition-all hover:border-blue-500/40 active:scale-95 disabled:opacity-70"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncing ? "animate-spin text-blue-400" : "text-slate-400"}`} />
              <span className="hidden sm:inline">{syncing ? "Syncing..." : "Sync All"}</span>
            </button>

            {/* Google Account Tag */}
            <Link
              href="/providers"
              className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs font-medium text-slate-200 transition-colors"
            >
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.17z"
                />
                <path
                  fill="#34A853"
                  d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.27 21.39 7.33 24 12 24z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.18 0 9.99 0 12s.45 3.82 1.25 5.42l4.03-3.15z"
                />
                <path
                  fill="#EA4335"
                  d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.27 2.61 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
                />
              </svg>
              <span className="hidden md:inline">Google Connected</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            </Link>
          </div>
        </header>

        {/* Scrollable Page Canvas */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8 custom-scrollbar">
          {children}
        </div>
      </main>
    </div>
  );
}
