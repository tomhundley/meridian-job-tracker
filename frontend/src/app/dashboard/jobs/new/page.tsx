"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";

const roleTypes = [
  { value: "", label: "Select role..." },
  { value: "cto", label: "CTO" },
  { value: "vp", label: "VP Engineering" },
  { value: "director", label: "Director" },
  { value: "architect", label: "Architect" },
  { value: "developer", label: "Developer" },
];

const sourceTypes = [
  { value: "", label: "Auto-detect" },
  { value: "linkedin", label: "LinkedIn" },
  { value: "indeed", label: "Indeed" },
  { value: "greenhouse", label: "Greenhouse" },
  { value: "lever", label: "Lever" },
  { value: "workday", label: "Workday" },
];

export default function NewJobPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);

  const [ingestData, setIngestData] = useState({
    url: "",
    source: "",
    notes: "",
  });

  const [formData, setFormData] = useState({
    title: "",
    company: "",
    location: "",
    url: "",
    description_raw: "",
    target_role: "",
    priority: 50,
    notes: "",
  });

  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!ingestData.url) {
      toast.error("Job URL is required");
      return;
    }

    setIsIngesting(true);

    try {
      const response = await fetch("/api/jobs/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: ingestData.url,
          source: ingestData.source || null,
          notes: ingestData.notes || null,
        }),
      });

      const data = await response.json().catch(() => null);

      if (response.ok && data) {
        toast.success("Job imported");
        router.push(`/dashboard/jobs/${data.id}`);
      } else {
        const message =
          data?.detail || data?.error || "Failed to import job";
        toast.error(message);
      }
    } catch (error) {
      toast.error("Failed to import job");
    } finally {
      setIsIngesting(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title || !formData.company) {
      toast.error("Title and company are required");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await fetch("/api/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          target_role: formData.target_role || null,
          location: formData.location || null,
          url: formData.url || null,
          description_raw: formData.description_raw || null,
          notes: formData.notes || null,
        }),
      });

      if (response.ok) {
        const job = await response.json();
        toast.success("Job created");
        router.push(`/dashboard/jobs/${job.id}`);
      } else {
        toast.error("Failed to create job");
      }
    } catch (error) {
      toast.error("Failed to create job");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/dashboard"
          className="p-2 hover:bg-[var(--color-bg-secondary)] rounded-lg transition-colors"
        >
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold">Add New Job</h1>
      </div>

      <form onSubmit={handleIngest} className="space-y-4">
        <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6 space-y-4">
          <div>
            <h2 className="text-lg font-semibold">Import from URL</h2>
            <p className="text-sm text-[var(--color-text-tertiary)]">
              Paste a job posting URL and we will create the job automatically.
            </p>
          </div>

          <div>
            <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
              Job URL *
            </label>
            <input
              type="url"
              value={ingestData.url}
              onChange={(e) => setIngestData({ ...ingestData, url: e.target.value })}
              className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
              placeholder="https://linkedin.com/jobs/view/123456"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                Source
              </label>
              <select
                value={ingestData.source}
                onChange={(e) => setIngestData({ ...ingestData, source: e.target.value })}
                className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
              >
                {sourceTypes.map((source) => (
                  <option key={source.value} value={source.value}>
                    {source.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                Notes
              </label>
              <input
                type="text"
                value={ingestData.notes}
                onChange={(e) => setIngestData({ ...ingestData, notes: e.target.value })}
                className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                placeholder="Referred by John"
              />
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={isIngesting}
            className="px-6 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {isIngesting ? "Importing..." : "Import Job"}
          </button>
          <Link
            href="/dashboard"
            className="px-6 py-2 bg-[var(--color-bg-secondary)] rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors"
          >
            Cancel
          </Link>
        </div>
      </form>

      <div className="flex items-center gap-3 text-[var(--color-text-tertiary)] text-sm">
        <span className="h-px flex-1 bg-[var(--color-border-subtle)]" />
        Or add manually
        <span className="h-px flex-1 bg-[var(--color-border-subtle)]" />
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                Job Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                placeholder="Senior Software Engineer"
                required
              />
            </div>

            <div>
              <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                Company *
              </label>
              <input
                type="text"
                value={formData.company}
                onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                placeholder="Acme Corp"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                Location
              </label>
              <input
                type="text"
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
                placeholder="Remote / San Francisco, CA"
              />
            </div>

            <div>
              <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                Target Role
              </label>
              <select
                value={formData.target_role}
                onChange={(e) => setFormData({ ...formData, target_role: e.target.value })}
                className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
              >
                {roleTypes.map((r) => (
                  <option key={r.value} value={r.value}>
                    {r.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
              Job Posting URL
            </label>
            <input
              type="url"
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
              placeholder="https://linkedin.com/jobs/..."
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
              Priority
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-[var(--color-text-tertiary)]">
              <span>Low</span>
              <span>{formData.priority}</span>
              <span>High</span>
            </div>
          </div>

          <div>
            <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
              Job Description
            </label>
            <textarea
              value={formData.description_raw}
              onChange={(e) => setFormData({ ...formData, description_raw: e.target.value })}
              rows={8}
              className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
              placeholder="Paste the full job description here..."
            />
          </div>

          <div>
            <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
              placeholder="Any initial notes about this job..."
            />
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {isSubmitting ? "Creating..." : "Create Job"}
          </button>
          <Link
            href="/dashboard"
            className="px-6 py-2 bg-[var(--color-bg-secondary)] rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
