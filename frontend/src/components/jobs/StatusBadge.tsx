import { clsx } from "clsx";

const statusColors: Record<string, string> = {
  saved: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  researching: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  ready_to_apply: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  applying: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  applied: "bg-green-500/10 text-green-400 border-green-500/20",
  interviewing: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  offer: "bg-pink-500/10 text-pink-400 border-pink-500/20",
  rejected: "bg-red-500/10 text-red-400 border-red-500/20",
  withdrawn: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  archived: "bg-gray-500/10 text-gray-400 border-gray-500/20",
};

const statusLabels: Record<string, string> = {
  saved: "Saved",
  researching: "Researching",
  ready_to_apply: "Ready to Apply",
  applying: "Applying",
  applied: "Applied",
  interviewing: "Interviewing",
  offer: "Offer",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
  archived: "Archived",
};

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const colorClass = statusColors[status] || statusColors.saved;
  const label = statusLabels[status] || status;

  return (
    <span
      className={clsx(
        "inline-flex px-2 py-1 text-xs font-medium rounded-full border",
        colorClass
      )}
    >
      {label}
    </span>
  );
}
