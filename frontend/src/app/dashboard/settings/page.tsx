"use client";

import { useState } from "react";
import { toast } from "sonner";

export default function SettingsPage() {
  const [backendUrl, setBackendUrl] = useState(
    process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8005"
  );

  const handleLogout = () => {
    document.cookie = "auth_token=; path=/; max-age=0";
    window.location.href = "/login";
  };

  const testConnection = async () => {
    try {
      const response = await fetch("/api/auth/verify");
      if (response.ok) {
        toast.success("Connection to backend is working");
      } else {
        toast.error("Connection failed - check your API key");
      }
    } catch (error) {
      toast.error("Connection failed - backend may be offline");
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6 space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-4">Backend Connection</h2>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                Backend URL
              </label>
              <input
                type="text"
                value={backendUrl}
                disabled
                className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg text-[var(--color-text-secondary)]"
              />
              <p className="text-xs text-[var(--color-text-tertiary)] mt-1">
                Set via BACKEND_URL environment variable
              </p>
            </div>

            <button
              onClick={testConnection}
              className="px-4 py-2 bg-[var(--color-accent)] text-white rounded-lg hover:opacity-90 transition-opacity"
            >
              Test Connection
            </button>
          </div>
        </div>

        <hr className="border-[var(--color-border-subtle)]" />

        <div>
          <h2 className="text-lg font-semibold mb-4">Account</h2>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>

      <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
        <h2 className="text-lg font-semibold mb-4">About</h2>
        <div className="space-y-2 text-sm text-[var(--color-text-secondary)]">
          <p>
            <strong>Meridian Job Tracker</strong>
          </p>
          <p>A human-in-the-loop job application tracking system.</p>
          <p className="text-[var(--color-text-tertiary)]">
            Built with Next.js, FastAPI, and PostgreSQL.
          </p>
        </div>
      </div>
    </div>
  );
}
