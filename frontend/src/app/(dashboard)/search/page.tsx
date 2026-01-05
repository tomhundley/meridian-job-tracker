"use client";

import { useState } from "react";
import Link from "next/link";
import { Search } from "lucide-react";
import { StatusBadge } from "@/components/jobs/StatusBadge";

interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  status: string;
  created_at: string;
}

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Job[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setHasSearched(true);

    try {
      const response = await fetch(`/api/jobs?search=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        setResults(data.items || []);
      }
    } catch (error) {
      console.error("Search error:", error);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Search Jobs</h1>

      <form onSubmit={handleSearch} className="max-w-2xl">
        <div className="relative">
          <Search
            className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-text-tertiary)]"
            size={20}
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by title, company, description, notes..."
            className="w-full pl-12 pr-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border-subtle)] rounded-xl text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
          />
        </div>
      </form>

      {isSearching && (
        <div className="text-center py-8 text-[var(--color-text-tertiary)]">
          Searching...
        </div>
      )}

      {hasSearched && !isSearching && (
        <div className="space-y-4">
          <p className="text-[var(--color-text-tertiary)]">
            {results.length} result{results.length !== 1 ? "s" : ""} found
          </p>

          {results.length > 0 ? (
            <div className="space-y-2">
              {results.map((job) => (
                <Link
                  key={job.id}
                  href={`/dashboard/jobs/${job.id}`}
                  className="block p-4 bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] hover:bg-[var(--color-bg-elevated)] transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{job.title}</h3>
                      <p className="text-sm text-[var(--color-text-secondary)]">
                        {job.company}
                        {job.location && ` • ${job.location}`}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <StatusBadge status={job.status} />
                      <span className="text-xs text-[var(--color-text-tertiary)]">
                        {new Date(job.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)]">
              <p className="text-[var(--color-text-tertiary)]">
                No jobs found matching your search.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
