"use client";

import { useState } from "react";
import { JobsTable, SortField, SortOrder } from "@/components/jobs/JobsTable";
import { JobFilters } from "@/components/jobs/JobFilters";
import { StatsCards } from "@/components/jobs/StatsCards";
import { usePersistentFilters } from "@/lib/usePersistentFilters";

export default function DashboardPage() {
  const { filters, updateFilter, isInitialized } = usePersistentFilters();
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSortChange = (field: SortField, order: SortOrder) => {
    updateFilter("sortBy", field);
    updateFilter("sortOrder", order);
  };

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  // Show loading state while filters are being loaded from cookies
  if (!isInitialized) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold">Job Applications</h1>
        </div>
        <div className="animate-pulse space-y-4">
          <div className="h-24 bg-[var(--color-bg-secondary)] rounded-lg"></div>
          <div className="h-16 bg-[var(--color-bg-secondary)] rounded-lg"></div>
          <div className="h-64 bg-[var(--color-bg-secondary)] rounded-lg"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Job Applications</h1>
        <a
          href="/dashboard/jobs/new"
          className="px-4 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity"
        >
          Add Job
        </a>
      </div>

      <StatsCards />
      <JobFilters
        search={filters.search}
        status={filters.status}
        workLocationType={filters.workLocationType}
        isEasyApply={filters.isEasyApply}
        isFavorite={filters.isFavorite}
        isPerfectFit={filters.isPerfectFit}
        isAiForward={filters.isAiForward}
        minPriority={filters.minPriority}
        minSalary={filters.minSalary}
        maxAgeDays={filters.maxAgeDays}
        onSearchChange={(v) => updateFilter("search", v)}
        onStatusChange={(v) => updateFilter("status", v)}
        onWorkLocationTypeChange={(v) => updateFilter("workLocationType", v)}
        onIsEasyApplyChange={(v) => updateFilter("isEasyApply", v)}
        onIsFavoriteChange={(v) => updateFilter("isFavorite", v)}
        onIsPerfectFitChange={(v) => updateFilter("isPerfectFit", v)}
        onIsAiForwardChange={(v) => updateFilter("isAiForward", v)}
        onMinPriorityChange={(v) => updateFilter("minPriority", v)}
        onMinSalaryChange={(v) => updateFilter("minSalary", v)}
        onMaxAgeDaysChange={(v) => updateFilter("maxAgeDays", v)}
        onRefresh={handleRefresh}
      />
      <JobsTable
        search={filters.search}
        status={filters.status}
        workLocationType={filters.workLocationType}
        isEasyApply={filters.isEasyApply === "true" ? true : filters.isEasyApply === "false" ? false : undefined}
        isFavorite={filters.isFavorite === "true" ? true : filters.isFavorite === "false" ? false : undefined}
        isPerfectFit={filters.isPerfectFit === "true" ? true : filters.isPerfectFit === "false" ? false : undefined}
        isAiForward={filters.isAiForward === "true" ? true : filters.isAiForward === "false" ? false : undefined}
        minPriority={filters.minPriority}
        minSalary={filters.minSalary}
        maxAgeDays={filters.maxAgeDays || undefined}
        refreshKey={refreshKey}
        sortBy={filters.sortBy as SortField}
        sortOrder={filters.sortOrder as SortOrder}
        onSortChange={handleSortChange}
      />
    </div>
  );
}
