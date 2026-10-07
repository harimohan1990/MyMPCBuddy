"use client";

import React, { useState, useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import {
  Sparkles,
  Send,
  ShieldAlert,
  CheckCircle,
  XCircle,
  Layers,
  Terminal,
  Clock,
  ExternalLink,
  Bot,
  User,
  Zap,
  CornerDownLeft,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  ShieldCheck,
} from "lucide-react";
import { apiFetch } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  toolsCalled?: string[];
  sources?: any[];
  suggestedActions?: any[];
}

function AssistantContent() {
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello Hari! I'm your Personal MCP Copilot. I have secure, read-only access to your Gmail, WhatsApp, Teams, GitHub, and Google Calendar. I can synthesize threads, highlight pending action items, and stage draft replies with human confirmation gates. How can I assist you right now?",
    },
  ]);
  const [inputQuery, setInputQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [expandedTools, setExpandedTools] = useState<Record<number, boolean>>({});

  // Human-in-the-loop confirmation states
  const [stagedAction, setStagedAction] = useState<any | null>(null);
  const [confirmationToken, setConfirmationToken] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sampleQueries = [
    { title: "Inbox Briefing", query: "What happened while I was away? Summarize urgent updates." },
    { title: "Pending Replies", query: "Who do I need to reply to across Gmail and Teams today?" },
    { title: "Rahul's Project Update", query: "What did Rahul say about the project deliverables?" },
    { title: "Today's Agenda", query: "What meetings and deadlines do I have on my calendar today?" },
  ];

  // Auto-scroll on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Handle URL query parameter pre-fill
  useEffect(() => {
    const q = searchParams.get("q");
    if (q) {
      handleSend(q);
    }
  }, [searchParams]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    const userMessage: Message = { role: "user", content: textToSend };
    setMessages((prev) => [...prev, userMessage]);
    setInputQuery("");
    setLoading(true);

    try {
      const res = await apiFetch<any>("/api/v1/assistant/query", {
        method: "POST",
        body: JSON.stringify({ query: textToSend }),
      });

      const assistantMessage: Message = {
        role: "assistant",
        content: res.answer,
        toolsCalled: res.tools_called,
        sources: res.sources,
        suggestedActions: res.suggested_actions,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Apologies, encountered an error querying communications: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerAction = async (action: any) => {
    try {
      setActionStatus("Requesting authorization token from MCP gateway...");
      const res = await apiFetch<any>("/api/v1/mcp/execute", {
        method: "POST",
        body: JSON.stringify({
          tool_name: action.tool_name,
          parameters: action.parameters,
          confirmed: false,
        }),
      });

      if (res.status === "CONFIRMATION_REQUIRED") {
        setStagedAction({
          ...action,
          prompt: res.confirmation_prompt,
        });
        setConfirmationToken(res.confirmation_token);
      } else if (res.status === "EXECUTED") {
        setActionStatus("Action executed successfully.");
      }
    } catch (err: any) {
      alert(`Error staging tool call: ${err.message}`);
    }
  };

  const handleAuthorizeAction = async () => {
    if (!stagedAction || !confirmationToken) return;

    try {
      setActionStatus("Authorizing and executing MCP tool call...");
      const res = await apiFetch<any>("/api/v1/mcp/execute", {
        method: "POST",
        body: JSON.stringify({
          tool_name: stagedAction.tool_name,
          parameters: stagedAction.parameters,
          confirmed: true,
          confirmation_token: confirmationToken,
        }),
      });

      if (res.status === "EXECUTED") {
        alert(`Success: ${stagedAction.label} was executed safely through MCP.`);
        setStagedAction(null);
        setConfirmationToken(null);
        setActionStatus(null);
      } else {
        alert(`Failed: ${res.error}`);
      }
    } catch (err: any) {
      alert(`Execution error: ${err.message}`);
    }
  };

  const toggleTools = (idx: number) => {
    setExpandedTools((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="max-w-5xl mx-auto h-full flex flex-col space-y-4">
      {/* Top Protocol Status Bar */}
      <div className="glass-panel-elevated p-4 rounded-2xl flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-500 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              Personal MCP Copilot
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-300 border border-blue-500/30">
                gpt-4o-mini
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Model Context Protocol Gateway • Least Privilege Access Matrix Enforced
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-slate-900 border border-white/[0.08] text-xs text-emerald-400 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>HITL Gate: Active</span>
          </div>

          <button
            onClick={() =>
              setMessages([
                {
                  role: "assistant",
                  content:
                    "Conversation reset. How can I help you with your communications today?",
                },
              ])
            }
            className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-white/[0.08] transition-colors"
            title="Reset Chat"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Suggested Quick Starters */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
        {sampleQueries.map((item, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(item.query)}
            className="text-left p-3 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/[0.06] hover:border-blue-500/40 transition-all group"
          >
            <p className="text-[11px] font-bold text-white group-hover:text-blue-300 flex items-center justify-between">
              <span>{item.title}</span>
              <CornerDownLeft className="w-3 h-3 text-slate-500 group-hover:text-blue-400 transition-transform" />
            </p>
            <p className="text-[10px] text-slate-400 mt-1 line-clamp-1">{item.query}</p>
          </button>
        ))}
      </div>

      {/* Chat Messages Log */}
      <div className="flex-1 glass-panel rounded-2xl p-5 overflow-y-auto space-y-5 border border-white/[0.08]">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex items-start space-x-3.5 ${
              m.role === "user" ? "flex-row-reverse space-x-reverse" : "flex-row"
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold shadow-sm ${
                m.role === "user"
                  ? "bg-gradient-to-tr from-blue-600 to-indigo-600 text-white"
                  : "bg-gradient-to-tr from-cyan-600 to-blue-600 text-white"
              }`}
            >
              {m.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>

            {/* Bubble */}
            <div
              className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed space-y-3.5 ${
                m.role === "user"
                  ? "bg-blue-600 text-white rounded-tr-none shadow-md shadow-blue-600/20"
                  : "glass-panel-elevated text-slate-200 rounded-tl-none border border-white/[0.08]"
              }`}
            >
              <div className="whitespace-pre-wrap leading-relaxed">{m.content}</div>

              {/* Tools Called Telemetry */}
              {m.toolsCalled && m.toolsCalled.length > 0 && (
                <div className="pt-2 border-t border-white/[0.08]">
                  <button
                    onClick={() => toggleTools(idx)}
                    className="flex items-center space-x-2 text-[11px] text-slate-400 hover:text-slate-200"
                  >
                    <Terminal className="w-3.5 h-3.5 text-cyan-400" />
                    <span>
                      MCP Protocol Tools ({m.toolsCalled.length} invoked)
                    </span>
                    {expandedTools[idx] ? (
                      <ChevronUp className="w-3 h-3" />
                    ) : (
                      <ChevronDown className="w-3 h-3" />
                    )}
                  </button>

                  {expandedTools[idx] && (
                    <div className="flex flex-wrap gap-1.5 mt-2 animate-fade-in">
                      {m.toolsCalled.map((tool, tIdx) => (
                        <span
                          key={tIdx}
                          className="font-mono text-[10px] bg-slate-900 text-cyan-300 px-2 py-0.5 rounded-lg border border-cyan-500/20"
                        >
                          mcp::{tool}()
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Suggested Actions with Confirmation Gate */}
              {m.suggestedActions && m.suggestedActions.length > 0 && (
                <div className="pt-2 border-t border-white/[0.08] space-y-2">
                  <p className="text-[11px] font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5">
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                    <span>Suggested Action</span>
                  </p>
                  <div className="space-y-1.5">
                    {m.suggestedActions.map((act, actIdx) => (
                      <button
                        key={actIdx}
                        onClick={() => handleTriggerAction(act)}
                        className="w-full text-left px-3.5 py-2.5 rounded-xl bg-blue-600/10 hover:bg-blue-600/20 text-blue-300 border border-blue-500/30 text-xs font-semibold flex items-center justify-between transition-all"
                      >
                        <span>{act.label}</span>
                        <span className="text-[10px] font-mono bg-blue-500/30 text-blue-200 px-2 py-0.5 rounded-full uppercase">
                          Stage Tool Call
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center space-x-3 text-xs text-slate-400 p-3 bg-white/[0.02] rounded-xl border border-white/[0.05] animate-pulse">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            <span>Consulting MCP tool server & aggregating thread sources...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Confirmation Modal / Staged Gate */}
      {stagedAction && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-950/60 to-red-950/40 border border-amber-500/40 space-y-3 shadow-xl animate-fade-in">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
              <ShieldAlert className="w-4 h-4" />
              <span>Human-in-the-Loop Confirmation Gate Required</span>
            </div>
            <span className="text-[10px] font-mono bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded-full">
              HMAC Token Verified
            </span>
          </div>

          <p className="text-xs text-slate-200 leading-relaxed font-mono bg-black/40 p-3 rounded-xl border border-amber-500/20">
            {stagedAction.prompt}
          </p>

          <div className="flex items-center space-x-3 pt-1">
            <button
              onClick={handleAuthorizeAction}
              className="px-4 py-2 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs flex items-center space-x-1.5 shadow-md shadow-amber-500/20 transition-all active:scale-95"
            >
              <CheckCircle className="w-4 h-4" />
              <span>Authorize & Execute Tool Call</span>
            </button>
            <button
              onClick={() => {
                setStagedAction(null);
                setConfirmationToken(null);
              }}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold transition-colors"
            >
              Cancel Execution
            </button>
          </div>
        </div>
      )}

      {/* Query Input Box */}
      <div className="glass-panel-elevated p-2 rounded-2xl border border-white/[0.08] flex items-center space-x-2">
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask anything across your Gmail, WhatsApp, Teams, GitHub, and Calendar..."
          className="flex-1 bg-transparent px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none"
        />
        <button
          onClick={() => handleSend()}
          disabled={loading || !inputQuery.trim()}
          className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white transition-all active:scale-95 disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}

export default function AssistantPage() {
  return (
    <React.Suspense
      fallback={
        <div className="flex items-center justify-center h-full text-xs text-slate-400">
          Loading AI Copilot Assistant...
        </div>
      }
    >
      <AssistantContent />
    </React.Suspense>
  );
}
