"use client";

import { Heart, Target, Sparkles, Zap } from "lucide-react";

interface JobFlagsToggleProps {
  isFavorite: boolean;
  isPerfectFit: boolean;
  isAiForward: boolean;
  isEasyApply: boolean;
  onToggle: (flag: string, value: boolean) => void;
  disabled?: boolean;
}

export function JobFlagsToggle({
  isFavorite,
  isPerfectFit,
  isAiForward,
  isEasyApply,
  onToggle,
  disabled,
}: JobFlagsToggleProps) {
  const flags = [
    {
      key: "is_favorite",
      label: "Favorite",
      Icon: Heart,
      isActive: isFavorite,
      activeClasses: "bg-red-500/20 border-red-500 text-red-400 shadow-lg shadow-red-500/20",
      hoverClasses: "hover:border-red-500/50 hover:text-red-400/70 hover:bg-red-500/5",
      fillWhenActive: true,
    },
    {
      key: "is_perfect_fit",
      label: "Perfect Fit",
      Icon: Target,
      isActive: isPerfectFit,
      activeClasses: "bg-purple-500/20 border-purple-500 text-purple-400 shadow-lg shadow-purple-500/20",
      hoverClasses: "hover:border-purple-500/50 hover:text-purple-400/70 hover:bg-purple-500/5",
    },
    {
      key: "is_ai_forward",
      label: "AI Forward",
      Icon: Sparkles,
      isActive: isAiForward,
      activeClasses: "bg-cyan-500/20 border-cyan-500 text-cyan-400 shadow-lg shadow-cyan-500/20",
      hoverClasses: "hover:border-cyan-500/50 hover:text-cyan-400/70 hover:bg-cyan-500/5",
    },
    {
      key: "is_easy_apply",
      label: "Easy Apply",
      Icon: Zap,
      isActive: isEasyApply,
      activeClasses: "bg-green-500/20 border-green-500 text-green-400 shadow-lg shadow-green-500/20",
      hoverClasses: "hover:border-green-500/50 hover:text-green-400/70 hover:bg-green-500/5",
    },
  ];

  return (
    <div className="flex flex-wrap gap-3">
      {flags.map((flag) => {
        const { Icon, isActive, activeClasses, hoverClasses, fillWhenActive } = flag;

        return (
          <button
            key={flag.key}
            onClick={() => !disabled && onToggle(flag.key, !isActive)}
            disabled={disabled}
            className={`
              flex flex-col items-center gap-2 px-5 py-4 rounded-xl
              border-2 min-w-[90px] transition-all duration-200
              ${isActive
                ? activeClasses
                : `bg-[var(--color-bg-elevated)] border-[var(--color-border-subtle)] text-[var(--color-text-tertiary)] ${hoverClasses}`
              }
              ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
              active:scale-95
            `}
          >
            <Icon
              size={26}
              className={`transition-all duration-200 ${isActive && fillWhenActive ? "fill-current" : ""}`}
            />
            <span className="text-xs font-semibold tracking-wide">{flag.label}</span>
          </button>
        );
      })}
    </div>
  );
}
