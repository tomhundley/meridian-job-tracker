"use client";

import { Search } from "lucide-react";

const statuses = [
  { value: "", label: "All Statuses" },
  { value: "saved", label: "Saved" },
  { value: "applied", label: "Applied" },
  { value: "interviewing", label: "Interviewing" },
  { value: "offer", label: "Offer" },
  { value: "rejected", label: "Rejected" },
];

const locationTypes = [
  { value: "", label: "All" },
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "on_site", label: "On-site" },
];

// Priority levels: 0 = All, 1-5 = minimum stars
const priorityLevels = [
  { value: 0, label: "All", minPriority: 0 },
  { value: 1, label: "1+", minPriority: 1 },
  { value: 2, label: "2+", minPriority: 21 },
  { value: 3, label: "3+", minPriority: 41 },
  { value: 4, label: "4+", minPriority: 61 },
  { value: 5, label: "5", minPriority: 81 },
];

interface JobFiltersProps {
  search: string;
  status: string;
  workLocationType: string;
  minPriority: number;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onWorkLocationTypeChange: (value: string) => void;
  onMinPriorityChange: (value: number) => void;
}

export function JobFilters({
  search,
  status,
  workLocationType,
  minPriority,
  onSearchChange,
  onStatusChange,
  onWorkLocationTypeChange,
  onMinPriorityChange,
}: JobFiltersProps) {
  // Find current priority level from minPriority value
  const currentPriorityLevel = priorityLevels.find(
    (p) => p.minPriority === minPriority
  )?.value ?? 0;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-md">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]"
            size={18}
          />
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search jobs..."
            className="w-full pl-10 pr-4 py-2 bg-[var(--color-bg-secondary)] border border-[var(--color-border-subtle)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
          />
        </div>

        <select
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
          className="px-4 py-2 bg-[var(--color-bg-secondary)] border border-[var(--color-border-subtle)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
        >
          {statuses.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex gap-6 items-center flex-wrap">
        <div className="flex gap-2 items-center">
          <span className="text-sm text-[var(--color-text-tertiary)]">Location:</span>
          {locationTypes.map((loc) => (
            <button
              key={loc.value}
              onClick={() => onWorkLocationTypeChange(loc.value)}
              className={`px-3 py-1.5 text-sm rounded-full transition-colors ${
                workLocationType === loc.value
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)]"
              }`}
            >
              {loc.label}
            </button>
          ))}
        </div>

        <div className="flex gap-2 items-center">
          <span className="text-sm text-[var(--color-text-tertiary)]">Priority:</span>
          {priorityLevels.map((p) => (
            <button
              key={p.value}
              onClick={() => onMinPriorityChange(p.minPriority)}
              className={`px-3 py-1.5 text-sm rounded-full transition-colors flex items-center gap-1 ${
                currentPriorityLevel === p.value
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-[var(--color-bg-secondary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)]"
              }`}
            >
              {p.value === 0 ? (
                "All"
              ) : (
                <>
                  <span className="text-yellow-400">{"★".repeat(p.value)}</span>
                  {p.value < 5 && <span className="text-xs">+</span>}
                </>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
