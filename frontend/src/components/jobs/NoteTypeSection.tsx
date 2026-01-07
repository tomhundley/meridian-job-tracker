"use client";

import { ChevronDown, ChevronRight } from "lucide-react";

import type { NoteEntry, NoteTypeConfig } from "@/types/notes";
import { AnalysisNoteCard } from "./AnalysisNoteCard";

interface NoteTypeSectionProps {
  config: NoteTypeConfig;
  notes: NoteEntry[];
  isExpanded: boolean;
  onToggle: () => void;
}

/**
 * Collapsible section for a specific note type.
 */
export function NoteTypeSection({ config, notes, isExpanded, onToggle }: NoteTypeSectionProps) {
  const Icon = config.icon;

  if (notes.length === 0) {
    return null;
  }

  return (
    <div className={`rounded-lg border ${config.borderClass} overflow-hidden`}>
      {/* Section Header */}
      <button
        onClick={onToggle}
        className={`w-full flex items-center justify-between p-3 ${config.bgClass} hover:opacity-90 transition-opacity cursor-pointer`}
      >
        <div className="flex items-center gap-2">
          <Icon size={16} className={config.iconColorClass} />
          <span className="text-sm font-medium text-[var(--color-text-primary)]">
            {config.label}
          </span>
          <span
            className={`text-xs px-2 py-0.5 rounded-full ${config.bgClass} ${config.colorClass} border ${config.borderClass}`}
          >
            {notes.length}
          </span>
        </div>
        {isExpanded ? (
          <ChevronDown size={16} className="text-[var(--color-text-tertiary)]" />
        ) : (
          <ChevronRight size={16} className="text-[var(--color-text-tertiary)]" />
        )}
      </button>

      {/* Section Content */}
      {isExpanded && (
        <div className="px-4 py-2 bg-[var(--color-bg-secondary)] divide-y divide-[var(--color-border-subtle)]">
          {notes.map((note, index) => (
            <AnalysisNoteCard
              key={`${note.timestamp}-${index}`}
              note={note}
              config={config}
              showHeader={false}
            />
          ))}
        </div>
      )}
    </div>
  );
}
