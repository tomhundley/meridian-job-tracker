"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Briefcase, Search, Settings, LogOut } from "lucide-react";
import { clsx } from "clsx";

const navItems = [
  { href: "/dashboard", label: "Jobs", icon: Briefcase },
  { href: "/dashboard/search", label: "Search", icon: Search },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-[var(--color-bg-secondary)] border-r border-[var(--color-border-subtle)] flex flex-col">
      <div className="p-6 border-b border-[var(--color-border-subtle)]">
        <h1 className="text-xl font-bold">Meridian</h1>
        <p className="text-sm text-[var(--color-text-tertiary)]">Job Tracker</p>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-colors",
                isActive
                  ? "bg-[var(--color-accent)]/10 text-[var(--color-accent)]"
                  : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)]"
              )}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-[var(--color-border-subtle)]">
        <button
          onClick={() => {
            // Clear auth cookie and redirect
            document.cookie = "auth_token=; path=/; max-age=0";
            window.location.href = "/login";
          }}
          className="flex items-center gap-3 px-4 py-3 w-full text-[var(--color-text-secondary)] hover:text-red-400 transition-colors"
        >
          <LogOut size={20} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
