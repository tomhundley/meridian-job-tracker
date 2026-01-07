"use client";

import { useState, useMemo } from "react";
import { Sparkles, ChevronDown, ChevronRight, CheckCircle, XCircle, MinusCircle } from "lucide-react";

import type { NoteEntry, NoteType, GroupedNotes } from "@/types/notes";
import { isAnalysisNote, groupNotesByType, ANALYSIS_NOTE_TYPES } from "@/types/notes";
import { getAnalysisNoteTypeConfigs, getNoteTypeConfig } from "./noteTypeConfig";
import { NoteTypeSection } from "./NoteTypeSection";
import { AnalysisNoteCard } from "./AnalysisNoteCard";

interface AnalysisInsightsPanelProps {
  jobId: string;
  notes: NoteEntry[] | null;
  priority?: number;
  isAiForward?: boolean;
}

/**
 * Get recommendation badge based on metadata.
 */
function getRecommendationBadge(metadata?: NoteEntry["metadata"]): {
  icon: React.ElementType;
  label: string;
  colorClass: string;
} | null {
  if (!metadata?.recommendation) return null;

  const recommendation = metadata.recommendation.toUpperCase();

  if (recommendation.includes("STRONG") || recommendation === "APPLY") {
    return {
      icon: CheckCircle,
      label: recommendation,
      colorClass: "text-green-400 bg-green-500/10 border-green-500/20",
    };
  }
  if (recommendation.includes("SKIP") || recommendation.includes("PASS")) {
    return {
      icon: XCircle,
      label: recommendation,
      colorClass: "text-red-400 bg-red-500/10 border-red-500/20",
    };
  }
  return {
    icon: MinusCircle,
    label: recommendation,
    colorClass: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
  };
}

/**
 * Main panel for displaying analysis insights grouped by type.
 */
export function AnalysisInsightsPanel({
  notes,
  priority,
  isAiForward,
}: AnalysisInsightsPanelProps) {
  // Filter to only analysis notes
  const analysisNotes = useMemo(() => {
    if (!notes) return [];
    return notes.filter(isAnalysisNote);
  }, [notes]);

  // Group notes by type
  const groupedNotes = useMemo(() => groupNotesByType(analysisNotes), [analysisNotes]);

  // Track which sections are expanded
  const [expandedSections, setExpandedSections] = useState<Set<NoteType>>(
    new Set(["ai_analysis_summary"])
  );

  // Track if entire panel is collapsed
  const [isPanelExpanded, setIsPanelExpanded] = useState(true);

  // Get config for note types that have notes
  const noteTypeConfigs = getAnalysisNoteTypeConfigs();

  // Get the summary note (special treatment)
  const summaryNote = groupedNotes.ai_analysis_summary?.[0];
  const summaryConfig = getNoteTypeConfig("ai_analysis_summary");

  // Get other note types that have notes
  const otherNoteTypes = noteTypeConfigs.filter(
    (config) =>
      config.type !== "ai_analysis_summary" &&
      groupedNotes[config.type] &&
      groupedNotes[config.type]!.length > 0
  );

  // Count total insights
  const totalInsights = analysisNotes.length;

  // Toggle a section
  const toggleSection = (type: NoteType) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  };

  // Expand/collapse all
  const toggleAll = () => {
    if (expandedSections.size === 0) {
      // Expand all
      setExpandedSections(new Set(ANALYSIS_NOTE_TYPES));
    } else {
      // Collapse all except summary
      setExpandedSections(new Set(["ai_analysis_summary"]));
    }
  };

  // If no analysis notes, show empty state
  if (analysisNotes.length === 0) {
    return (
      <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
        <div className="flex items-center gap-2 mb-4">
          <Sparkles size={20} className="text-[var(--color-text-tertiary)]" />
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
            Analysis Insights
          </h2>
        </div>
        <p className="text-sm text-[var(--color-text-tertiary)] text-center py-4">
          No analysis insights yet. Run analysis with apply_suggestions=true to generate insights.
        </p>
      </div>
    );
  }

  const recommendationBadge = summaryNote ? getRecommendationBadge(summaryNote.metadata) : null;

  return (
    <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] overflow-hidden">
      {/* Panel Header */}
      <div
        className="flex items-center justify-between p-4 border-b border-[var(--color-border-subtle)] cursor-pointer hover:bg-[var(--color-bg-elevated)] transition-colors"
        onClick={() => setIsPanelExpanded(!isPanelExpanded)}
      >
        <div className="flex items-center gap-3">
          <Sparkles size={20} className="text-purple-400" />
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
            Analysis Insights
          </h2>
          <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
            {totalInsights} {totalInsights === 1 ? "insight" : "insights"}
          </span>
          {recommendationBadge && (
            <span
              className={`text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 ${recommendationBadge.colorClass}`}
            >
              <recommendationBadge.icon size={12} />
              {recommendationBadge.label}
            </span>
          )}
          {priority !== undefined && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              Score: {priority}/100
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {isPanelExpanded && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                toggleAll();
              }}
              className="text-xs text-[var(--color-text-tertiary)] hover:text-[var(--color-text-secondary)] transition-colors"
            >
              {expandedSections.size <= 1 ? "Expand all" : "Collapse all"}
            </button>
          )}
          {isPanelExpanded ? (
            <ChevronDown size={20} className="text-[var(--color-text-tertiary)]" />
          ) : (
            <ChevronRight size={20} className="text-[var(--color-text-tertiary)]" />
          )}
        </div>
      </div>

      {/* Panel Content */}
      {isPanelExpanded && (
        <div className="p-4 space-y-4">
          {/* Summary Card (always first, special styling) */}
          {summaryNote && (
            <div
              className={`rounded-lg border ${summaryConfig.borderClass} ${summaryConfig.bgClass} p-4`}
            >
              <div className="flex items-center gap-2 mb-3">
                <summaryConfig.icon size={18} className={summaryConfig.iconColorClass} />
                <span className="text-sm font-semibold text-[var(--color-text-primary)]">
                  {summaryConfig.label}
                </span>
                {summaryNote.metadata?.priority_score !== undefined && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-medium">
                    {summaryNote.metadata.priority_score}/100
                  </span>
                )}
                {summaryNote.metadata?.ai_forward && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400 border border-purple-500/30">
                    AI-Forward
                  </span>
                )}
                {summaryNote.metadata?.suggested_role && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                    {summaryNote.metadata.suggested_role.toUpperCase()}
                  </span>
                )}
              </div>
              <AnalysisNoteCard note={summaryNote} config={summaryConfig} showHeader={false} />
            </div>
          )}

          {/* Other Note Type Sections */}
          {otherNoteTypes.map((config) => (
            <NoteTypeSection
              key={config.type}
              config={config}
              notes={groupedNotes[config.type] || []}
              isExpanded={expandedSections.has(config.type)}
              onToggle={() => toggleSection(config.type)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
