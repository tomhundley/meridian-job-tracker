"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import useSWRInfinite from "swr/infinite";
import Link from "next/link";
import { ChevronUp, ChevronDown, ChevronsUpDown, User, Zap, Target, Sparkles, Heart, Loader2 } from "lucide-react";
import { StatusBadge } from "./StatusBadge";

const fetcher = (url: string) => fetch(url).then((res) => res.json());
const PAGE_SIZE = 50;

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
  posted_at: string | null;
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
  maxAgeDays?: number;
  refreshKey?: number;
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

function getDaysAgo(postedAt: string | null): { text: string; color: string } {
  if (!postedAt) {
    return { text: "-", color: "text-[var(--color-text-tertiary)]" };
  }
  const days = Math.floor((Date.now() - new Date(postedAt).getTime()) / 86400000);
  if (days === 0) return { text: "Today", color: "text-green-400" };
  if (days === 1) return { text: "1d", color: "text-green-400" };
  if (days <= 7) return { text: `${days}d`, color: "text-green-400" };
  if (days <= 14) return { text: `${days}d`, color: "text-yellow-400" };
  if (days <= 30) return { text: `${days}d`, color: "text-orange-400" };
  return { text: `${days}d`, color: "text-red-400" };
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
  maxAgeDays,
  refreshKey,
  sortBy = "updated_at",
  sortOrder = "desc",
  onSortChange,
}: JobsTableProps) {
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Build base query string (without pagination)
  const buildQueryString = useCallback((page: number) => {
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
    if (maxAgeDays) params.append("max_age_days", maxAgeDays.toString());
    params.append("sort_by", sortBy);
    params.append("sort_order", sortOrder);
    params.append("page", page.toString());
    params.append("page_size", PAGE_SIZE.toString());
    return params.toString();
  }, [search, status, workLocationType, isEasyApply, isFavorite, isPerfectFit, isAiForward, minPriority, minSalary, maxSalary, maxAgeDays, sortBy, sortOrder]);

  // SWR Infinite for pagination
  const getKey = useCallback((pageIndex: number, previousPageData: { items: Job[]; total: number; total_pages: number } | null) => {
    // First page
    if (pageIndex === 0) return `/api/jobs?${buildQueryString(1)}`;
    // Reached the end
    if (previousPageData && previousPageData.items.length === 0) return null;
    if (previousPageData && pageIndex >= previousPageData.total_pages) return null;
    // Next page
    return `/api/jobs?${buildQueryString(pageIndex + 1)}`;
  }, [buildQueryString]);

  const { data, error, isLoading, isValidating, size, setSize, mutate } = useSWRInfinite(getKey, fetcher, {
    revalidateFirstPage: false,
    revalidateOnFocus: false,
  });

  // Flatten all pages into single array
  const jobs: Job[] = data ? data.flatMap((page) => page.items || []) : [];
  const total = data?.[0]?.total || 0;
  const totalPages = data?.[0]?.total_pages || 1;
  const isLoadingMore = isValidating && size > 1;
  const hasMore = size < totalPages;

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

  // Trigger refresh when refreshKey changes
  useEffect(() => {
    if (refreshKey && refreshKey > 0) {
      mutate();
    }
  }, [refreshKey, mutate]);

  // Infinite scroll: observe the load more element
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isValidating) {
          setSize(size + 1);
        }
      },
      { threshold: 0.1 }
    );

    if (loadMoreRef.current) {
      observer.observe(loadMoreRef.current);
    }

    return () => observer.disconnect();
  }, [hasMore, isValidating, setSize, size]);

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
    <div className="space-y-2">
      {/* Total count header */}
      <div className="flex items-center justify-between px-1">
        <p className="text-sm text-[var(--color-text-secondary)]">
          Showing <span className="font-semibold text-[var(--color-text-primary)]">{jobs.length}</span> of{" "}
          <span className="font-semibold text-[var(--color-text-primary)]">{total}</span> jobs
        </p>
        {isLoadingMore && (
          <div className="flex items-center gap-2 text-sm text-[var(--color-text-tertiary)]">
            <Loader2 size={14} className="animate-spin" />
            Loading more...
          </div>
        )}
      </div>

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
            <th className="w-8 px-1 py-3" title="Easy Apply">
              <Zap size={14} className="text-[var(--color-text-tertiary)] opacity-40" />
            </th>
            <th className="w-8 px-1 py-3" title="Perfect Fit">
              <Target size={14} className="text-[var(--color-text-tertiary)] opacity-40" />
            </th>
            <th className="w-8 px-1 py-3" title="AI Forward">
              <Sparkles size={14} className="text-[var(--color-text-tertiary)] opacity-40" />
            </th>
            <th className="w-8 px-1 py-3" title="Favorite">
              <Heart size={14} className="text-[var(--color-text-tertiary)] opacity-40" />
            </th>
            <th className="text-left px-3 py-3 text-sm font-medium text-[var(--color-text-tertiary)]">
              Age
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
                <Link
                  href={`/dashboard/jobs/${job.id}`}
                  className="font-medium hover:text-[var(--color-accent)] transition-colors"
                >
                  {job.title}
                </Link>
              </td>
              <td className="px-1 py-3 text-center">
                {job.contact_count > 0 && (
                  <span title={`${job.contact_count} contact${job.contact_count > 1 ? 's' : ''}`}>
                    <User size={14} className="text-[var(--color-accent)] opacity-70" />
                  </span>
                )}
              </td>
              <td className="px-1 py-3 text-center">
                {job.is_easy_apply && (
                  <Zap size={14} className="text-green-400" />
                )}
              </td>
              <td className="px-1 py-3 text-center">
                {job.is_perfect_fit && (
                  <Target size={14} className="text-purple-400" />
                )}
              </td>
              <td className="px-1 py-3 text-center">
                {job.is_ai_forward && (
                  <Sparkles size={14} className="text-cyan-400" />
                )}
              </td>
              <td className="px-1 py-3 text-center">
                {job.is_favorite && (
                  <Heart size={14} className="text-red-400 fill-red-400" />
                )}
              </td>
              <td className="px-3 py-3 text-sm">
                {(() => {
                  const { text, color } = getDaysAgo(job.posted_at);
                  return <span className={color}>{text}</span>;
                })()}
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

      {/* Infinite scroll trigger */}
      <div
        ref={loadMoreRef}
        className="h-16 flex items-center justify-center"
      >
        {isLoadingMore && (
          <div className="flex items-center gap-2 text-[var(--color-text-tertiary)]">
            <Loader2 size={18} className="animate-spin" />
            <span className="text-sm">Loading more jobs...</span>
          </div>
        )}
        {!hasMore && jobs.length > 0 && (
          <p className="text-sm text-[var(--color-text-tertiary)]">
            All {total} jobs loaded
          </p>
        )}
      </div>
      </div>
    </div>
  );
}
