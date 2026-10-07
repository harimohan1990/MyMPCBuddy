"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Bell,
  Mail,
  MessageSquare,
  Calendar,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  Sparkles,
  ExternalLink,
  RefreshCw,
  Video,
  ShieldAlert,
  Layers,
  ArrowUpRight,
  ChevronRight,
  Zap,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { DailyBriefing, NotificationSummary } from "@/lib/types";

export default function DashboardPage() {
  const [briefing, setBriefing] = useState<DailyBriefing | null>(null);
  const [summary, setSummary] = useState<NotificationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [completedPriorities, setCompletedPriorities] = useState<Record<number, boolean>>({});

  async function loadDashboardData() {
    try {
      setLoading(true);
      const [briefingData, summaryData] = await Promise.all([
        apiFetch<DailyBriefing>("/api/v1/assistant/briefing"),
        apiFetch<NotificationSummary>("/api/v1/notifications/summary"),
      ]);
      setBriefing(briefingData);
      setSummary(summaryData);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboardData();
    const handleSync = () => loadDashboardData();
    window.addEventListener("mcp:sync-complete", handleSync);
    return () => window.removeEventListener("mcp:sync-complete", handleSync);
  }, []);

  const handleManualSync = async () => {
    try {
      setSyncing(true);
      await apiFetch("/api/v1/notifications/sync", { method: "POST" });
      await loadDashboardData();
    } finally {
      setSyncing(false);
    }
  };

  const togglePriority = (idx: number) => {
    setCompletedPriorities((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  const getProviderConfig = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "gmail":
        return {
          bg: "bg-red-500/10",
          text: "text-red-400",
          border: "border-red-500/20",
          iconBg: "bg-red-500/20 text-red-300",
          label: "Gmail",
        };
      case "whatsapp":
        return {
          bg: "bg-emerald-500/10",
          text: "text-emerald-400",
          border: "border-emerald-500/20",
          iconBg: "bg-emerald-500/20 text-emerald-300",
          label: "WhatsApp",
        };
      case "teams":
        return {
          bg: "bg-indigo-500/10",
          text: "text-indigo-400",
          border: "border-indigo-500/20",
          iconBg: "bg-indigo-500/20 text-indigo-300",
          label: "MS Teams",
        };
      case "github":
        return {
          bg: "bg-purple-500/10",
          text: "text-purple-400",
          border: "border-purple-500/20",
          iconBg: "bg-purple-500/20 text-purple-300",
          label: "GitHub",
        };
      case "calendar":
      case "google_calendar":
      case "outlook_calendar":
        return {
          bg: "bg-blue-500/10",
          text: "text-blue-400",
          border: "border-blue-500/20",
          iconBg: "bg-blue-500/20 text-blue-300",
          label: "Calendar",
        };
      default:
        return {
          bg: "bg-slate-500/10",
          text: "text-slate-400",
          border: "border-slate-500/20",
          iconBg: "bg-slate-500/20 text-slate-300",
          label: provider,
        };
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
      {/* Executive Intelligence Hero Card */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#101b33] via-[#0d162a] to-[#0a0f1d] border border-blue-500/20 p-6 md:p-8 shadow-2xl shadow-blue-950/40">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-16 w-80 h-80 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-3xl">
            <div className="flex items-center space-x-3">
              <span className="flex items-center space-x-1.5 px-3 py-1 rounded-full bg-blue-500/15 border border-blue-400/30 text-blue-300 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
                <span>Executive Morning Intelligence</span>
              </span>
              <span className="text-xs text-slate-400 font-mono">
                {briefing?.date || "Today"}
              </span>
            </div>

            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight leading-snug">
              {briefing?.greeting || "Good morning, Hari"}
            </h2>

            <p className="text-sm md:text-base text-slate-300 font-normal leading-relaxed">
              {briefing?.summary_headline ||
                "Unified personal communications across Gmail, Teams, WhatsApp, and GitHub are synchronized. 4 items require attention before noon."}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0">
            <button
              onClick={handleManualSync}
              disabled={syncing}
              className="flex items-center justify-center space-x-2 px-4 py-2.5 rounded-xl bg-white/[0.06] hover:bg-white/[0.12] border border-white/10 text-xs font-semibold text-slate-200 transition-all active:scale-95 disabled:opacity-60"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${syncing ? "animate-spin text-blue-400" : ""}`} />
              <span>{syncing ? "Refreshing Feeds..." : "Refresh Intelligence"}</span>
            </button>

            <Link
              href="/assistant"
              className="flex items-center justify-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition-all active:scale-95"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>Open AI Copilot</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Metrics Row: 5 Dynamic Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
        {/* Total Notifications */}
        <div className="glass-card-interactive rounded-2xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Total Inbox</span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Bell className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-bold text-white tracking-tight">
              {summary?.total_notifications || 6}
            </p>
            <p className="text-[11px] text-emerald-400 mt-0.5 flex items-center">
              <span>Synchronized</span>
            </p>
          </div>
        </div>

        {/* Gmail Unread */}
        <div className="glass-card-interactive rounded-2xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Gmail Unread</span>
            <div className="p-2 rounded-xl bg-red-500/10 text-red-400 border border-red-500/20">
              <Mail className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-bold text-white tracking-tight">
              {summary?.provider_counts?.["gmail"] || 2}
            </p>
            <p className="text-[11px] text-slate-400 mt-0.5">Inbox priority</p>
          </div>
        </div>

        {/* WhatsApp & Teams Messages */}
        <div className="glass-card-interactive rounded-2xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Direct Chats</span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-bold text-white tracking-tight">
              {(summary?.provider_counts?.["whatsapp"] || 1) + (summary?.provider_counts?.["teams"] || 1)}
            </p>
            <p className="text-[11px] text-emerald-400 mt-0.5">WhatsApp + Teams</p>
          </div>
        </div>

        {/* Today's Meetings */}
        <div className="glass-card-interactive rounded-2xl p-4 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Scheduled Events</span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Calendar className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-bold text-white tracking-tight">
              {briefing?.calendar_overview?.length || 3}
            </p>
            <p className="text-[11px] text-indigo-400 mt-0.5">Next in 45 min</p>
          </div>
        </div>

        {/* Action Required */}
        <div className="glass-card-interactive rounded-2xl p-4 flex flex-col justify-between border-amber-500/30">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-amber-300">Requires Action</span>
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <p className="text-2xl font-bold text-amber-400 tracking-tight font-mono">
              {summary?.action_required_count || 4}
            </p>
            <p className="text-[11px] text-amber-400/80 mt-0.5">Needs reply / decision</p>
          </div>
        </div>
      </div>

      {/* Main Two-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Requires Attention Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="relative">
                <span className="w-3 h-3 rounded-full bg-red-500 block" />
                <span className="w-3 h-3 rounded-full bg-red-500 animate-ping absolute inset-0 opacity-75" />
              </div>
              <h3 className="text-sm font-bold text-white tracking-wide uppercase">
                Requires Immediate Attention
              </h3>
            </div>
            <Link
              href="/inbox"
              className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center space-x-1 group"
            >
              <span>Open Unified Inbox</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>

          <div className="space-y-3">
            {briefing?.urgent_items?.map((item, idx) => {
              const provConfig = getProviderConfig(item.source_provider);
              return (
                <div
                  key={idx}
                  className="glass-card-interactive rounded-2xl p-5 border border-white/[0.07] hover:border-blue-500/30 transition-all group"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-2 flex-1">
                      {/* Meta Pills */}
                      <div className="flex items-center flex-wrap gap-2">
                        <span
                          className={`text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full border ${provConfig.bg} ${provConfig.text} ${provConfig.border}`}
                        >
                          {provConfig.label}
                        </span>

                        <span className="text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
                          {item.priority}
                        </span>

                        <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                          <Clock className="w-3 h-3 text-slate-400" />
                          <span>Today</span>
                        </span>
                      </div>

                      {/* Title & Description */}
                      <h4 className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors">
                        {item.title}
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed line-clamp-2">
                        {item.description}
                      </p>
                    </div>

                    {/* Quick Action Button */}
                    <Link
                      href={`/assistant?q=${encodeURIComponent("Help me address: " + item.title)}`}
                      className="shrink-0 flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-blue-600/10 hover:bg-blue-600 text-blue-400 hover:text-white border border-blue-500/20 text-xs font-semibold transition-all group-hover:shadow-md"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Act with AI</span>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 1 Col: AI Priorities & Today's Schedule */}
        <div className="space-y-6">
          {/* AI Recommended Priorities Checklist */}
          <div className="glass-panel-elevated rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-blue-400">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">
                  Recommended Priorities
                </h3>
              </div>
              <span className="text-[10px] font-mono bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded-full">
                AI Suggested
              </span>
            </div>

            <div className="space-y-2.5">
              {briefing?.recommended_priorities?.map((p, idx) => {
                const isChecked = !!completedPriorities[idx];
                return (
                  <div
                    key={idx}
                    onClick={() => togglePriority(idx)}
                    className={`flex items-start space-x-3 p-2.5 rounded-xl border cursor-pointer transition-all ${
                      isChecked
                        ? "bg-slate-900/50 border-white/5 opacity-60"
                        : "bg-white/[0.02] hover:bg-white/[0.05] border-white/[0.06]"
                    }`}
                  >
                    <button className="mt-0.5 shrink-0">
                      {isChecked ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 fill-emerald-500/20" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border border-slate-500 hover:border-blue-400 transition-colors" />
                      )}
                    </button>
                    <p
                      className={`text-xs leading-relaxed transition-all ${
                        isChecked ? "text-slate-400 line-through" : "text-slate-200"
                      }`}
                    >
                      {p}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Today's Schedule Snapshot */}
          <div className="glass-panel-elevated rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-indigo-400">
                <Calendar className="w-4 h-4 text-indigo-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-white">
                  Today&apos;s Agenda
                </h3>
              </div>
              <Link
                href="/calendar"
                className="text-[11px] text-blue-400 hover:text-blue-300 font-semibold flex items-center space-x-1"
              >
                <span>Full Schedule</span>
                <ChevronRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="space-y-2.5">
              {briefing?.calendar_overview?.map((ev, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-900/80 border border-white/[0.06] flex items-center justify-between gap-3 text-xs hover:border-indigo-500/30 transition-all"
                >
                  <div className="space-y-1">
                    <p className="font-semibold text-slate-100">{ev.summary}</p>
                    <div className="flex items-center space-x-2 text-[11px] text-slate-400">
                      <Clock className="w-3 h-3 text-indigo-400" />
                      <span>{ev.time}</span>
                      {ev.location && <span>• {ev.location}</span>}
                    </div>
                  </div>

                  {ev.link && (
                    <a
                      href={ev.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="shrink-0 px-2.5 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 text-[11px] font-semibold flex items-center space-x-1 transition-all"
                    >
                      <Video className="w-3 h-3" />
                      <span>Join</span>
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
