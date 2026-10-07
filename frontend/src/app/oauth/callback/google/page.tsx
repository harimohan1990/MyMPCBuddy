"use client";

import React, { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiFetch, setAuthToken } from "@/lib/api";
import { CheckCircle2, AlertCircle } from "lucide-react";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState("Exchanging Google credentials...");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function handleExchange() {
      const code = searchParams.get("code");
      const state = searchParams.get("state");

      if (!code) {
        setError("Missing authorization code from Google OAuth response.");
        return;
      }

      try {
        setStatus("Authorizing account & establishing secure session...");
        const res = await apiFetch<{ access_token: string; refresh_token: string }>(
          "/api/v1/auth/google/callback",
          {
            method: "POST",
            body: JSON.stringify({ code, state }),
          }
        );

        if (res.access_token) {
          setAuthToken(res.access_token);
          setStatus("Success! Redirecting to your dashboard...");
          setTimeout(() => {
            router.push("/dashboard");
          }, 600);
        } else {
          setError("Failed to retrieve access token from Google authentication.");
        }
      } catch (err: any) {
        setError(err.message || "An error occurred during Google sign-in.");
      }
    }

    handleExchange();
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#090d16] text-slate-100">
      <div className="max-w-md w-full bg-[#0c1222] border border-slate-800 p-8 rounded-2xl text-center space-y-4 shadow-xl">
        {error ? (
          <>
            <div className="w-12 h-12 mx-auto rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center text-red-400">
              <AlertCircle className="w-6 h-6" />
            </div>
            <h2 className="text-base font-bold text-white">Google Sign-In Error</h2>
            <p className="text-xs text-red-400 leading-relaxed">{error}</p>
            <button
              onClick={() => router.push("/login")}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold rounded-lg text-slate-300 transition-colors"
            >
              Return to Login
            </button>
          </>
        ) : (
          <>
            <div className="w-12 h-12 mx-auto rounded-full bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 animate-spin">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h2 className="text-base font-bold text-white">Google Authentication</h2>
            <p className="text-xs text-slate-400">{status}</p>
          </>
        )}
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-[#090d16] text-slate-400 text-xs">
          Loading authentication handler...
        </div>
      }
    >
      <GoogleCallbackContent />
    </Suspense>
  );
}
