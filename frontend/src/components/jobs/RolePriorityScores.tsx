"use client";

import { useState, useEffect } from "react";
import { RefreshCw } from "lucide-react";

interface RoleScore {
  role: string;
  score: number;
  label: string;
}

interface RolePriorityScoresProps {
  jobId: string;
  hasDescription: boolean;
  fallbackPriority?: number;
}

function getPriorityConfig(value: number) {
  if (value >= 81) return { label: "TOP", color: "#10b981" };
  if (value >= 61) return { label: "HIGH", color: "#eab308" };
  if (value >= 41) return { label: "MED", color: "#f97316" };
  return { label: "LOW", color: "#ef4444" };
}

function MiniGauge({ value, label, size = 90 }: { value: number; label: string; size?: number }) {
  const config = getPriorityConfig(value);
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * Math.PI * 1.5; // 270 degrees
  const progress = (value / 100) * circumference;
  const center = size / 2;

  return (
    <div className="flex flex-col items-center">
      <div className="relative flex items-center justify-center">
        <svg
          width={size}
          height={size}
          className="transform rotate-[135deg]"
        >
          <defs>
            <filter id={`glow-${label}`} x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>

          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference} ${circumference * 0.333}`}
            strokeLinecap="round"
          />

          {/* Progress arc with glow */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={config.color}
            strokeWidth={strokeWidth}
            strokeDasharray={`${progress} ${circumference}`}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
            style={{
              filter: `drop-shadow(0 0 8px ${config.color})`
            }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-2xl font-bold tracking-tight transition-all duration-500"
            style={{
              color: config.color,
              textShadow: `0 0 20px ${config.color}40`
            }}
          >
            {value}
          </span>
        </div>
      </div>
      <span className="text-xs font-semibold text-[var(--color-text-secondary)] mt-1 uppercase tracking-wider">
        {label}
      </span>
    </div>
  );
}

export function RolePriorityScores({ jobId, hasDescription, fallbackPriority = 50 }: RolePriorityScoresProps) {
  const [roleScores, setRoleScores] = useState<RoleScore[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalysis = async () => {
    if (!hasDescription) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/jobs/${jobId}/analyze`, {
        method: "POST",
      });

      if (response.ok) {
        const data = await response.json();
        if (data.role_scores) {
          setRoleScores(data.role_scores);
        }
      } else {
        setError("Failed to analyze job");
      }
    } catch (err) {
      setError("Failed to analyze job");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (hasDescription) {
      fetchAnalysis();
    }
  }, [jobId, hasDescription]);

  // If no description, show single fallback gauge
  if (!hasDescription) {
    return (
      <div className="flex flex-col items-center">
        <MiniGauge value={fallbackPriority} label="Priority" size={120} />
        <p className="text-xs text-[var(--color-text-tertiary)] mt-2 text-center">
          Add job description for role-specific scores
        </p>
      </div>
    );
  }

  // Loading state
  if (isLoading && !roleScores) {
    return (
      <div className="flex flex-col items-center justify-center py-8">
        <RefreshCw className="w-8 h-8 text-[var(--color-text-tertiary)] animate-spin" />
        <p className="text-sm text-[var(--color-text-tertiary)] mt-2">Analyzing job fit...</p>
      </div>
    );
  }

  // Error state with refresh button
  if (error && !roleScores) {
    return (
      <div className="flex flex-col items-center justify-center py-4">
        <MiniGauge value={fallbackPriority} label="Priority" size={120} />
        <button
          onClick={fetchAnalysis}
          className="mt-3 flex items-center gap-1 text-xs text-[var(--color-accent)] hover:underline"
        >
          <RefreshCw size={12} />
          Analyze for role scores
        </button>
      </div>
    );
  }

  // Role scores display
  if (roleScores && roleScores.length > 0) {
    // Find the best role
    const bestRole = roleScores.reduce((best, current) =>
      current.score > best.score ? current : best
    );

    return (
      <div className="space-y-4">
        {/* All roles in a row */}
        <div className="flex flex-wrap justify-center gap-8">
          {roleScores.map((rs) => (
            <div
              key={rs.role}
              className={`transition-all duration-300 ${
                rs.role === bestRole.role
                  ? "scale-110 z-10"
                  : "opacity-80 hover:opacity-100"
              }`}
            >
              <MiniGauge value={rs.score} label={rs.label} size={85} />
              {rs.role === bestRole.role && (
                <div className="text-center mt-1">
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">
                    Best Fit
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Refresh button */}
        <div className="flex justify-center">
          <button
            onClick={fetchAnalysis}
            disabled={isLoading}
            className="flex items-center gap-1 text-xs text-[var(--color-text-tertiary)] hover:text-[var(--color-accent)] transition-colors disabled:opacity-50"
          >
            <RefreshCw size={12} className={isLoading ? "animate-spin" : ""} />
            Re-analyze
          </button>
        </div>
      </div>
    );
  }

  // Fallback
  return (
    <div className="flex flex-col items-center">
      <MiniGauge value={fallbackPriority} label="Priority" size={120} />
    </div>
  );
}
