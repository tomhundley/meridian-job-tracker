"use client";

import { useParams, useRouter } from "next/navigation";
import useSWR, { mutate } from "swr";
import Link from "next/link";
import { useState } from "react";
import { ArrowLeft, ExternalLink, Trash2, FileText, Clock } from "lucide-react";
import { StatusBadge } from "@/components/jobs/StatusBadge";
import { toast } from "sonner";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

const statuses = [
  "saved",
  "researching",
  "ready_to_apply",
  "applying",
  "applied",
  "interviewing",
  "offer",
  "rejected",
  "withdrawn",
  "archived",
];

const roleTypes = [
  { value: "cto", label: "CTO" },
  { value: "vp", label: "VP Engineering" },
  { value: "director", label: "Director" },
  { value: "architect", label: "Architect" },
  { value: "developer", label: "Developer" },
];

interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  url: string | null;
  description_raw: string | null;
  status: string;
  target_role: string | null;
  priority: number;
  notes: string | null;
  tags: string[];
  applied_at: string | null;
  created_at: string;
  updated_at: string;
}

interface CoverLetter {
  id: string;
  content: string;
  target_role: string;
  is_approved: boolean;
  created_at: string;
}

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const { data: job, error, isLoading } = useSWR<Job>(`/api/jobs/${id}`, fetcher);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [editingNotes, setEditingNotes] = useState(false);
  const [notes, setNotes] = useState("");
  const [coverLetters, setCoverLetters] = useState<CoverLetter[]>([]);

  if (isLoading) {
    return (
      <div className="text-center py-12 text-[var(--color-text-tertiary)]">
        Loading job details...
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="text-center py-12 text-red-400">
        Failed to load job details
      </div>
    );
  }

  const handleStatusChange = async (newStatus: string) => {
    setIsUpdating(true);
    try {
      const response = await fetch(`/api/jobs/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        mutate(`/api/jobs/${id}`);
        mutate("/api/jobs");
        toast.success("Status updated");
      } else {
        toast.error("Failed to update status");
      }
    } catch (error) {
      toast.error("Failed to update status");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleUpdateJob = async (updates: Partial<Job>) => {
    setIsUpdating(true);
    try {
      const response = await fetch(`/api/jobs/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        mutate(`/api/jobs/${id}`);
        toast.success("Job updated");
      } else {
        toast.error("Failed to update job");
      }
    } catch (error) {
      toast.error("Failed to update job");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this job?")) return;

    try {
      const response = await fetch(`/api/jobs/${id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast.success("Job deleted");
        router.push("/dashboard");
      } else {
        toast.error("Failed to delete job");
      }
    } catch (error) {
      toast.error("Failed to delete job");
    }
  };

  const handleGenerateCoverLetter = async (targetRole: string) => {
    setIsGenerating(true);
    try {
      const response = await fetch(`/api/jobs/${id}/cover-letter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_role: targetRole }),
      });

      if (response.ok) {
        const newLetter = await response.json();
        setCoverLetters([...coverLetters, newLetter]);
        toast.success("Cover letter generated");
      } else {
        toast.error("Failed to generate cover letter");
      }
    } catch (error) {
      toast.error("Failed to generate cover letter");
    } finally {
      setIsGenerating(false);
    }
  };

  const saveNotes = async () => {
    await handleUpdateJob({ notes });
    setEditingNotes(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/dashboard"
            className="p-2 hover:bg-[var(--color-bg-secondary)] rounded-lg transition-colors"
          >
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold">{job.title}</h1>
            <p className="text-[var(--color-text-secondary)]">{job.company}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-[var(--color-bg-secondary)] rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors"
            >
              <ExternalLink size={16} />
              View Posting
            </a>
          )}
          <button
            onClick={handleDelete}
            className="p-2 text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
          >
            <Trash2 size={20} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* Status & Details Card */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h2 className="text-lg font-semibold mb-4">Details</h2>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                  Status
                </label>
                <select
                  value={job.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  disabled={isUpdating}
                  className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                >
                  {statuses.map((s) => (
                    <option key={s} value={s}>
                      {s.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                  Target Role
                </label>
                <select
                  value={job.target_role || ""}
                  onChange={(e) => handleUpdateJob({ target_role: e.target.value || null })}
                  disabled={isUpdating}
                  className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                >
                  <option value="">Select role...</option>
                  {roleTypes.map((r) => (
                    <option key={r.value} value={r.value}>
                      {r.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                  Location
                </label>
                <p className="px-3 py-2">{job.location || "-"}</p>
              </div>

              <div>
                <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                  Priority
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={job.priority}
                  onChange={(e) => handleUpdateJob({ priority: parseInt(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-[var(--color-text-tertiary)]">
                  <span>Low</span>
                  <span>{job.priority}</span>
                  <span>High</span>
                </div>
              </div>
            </div>
          </div>

          {/* Job Description */}
          {job.description_raw && (
            <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
              <h2 className="text-lg font-semibold mb-4">Job Description</h2>
              <div className="prose prose-invert max-w-none text-sm whitespace-pre-wrap">
                {job.description_raw}
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Notes</h2>
              {!editingNotes && (
                <button
                  onClick={() => {
                    setNotes(job.notes || "");
                    setEditingNotes(true);
                  }}
                  className="text-sm text-[var(--color-accent)] hover:underline"
                >
                  Edit
                </button>
              )}
            </div>

            {editingNotes ? (
              <div className="space-y-3">
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={6}
                  className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                  placeholder="Add notes about this job..."
                />
                <div className="flex gap-2">
                  <button
                    onClick={saveNotes}
                    disabled={isUpdating}
                    className="px-4 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setEditingNotes(false)}
                    className="px-4 py-2 bg-[var(--color-bg-elevated)] rounded-lg hover:opacity-90 transition-opacity"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <p className="text-[var(--color-text-secondary)] whitespace-pre-wrap">
                {job.notes || "No notes yet."}
              </p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Info */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h2 className="text-lg font-semibold mb-4">Timeline</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Clock size={16} className="text-[var(--color-text-tertiary)]" />
                <span className="text-[var(--color-text-tertiary)]">Added:</span>
                <span>{new Date(job.created_at).toLocaleDateString()}</span>
              </div>
              {job.applied_at && (
                <div className="flex items-center gap-2 text-sm">
                  <Clock size={16} className="text-green-400" />
                  <span className="text-[var(--color-text-tertiary)]">Applied:</span>
                  <span>{new Date(job.applied_at).toLocaleDateString()}</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-sm">
                <Clock size={16} className="text-[var(--color-text-tertiary)]" />
                <span className="text-[var(--color-text-tertiary)]">Updated:</span>
                <span>{new Date(job.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          {/* Cover Letter Generation */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h2 className="text-lg font-semibold mb-4">Cover Letter</h2>

            <div className="space-y-3">
              <select
                id="coverLetterRole"
                defaultValue={job.target_role || ""}
                className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
              >
                <option value="">Select target role...</option>
                {roleTypes.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>

              <button
                onClick={() => {
                  const select = document.getElementById("coverLetterRole") as HTMLSelectElement;
                  if (select.value) {
                    handleGenerateCoverLetter(select.value);
                  } else {
                    toast.error("Please select a target role");
                  }
                }}
                disabled={isGenerating || !job.description_raw}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
              >
                <FileText size={16} />
                {isGenerating ? "Generating..." : "Generate Cover Letter"}
              </button>

              {!job.description_raw && (
                <p className="text-xs text-[var(--color-text-tertiary)]">
                  Add a job description to generate a cover letter.
                </p>
              )}
            </div>

            {coverLetters.length > 0 && (
              <div className="mt-4 space-y-3">
                {coverLetters.map((letter) => (
                  <div
                    key={letter.id}
                    className="p-3 bg-[var(--color-bg-elevated)] rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">
                        {roleTypes.find((r) => r.value === letter.target_role)?.label}
                      </span>
                      <span className="text-xs text-[var(--color-text-tertiary)]">
                        {new Date(letter.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-[var(--color-text-secondary)] line-clamp-3">
                      {letter.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Tags */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h2 className="text-lg font-semibold mb-4">Tags</h2>
            {job.tags && job.tags.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {job.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 text-xs bg-[var(--color-bg-elevated)] rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--color-text-tertiary)]">No tags</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
