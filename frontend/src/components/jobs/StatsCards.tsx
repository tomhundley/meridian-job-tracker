"use client";

import useSWR from "swr";
import { Briefcase, Clock, CheckCircle, XCircle } from "lucide-react";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

interface Stats {
  total: number;
  applied: number;
  interviewing: number;
  rejected: number;
}

export function StatsCards() {
  const { data: jobs } = useSWR("/api/jobs", fetcher);

  // Calculate stats from jobs
  const stats: Stats = {
    total: jobs?.items?.length || 0,
    applied: jobs?.items?.filter((j: any) => j.status === "applied").length || 0,
    interviewing: jobs?.items?.filter((j: any) => j.status === "interviewing").length || 0,
    rejected: jobs?.items?.filter((j: any) => j.status === "rejected").length || 0,
  };

  const cards = [
    { label: "Total Jobs", value: stats.total, icon: Briefcase, color: "text-blue-400" },
    { label: "Applied", value: stats.applied, icon: CheckCircle, color: "text-green-400" },
    { label: "Interviewing", value: stats.interviewing, icon: Clock, color: "text-yellow-400" },
    { label: "Rejected", value: stats.rejected, icon: XCircle, color: "text-red-400" },
  ];

  return (
    <div className="grid grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.label}
            className="p-4 bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)]"
          >
            <div className="flex items-center gap-3">
              <Icon className={card.color} size={24} />
              <div>
                <p className="text-2xl font-bold">{card.value}</p>
                <p className="text-sm text-[var(--color-text-tertiary)]">
                  {card.label}
                </p>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
