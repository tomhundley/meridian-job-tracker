"use client";

import { useState, useEffect } from "react";
import useSWR from "swr";
import { ChevronDown, ChevronRight } from "lucide-react";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

interface DeclineReason {
  code: string;
  display_name: string;
  category: string;
  description: string | null;
}

interface Category {
  name: string;
  display_name: string;
  reasons: DeclineReason[];
}

interface DeclineReasonsResponse {
  categories: Category[];
}

interface DeclineReasonsPickerProps {
  type: "user" | "company";
  selectedReasons: string[];
  onChange: (reasons: string[]) => void;
  disabled?: boolean;
}

export function DeclineReasonsPicker({
  type,
  selectedReasons,
  onChange,
  disabled = false,
}: DeclineReasonsPickerProps) {
  const { data, error, isLoading } = useSWR<DeclineReasonsResponse>(
    `/api/decline-reasons?type=${type}`,
    fetcher
  );

  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(
    new Set()
  );

  // Auto-expand categories that have selected reasons
  useEffect(() => {
    if (data && selectedReasons.length > 0) {
      const categoriesToExpand = new Set<string>();
      data.categories.forEach((category) => {
        if (category.reasons.some((r) => selectedReasons.includes(r.code))) {
          categoriesToExpand.add(category.name);
        }
      });
      if (categoriesToExpand.size > 0) {
        setExpandedCategories(categoriesToExpand);
      }
    }
  }, [data, selectedReasons]);

  const toggleCategory = (categoryName: string) => {
    setExpandedCategories((prev) => {
      const next = new Set(prev);
      if (next.has(categoryName)) {
        next.delete(categoryName);
      } else {
        next.add(categoryName);
      }
      return next;
    });
  };

  const toggleReason = (code: string) => {
    if (disabled) return;

    if (selectedReasons.includes(code)) {
      onChange(selectedReasons.filter((r) => r !== code));
    } else {
      onChange([...selectedReasons, code]);
    }
  };

  if (isLoading) {
    return (
      <div className="text-sm text-[var(--color-text-tertiary)]">
        Loading reasons...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="text-sm text-red-400">
        Failed to load decline reasons
      </div>
    );
  }

  const title = type === "user" ? "Why did you pass?" : "Why did they decline?";

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-[var(--color-text-secondary)]">
        {title}
      </h3>

      <div className="space-y-1">
        {data.categories.map((category) => {
          const isExpanded = expandedCategories.has(category.name);
          const selectedInCategory = category.reasons.filter((r) =>
            selectedReasons.includes(r.code)
          ).length;

          return (
            <div
              key={category.name}
              className="border border-[var(--color-border-subtle)] rounded-lg overflow-hidden"
            >
              <button
                type="button"
                onClick={() => toggleCategory(category.name)}
                className="w-full flex items-center justify-between px-3 py-2 bg-[var(--color-bg-elevated)] hover:bg-[var(--color-bg-secondary)] transition-colors text-left"
              >
                <div className="flex items-center gap-2">
                  {isExpanded ? (
                    <ChevronDown size={16} className="text-[var(--color-text-tertiary)]" />
                  ) : (
                    <ChevronRight size={16} className="text-[var(--color-text-tertiary)]" />
                  )}
                  <span className="text-sm font-medium">{category.display_name}</span>
                </div>
                {selectedInCategory > 0 && (
                  <span className="text-xs bg-[var(--color-accent)] text-white px-2 py-0.5 rounded-full">
                    {selectedInCategory}
                  </span>
                )}
              </button>

              {isExpanded && (
                <div className="px-3 py-2 space-y-1 bg-[var(--color-bg-primary)]">
                  {category.reasons.map((reason) => {
                    const isSelected = selectedReasons.includes(reason.code);
                    return (
                      <label
                        key={reason.code}
                        className={`flex items-start gap-2 px-2 py-1.5 rounded cursor-pointer transition-colors ${
                          isSelected
                            ? "bg-[var(--color-accent)]/10"
                            : "hover:bg-[var(--color-bg-secondary)]"
                        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
                      >
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleReason(reason.code)}
                          disabled={disabled}
                          className="mt-0.5 rounded border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)] text-[var(--color-accent)] focus:ring-[var(--color-accent)] focus:ring-offset-0"
                        />
                        <span className="text-sm">{reason.display_name}</span>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selectedReasons.length > 0 && (
        <div className="pt-2">
          <div className="flex flex-wrap gap-1">
            {selectedReasons.map((code) => {
              const reason = data.categories
                .flatMap((c) => c.reasons)
                .find((r) => r.code === code);
              return (
                <span
                  key={code}
                  className="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-full"
                >
                  {reason?.display_name || code}
                  {!disabled && (
                    <button
                      type="button"
                      onClick={() => toggleReason(code)}
                      className="ml-1 hover:text-red-400"
                    >
                      &times;
                    </button>
                  )}
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
