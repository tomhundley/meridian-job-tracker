"use client";

import { useState } from "react";
import { mutate } from "swr";
import { toast } from "sonner";
import { Bot, User, Send } from "lucide-react";

interface NoteEntry {
  text: string;
  timestamp: string;
  source: "user" | "agent";
  note_type?: string;
}

/**
 * Check if a note is a user note (should be shown in JobNotes component).
 * User notes are: source === "user" OR note_type is "general" or undefined.
 * Analysis notes (source === "agent" with specific note_type) are shown in AnalysisInsightsPanel.
 */
function isUserNote(note: NoteEntry): boolean {
  // User-created notes always show
  if (note.source === "user") return true;
  // General notes or notes without type show here
  if (!note.note_type || note.note_type === "general") return true;
  // Agent notes with specific analysis types go to AnalysisInsightsPanel
  return false;
}

interface JobNotesProps {
  jobId: string;
  notes: NoteEntry[] | null;
}

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

export function JobNotes({ jobId, notes }: JobNotesProps) {
  const [newNote, setNewNote] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAddNote = async () => {
    if (!newNote.trim()) return;

    setIsSubmitting(true);
    try {
      const response = await fetch(`/api/jobs/${jobId}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: newNote.trim(),
          source: "user",
        }),
      });

      if (response.ok) {
        setNewNote("");
        mutate(`/api/jobs/${jobId}`);
        toast.success("Note added");
      } else {
        toast.error("Failed to add note");
      }
    } catch (error) {
      toast.error("Failed to add note");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAddNote();
    }
  };

  // Filter to only user notes (analysis notes shown in AnalysisInsightsPanel)
  const sortedNotes = notes
    ? [...notes]
        .filter(isUserNote)
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    : [];

  return (
    <div className="space-y-4">
      {/* Add Note Input */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <textarea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Add a note..."
            rows={2}
            className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] text-sm resize-none"
          />
        </div>
        <button
          onClick={handleAddNote}
          disabled={isSubmitting || !newNote.trim()}
          className="px-3 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed self-end"
          title="Add note"
        >
          <Send size={16} />
        </button>
      </div>

      {/* Notes List */}
      {sortedNotes.length > 0 ? (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {sortedNotes.map((note, index) => (
            <div
              key={`${note.timestamp}-${index}`}
              className={`p-3 rounded-lg ${
                note.source === "agent"
                  ? "bg-blue-500/10 border border-blue-500/20"
                  : "bg-[var(--color-bg-elevated)]"
              }`}
            >
              <div className="flex items-center gap-2 mb-2">
                {note.source === "agent" ? (
                  <Bot size={14} className="text-blue-400" />
                ) : (
                  <User size={14} className="text-[var(--color-text-tertiary)]" />
                )}
                <span className="text-xs font-medium text-[var(--color-text-secondary)]">
                  {note.source === "agent" ? "Agent" : "You"}
                </span>
                <span className="text-xs text-[var(--color-text-tertiary)]">
                  {formatTimestamp(note.timestamp)}
                </span>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)] whitespace-pre-wrap">
                {note.text}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-[var(--color-text-tertiary)] text-center py-4">
          No notes yet. Add one above!
        </p>
      )}
    </div>
  );
}
