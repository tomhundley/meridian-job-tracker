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

export default function NewJobPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);

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
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <Link
          href="/dashboard"
          className="p-2 hover:bg-[var(--color-bg-secondary)] rounded-lg transition-colors"
        >
          <ArrowLeft size={20} />
        </Link>
        <h1 className="text-2xl font-bold">Add New Job</h1>
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
