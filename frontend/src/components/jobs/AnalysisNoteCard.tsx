"use client";

import type { NoteEntry, NoteTypeConfig } from "@/types/notes";

interface AnalysisNoteCardProps {
  note: NoteEntry;
  config: NoteTypeConfig;
  showHeader?: boolean;
}

/**
 * Format timestamp for display.
 */
function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return `Today at ${date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  }
  if (diffDays === 1) {
    return `Yesterday at ${date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}`;
  }
  if (diffDays < 7) {
    return `${diffDays} days ago`;
  }
  return date.toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" });
}

/**
 * Parse simple markdown bold (**text**) to styled spans.
 */
function parseMarkdownBold(text: string): React.ReactNode[] {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <span key={i} className="font-semibold text-[var(--color-text-primary)]">
          {part.slice(2, -2)}
        </span>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

/**
 * Displays a single analysis note with optional header.
 */
export function AnalysisNoteCard({ note, config, showHeader = false }: AnalysisNoteCardProps) {
  const Icon = config.icon;

  return (
    <div className="py-2">
      {showHeader && (
        <div className="flex items-center gap-2 mb-2">
          <Icon size={14} className={config.iconColorClass} />
          <span className="text-xs font-medium text-[var(--color-text-secondary)]">
            {config.label}
          </span>
          <span className="text-xs text-[var(--color-text-tertiary)]">
            {formatTimestamp(note.timestamp)}
          </span>
        </div>
      )}
      <div className="text-sm text-[var(--color-text-secondary)] whitespace-pre-wrap leading-relaxed">
        {parseMarkdownBold(note.text)}
      </div>
      {!showHeader && (
        <div className="mt-2 text-xs text-[var(--color-text-tertiary)]">
          {formatTimestamp(note.timestamp)}
        </div>
      )}
    </div>
  );
}
