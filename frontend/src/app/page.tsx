"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch, setAuthToken, getAuthToken } from "@/lib/api";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    async function initSession() {
      try {
        const token = getAuthToken();
        if (!token) {
          // Auto-login or register demo session
          const res = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/login`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                email: "hari.mohan@example.com",
                password: "StrongPassword123!",
              }),
            }
          );
          if (res.ok) {
            const data = await res.json();
            setAuthToken(data.access_token);
          } else {
            // Register if not exists
            const regRes = await fetch(
              `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/register`,
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  email: "hari.mohan@example.com",
                  password: "StrongPassword123!",
                  full_name: "Hari Mohan",
                }),
              }
            );
            if (regRes.ok) {
              const regData = await regRes.json();
              setAuthToken(regData.access_token);
            }
          }
        }
      } catch (err) {
        console.error("Auto session setup error:", err);
      } finally {
        router.push("/dashboard");
      }
    }

    initSession();
  }, [router]);

  return (
    <div className="flex h-full items-center justify-center">
      <div className="flex flex-col items-center space-y-4">
        <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-slate-400">Loading Personal MCP Hub...</p>
      </div>
    </div>
  );
}
