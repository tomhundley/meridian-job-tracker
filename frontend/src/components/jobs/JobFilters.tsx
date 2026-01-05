"use client";

import { useState } from "react";
import { Search } from "lucide-react";

const statuses = [
  { value: "", label: "All Statuses" },
  { value: "saved", label: "Saved" },
  { value: "applied", label: "Applied" },
  { value: "interviewing", label: "Interviewing" },
  { value: "offer", label: "Offer" },
  { value: "rejected", label: "Rejected" },
];

export function JobFilters() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");

  return (
    <div className="flex gap-4 items-center">
      <div className="relative flex-1 max-w-md">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]"
          size={18}
        />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search jobs..."
          className="w-full pl-10 pr-4 py-2 bg-[var(--color-bg-secondary)] border border-[var(--color-border-subtle)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
        />
      </div>

      <select
        value={status}
        onChange={(e) => setStatus(e.target.value)}
        className="px-4 py-2 bg-[var(--color-bg-secondary)] border border-[var(--color-border-subtle)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
      >
        {statuses.map((s) => (
          <option key={s.value} value={s.value}>
            {s.label}
          </option>
        ))}
      </select>
    </div>
  );
}
