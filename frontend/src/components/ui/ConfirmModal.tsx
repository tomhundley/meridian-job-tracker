"use client";

import { useEffect } from "react";
import { AlertTriangle, X } from "lucide-react";

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: "danger" | "warning";
  isLoading?: boolean;
}

export function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  variant = "danger",
  isLoading = false,
}: ConfirmModalProps) {
  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const variantStyles = {
    danger: {
      icon: "bg-red-500/10 text-red-400",
      button: "bg-red-500 hover:bg-red-600 text-white",
    },
    warning: {
      icon: "bg-amber-500/10 text-amber-400",
      button: "bg-amber-500 hover:bg-amber-600 text-white",
    },
  };

  const styles = variantStyles[variant];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md mx-4 animate-in zoom-in-95 fade-in duration-200">
        <div className="bg-[var(--color-bg-secondary)] rounded-2xl border border-[var(--color-border-subtle)] shadow-2xl overflow-hidden">
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-1 rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors"
          >
            <X size={18} className="text-[var(--color-text-tertiary)]" />
          </button>

          <div className="p-6">
            {/* Icon */}
            <div className={`w-12 h-12 rounded-full ${styles.icon} flex items-center justify-center mx-auto mb-4`}>
              <AlertTriangle size={24} />
            </div>

            {/* Title */}
            <h2 className="text-xl font-semibold text-center mb-2">
              {title}
            </h2>

            {/* Message */}
            <p className="text-[var(--color-text-secondary)] text-center text-sm leading-relaxed">
              {message}
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 p-4 bg-[var(--color-bg-elevated)] border-t border-[var(--color-border-subtle)]">
            <button
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-4 py-2.5 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-secondary)] hover:bg-[var(--color-bg-elevated)] transition-colors font-medium text-sm disabled:opacity-50"
            >
              {cancelLabel}
            </button>
            <button
              onClick={onConfirm}
              disabled={isLoading}
              className={`flex-1 px-4 py-2.5 rounded-xl ${styles.button} transition-colors font-medium text-sm disabled:opacity-50`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Deleting...
                </span>
              ) : (
                confirmLabel
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
