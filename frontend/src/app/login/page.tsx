"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Lock, Mail, ArrowRight, ShieldCheck, Sparkles, CheckCircle2, Zap, Key } from "lucide-react";
import { apiFetch, setAuthToken } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("hari.mohan@gmail.com");
  const [password, setPassword] = useState("StrongPassword123!");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGoogleLogin = async () => {
    try {
      setLoading(true);
      setError(null);
      // Fetch Google authorization URL from backend
      const res = await apiFetch<{ authorization_url: string; state: string }>("/api/v1/auth/google/url");
      if (res.authorization_url) {
        window.location.href = res.authorization_url;
      }
    } catch (err: any) {
      setError(`Google OAuth error: ${err.message}`);
      setLoading(false);
    }
  };

  const handleGoogleOneTap = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiFetch<{ access_token: string; refresh_token: string }>("/api/v1/auth/google/one-tap", {
        method: "POST",
        body: JSON.stringify({ email: "hari.mohan@gmail.com", name: "Hari Mohan" }),
      });
      setAuthToken(res.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(`Google One-Tap failed: ${err.message}`);
      setLoading(false);
    }
  };

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      const res = await apiFetch<{ access_token: string; refresh_token: string }>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setAuthToken(res.access_token);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid credentials");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#080c16] text-slate-100 relative overflow-hidden font-sans">
      {/* Ambient background glow elements */}
      <div className="absolute top-1/4 left-1/3 -mt-24 -ml-24 w-96 h-96 rounded-full bg-blue-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 -mb-24 -mr-24 w-96 h-96 rounded-full bg-indigo-600/10 blur-[120px] pointer-events-none" />

      <div className="max-w-md w-full space-y-7 glass-panel-elevated p-8 md:p-10 rounded-3xl border border-white/[0.09] shadow-2xl relative z-10 animate-fade-in">
        {/* Brand Logo & Header */}
        <div className="text-center space-y-2.5">
          <div className="w-12 h-12 mx-auto rounded-2xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-cyan-400 flex items-center justify-center font-bold text-white shadow-xl shadow-blue-500/30">
            <Zap className="w-6 h-6 fill-white/20" />
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight text-white">Personal MCP Hub</h2>
          <p className="text-xs text-slate-400 leading-relaxed max-w-xs mx-auto">
            Unified personal digital assistant & notification intelligence center
          </p>
        </div>

        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/25 rounded-2xl text-xs text-red-400 text-center animate-fade-in">
            {error}
          </div>
        )}

        {/* Primary Google Sign-In Buttons */}
        <div className="space-y-3">
          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-3 py-3 px-4 rounded-2xl bg-white hover:bg-slate-100 text-slate-900 font-bold text-xs shadow-lg shadow-white/10 transition-all active:scale-[0.98] disabled:opacity-70"
          >
            {/* Google G-Logo */}
            <svg className="w-4 h-4" viewBox="0 0 24 24">
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
            <span>Continue with Google</span>
          </button>

          <button
            onClick={handleGoogleOneTap}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 py-2.5 px-3 rounded-2xl bg-blue-600/15 hover:bg-blue-600/25 text-blue-300 border border-blue-500/30 text-xs font-semibold transition-all active:scale-[0.98]"
          >
            <Sparkles className="w-4 h-4 text-cyan-300" />
            <span>1-Click Fast Google Sign-In (Demo)</span>
          </button>
        </div>

        {/* Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/[0.08]" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-[#0e1628] px-3 text-slate-500 text-[10px] font-bold tracking-wider">
              Or sign in with email
            </span>
          </div>
        </div>

        {/* Password Form */}
        <form onSubmit={handleEmailLogin} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-slate-300">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-slate-900/90 border border-white/[0.08] rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold text-slate-300">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-3 text-slate-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full bg-slate-900/90 border border-white/[0.08] rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-center space-x-2 shadow-lg shadow-blue-600/30 transition-all active:scale-[0.98] disabled:opacity-70"
          >
            <span>{loading ? "Authenticating..." : "Sign In to MCP Hub"}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>

        {/* Security Footer */}
        <div className="pt-2 text-center text-[11px] text-slate-400 flex items-center justify-center space-x-1.5">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>OAuth 2.0 PKCE • AES-256-GCM Token Encryption</span>
        </div>
      </div>
    </div>
  );
}
