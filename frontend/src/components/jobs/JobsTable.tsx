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
  work_location_type: string | null;
  status: string;
  priority: number;
  created_at: string;
  applied_at: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  employment_type: string | null;
}

interface JobsTableProps {
  search?: string;
  status?: string;
  workLocationType?: string;
  minPriority?: number;
  minSalary?: number;
  maxSalary?: number;
}

function formatSalary(min: number | null, max: number | null, currency: string | null): string {
  const curr = currency || "USD";
  const formatter = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: curr,
    maximumFractionDigits: 0,
  });

  if (min && max) {
    if (min === max) {
      return formatter.format(min);
    }
    return `${formatter.format(min)} - ${formatter.format(max)}`;
  }
  if (min) {
    return `${formatter.format(min)}+`;
  }
  if (max) {
    return `Up to ${formatter.format(max)}`;
  }
  return "-";
}

const locationTypeLabels: Record<string, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  on_site: "On-site",
};

export function JobsTable({ search, status, workLocationType, minPriority, minSalary, maxSalary }: JobsTableProps) {
  // Build query string
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (status) params.append("status", status);
  if (workLocationType) params.append("work_location_type", workLocationType);
  if (minPriority) params.append("min_priority", minPriority.toString());
  if (minSalary) params.append("min_salary", minSalary.toString());
  if (maxSalary) params.append("max_salary", maxSalary.toString());
  const queryString = params.toString();
  const url = `/api/jobs${queryString ? `?${queryString}` : ""}`;

  const { data, error, isLoading } = useSWR(url, fetcher);

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
              Type
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Salary
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
                {job.work_location_type ? (
                  <span className="px-2 py-0.5 text-xs rounded-full bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)]">
                    {locationTypeLabels[job.work_location_type] || job.work_location_type}
                  </span>
                ) : (
                  <span className="text-[var(--color-text-tertiary)]">-</span>
                )}
              </td>
              <td className="px-4 py-3 text-[var(--color-text-secondary)] text-sm">
                {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
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
