/**
 * Configuration for note type display in AnalysisInsightsPanel.
 */

import {
  ClipboardCheck,
  ThumbsUp,
  MessageSquare,
  Lightbulb,
  GraduationCap,
  AlertTriangle,
  FileSearch,
  FileText,
} from "lucide-react";

import type { NoteType, NoteTypeConfig } from "@/types/notes";

/**
 * Configuration for each note type's visual appearance.
 */
export const noteTypeConfigs: Record<NoteType, NoteTypeConfig> = {
  ai_analysis_summary: {
    type: "ai_analysis_summary",
    label: "Analysis Summary",
    icon: ClipboardCheck,
    colorClass: "text-emerald-400",
    bgClass: "bg-emerald-500/10",
    borderClass: "border-emerald-500/20",
    iconColorClass: "text-emerald-400",
    description: "Overall fit assessment and recommendation",
    order: 1,
  },
  strengths: {
    type: "strengths",
    label: "Key Strengths",
    icon: ThumbsUp,
    colorClass: "text-green-400",
    bgClass: "bg-green-500/10",
    borderClass: "border-green-500/20",
    iconColorClass: "text-green-400",
    description: "Strengths to highlight in application",
    order: 2,
  },
  talking_points: {
    type: "talking_points",
    label: "Interview Talking Points",
    icon: MessageSquare,
    colorClass: "text-blue-400",
    bgClass: "bg-blue-500/10",
    borderClass: "border-blue-500/20",
    iconColorClass: "text-blue-400",
    description: "Points to discuss in interviews",
    order: 3,
  },
  coaching_notes: {
    type: "coaching_notes",
    label: "Application Coaching",
    icon: Lightbulb,
    colorClass: "text-purple-400",
    bgClass: "bg-purple-500/10",
    borderClass: "border-purple-500/20",
    iconColorClass: "text-purple-400",
    description: "What to emphasize in applications",
    order: 4,
  },
  study_recommendations: {
    type: "study_recommendations",
    label: "Study Recommendations",
    icon: GraduationCap,
    colorClass: "text-amber-400",
    bgClass: "bg-amber-500/10",
    borderClass: "border-amber-500/20",
    iconColorClass: "text-amber-400",
    description: "Skills and topics to review",
    order: 5,
  },
  watch_outs: {
    type: "watch_outs",
    label: "Watch-Outs",
    icon: AlertTriangle,
    colorClass: "text-orange-400",
    bgClass: "bg-orange-500/10",
    borderClass: "border-orange-500/20",
    iconColorClass: "text-orange-400",
    description: "Potential concerns or red flags",
    order: 6,
  },
  rag_evidence: {
    type: "rag_evidence",
    label: "Career Evidence",
    icon: FileSearch,
    colorClass: "text-cyan-400",
    bgClass: "bg-cyan-500/10",
    borderClass: "border-cyan-500/20",
    iconColorClass: "text-cyan-400",
    description: "Evidence from career documents",
    order: 7,
  },
  general: {
    type: "general",
    label: "General Notes",
    icon: FileText,
    colorClass: "text-gray-400",
    bgClass: "bg-gray-500/10",
    borderClass: "border-gray-500/20",
    iconColorClass: "text-gray-400",
    description: "General notes and comments",
    order: 99,
  },
};

/**
 * Get sorted note type configs for analysis notes only (excludes general).
 */
export function getAnalysisNoteTypeConfigs(): NoteTypeConfig[] {
  return Object.values(noteTypeConfigs)
    .filter((config) => config.type !== "general")
    .sort((a, b) => a.order - b.order);
}

/**
 * Get config for a specific note type.
 */
export function getNoteTypeConfig(type: NoteType): NoteTypeConfig {
  return noteTypeConfigs[type] || noteTypeConfigs.general;
}
