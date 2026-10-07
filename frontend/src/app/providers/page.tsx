"use client";

import React, { useEffect, useState } from "react";
import {
  Layers,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  ExternalLink,
  ShieldCheck,
  Plus,
  Trash2,
  Check,
  Zap,
  Lock,
  Mail,
  MessageSquare,
  Sparkles,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { ProviderAccount } from "@/lib/types";

export default function ProvidersPage() {
  const [providers, setProviders] = useState<ProviderAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const availableServices = [
    {
      id: "gmail",
      name: "Google (Gmail & Google Calendar)",
      description: "Read, search, draft replies, aggregate inbox emails, and sync calendar events with zero raw token exposure.",
      scopes: ["gmail.readonly", "gmail.send", "calendar.readonly", "userinfo.email"],
      officialApi: "Google Workspace / Gmail API (OAuth 2.0 PKCE)",
      email: "hari.mohan@gmail.com",
      accent: "border-red-500/30 hover:border-red-500/50",
      iconColor: "text-red-400 bg-red-500/10 border-red-500/20",
    },
    {
      id: "teams",
      name: "Microsoft (Teams & Outlook)",
      description: "Search corporate chat channels, detect @mentions, and read Outlook emails securely via Microsoft Graph.",
      scopes: ["Mail.Read", "Chat.Read", "Calendars.Read", "User.Read"],
      officialApi: "Microsoft Graph API (OAuth 2.0 PKCE)",
      email: "hari.mohan@teams.enterprise.com",
      accent: "border-indigo-500/30 hover:border-indigo-500/50",
      iconColor: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20",
    },
    {
      id: "github",
      name: "GitHub",
      description: "Real-time pull request reviews, repository notifications, build failure alerts, and assignment dispatching.",
      scopes: ["read:user", "notifications", "repo"],
      officialApi: "GitHub REST & GraphQL API",
      email: "harimohan",
      accent: "border-purple-500/30 hover:border-purple-500/50",
      iconColor: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    },
    {
      id: "whatsapp",
      name: "WhatsApp (Official Meta Cloud API)",
      description: "Official Meta Cloud API adapter. Direct webhook integration with token isolation. Unofficial scraping strictly prohibited.",
      scopes: ["whatsapp_business_messaging (Meta Cloud API isolated)"],
      officialApi: "Meta WhatsApp Cloud API (Isolated Adapter)",
      email: "+1 (555) 019-2834 (Cloud API)",
      accent: "border-emerald-500/30 hover:border-emerald-500/50",
      iconColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
    },
  ];

  async function loadProviders() {
    try {
      setLoading(true);
      const data = await apiFetch<ProviderAccount[]>("/api/v1/providers");
      setProviders(data);
    } catch (err) {
      console.error("Failed to load providers:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProviders();
  }, []);

  const handleConnectProvider = async (providerId: string, email: string) => {
    try {
      setActionLoading(providerId);
      if (providerId === "gmail") {
        const res = await apiFetch<{ authorization_url: string }>("/api/v1/auth/google/url");
        if (res.authorization_url) {
          window.location.href = res.authorization_url;
          return;
        }
      }
      await apiFetch("/api/v1/oauth/connect-sandbox", {
        method: "POST",
        body: JSON.stringify({
          provider: providerId,
          account_email: email,
        }),
      });
      await loadProviders();
    } catch (err: any) {
      alert(`Connect error: ${err.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleConnectAll = async () => {
    try {
      setActionLoading("all");
      const data = await apiFetch<ProviderAccount[]>("/api/v1/providers/connect-all", {
        method: "POST",
      });
      setProviders(data);
    } catch (err: any) {
      alert(`Connect error: ${err.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleDisconnect = async (id: string) => {
    if (!confirm("Are you sure you want to disconnect this account?")) return;
    try {
      setActionLoading(id);
      await apiFetch(`/api/v1/providers/${id}`, { method: "DELETE" });
      await loadProviders();
    } catch (err: any) {
      alert(`Disconnect error: ${err.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  const handleSync = async (id: string) => {
    try {
      setActionLoading(id);
      await apiFetch(`/api/v1/providers/${id}/sync`, { method: "POST" });
      await loadProviders();
    } catch (err: any) {
      alert(`Sync error: ${err.message}`);
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Connected Communication Feeds</span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
              {providers.filter((p) => p.is_active).length} / {availableServices.length} Active
            </span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Manage your personal communication sources, OAuth 2.0 scopes, and AES-256-GCM token isolation
          </p>
        </div>

        <button
          onClick={handleConnectAll}
          disabled={actionLoading === "all"}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold flex items-center space-x-2 shadow-lg shadow-blue-600/30 transition-all active:scale-95 disabled:opacity-60"
        >
          <Zap className="w-4 h-4 fill-white" />
          <span>{actionLoading === "all" ? "Connecting All Feeds..." : "Auto-Connect All 4 Providers"}</span>
        </button>
      </div>

      {/* Services Cards */}
      <div className="space-y-4">
        {availableServices.map((svc) => {
          const connected = providers.find((p) => p.provider.toLowerCase() === svc.id);
          const isProcessing =
            actionLoading === svc.id || (connected && actionLoading === connected.id);

          return (
            <div
              key={svc.id}
              className={`glass-panel-elevated rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-5 transition-all ${
                connected ? svc.accent : "opacity-85 border-white/[0.06]"
              }`}
            >
              <div className="space-y-2.5 max-w-2xl">
                {/* Provider Title & Status Pill */}
                <div className="flex items-center flex-wrap gap-2.5">
                  <h3 className="text-base font-bold text-white">{svc.name}</h3>

                  {connected ? (
                    <span className="flex items-center space-x-1.5 text-xs bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 px-2.5 py-0.5 rounded-full font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Connected ({connected.provider_account_id})</span>
                    </span>
                  ) : (
                    <span className="text-xs bg-slate-800 text-slate-400 border border-white/5 px-2.5 py-0.5 rounded-full font-medium">
                      Not Connected
                    </span>
                  )}
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">{svc.description}</p>

                {/* API & Security Badges */}
                <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
                  <span className="text-slate-400 font-mono">API: {svc.officialApi}</span>

                  {connected && (
                    <span className="bg-blue-500/15 text-blue-300 px-2 py-0.5 rounded-full border border-blue-500/30 font-mono flex items-center space-x-1">
                      <Lock className="w-3 h-3 text-cyan-400" />
                      <span>AES-256-GCM Encrypted Token</span>
                    </span>
                  )}
                </div>

                {/* Scopes */}
                {connected && connected.granted_scopes && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {connected.granted_scopes.map((scope, sIdx) => (
                      <span
                        key={sIdx}
                        className="text-[10px] bg-slate-900/90 text-slate-300 px-2 py-0.5 rounded-lg border border-white/[0.08] font-mono"
                      >
                        ✓ {scope}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2 shrink-0 self-end md:self-center">
                {connected ? (
                  <>
                    <button
                      onClick={() => handleSync(connected.id)}
                      disabled={isProcessing}
                      className="px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-white/[0.1] text-slate-200 text-xs font-semibold flex items-center space-x-2 transition-all active:scale-95"
                    >
                      <RefreshCw
                        className={`w-3.5 h-3.5 ${isProcessing ? "animate-spin text-blue-400" : ""}`}
                      />
                      <span>Sync Feed</span>
                    </button>
                    <button
                      onClick={() => handleDisconnect(connected.id)}
                      disabled={isProcessing}
                      className="p-2 rounded-xl border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-colors"
                      title="Disconnect account"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => handleConnectProvider(svc.id, svc.email)}
                    disabled={isProcessing}
                    className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center space-x-2 shadow-md shadow-blue-600/30 transition-all active:scale-95"
                  >
                    <Plus className="w-4 h-4" />
                    <span>Connect Account</span>
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
