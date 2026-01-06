"use client";

import { useState } from "react";
import { JobsTable } from "@/components/jobs/JobsTable";
import { JobFilters } from "@/components/jobs/JobFilters";
import { StatsCards } from "@/components/jobs/StatsCards";

export default function DashboardPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [workLocationType, setWorkLocationType] = useState("");
  const [minPriority, setMinPriority] = useState(0);

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
        onSearchChange={setSearch}
        onStatusChange={setStatus}
        onWorkLocationTypeChange={setWorkLocationType}
        onMinPriorityChange={setMinPriority}
      />
      <JobsTable
        search={search}
        status={status}
        workLocationType={workLocationType}
        minPriority={minPriority}
      />
    </div>
  );
}
