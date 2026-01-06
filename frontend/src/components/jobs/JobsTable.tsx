"use client";

import useSWR from "swr";
import Link from "next/link";
import { ChevronUp, ChevronDown, ChevronsUpDown, User } from "lucide-react";
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
  updated_at: string;
  applied_at: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  employment_type: string | null;
  contact_count: number;
  is_easy_apply: boolean;
  is_favorite: boolean;
  is_perfect_fit: boolean;
  is_ai_forward: boolean;
}

export type SortField = "updated_at" | "created_at" | "priority" | "salary" | "title" | "company";
export type SortOrder = "asc" | "desc";

interface JobsTableProps {
  search?: string;
  status?: string;
  workLocationType?: string;
  isEasyApply?: boolean;
  isFavorite?: boolean;
  isPerfectFit?: boolean;
  isAiForward?: boolean;
  minPriority?: number;
  minSalary?: number;
  maxSalary?: number;
  sortBy?: SortField;
  sortOrder?: SortOrder;
  onSortChange?: (field: SortField, order: SortOrder) => void;
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

function getPriorityLabel(priority: number): { label: string; color: string } {
  if (priority >= 81) return { label: "Top", color: "text-emerald-400" };
  if (priority >= 61) return { label: "High", color: "text-blue-400" };
  if (priority >= 41) return { label: "Med", color: "text-[var(--color-text-secondary)]" };
  if (priority >= 1) return { label: "Low", color: "text-[var(--color-text-tertiary)]" };
  return { label: "-", color: "text-[var(--color-text-tertiary)]" };
}

export function JobsTable({
  search,
  status,
  workLocationType,
  isEasyApply,
  isFavorite,
  isPerfectFit,
  isAiForward,
  minPriority,
  minSalary,
  maxSalary,
  sortBy = "updated_at",
  sortOrder = "desc",
  onSortChange,
}: JobsTableProps) {
  // Build query string
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (status) params.append("status", status);
  if (workLocationType) params.append("work_location_type", workLocationType);
  if (isEasyApply !== undefined) params.append("is_easy_apply", isEasyApply.toString());
  if (isFavorite !== undefined) params.append("is_favorite", isFavorite.toString());
  if (isPerfectFit !== undefined) params.append("is_perfect_fit", isPerfectFit.toString());
  if (isAiForward !== undefined) params.append("is_ai_forward", isAiForward.toString());
  if (minPriority) params.append("min_priority", minPriority.toString());
  if (minSalary) params.append("min_salary", minSalary.toString());
  if (maxSalary) params.append("max_salary", maxSalary.toString());
  params.append("sort_by", sortBy);
  params.append("sort_order", sortOrder);
  const queryString = params.toString();
  const url = `/api/jobs${queryString ? `?${queryString}` : ""}`;

  const handleSort = (field: SortField) => {
    if (!onSortChange) return;
    // If clicking the same field, toggle order; otherwise, default to desc
    const newOrder = sortBy === field && sortOrder === "desc" ? "asc" : "desc";
    onSortChange(field, newOrder);
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortBy !== field) {
      return <ChevronsUpDown size={14} className="opacity-30" />;
    }
    return sortOrder === "desc"
      ? <ChevronDown size={14} className="text-[var(--color-accent)]" />
      : <ChevronUp size={14} className="text-[var(--color-accent)]" />;
  };

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
            <th
              className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)] cursor-pointer hover:text-[var(--color-text-secondary)] transition-colors select-none"
              onClick={() => handleSort("title")}
            >
              <div className="flex items-center gap-1">
                Title
                <SortIcon field="title" />
              </div>
            </th>
            <th className="w-8 px-1 py-3" title="Has contacts">
              <User size={14} className="text-[var(--color-text-tertiary)] opacity-40" />
            </th>
            <th
              className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)] cursor-pointer hover:text-[var(--color-text-secondary)] transition-colors select-none"
              onClick={() => handleSort("company")}
            >
              <div className="flex items-center gap-1">
                Company
                <SortIcon field="company" />
              </div>
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Location
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Type
            </th>
            <th
              className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)] cursor-pointer hover:text-[var(--color-text-secondary)] transition-colors select-none"
              onClick={() => handleSort("salary")}
            >
              <div className="flex items-center gap-1">
                Salary
                <SortIcon field="salary" />
              </div>
            </th>
            <th className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Status
            </th>
            <th
              className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)] cursor-pointer hover:text-[var(--color-text-secondary)] transition-colors select-none"
              onClick={() => handleSort("priority")}
            >
              <div className="flex items-center gap-1">
                Priority
                <SortIcon field="priority" />
              </div>
            </th>
            <th
              className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)] cursor-pointer hover:text-[var(--color-text-secondary)] transition-colors select-none"
              onClick={() => handleSort("created_at")}
            >
              <div className="flex items-center gap-1">
                Added
                <SortIcon field="created_at" />
              </div>
            </th>
            <th
              className="text-left px-4 py-3 text-sm font-medium text-[var(--color-text-tertiary)] cursor-pointer hover:text-[var(--color-text-secondary)] transition-colors select-none"
              onClick={() => handleSort("updated_at")}
            >
              <div className="flex items-center gap-1">
                Modified
                <SortIcon field="updated_at" />
              </div>
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
                <div className="flex items-center gap-1.5 flex-wrap">
                  <Link
                    href={`/dashboard/jobs/${job.id}`}
                    className="font-medium hover:text-[var(--color-accent)] transition-colors"
                  >
                    {job.title}
                  </Link>
                  {job.is_favorite && (
                    <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-yellow-500/20 text-yellow-400" title="Favorite">
                      ★
                    </span>
                  )}
                  {job.is_perfect_fit && (
                    <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-purple-500/20 text-purple-400 whitespace-nowrap" title="Perfect Fit">
                      Perfect
                    </span>
                  )}
                  {job.is_ai_forward && (
                    <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-blue-500/20 text-blue-400 whitespace-nowrap" title="AI Forward">
                      AI
                    </span>
                  )}
                  {job.is_easy_apply && (
                    <span className="px-1.5 py-0.5 text-[10px] font-medium rounded bg-green-500/20 text-green-400 whitespace-nowrap" title="Easy Apply">
                      Easy
                    </span>
                  )}
                </div>
              </td>
              <td className="px-1 py-3 text-center">
                {job.contact_count > 0 && (
                  <span title={`${job.contact_count} contact${job.contact_count > 1 ? 's' : ''}`}>
                    <User size={14} className="text-[var(--color-accent)] opacity-70" />
                  </span>
                )}
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
                {(() => {
                  const { label, color } = getPriorityLabel(job.priority);
                  return (
                    <span className={`text-sm font-medium ${color}`}>
                      {label}
                    </span>
                  );
                })()}
              </td>
              <td className="px-4 py-3 text-[var(--color-text-tertiary)] text-sm">
                {new Date(job.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-3 text-[var(--color-text-tertiary)] text-sm">
                {new Date(job.updated_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
