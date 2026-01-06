"use client";

import { useState } from "react";
import { JobsTable, SortField, SortOrder } from "@/components/jobs/JobsTable";
import { JobFilters } from "@/components/jobs/JobFilters";
import { StatsCards } from "@/components/jobs/StatsCards";

export default function DashboardPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [workLocationType, setWorkLocationType] = useState("");
  const [minPriority, setMinPriority] = useState(0);
  const [minSalary, setMinSalary] = useState(0);
  const [sortBy, setSortBy] = useState<SortField>("updated_at");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");

  const handleSortChange = (field: SortField, order: SortOrder) => {
    setSortBy(field);
    setSortOrder(order);
  };

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
        search={search}
        status={status}
        workLocationType={workLocationType}
        minPriority={minPriority}
        minSalary={minSalary}
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        onWorkLocationTypeChange={setWorkLocationType}
        onMinPriorityChange={setMinPriority}
        onMinSalaryChange={setMinSalary}
      />
      <JobsTable
        search={search}
        status={status}
        workLocationType={workLocationType}
        minPriority={minPriority}
        minSalary={minSalary}
        sortBy={sortBy}
        sortOrder={sortOrder}
        onSortChange={handleSortChange}
      />
    </div>
  );
}
