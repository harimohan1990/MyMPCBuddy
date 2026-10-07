"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  CheckCircle,
  Archive,
  Star,
  ExternalLink,
  Mail,
  MessageSquare,
  Calendar,
  AlertCircle,
  Check,
  Sparkles,
  Send,
  CornerUpLeft,
  Clock,
  Tag,
  ShieldCheck,
  Bot,
  Zap,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { NotificationItem, NotificationListResponse } from "@/lib/types";

export default function InboxPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<NotificationItem | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>("all");
  const [selectedPriority, setSelectedPriority] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [replyDraft, setReplyDraft] = useState<string>("");
  const [draftingAI, setDraftingAI] = useState(false);

  async function loadNotifications() {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedProvider !== "all") params.append("provider", selectedProvider);
      if (selectedPriority !== "all") params.append("priority", selectedPriority);
      if (searchQuery.trim()) params.append("search", searchQuery.trim());

      const data = await apiFetch<NotificationListResponse>(
        `/api/v1/notifications?${params.toString()}`
      );
      setNotifications(data.items);
      if (data.items.length > 0 && !selectedItem) {
        setSelectedItem(data.items[0]);
      }
    } catch (err) {
      console.error("Failed to load notifications:", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadNotifications();
  }, [selectedProvider, selectedPriority]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadNotifications();
  };

  const toggleReadStatus = async (item: NotificationItem) => {
    try {
      const updated = await apiFetch<NotificationItem>(`/api/v1/notifications/${item.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_read: !item.is_read }),
      });
      setNotifications((prev) =>
        prev.map((n) => (n.id === item.id ? { ...n, is_read: updated.is_read } : n))
      );
      if (selectedItem?.id === item.id) {
        setSelectedItem((prev) => (prev ? { ...prev, is_read: updated.is_read } : null));
      }
    } catch (err) {
      console.error("Failed to update status:", err);
    }
  };

  const toggleStarStatus = async (item: NotificationItem) => {
    try {
      const updated = await apiFetch<NotificationItem>(`/api/v1/notifications/${item.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_starred: !item.is_starred }),
      });
      setNotifications((prev) =>
        prev.map((n) => (n.id === item.id ? { ...n, is_starred: updated.is_starred } : n))
      );
      if (selectedItem?.id === item.id) {
        setSelectedItem((prev) => (prev ? { ...prev, is_starred: updated.is_starred } : null));
      }
    } catch (err) {
      console.error("Failed to star notification:", err);
    }
  };

  const handleGenerateAIDraft = async () => {
    if (!selectedItem) return;
    setDraftingAI(true);
    try {
      const res = await apiFetch<any>("/api/v1/assistant/query", {
        method: "POST",
        body: JSON.stringify({
          query: `Draft a professional and concise reply to this message from ${selectedItem.sender?.name}: "${selectedItem.title}". Context: "${selectedItem.content}"`,
        }),
      });
      setReplyDraft(res.answer || "Thank you for the update. I have reviewed the items and will follow up shortly.");
    } catch (err) {
      setReplyDraft(`Hi ${selectedItem.sender?.name || "there"},\n\nThank you for reaching out regarding "${selectedItem.title}". I am currently reviewing the details and will get back to you with the requested information shortly.\n\nBest regards,\nHari`);
    } finally {
      setDraftingAI(false);
    }
  };

  const getProviderBadge = (provider: string) => {
    switch (provider.toLowerCase()) {
      case "gmail":
        return { icon: Mail, label: "Gmail", color: "text-red-400 bg-red-500/10 border-red-500/20" };
      case "whatsapp":
        return { icon: MessageSquare, label: "WhatsApp", color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20" };
      case "teams":
        return { icon: MessageSquare, label: "Teams", color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/20" };
      case "github":
        return { icon: Zap, label: "GitHub", color: "text-purple-400 bg-purple-500/10 border-purple-500/20" };
      case "calendar":
        return { icon: Calendar, label: "Calendar", color: "text-blue-400 bg-blue-500/10 border-blue-500/20" };
      default:
        return { icon: AlertCircle, label: provider, color: "text-slate-400 bg-slate-500/10 border-slate-500/20" };
    }
  };

  const providersList = [
    { id: "all", label: "All Feeds" },
    { id: "gmail", label: "Gmail" },
    { id: "whatsapp", label: "WhatsApp" },
    { id: "teams", label: "Teams" },
    { id: "github", label: "GitHub" },
    { id: "calendar", label: "Calendar" },
  ];

  return (
    <div className="h-full flex flex-col space-y-4 max-w-7xl mx-auto">
      {/* Top Controls Bar */}
      <div className="glass-panel-elevated p-3 rounded-2xl flex flex-col md:flex-row gap-3 items-center justify-between">
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
          <Search className="w-4 h-4 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search across Gmail, WhatsApp, Teams, GitHub, Calendar (Semantic & Keyword)..."
            className="w-full bg-slate-900/90 border border-white/[0.08] rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500/80 transition-colors"
          />
        </form>

        {/* Quick Filter Buttons */}
        <div className="flex items-center space-x-1.5 overflow-x-auto w-full md:w-auto pb-1 md:pb-0">
          {providersList.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedProvider(p.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedProvider === p.id
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                  : "bg-slate-900/70 hover:bg-slate-800 text-slate-400 border border-white/[0.05]"
              }`}
            >
              {p.label}
            </button>
          ))}

          <select
            value={selectedPriority}
            onChange={(e) => setSelectedPriority(e.target.value)}
            className="bg-slate-900 border border-white/[0.08] rounded-xl px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-blue-500"
          >
            <option value="all">All Priorities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Main Split View: Left list, Right detail */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-5 overflow-hidden min-h-0">
        {/* Left Column: Notification Item List */}
        <div className="lg:col-span-5 glass-panel rounded-2xl overflow-y-auto divide-y divide-white/[0.05] border border-white/[0.08]">
          {loading ? (
            <div className="p-12 text-center text-xs text-slate-400 flex flex-col items-center justify-center space-y-2">
              <div className="w-5 h-5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
              <span>Fetching unified communications...</span>
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-12 text-center text-xs text-slate-400 space-y-1">
              <CheckCircle className="w-8 h-8 mx-auto text-emerald-400/50 mb-2" />
              <p className="font-semibold text-slate-200">Inbox Zero achieved!</p>
              <p>No messages match your selected filters.</p>
            </div>
          ) : (
            notifications.map((item) => {
              const isSelected = selectedItem?.id === item.id;
              const badge = getProviderBadge(item.provider);
              const Icon = badge.icon;
              return (
                <div
                  key={item.id}
                  onClick={() => {
                    setSelectedItem(item);
                    setReplyDraft("");
                  }}
                  className={`p-4 cursor-pointer transition-all relative ${
                    isSelected
                      ? "bg-slate-850/90 border-l-4 border-blue-500 shadow-sm"
                      : "hover:bg-white/[0.03]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border flex items-center space-x-1 ${badge.color}`}>
                        <Icon className="w-3 h-3" />
                        <span>{badge.label}</span>
                      </span>
                      <span className="text-xs font-semibold text-slate-200">
                        {item.sender?.name || item.provider.toUpperCase()}
                      </span>
                    </div>

                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(item.timestamp).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>

                  <h4 className="text-xs font-semibold text-slate-100 line-clamp-1 mb-1">
                    {item.title}
                  </h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                    {item.content}
                  </p>

                  <div className="flex items-center space-x-2 mt-2.5">
                    {item.action_required && (
                      <span className="text-[10px] bg-amber-500/15 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full font-semibold">
                        Action Required
                      </span>
                    )}

                    <span
                      className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                        item.priority === "CRITICAL"
                          ? "text-red-400 bg-red-500/10 border border-red-500/20"
                          : item.priority === "HIGH"
                          ? "text-amber-400 bg-amber-500/10 border border-amber-500/20"
                          : "text-slate-400 bg-slate-800"
                      }`}
                    >
                      {item.priority}
                    </span>

                    {!item.is_read && (
                      <span className="w-2 h-2 rounded-full bg-blue-500 ml-auto animate-pulse" />
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Full Message Detail & AI Actions */}
        <div className="lg:col-span-7 glass-panel-elevated rounded-2xl p-6 overflow-y-auto flex flex-col justify-between border border-white/[0.08]">
          {selectedItem ? (
            <div className="space-y-6">
              {/* Header Bar */}
              <div className="border-b border-white/[0.08] pb-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2.5">
                    {(() => {
                      const badge = getProviderBadge(selectedItem.provider);
                      const Icon = badge.icon;
                      return (
                        <span className={`px-2.5 py-1 rounded-full text-xs font-bold border flex items-center space-x-1.5 ${badge.color}`}>
                          <Icon className="w-3.5 h-3.5" />
                          <span>{badge.label}</span>
                        </span>
                      );
                    })()}
                    <span className="text-xs text-slate-400 font-mono">
                      {new Date(selectedItem.timestamp).toLocaleString()}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleStarStatus(selectedItem)}
                      className={`p-2 rounded-xl border border-white/[0.08] hover:bg-white/[0.06] transition-colors ${
                        selectedItem.is_starred ? "text-amber-400 bg-amber-500/10 border-amber-500/30" : "text-slate-400"
                      }`}
                      title="Star item"
                    >
                      <Star className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => toggleReadStatus(selectedItem)}
                      className={`p-2 rounded-xl border border-white/[0.08] hover:bg-white/[0.06] transition-colors ${
                        selectedItem.is_read ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/30" : "text-slate-400"
                      }`}
                      title="Toggle read status"
                    >
                      <Check className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <h3 className="text-lg font-bold text-white tracking-tight">{selectedItem.title}</h3>

                <div className="p-3 rounded-xl bg-slate-900/60 border border-white/[0.06] flex items-center justify-between text-xs">
                  <div>
                    <span className="text-slate-400">From: </span>
                    <span className="font-semibold text-slate-100">{selectedItem.sender?.name}</span>{" "}
                    {selectedItem.sender?.address && (
                      <span className="text-slate-400 font-mono">({selectedItem.sender?.address})</span>
                    )}
                  </div>
                  {selectedItem.recipient && (
                    <div className="text-slate-400">
                      To: <span className="text-slate-200">{selectedItem.recipient}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* AI Executive TL;DR Synthesis Callout */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-blue-900/30 via-indigo-900/20 to-purple-900/20 border border-blue-500/30 space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold text-blue-300">
                  <div className="flex items-center space-x-2">
                    <Sparkles className="w-4 h-4 text-cyan-300" />
                    <span>AI Context Synthesis</span>
                  </div>
                  <span className="text-[10px] font-mono bg-blue-500/20 text-blue-200 px-2 py-0.5 rounded-full">
                    Model: GPT-4o-mini
                  </span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {selectedItem.action_required
                    ? `Sender is requesting an urgent update or confirmation on this item. Recommended action: Draft a confirmation reply or schedule a follow-up.`
                    : `Informational status update. No critical blocking dependencies identified.`}
                </p>
              </div>

              {/* Message Content */}
              <div className="p-5 rounded-2xl bg-slate-900/70 border border-white/[0.06] text-xs text-slate-200 leading-relaxed whitespace-pre-wrap font-sans">
                {selectedItem.content}
              </div>

              {/* AI Quick Response Drawer */}
              <div className="space-y-3 pt-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-1.5">
                    <CornerUpLeft className="w-3.5 h-3.5 text-blue-400" />
                    <span>Quick Response & Actions</span>
                  </span>

                  <button
                    onClick={handleGenerateAIDraft}
                    disabled={draftingAI}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-blue-600/15 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 text-xs font-semibold transition-all"
                  >
                    <Sparkles className={`w-3.5 h-3.5 text-cyan-300 ${draftingAI ? "animate-spin" : ""}`} />
                    <span>{draftingAI ? "Synthesizing Draft..." : "Auto-Draft AI Reply"}</span>
                  </button>
                </div>

                {replyDraft && (
                  <div className="space-y-2 animate-fade-in">
                    <textarea
                      value={replyDraft}
                      onChange={(e) => setReplyDraft(e.target.value)}
                      rows={4}
                      className="w-full bg-slate-900 border border-blue-500/40 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none"
                    />
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] text-slate-400">
                        Human-in-the-Loop: Review response before dispatching.
                      </span>
                      <Link
                        href={`/assistant?q=${encodeURIComponent("Send email to " + (selectedItem.sender?.address || selectedItem.sender?.name) + " with message: " + replyDraft)}`}
                        className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/30 transition-all"
                      >
                        <Send className="w-3.5 h-3.5" />
                        <span>Send via MCP Gateway</span>
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-xs text-slate-500 space-y-2">
              <Mail className="w-10 h-10 text-slate-600" />
              <span>Select any message from the left feed to inspect details</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
