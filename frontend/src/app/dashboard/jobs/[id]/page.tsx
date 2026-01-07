"use client";

import { useParams, useRouter } from "next/navigation";
import useSWR, { mutate } from "swr";
import Link from "next/link";
import { useState } from "react";
import { ArrowLeft, ExternalLink, Trash2, FileText, Clock, User, Linkedin, Mail, X, Heart, DollarSign, MapPin, Briefcase } from "lucide-react";
import { StatusBadge } from "@/components/jobs/StatusBadge";
import { DeclineReasonsPicker } from "@/components/jobs/DeclineReasonsPicker";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { StatusPipeline } from "@/components/jobs/StatusPipeline";
import { JobFlagsToggle } from "@/components/jobs/JobFlagsToggle";
import { RolePriorityScores } from "@/components/jobs/RolePriorityScores";
import { JobNotes } from "@/components/jobs/JobNotes";
import { toast } from "sonner";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

const statuses = [
  "saved",
  "researching",
  "ready_to_apply",
  "applying",
  "applied",
  "interviewing",
  "offer",
  "rejected",
  "withdrawn",
  "archived",
];

const roleTypes = [
  { value: "cto", label: "CTO" },
  { value: "vp", label: "VP Engineering" },
  { value: "director", label: "Director" },
  { value: "architect", label: "Architect" },
  { value: "developer", label: "Developer" },
];

interface NoteEntry {
  text: string;
  timestamp: string;
  source: "user" | "agent";
}

interface Job {
  id: string;
  title: string;
  company: string;
  location: string | null;
  work_location_type: "remote" | "hybrid" | "on_site" | null;
  employment_type: "full_time" | "part_time" | "contract" | "contract_to_hire" | "temporary" | "internship" | null;
  url: string | null;
  description_raw: string | null;
  status: string;
  target_role: string | null;
  priority: number;
  notes: NoteEntry[] | null;
  tags: string[];
  posted_at: string | null;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  is_easy_apply: boolean;
  is_favorite: boolean;
  is_perfect_fit: boolean;
  is_ai_forward: boolean;
  is_location_compatible: boolean;
  user_decline_reasons: string[] | null;
  company_decline_reasons: string[] | null;
  decline_notes: string | null;
}

function formatPostedAge(postedAt: string | null): string {
  if (!postedAt) return "-";
  const days = Math.floor((Date.now() - new Date(postedAt).getTime()) / 86400000);
  if (days === 0) return "Today";
  if (days === 1) return "1 day ago";
  return `${days} days ago`;
}

function formatSalary(min: number | null, max: number | null, currency: string | null): string {
  if (!min && !max) return "Not specified";
  const currencySymbol = currency === "USD" ? "$" : currency || "$";
  const formatNum = (n: number) => {
    if (n >= 1000) return `${currencySymbol}${Math.round(n / 1000)}k`;
    return `${currencySymbol}${n.toLocaleString()}`;
  };
  if (min && max) {
    if (min === max) return formatNum(min);
    return `${formatNum(min)} - ${formatNum(max)}`;
  }
  if (min) return `${formatNum(min)}+`;
  if (max) return `Up to ${formatNum(max)}`;
  return "Not specified";
}

const workLocationTypeLabels: Record<string, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  on_site: "On-site",
};

const employmentTypeLabels: Record<string, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
  contract: "Contract",
  contract_to_hire: "Contract to Hire",
  temporary: "Temporary",
  internship: "Internship",
};

interface CoverLetter {
  id: string;
  content: string;
  target_role: string;
  is_approved: boolean;
  created_at: string;
}

interface Contact {
  id: string;
  name: string;
  title: string | null;
  email: string | null;
  linkedin_url: string | null;
  contact_type: string;
  is_job_poster: boolean;
  notes: string | null;
  contacted_at: string | null;
}

const contactTypeLabels: Record<string, string> = {
  recruiter: "Recruiter",
  hiring_manager: "Hiring Manager",
  team_member: "Team Member",
  job_poster: "Job Poster",
  hr_contact: "HR Contact",
};

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const { data: job, error, isLoading } = useSWR<Job>(`/api/jobs/${id}`, fetcher);
  const { data: contacts } = useSWR<Contact[]>(`/api/jobs/${id}/contacts`, fetcher);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [coverLetters, setCoverLetters] = useState<CoverLetter[]>([]);
  const [deleteJobModalOpen, setDeleteJobModalOpen] = useState(false);
  const [deleteContactModalOpen, setDeleteContactModalOpen] = useState(false);
  const [contactToDelete, setContactToDelete] = useState<Contact | null>(null);

  if (isLoading) {
    return (
      <div className="text-center py-12 text-[var(--color-text-tertiary)]">
        Loading job details...
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="text-center py-12 text-red-400">
        Failed to load job details
      </div>
    );
  }

  const handleStatusChange = async (newStatus: string) => {
    setIsUpdating(true);
    try {
      const response = await fetch(`/api/jobs/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });

      if (response.ok) {
        mutate(`/api/jobs/${id}`);
        mutate("/api/jobs");
        toast.success("Status updated");
      } else {
        toast.error("Failed to update status");
      }
    } catch (error) {
      toast.error("Failed to update status");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleUpdateJob = async (updates: Partial<Job>) => {
    setIsUpdating(true);
    try {
      const response = await fetch(`/api/jobs/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });

      if (response.ok) {
        mutate(`/api/jobs/${id}`);
        toast.success("Job updated");
      } else {
        toast.error("Failed to update job");
      }
    } catch (error) {
      toast.error("Failed to update job");
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDeleteJob = async () => {
    setIsDeleting(true);
    try {
      const response = await fetch(`/api/jobs/${id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast.success("Job deleted");
        router.push("/dashboard");
      } else {
        toast.error("Failed to delete job");
      }
    } catch (error) {
      toast.error("Failed to delete job");
    } finally {
      setIsDeleting(false);
      setDeleteJobModalOpen(false);
    }
  };

  const handleGenerateCoverLetter = async (targetRole: string) => {
    setIsGenerating(true);
    try {
      const response = await fetch(`/api/jobs/${id}/cover-letter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_role: targetRole }),
      });

      if (response.ok) {
        const newLetter = await response.json();
        setCoverLetters([...coverLetters, newLetter]);
        toast.success("Cover letter generated");
      } else {
        toast.error("Failed to generate cover letter");
      }
    } catch (error) {
      toast.error("Failed to generate cover letter");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteContact = async () => {
    if (!contactToDelete) return;

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/jobs/${id}/contacts/${contactToDelete.id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        mutate(`/api/jobs/${id}/contacts`);
        mutate("/api/jobs");
        toast.success("Contact deleted");
      } else {
        toast.error("Failed to delete contact");
      }
    } catch (error) {
      toast.error("Failed to delete contact");
    } finally {
      setIsDeleting(false);
      setDeleteContactModalOpen(false);
      setContactToDelete(null);
    }
  };

  const openDeleteContactModal = (contact: Contact) => {
    setContactToDelete(contact);
    setDeleteContactModalOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/dashboard"
            className="p-2 hover:bg-[var(--color-bg-secondary)] rounded-lg transition-colors"
          >
            <ArrowLeft size={20} />
          </Link>
          <div>
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-2xl font-bold">{job.title}</h1>
              {job.is_favorite && (
                <span className="px-2 py-1 text-xs font-medium rounded bg-red-500/20 text-red-400 flex items-center gap-1">
                  <Heart size={12} className="fill-red-400" /> Favorite
                </span>
              )}
              {job.is_perfect_fit && (
                <span className="px-2 py-1 text-xs font-medium rounded bg-purple-500/20 text-purple-400">
                  Perfect Fit
                </span>
              )}
              {job.is_ai_forward && (
                <span className="px-2 py-1 text-xs font-medium rounded bg-blue-500/20 text-blue-400">
                  AI Forward
                </span>
              )}
              {job.is_easy_apply && (
                <span className="px-2 py-1 text-xs font-medium rounded bg-green-500/20 text-green-400">
                  Easy Apply
                </span>
              )}
              {!job.is_location_compatible && (
                <span className="px-2 py-1 text-xs font-medium rounded bg-orange-500/20 text-orange-400">
                  Location Restricted
                </span>
              )}
            </div>
            <p className="text-[var(--color-text-secondary)]">{job.company}</p>
            <p className="text-xs text-[var(--color-text-tertiary)] font-mono mt-1">
              Job ID: {job.id}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {job.url && (
            <a
              href={job.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-[#0077B5] text-white rounded-lg hover:bg-[#005885] transition-colors font-medium"
            >
              <Linkedin size={18} />
              Open in LinkedIn
            </a>
          )}
          <button
            onClick={() => setDeleteJobModalOpen(true)}
            className="p-2 text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
            title="Delete job"
          >
            <Trash2 size={20} />
          </button>
        </div>
      </div>

      {/* Key Details - Prominent Info Box */}
      <div className="bg-gradient-to-r from-[var(--color-bg-secondary)] to-[var(--color-bg-elevated)] rounded-xl border-2 border-[var(--color-accent)]/30 p-6 shadow-lg">
        <div className="grid grid-cols-3 gap-8">
          {/* Job Title */}
          <div className="flex items-start gap-4">
            <div className="p-3 bg-[var(--color-accent)]/20 rounded-lg">
              <Briefcase size={24} className="text-[var(--color-accent)]" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.15em] text-[var(--color-text-tertiary)] font-semibold mb-1">
                Position
              </p>
              <p className="text-xl font-bold text-[var(--color-text-primary)]">
                {job.title}
              </p>
              {job.employment_type && (
                <p className="text-sm text-[var(--color-text-secondary)] mt-1">
                  {employmentTypeLabels[job.employment_type] || job.employment_type}
                </p>
              )}
            </div>
          </div>

          {/* Compensation */}
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-lg ${job.salary_min || job.salary_max ? "bg-green-500/20" : "bg-[var(--color-bg-elevated)]"}`}>
              <DollarSign size={24} className={job.salary_min || job.salary_max ? "text-green-400" : "text-[var(--color-text-tertiary)]"} />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.15em] text-[var(--color-text-tertiary)] font-semibold mb-1">
                Compensation
              </p>
              <p className={`text-xl font-bold ${job.salary_min || job.salary_max ? "text-green-400" : "text-[var(--color-text-tertiary)]"}`}>
                {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
              </p>
              {(job.salary_min || job.salary_max) && (
                <p className="text-sm text-[var(--color-text-secondary)] mt-1">
                  per year
                </p>
              )}
            </div>
          </div>

          {/* Location */}
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-lg ${!job.is_location_compatible ? "bg-orange-500/20" : "bg-blue-500/20"}`}>
              <MapPin size={24} className={!job.is_location_compatible ? "text-orange-400" : "text-blue-400"} />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.15em] text-[var(--color-text-tertiary)] font-semibold mb-1">
                Location
              </p>
              <p className={`text-xl font-bold ${!job.is_location_compatible ? "text-orange-400" : "text-[var(--color-text-primary)]"}`}>
                {job.location || "Not specified"}
              </p>
              <div className="flex items-center gap-2 mt-1">
                {job.work_location_type && (
                  <span className={`text-sm px-2 py-0.5 rounded ${
                    job.work_location_type === "remote"
                      ? "bg-green-500/20 text-green-400"
                      : job.work_location_type === "hybrid"
                      ? "bg-yellow-500/20 text-yellow-400"
                      : "bg-blue-500/20 text-blue-400"
                  }`}>
                    {workLocationTypeLabels[job.work_location_type]}
                  </span>
                )}
                {!job.is_location_compatible && (
                  <span className="text-xs text-orange-400">Restricted</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* Role Fit Scores */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h3 className="text-[10px] uppercase tracking-[0.15em] text-[var(--color-text-tertiary)] mb-4 font-semibold text-center">
              Role Fit Scores
            </h3>
            <RolePriorityScores
              jobId={id}
              hasDescription={!!job.description_raw}
              fallbackPriority={job.priority}
            />
          </div>

          {/* Application Status */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h3 className="text-[10px] uppercase tracking-[0.15em] text-[var(--color-text-tertiary)] mb-4 font-semibold">
              Application Status
            </h3>
            <StatusPipeline
              currentStatus={job.status}
              onStatusChange={handleStatusChange}
              disabled={isUpdating}
            />
          </div>

          {/* Job Flags */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h3 className="text-[10px] uppercase tracking-[0.15em] text-[var(--color-text-tertiary)] mb-4 font-semibold">
              Job Flags
            </h3>
            <JobFlagsToggle
              isFavorite={job.is_favorite}
              isPerfectFit={job.is_perfect_fit}
              isAiForward={job.is_ai_forward}
              isEasyApply={job.is_easy_apply}
              onToggle={(flag, value) => handleUpdateJob({ [flag]: value })}
              disabled={isUpdating}
            />
          </div>

          {/* Decline Details Card - shown when rejected or withdrawn */}
          {(job.status === "rejected" || job.status === "withdrawn") && (
            <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
              <h2 className="text-lg font-semibold mb-4">Decline Details</h2>

              <div className="grid grid-cols-2 gap-6">
                {/* User Decline Reasons */}
                <div>
                  <DeclineReasonsPicker
                    type="user"
                    selectedReasons={job.user_decline_reasons || []}
                    onChange={(reasons) =>
                      handleUpdateJob({ user_decline_reasons: reasons.length > 0 ? reasons : null })
                    }
                    disabled={isUpdating}
                  />
                </div>

                {/* Company Decline Reasons */}
                <div>
                  <DeclineReasonsPicker
                    type="company"
                    selectedReasons={job.company_decline_reasons || []}
                    onChange={(reasons) =>
                      handleUpdateJob({ company_decline_reasons: reasons.length > 0 ? reasons : null })
                    }
                    disabled={isUpdating}
                  />
                </div>
              </div>

              {/* Decline Notes */}
              <div className="mt-4">
                <label className="block text-sm text-[var(--color-text-tertiary)] mb-1">
                  Additional Notes
                </label>
                <textarea
                  value={job.decline_notes || ""}
                  onChange={(e) => handleUpdateJob({ decline_notes: e.target.value || null })}
                  disabled={isUpdating}
                  rows={3}
                  placeholder="Any additional context about why this didn't work out..."
                  className="w-full px-3 py-2 bg-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--color-accent)] text-sm"
                />
              </div>
            </div>
          )}

          {/* Job Description */}
          {job.description_raw && (
            <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
              <h2 className="text-lg font-semibold mb-4">Job Description</h2>
              <div className="prose prose-invert max-w-none text-sm whitespace-pre-wrap">
                {job.description_raw}
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h2 className="text-lg font-semibold mb-4">Notes</h2>
            <JobNotes jobId={id} notes={job.notes} />
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Info */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h2 className="text-lg font-semibold mb-4">Timeline</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm">
                <Clock size={16} className="text-[var(--color-text-tertiary)]" />
                <span className="text-[var(--color-text-tertiary)]">Posted:</span>
                <span>
                  {job.posted_at
                    ? `${new Date(job.posted_at).toLocaleDateString()} (${formatPostedAge(job.posted_at)})`
                    : "-"}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock size={16} className="text-[var(--color-text-tertiary)]" />
                <span className="text-[var(--color-text-tertiary)]">Added:</span>
                <span>{new Date(job.created_at).toLocaleDateString()}</span>
              </div>
              {job.applied_at && (
                <div className="flex items-center gap-2 text-sm">
                  <Clock size={16} className="text-green-400" />
                  <span className="text-[var(--color-text-tertiary)]">Applied:</span>
                  <span>{new Date(job.applied_at).toLocaleDateString()}</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-sm">
                <Clock size={16} className="text-[var(--color-text-tertiary)]" />
                <span className="text-[var(--color-text-tertiary)]">Updated:</span>
                <span>{new Date(job.updated_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          {/* Contacts */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <User size={18} />
              Contacts
              {contacts && contacts.length > 0 && (
                <span className="text-xs bg-[var(--color-bg-elevated)] px-2 py-0.5 rounded-full text-[var(--color-text-secondary)]">
                  {contacts.length}
                </span>
              )}
            </h2>

            {contacts && contacts.length > 0 ? (
              <div className="space-y-3">
                {contacts.map((contact) => (
                  <div
                    key={contact.id}
                    className="p-3 bg-[var(--color-bg-elevated)] rounded-lg"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-sm">{contact.name}</p>
                        {contact.title && (
                          <p className="text-xs text-[var(--color-text-secondary)]">
                            {contact.title}
                          </p>
                        )}
                        <p className="text-xs text-[var(--color-text-tertiary)] mt-1">
                          {contactTypeLabels[contact.contact_type] || contact.contact_type}
                          {contact.is_job_poster && " • Job Poster"}
                        </p>
                      </div>
                      <div className="flex gap-1">
                        {contact.linkedin_url && (
                          <a
                            href={contact.linkedin_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 hover:bg-[var(--color-bg-secondary)] rounded transition-colors"
                            title="View LinkedIn"
                          >
                            <Linkedin size={14} className="text-[#0077B5]" />
                          </a>
                        )}
                        {contact.email && (
                          <a
                            href={`mailto:${contact.email}`}
                            className="p-1.5 hover:bg-[var(--color-bg-secondary)] rounded transition-colors"
                            title={contact.email}
                          >
                            <Mail size={14} className="text-[var(--color-text-secondary)]" />
                          </a>
                        )}
                        <button
                          onClick={() => openDeleteContactModal(contact)}
                          className="p-1.5 hover:bg-red-500/10 rounded transition-colors"
                          title="Delete contact"
                        >
                          <X size={14} className="text-[var(--color-text-tertiary)] hover:text-red-400" />
                        </button>
                      </div>
                    </div>
                    {contact.notes && (
                      <p className="text-xs text-[var(--color-text-tertiary)] mt-2 border-t border-[var(--color-border-subtle)] pt-2">
                        {contact.notes}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--color-text-tertiary)]">
                No contacts added yet
              </p>
            )}
          </div>

          {/* Cover Letter Generation */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <FileText size={18} />
                Cover Letter
              </h2>
              {coverLetters.length > 0 && (
                <span className="text-xs bg-[var(--color-bg-elevated)] px-2 py-0.5 rounded-full text-[var(--color-text-secondary)]">
                  {coverLetters.length}
                </span>
              )}
            </div>

            {job.description_raw ? (
              <div className="space-y-4">
                <div className="flex flex-wrap gap-2">
                  {roleTypes.map((r) => (
                    <button
                      key={r.value}
                      onClick={() => handleGenerateCoverLetter(r.value)}
                      disabled={isGenerating}
                      className="px-3 py-1.5 text-xs font-medium rounded-full border border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)] hover:border-[var(--color-accent)] hover:text-[var(--color-accent)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isGenerating ? "..." : r.label}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-[var(--color-text-tertiary)]">
                  Click a role to generate a tailored cover letter
                </p>
              </div>
            ) : (
              <p className="text-sm text-[var(--color-text-tertiary)]">
                Add a job description to generate cover letters
              </p>
            )}

            {coverLetters.length > 0 && (
              <div className="mt-4 pt-4 border-t border-[var(--color-border-subtle)] space-y-3">
                {coverLetters.map((letter) => (
                  <div
                    key={letter.id}
                    className="p-3 bg-[var(--color-bg-elevated)] rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium px-2 py-0.5 bg-[var(--color-bg-secondary)] rounded">
                        {roleTypes.find((r) => r.value === letter.target_role)?.label}
                      </span>
                      <span className="text-xs text-[var(--color-text-tertiary)]">
                        {new Date(letter.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-[var(--color-text-secondary)] line-clamp-3">
                      {letter.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Tags */}
          <div className="bg-[var(--color-bg-secondary)] rounded-xl border border-[var(--color-border-subtle)] p-6">
            <h2 className="text-lg font-semibold mb-4">Tags</h2>
            {job.tags && job.tags.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {job.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 text-xs bg-[var(--color-bg-elevated)] rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-[var(--color-text-tertiary)]">No tags</p>
            )}
          </div>
        </div>
      </div>

      {/* Delete Job Modal */}
      <ConfirmModal
        isOpen={deleteJobModalOpen}
        onClose={() => setDeleteJobModalOpen(false)}
        onConfirm={handleDeleteJob}
        title="Delete Job"
        message={`Are you sure you want to delete "${job.title}" at ${job.company}? This action cannot be undone.`}
        confirmLabel="Delete Job"
        variant="danger"
        isLoading={isDeleting}
      />

      {/* Delete Contact Modal */}
      <ConfirmModal
        isOpen={deleteContactModalOpen}
        onClose={() => {
          setDeleteContactModalOpen(false);
          setContactToDelete(null);
        }}
        onConfirm={handleDeleteContact}
        title="Delete Contact"
        message={contactToDelete ? `Are you sure you want to remove "${contactToDelete.name}" from this job?` : ""}
        confirmLabel="Delete Contact"
        variant="danger"
        isLoading={isDeleting}
      />
    </div>
  );
}
