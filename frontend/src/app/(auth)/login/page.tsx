"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [apiKey, setApiKey] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/auth/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ apiKey }),
      });

      if (res.ok) {
        router.push("/dashboard");
      } else {
        setError("Invalid API key");
      }
    } catch {
      setError("Failed to verify API key");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-primary)]">
      <div className="w-full max-w-md p-8 bg-[var(--color-bg-elevated)] rounded-xl border border-[var(--color-border-subtle)]">
        <h1 className="text-2xl font-bold text-center mb-6">
          Meridian Job Tracker
        </h1>
        <p className="text-[var(--color-text-secondary)] text-center mb-8">
          Enter your API key to access the dashboard
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="apiKey"
              className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2"
            >
              API Key
            </label>
            <input
              type="password"
              id="apiKey"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border-subtle)] rounded-lg text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)]"
              placeholder="Enter your API key"
              required
            />
          </div>

          {error && (
            <p className="text-red-400 text-sm text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-[var(--color-accent)] text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {loading ? "Verifying..." : "Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}
