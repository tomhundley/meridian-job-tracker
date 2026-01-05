"use client";

import useSWR from "swr";
import Link from "next/link";
import { StatusBadge } from "./StatusBadge";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  status: string;
  priority: number;
  created_at: string;
  applied_at: string | null;
}

export function JobsTable() {
  const { data, error, isLoading } = useSWR("/api/jobs", fetcher);

  if (isLoading) {
    return (
      <div className="text-center py-12 text-[var(--color-text-tertiary)]">
        Loading jobs...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12 text-red-400">
        Failed to load jobs
      </div>
    );
  }

  const jobs: Job[] = data?.items || [];

  if (jobs.length === 0) {
    return (
      <div className="text-center py-12 bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)]">
        <p className="text-[var(--color-text-tertiary)] mb-4">
          No jobs found. Add your first job to get started.
        </p>
        <Link
          href="/dashboard/jobs/new"
          className="px-4 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity inline-block"
        >
          Add Job
        </Link>
      </div>
    );
  }

  return (
    <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="border-b border-[var(--color-border-subtle)]">
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Title
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Company
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Location
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Status
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Priority
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Added
            </th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr
              key={job.id}
              className="border-b border-[var(--color-border-subtle)] hover:bg-[var(--color-bg-elevated)] transition-colors"
            >
              <td className="px-4 py-3">
                <Link
                  href={`/dashboard/jobs/${job.id}`}
                  className="font-medium hover:text-[var(--color-accent)] transition-colors"
                >
                  {job.title}
                </Link>
              </td>
              <td className="px-4 py-3 text-[var(--color-text-secondary)]">
                {job.company}
              </td>
              <td className="px-4 py-3 text-[var(--color-text-secondary)]">
                {job.location || "-"}
              </td>
              <td className="px-4 py-3">
                <StatusBadge status={job.status} />
              </td>
              <td className="px-4 py-3">
                <div className="flex gap-1">
                  {[...Array(5)].map((_, i) => (
                    <span
                      key={i}
                      className={
                        i < Math.ceil(job.priority / 20)
                          ? "text-yellow-400"
                          : "text-[var(--color-text-tertiary)]"
                      }
                    >
                      ★
                    </span>
                  ))}
                </div>
              </td>
              <td className="px-4 py-3 text-[var(--color-text-tertiary)] text-sm">
                {new Date(job.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
