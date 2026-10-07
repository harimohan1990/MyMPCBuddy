"use client";

import React, { useEffect, useState } from "react";
import {
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  Video,
  AlertTriangle,
  Users,
  Sparkles,
  ExternalLink,
  ChevronRight,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { CalendarEventItem } from "@/lib/types";

export default function CalendarPage() {
  const [events, setEvents] = useState<CalendarEventItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCalendar() {
      try {
        setLoading(true);
        const data = await apiFetch<CalendarEventItem[]>("/api/v1/calendar/today");
        setEvents(data);
      } catch (err) {
        console.error("Failed to load calendar events:", err);
      } finally {
        setLoading(false);
      }
    }
    loadCalendar();
  }, []);

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <span>Unified Executive Calendar</span>
            <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-blue-500/20 text-blue-300 border border-blue-500/30">
              {events.length} Events Today
            </span>
          </h2>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            Synchronized schedule across Google Calendar and Microsoft Outlook with meeting links & conflict detection
          </p>
        </div>
      </div>

      {/* Events Timeline Container */}
      <div className="glass-panel-elevated rounded-2xl divide-y divide-white/[0.06] border border-white/[0.08] overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400 flex flex-col items-center justify-center space-y-2">
            <div className="w-5 h-5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
            <span>Loading aggregated calendar...</span>
          </div>
        ) : events.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400 space-y-1">
            <CalendarIcon className="w-8 h-8 mx-auto text-blue-400/50 mb-2" />
            <p className="font-semibold text-slate-200">No scheduled meetings today</p>
            <p>Your calendar is clear for focused deep work.</p>
          </div>
        ) : (
          events.map((ev, idx) => {
            const startFormatted = new Date(ev.start_time).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            });
            const endFormatted = new Date(ev.end_time).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            });

            return (
              <div
                key={ev.id || idx}
                className="p-6 flex flex-col md:flex-row md:items-center justify-between gap-5 hover:bg-white/[0.02] transition-colors"
              >
                <div className="flex items-start space-x-4">
                  {/* Time Badge */}
                  <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-600/20 to-indigo-600/20 border border-blue-500/30 text-blue-300 shrink-0 text-center min-w-[76px]">
                    <Clock className="w-4 h-4 mx-auto mb-1 text-cyan-300" />
                    <span className="text-xs font-bold block">{startFormatted}</span>
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center flex-wrap gap-2">
                      <span className="text-sm font-bold text-white">{ev.summary}</span>

                      <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-slate-900 text-slate-300 border border-white/[0.08]">
                        {ev.provider}
                      </span>

                      {ev.has_conflict && (
                        <span className="flex items-center space-x-1 text-[10px] bg-red-500/15 text-red-400 border border-red-500/30 px-2 py-0.5 rounded-full font-semibold">
                          <AlertTriangle className="w-3 h-3" />
                          <span>Schedule Conflict</span>
                        </span>
                      )}
                    </div>

                    <p className="text-xs text-slate-400 font-mono">
                      {startFormatted} – {endFormatted}
                    </p>

                    {ev.description && (
                      <p className="text-xs text-slate-300 leading-relaxed max-w-xl">
                        {ev.description}
                      </p>
                    )}

                    {ev.location && (
                      <div className="flex items-center space-x-1.5 text-xs text-slate-400 pt-0.5">
                        <MapPin className="w-3.5 h-3.5 text-indigo-400" />
                        <span>{ev.location}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Join Meeting CTA */}
                {ev.meeting_link && (
                  <a
                    href={ev.meeting_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0 px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold flex items-center space-x-2 shadow-md shadow-blue-600/25 transition-all active:scale-95 self-start md:self-center"
                  >
                    <Video className="w-4 h-4" />
                    <span>Join Video Call</span>
                    <ExternalLink className="w-3 h-3 ml-1 opacity-70" />
                  </a>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
