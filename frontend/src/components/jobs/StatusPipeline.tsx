"use client";

interface StatusPipelineProps {
  currentStatus: string;
  onStatusChange: (status: string) => void;
  disabled?: boolean;
}

const statusConfig: Record<string, { label: string; color: string }> = {
  saved: { label: "Saved", color: "blue" },
  researching: { label: "Researching", color: "purple" },
  ready_to_apply: { label: "Ready", color: "cyan" },
  applying: { label: "Applying", color: "yellow" },
  applied: { label: "Applied", color: "green" },
  interviewing: { label: "Interviewing", color: "emerald" },
  offer: { label: "Offer", color: "pink" },
  rejected: { label: "Rejected", color: "red" },
  withdrawn: { label: "Withdrawn", color: "orange" },
  archived: { label: "Archived", color: "gray" },
};

const statusGroups = [
  { label: "Pre-Apply", statuses: ["saved", "researching", "ready_to_apply", "applying"], canUncheck: false },
  { label: "Post-Apply", statuses: ["applied", "interviewing"], canUncheck: true },
  { label: "Outcomes", statuses: ["offer", "rejected", "withdrawn"], canUncheck: true },
];

// Explicit class mappings to avoid Tailwind purging issues
const colorClasses: Record<string, { active: string; inactive: string; hover: string }> = {
  blue: {
    active: "bg-blue-500 text-white shadow-lg shadow-blue-500/30 ring-2 ring-blue-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-blue-500/10 text-blue-400 border border-blue-500/30",
    hover: "hover:bg-blue-500/20 hover:border-blue-500/50",
  },
  purple: {
    active: "bg-purple-500 text-white shadow-lg shadow-purple-500/30 ring-2 ring-purple-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-purple-500/10 text-purple-400 border border-purple-500/30",
    hover: "hover:bg-purple-500/20 hover:border-purple-500/50",
  },
  cyan: {
    active: "bg-cyan-500 text-white shadow-lg shadow-cyan-500/30 ring-2 ring-cyan-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30",
    hover: "hover:bg-cyan-500/20 hover:border-cyan-500/50",
  },
  yellow: {
    active: "bg-yellow-500 text-black shadow-lg shadow-yellow-500/30 ring-2 ring-yellow-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-yellow-500/10 text-yellow-400 border border-yellow-500/30",
    hover: "hover:bg-yellow-500/20 hover:border-yellow-500/50",
  },
  green: {
    active: "bg-green-500 text-white shadow-lg shadow-green-500/30 ring-2 ring-green-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-green-500/10 text-green-400 border border-green-500/30",
    hover: "hover:bg-green-500/20 hover:border-green-500/50",
  },
  emerald: {
    active: "bg-emerald-500 text-white shadow-lg shadow-emerald-500/30 ring-2 ring-emerald-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30",
    hover: "hover:bg-emerald-500/20 hover:border-emerald-500/50",
  },
  pink: {
    active: "bg-pink-500 text-white shadow-lg shadow-pink-500/30 ring-2 ring-pink-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-pink-500/10 text-pink-400 border border-pink-500/30",
    hover: "hover:bg-pink-500/20 hover:border-pink-500/50",
  },
  red: {
    active: "bg-red-500 text-white shadow-lg shadow-red-500/30 ring-2 ring-red-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-red-500/10 text-red-400 border border-red-500/30",
    hover: "hover:bg-red-500/20 hover:border-red-500/50",
  },
  orange: {
    active: "bg-orange-500 text-white shadow-lg shadow-orange-500/30 ring-2 ring-orange-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-orange-500/10 text-orange-400 border border-orange-500/30",
    hover: "hover:bg-orange-500/20 hover:border-orange-500/50",
  },
  gray: {
    active: "bg-gray-500 text-white shadow-lg shadow-gray-500/30 ring-2 ring-gray-400 ring-offset-2 ring-offset-[#111111]",
    inactive: "bg-gray-500/10 text-gray-400 border border-gray-500/30",
    hover: "hover:bg-gray-500/20 hover:border-gray-500/50",
  },
};

export function StatusPipeline({ currentStatus, onStatusChange, disabled }: StatusPipelineProps) {
  const handleStatusClick = (status: string, canUncheck: boolean) => {
    if (disabled) return;

    const isActive = currentStatus === status;

    if (isActive && canUncheck) {
      // Clicking active status in a group that allows unchecking reverts to "saved"
      onStatusChange("saved");
    } else if (!isActive) {
      // Clicking inactive status selects it
      onStatusChange(status);
    }
    // If active and can't uncheck (Pre-Apply), do nothing
  };

  const renderButton = (status: string, canUncheck: boolean) => {
    const config = statusConfig[status];
    const colors = colorClasses[config.color];
    const isActive = currentStatus === status;

    return (
      <button
        key={status}
        onClick={() => handleStatusClick(status, canUncheck)}
        disabled={disabled}
        className={`
          px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200
          ${isActive ? colors.active : `${colors.inactive} ${colors.hover}`}
          ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
          active:scale-95
        `}
      >
        {config.label}
      </button>
    );
  };

  return (
    <div className="space-y-4">
      {statusGroups.map((group) => (
        <div key={group.label}>
          <p className="text-[10px] uppercase tracking-[0.15em] text-[var(--color-text-tertiary)] mb-2 font-semibold">
            {group.label}
          </p>
          <div className="flex flex-wrap gap-2">
            {group.statuses.map((status) => renderButton(status, group.canUncheck))}
          </div>
        </div>
      ))}

      {/* Archived - separate section, can uncheck */}
      <div className="pt-3 border-t border-[var(--color-border-subtle)]">
        {renderButton("archived", true)}
      </div>
    </div>
  );
}
