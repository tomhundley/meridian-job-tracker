"use client";

import { Search, MapPin, TrendingUp, DollarSign, Filter, CircleDot, Zap, Star, Target, Sparkles, Calendar, RefreshCw } from "lucide-react";

const statuses = [
  { value: "", label: "Any" },
  { value: "saved", label: "Saved" },
  { value: "applied", label: "Applied" },
  { value: "interviewing", label: "Interview" },
  { value: "offer", label: "Offer" },
  { value: "rejected", label: "Rejected" },
];

const locationTypes = [
  { value: "", label: "Any" },
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "on_site", label: "On-site" },
];

// Priority levels with meaningful labels
const priorityLevels = [
  { label: "Any", minPriority: 0 },
  { label: "Low+", minPriority: 1 },
  { label: "Med+", minPriority: 41 },
  { label: "High+", minPriority: 61 },
  { label: "Top", minPriority: 81 },
];

// Salary range presets
const salaryRanges = [
  { label: "Any", minSalary: 0 },
  { label: "$100k+", minSalary: 100000 },
  { label: "$150k+", minSalary: 150000 },
  { label: "$200k+", minSalary: 200000 },
  { label: "$250k+", minSalary: 250000 },
];

// Posting age presets (in days)
const agePresets = [
  { label: "Any", maxDays: 0 },
  { label: "≤7d", maxDays: 7 },
  { label: "≤14d", maxDays: 14 },
  { label: "≤30d", maxDays: 30 },
  { label: "≤60d", maxDays: 60 },
];

// Easy Apply filter options
const easyApplyOptions = [
  { label: "Any", value: "" },
  { label: "Yes", value: "true" },
  { label: "No", value: "false" },
];

// Favorite filter options
const favoriteOptions = [
  { label: "Any", value: "" },
  { label: "Yes", value: "true" },
  { label: "No", value: "false" },
];

// Perfect Fit filter options
const perfectFitOptions = [
  { label: "Any", value: "" },
  { label: "Yes", value: "true" },
  { label: "No", value: "false" },
];

// AI Forward filter options
const aiForwardOptions = [
  { label: "Any", value: "" },
  { label: "Yes", value: "true" },
  { label: "No", value: "false" },
];

interface JobFiltersProps {
  search: string;
  status: string;
  workLocationType: string;
  isEasyApply: string;
  isFavorite: string;
  isPerfectFit: string;
  isAiForward: string;
  minPriority: number;
  minSalary: number;
  maxAgeDays: number;
  onSearchChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onWorkLocationTypeChange: (value: string) => void;
  onIsEasyApplyChange: (value: string) => void;
  onIsFavoriteChange: (value: string) => void;
  onIsPerfectFitChange: (value: string) => void;
  onIsAiForwardChange: (value: string) => void;
  onMinPriorityChange: (value: number) => void;
  onMinSalaryChange: (value: number) => void;
  onMaxAgeDaysChange: (value: number) => void;
  onRefresh?: () => void;
}

interface SegmentedControlProps {
  icon?: React.ReactNode;
  label: string;
  options: { label: string; value: string | number }[];
  value: string | number;
  onChange: (value: string | number) => void;
  accentColor?: string;
}

function SegmentedControl({ icon, label, options, value, onChange, accentColor }: SegmentedControlProps) {
  const colorClass = accentColor || "text-[var(--color-text-tertiary)]";
  return (
    <div
      className="flex items-center gap-2.5 px-3 py-2 rounded-lg backdrop-blur-sm border border-white/10"
      style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)' }}
    >
      {icon && <span className={colorClass}>{icon}</span>}
      <span className={`text-xs font-medium uppercase tracking-wide ${colorClass}`}>
        {label}
      </span>
      <div className="flex bg-[var(--color-bg-tertiary)] rounded-md p-0.5">
        {options.map((option) => (
          <button
            key={option.label}
            onClick={() => onChange(option.value)}
            className={`px-3 py-1 text-sm font-medium rounded transition-all ${
              value === option.value
                ? "bg-[var(--color-bg-primary)] text-[var(--color-text-primary)] shadow-sm"
                : "text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)]"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function JobFilters({
  search,
  status,
  workLocationType,
  isEasyApply,
  isFavorite,
  isPerfectFit,
  isAiForward,
  minPriority,
  minSalary,
  maxAgeDays,
  onSearchChange,
  onStatusChange,
  onWorkLocationTypeChange,
  onIsEasyApplyChange,
  onIsFavoriteChange,
  onIsPerfectFitChange,
  onIsAiForwardChange,
  onMinPriorityChange,
  onMinSalaryChange,
  onMaxAgeDaysChange,
  onRefresh,
}: JobFiltersProps) {
  // Check if any filters are active
  const hasActiveFilters = status || workLocationType || isEasyApply || isFavorite || isPerfectFit || isAiForward || minPriority > 0 || minSalary > 0 || maxAgeDays > 0;

  const clearAllFilters = () => {
    onStatusChange("");
    onWorkLocationTypeChange("");
    onIsEasyApplyChange("");
    onIsFavoriteChange("");
    onIsPerfectFitChange("");
    onIsAiForwardChange("");
    onMinPriorityChange(0);
    onMinSalaryChange(0);
    onMaxAgeDaysChange(0);
  };

  return (
    <div className="space-y-3">
      {/* Search Row */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-xl">
          <Search
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]"
            size={18}
          />
          <input
            type="text"
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search by title, company, or description..."
            className="w-full pl-11 pr-4 py-2.5 bg-[var(--color-bg-secondary)] border border-[var(--color-border-subtle)] rounded-lg text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]/20 focus:border-[var(--color-accent)]/50 transition-all"
          />
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="flex items-center gap-2 px-4 py-2.5 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-secondary)] rounded-lg transition-all border border-[var(--color-border-subtle)]"
            title="Refresh jobs"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        )}

        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="px-4 py-2.5 text-sm text-[var(--color-text-tertiary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-secondary)] rounded-lg transition-all"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Filter Controls Row */}
      <div className="flex items-center gap-3 flex-wrap pt-3 border-t border-[var(--color-border-subtle)]">
        <SegmentedControl
          icon={<CircleDot size={14} />}
          label="Status"
          options={statuses.map((s) => ({ label: s.label, value: s.value }))}
          value={status}
          onChange={(v) => onStatusChange(v as string)}
          accentColor="text-blue-400"
        />

        <SegmentedControl
          icon={<MapPin size={14} />}
          label="Location"
          options={locationTypes.map((l) => ({ label: l.label, value: l.value }))}
          value={workLocationType}
          onChange={(v) => onWorkLocationTypeChange(v as string)}
          accentColor="text-orange-400"
        />

        <SegmentedControl
          icon={<Zap size={14} />}
          label="Easy Apply"
          options={easyApplyOptions.map((e) => ({ label: e.label, value: e.value }))}
          value={isEasyApply}
          onChange={(v) => onIsEasyApplyChange(v as string)}
          accentColor="text-green-400"
        />

        <SegmentedControl
          icon={<Star size={14} />}
          label="Favorite"
          options={favoriteOptions.map((f) => ({ label: f.label, value: f.value }))}
          value={isFavorite}
          onChange={(v) => onIsFavoriteChange(v as string)}
          accentColor="text-yellow-400"
        />

        <SegmentedControl
          icon={<Target size={14} />}
          label="Perfect Fit"
          options={perfectFitOptions.map((p) => ({ label: p.label, value: p.value }))}
          value={isPerfectFit}
          onChange={(v) => onIsPerfectFitChange(v as string)}
          accentColor="text-purple-400"
        />

        <SegmentedControl
          icon={<Sparkles size={14} />}
          label="AI Forward"
          options={aiForwardOptions.map((a) => ({ label: a.label, value: a.value }))}
          value={isAiForward}
          onChange={(v) => onIsAiForwardChange(v as string)}
          accentColor="text-cyan-400"
        />

        <SegmentedControl
          icon={<TrendingUp size={14} />}
          label="Priority"
          options={priorityLevels.map((p) => ({ label: p.label, value: p.minPriority }))}
          value={minPriority}
          onChange={(v) => onMinPriorityChange(v as number)}
          accentColor="text-emerald-400"
        />

        <SegmentedControl
          icon={<DollarSign size={14} />}
          label="Salary"
          options={salaryRanges.map((s) => ({ label: s.label, value: s.minSalary }))}
          value={minSalary}
          onChange={(v) => onMinSalaryChange(v as number)}
          accentColor="text-lime-400"
        />

        <SegmentedControl
          icon={<Calendar size={14} />}
          label="Posted"
          options={agePresets.map((a) => ({ label: a.label, value: a.maxDays }))}
          value={maxAgeDays}
          onChange={(v) => onMaxAgeDaysChange(v as number)}
          accentColor="text-amber-400"
        />
      </div>
    </div>
  );
}
