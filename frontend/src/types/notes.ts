/**
 * TypeScript types for job notes system.
 * Mirrors backend schemas in backend/src/schemas/job_note.py
 */

import { type LucideIcon } from "lucide-react";

/**
 * Source of a note - who created it.
 */
export type NoteSource = "user" | "agent";

/**
 * Type of note for categorization.
 * Matches backend NoteType enum.
 */
export type NoteType =
  | "general"
  | "ai_analysis_summary"
  | "coaching_notes"
  | "talking_points"
  | "study_recommendations"
  | "strengths"
  | "watch_outs"
  | "rag_evidence";

/**
 * Analysis note types (excludes general).
 * These are displayed in the AnalysisInsightsPanel.
 */
export const ANALYSIS_NOTE_TYPES: NoteType[] = [
  "ai_analysis_summary",
  "strengths",
  "talking_points",
  "coaching_notes",
  "study_recommendations",
  "watch_outs",
  "rag_evidence",
];

/**
 * Metadata that may be attached to notes.
 * Different note types have different metadata.
 */
export interface NoteMetadata {
  // ai_analysis_summary metadata
  priority_score?: number;
  recommendation?: string;
  ai_forward?: boolean;
  suggested_role?: string;

  // rag_evidence metadata
  evidence_count?: number;
  strong_count?: number;
  gap_count?: number;

  // watch_outs metadata
  location_incompatible?: boolean;

  // Allow additional fields
  [key: string]: unknown;
}

/**
 * Single note entry in the notes array.
 * Extended version of backend JobNoteEntry.
 */
export interface NoteEntry {
  text: string;
  timestamp: string;
  source: NoteSource;
  note_type?: NoteType;
  metadata?: NoteMetadata | null;
}

/**
 * Configuration for displaying a note type.
 */
export interface NoteTypeConfig {
  type: NoteType;
  label: string;
  icon: LucideIcon;
  colorClass: string;
  bgClass: string;
  borderClass: string;
  iconColorClass: string;
  description: string;
  order: number;
}

/**
 * Grouped notes by type.
 */
export type GroupedNotes = {
  [K in NoteType]?: NoteEntry[];
};

/**
 * Helper to check if a note is an analysis note (not general/user).
 */
export function isAnalysisNote(note: NoteEntry): boolean {
  return (
    note.source === "agent" &&
    note.note_type !== undefined &&
    note.note_type !== "general" &&
    ANALYSIS_NOTE_TYPES.includes(note.note_type)
  );
}

/**
 * Helper to check if a note is a user note or general note.
 */
export function isUserNote(note: NoteEntry): boolean {
  return note.source === "user" || note.note_type === "general" || note.note_type === undefined;
}

/**
 * Group notes by their type.
 */
export function groupNotesByType(notes: NoteEntry[]): GroupedNotes {
  const grouped: GroupedNotes = {};

  for (const note of notes) {
    const noteType = note.note_type || "general";
    if (!grouped[noteType]) {
      grouped[noteType] = [];
    }
    grouped[noteType]!.push(note);
  }

  // Sort notes within each group by timestamp (newest first)
  for (const type of Object.keys(grouped) as NoteType[]) {
    grouped[type]!.sort(
      (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
  }

  return grouped;
}
