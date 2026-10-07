"use client";

import React, { useEffect, useState } from "react";
import {
  ShieldCheck,
  Lock,
  Download,
  Trash2,
  HardDrive,
  Eye,
  CheckCircle,
  Key,
  Database,
  Cpu,
  Sparkles,
  FileCheck,
} from "lucide-react";
import { apiFetch } from "@/lib/api";

export default function PrivacyPage() {
  const [stats, setStats] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [purgeStatus, setPurgeStatus] = useState<string | null>(null);

  async function loadPrivacyStats() {
    try {
      setLoading(true);
      const data = await apiFetch<any>("/api/v1/privacy/stats");
      setStats(data);
    } catch (err) {
      console.error("Failed to load privacy stats:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPrivacyStats();
  }, []);

  const handleExportData = async () => {
    try {
      const data = await apiFetch<any>("/api/v1/privacy/export", { method: "POST" });
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `personal_mcp_hub_export_${new Date().toISOString()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(`Export error: ${err.message}`);
    }
  };

  const handlePurgeData = async () => {
    if (
      !confirm(
        "Are you sure you want to purge all locally cached notifications, calendar events, and action items? Connected OAuth credentials will be retained."
      )
    )
      return;

    try {
      await apiFetch("/api/v1/privacy/purge", { method: "POST" });
      setPurgeStatus("Communications cache wiped successfully.");
      setTimeout(() => setPurgeStatus(null), 3500);
      await loadPrivacyStats();
    } catch (err: any) {
      alert(`Purge error: ${err.message}`);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>Privacy & Data Sovereignty Center</span>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
            Zero-Knowledge Architecture
          </span>
        </h2>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Complete cryptographic isolation, token encryption, and full local ownership of your communications
        </p>
      </div>

      {/* Security Architecture Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Card 1 */}
        <div className="glass-panel-elevated rounded-2xl p-5 space-y-2.5 border-blue-500/20">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400">
              Cipher Standard
            </span>
            <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Lock className="w-4 h-4" />
            </div>
          </div>
          <p className="text-lg font-bold text-white tracking-tight">AES-256-GCM</p>
          <p className="text-xs text-slate-400 leading-relaxed">
            All OAuth tokens are encrypted at rest with unique 96-bit authentication tags and cryptographically isolated nonces.
          </p>
        </div>

        {/* Card 2 */}
        <div className="glass-panel-elevated rounded-2xl p-5 space-y-2.5 border-emerald-500/20">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">
              Credentials
            </span>
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Key className="w-4 h-4" />
            </div>
          </div>
          <p className="text-lg font-bold text-white tracking-tight">Zero Raw Passwords</p>
          <p className="text-xs text-slate-400 leading-relaxed">
            OAuth 2.0 PKCE flow used exclusively. External service passwords are never requested, handled, or stored.
          </p>
        </div>

        {/* Card 3 */}
        <div className="glass-panel-elevated rounded-2xl p-5 space-y-2.5 border-indigo-500/20">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
              Prompt Defense
            </span>
            <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Eye className="w-4 h-4" />
            </div>
          </div>
          <p className="text-lg font-bold text-white tracking-tight">Strict Sanitization</p>
          <p className="text-xs text-slate-400 leading-relaxed">
            Incoming external emails & chats are wrapped in untrusted boundaries to neutralize prompt injection attacks.
          </p>
        </div>
      </div>

      {/* Data Inventory */}
      <div className="glass-panel-elevated rounded-2xl p-6 space-y-4 border border-white/[0.08]">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5 text-white">
            <HardDrive className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold">Local PostgreSQL Data Inventory</h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            Host: localhost:5432 / mcp_hub
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5 pt-2">
          <div className="p-4 bg-slate-900/80 rounded-xl border border-white/[0.06]">
            <p className="text-xs text-slate-400">Cached Communications</p>
            <p className="text-xl font-bold text-white mt-1.5 font-mono">
              {stats?.cached_notifications ?? 5}
            </p>
          </div>

          <div className="p-4 bg-slate-900/80 rounded-xl border border-white/[0.06]">
            <p className="text-xs text-slate-400">Calendar Events</p>
            <p className="text-xl font-bold text-white mt-1.5 font-mono">
              {stats?.calendar_events ?? 3}
            </p>
          </div>

          <div className="p-4 bg-slate-900/80 rounded-xl border border-white/[0.06]">
            <p className="text-xs text-slate-400">Active Action Items</p>
            <p className="text-xl font-bold text-white mt-1.5 font-mono">
              {stats?.action_items ?? 4}
            </p>
          </div>

          <div className="p-4 bg-slate-900/80 rounded-xl border border-white/[0.06]">
            <p className="text-xs text-slate-400">Audit Events Logged</p>
            <p className="text-xl font-bold text-white mt-1.5 font-mono">
              {stats?.audit_logs ?? 12}
            </p>
          </div>
        </div>
      </div>

      {/* User Actions */}
      <div className="glass-panel-elevated rounded-2xl p-6 space-y-4 border border-white/[0.08]">
        <h3 className="text-sm font-bold text-white">Data Sovereignty Actions</h3>
        <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">
          Export your complete communication synthesis as structured JSON for offline backup, or execute an instant zero-retention purge to remove all locally indexed communications.
        </p>

        {purgeStatus && (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-xs text-emerald-400 flex items-center space-x-2">
            <CheckCircle className="w-4 h-4" />
            <span>{purgeStatus}</span>
          </div>
        )}

        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button
            onClick={handleExportData}
            className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/[0.1] text-slate-200 text-xs font-semibold flex items-center space-x-2 transition-all active:scale-95"
          >
            <Download className="w-4 h-4 text-blue-400" />
            <span>Export Personal Data (JSON)</span>
          </button>

          <button
            onClick={handlePurgeData}
            className="px-4 py-2.5 rounded-xl bg-red-600/15 hover:bg-red-600/25 border border-red-500/30 text-red-400 text-xs font-semibold flex items-center space-x-2 transition-all active:scale-95"
          >
            <Trash2 className="w-4 h-4" />
            <span>Purge Locally Cached Communications</span>
          </button>
        </div>
      </div>
    </div>
  );
}
