"use client";

import { useState, useEffect, useCallback } from "react";

const COOKIE_NAME = "job_filters";
const COOKIE_EXPIRY_DAYS = 90;

interface FilterState {
  search: string;
  status: string;
  workLocationType: string;
  isEasyApply: string;
  isFavorite: string;
  isPerfectFit: string;
  isAiForward: string;
  minPriority: number;
  minSalary: number;
  maxAgeDays: number;
  sortBy: string;
  sortOrder: string;
}

// Default statuses: everything except "applied" and "rejected"
export const DEFAULT_STATUSES = "saved,researching,ready_to_apply,applying,interviewing,offer,withdrawn,archived";

const defaultFilters: FilterState = {
  search: "",
  status: DEFAULT_STATUSES,
  workLocationType: "",
  isEasyApply: "",
  isFavorite: "",
  isPerfectFit: "",
  isAiForward: "",
  minPriority: 0,
  minSalary: 0,
  maxAgeDays: 0,
  sortBy: "updated_at",
  sortOrder: "desc",
};

function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    return parts.pop()?.split(";").shift() || null;
  }
  return null;
}

function setCookie(name: string, value: string, days: number): void {
  if (typeof document === "undefined") return;
  const date = new Date();
  date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
  const expires = `expires=${date.toUTCString()}`;
  document.cookie = `${name}=${value}; ${expires}; path=/; SameSite=Lax`;
}

function loadFiltersFromCookie(): FilterState {
  const cookieValue = getCookie(COOKIE_NAME);
  if (!cookieValue) return defaultFilters;

  try {
    const parsed = JSON.parse(decodeURIComponent(cookieValue));
    return { ...defaultFilters, ...parsed };
  } catch {
    return defaultFilters;
  }
}

function saveFiltersToCookie(filters: FilterState): void {
  const value = encodeURIComponent(JSON.stringify(filters));
  setCookie(COOKIE_NAME, value, COOKIE_EXPIRY_DAYS);
}

export function usePersistentFilters() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [filters, setFilters] = useState<FilterState>(defaultFilters);

  // Load filters from cookie on mount
  useEffect(() => {
    const savedFilters = loadFiltersFromCookie();
    setFilters(savedFilters);
    setIsInitialized(true);
  }, []);

  // Save filters to cookie whenever they change (after initialization)
  useEffect(() => {
    if (isInitialized) {
      saveFiltersToCookie(filters);
    }
  }, [filters, isInitialized]);

  const updateFilter = useCallback(<K extends keyof FilterState>(
    key: K,
    value: FilterState[K]
  ) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }, []);

  const clearAllFilters = useCallback(() => {
    setFilters({
      ...defaultFilters,
      sortBy: filters.sortBy,
      sortOrder: filters.sortOrder,
    });
  }, [filters.sortBy, filters.sortOrder]);

  return {
    filters,
    updateFilter,
    clearAllFilters,
    isInitialized,
  };
}
