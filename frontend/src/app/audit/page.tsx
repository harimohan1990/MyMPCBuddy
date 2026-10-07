"use client";

import React, { useEffect, useState } from "react";
import {
  FileText,
  Shield,
  Terminal,
  CheckCircle2,
  XCircle,
  Clock,
  Filter,
  Search,
  ShieldAlert,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { AuditLogItem } from "@/lib/types";

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<AuditLogItem[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadLogs() {
      try {
        setLoading(true);
        const data = await apiFetch<AuditLogItem[]>("/api/v1/audit/logs");
        setLogs(data);
        setFilteredLogs(data);
      } catch (err) {
        console.error("Failed to load audit logs:", err);
      } finally {
        setLoading(false);
      }
    }
    loadLogs();
  }, []);

  useEffect(() => {
    let result = [...logs];
    if (filterStatus !== "all") {
      result = result.filter((l) => l.status === filterStatus);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (l) =>
          (l.tool_name && l.tool_name.toLowerCase().includes(q)) ||
          (l.provider && l.provider.toLowerCase().includes(q)) ||
          (l.event_type && l.event_type.toLowerCase().includes(q))
      );
    }
    setFilteredLogs(result);
  }, [logs, filterStatus, searchQuery]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "SUCCESS":
        return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
      case "CONFIRMATION_REJECTED":
        return "bg-amber-500/15 text-amber-300 border-amber-500/30";
      case "FAILED":
        return "bg-red-500/15 text-red-300 border-red-500/30";
      default:
        return "bg-blue-500/15 text-blue-300 border-blue-500/30";
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <span>Security & MCP Gateway Audit Log</span>
          <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
            Immutable Audit Trail
          </span>
        </h2>
        <p className="text-xs md:text-sm text-slate-400 mt-1">
          Cryptographically recorded timeline of all automated reads, assistant tool executions, and confirmed human actions
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel-elevated p-3 rounded-2xl flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by tool name, provider, or event type..."
            className="w-full bg-slate-900 border border-white/[0.08] rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center space-x-1.5 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          {["all", "SUCCESS", "CONFIRMATION_REJECTED", "FAILED"].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                filterStatus === st
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                  : "bg-slate-900 hover:bg-slate-800 text-slate-400 border border-white/[0.05]"
              }`}
            >
              {st === "all" ? "All Statuses" : st.replace("_", " ")}
            </button>
          ))}
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="glass-panel-elevated rounded-2xl border border-white/[0.08] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 border-b border-white/[0.08]">
              <tr>
                <th className="py-3.5 px-4 font-semibold uppercase tracking-wider text-[10px]">
                  Timestamp
                </th>
                <th className="py-3.5 px-4 font-semibold uppercase tracking-wider text-[10px]">
                  Event / Tool
                </th>
                <th className="py-3.5 px-4 font-semibold uppercase tracking-wider text-[10px]">
                  Permission Level
                </th>
                <th className="py-3.5 px-4 font-semibold uppercase tracking-wider text-[10px]">
                  Source Provider
                </th>
                <th className="py-3.5 px-4 font-semibold uppercase tracking-wider text-[10px]">
                  Execution Status
                </th>
                <th className="py-3.5 px-4 font-semibold uppercase tracking-wider text-[10px]">
                  Payload Details
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05] text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    Loading security audit records...
                  </td>
                </tr>
              ) : filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    No matching audit records found.
                  </td>
                </tr>
              ) : (
                filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-white flex items-center space-x-1.5">
                        <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{log.tool_name ? `${log.tool_name}()` : log.event_type}</span>
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono pl-5">{log.event_type}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      {log.permission_level ? (
                        <span
                          className={`font-mono text-[10px] px-2 py-0.5 rounded-full border ${
                            log.permission_level === "DESTRUCTIVE"
                              ? "bg-red-500/15 text-red-300 border-red-500/30 font-bold"
                              : log.permission_level === "WRITE"
                              ? "bg-amber-500/15 text-amber-300 border-amber-500/30"
                              : "bg-blue-500/15 text-blue-300 border-blue-500/30"
                          }`}
                        >
                          {log.permission_level}
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 uppercase text-[10px] font-mono text-slate-300">
                      {log.provider || "system"}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span
                        className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${getStatusBadge(
                          log.status
                        )}`}
                      >
                        {log.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400 max-w-xs truncate">
                      {JSON.stringify(log.payload_summary)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
