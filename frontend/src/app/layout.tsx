import type { Metadata } from "next";
import "./globals.css";
import { Shell } from "@/components/layout/Shell";

export const metadata: Metadata = {
  title: "Personal MCP Hub — Unified Communication & Notification Platform",
  description: "One application to see, search, summarize, and act on personal communications with Model Context Protocol (MCP)",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-[#090d16] text-slate-100 antialiased selection:bg-blue-500 selection:text-white">
        <Shell>{children}</Shell>
      </body>
    </html>
  );
}
