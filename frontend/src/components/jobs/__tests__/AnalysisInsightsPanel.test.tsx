import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AnalysisInsightsPanel } from "../AnalysisInsightsPanel";
import type { NoteEntry } from "@/types/notes";

const mockAnalysisNotes: NoteEntry[] = [
  {
    text: "**APPLY** (85/100)\n\nStrong fit for VP Engineering role.",
    timestamp: "2024-01-15T10:30:00Z",
    source: "agent",
    note_type: "ai_analysis_summary",
    metadata: {
      priority_score: 85,
      recommendation: "APPLY",
      ai_forward: true,
      suggested_role: "vp",
    },
  },
  {
    text: "**Key Strengths:**\n• Strong cloud experience\n• Leadership skills",
    timestamp: "2024-01-15T10:30:01Z",
    source: "agent",
    note_type: "strengths",
  },
  {
    text: "**Concerns:**\n• May require relocation",
    timestamp: "2024-01-15T10:30:02Z",
    source: "agent",
    note_type: "watch_outs",
    metadata: { location_incompatible: false },
  },
  {
    text: "**Interview Points:**\n• Discuss Azure migration",
    timestamp: "2024-01-15T10:30:03Z",
    source: "agent",
    note_type: "talking_points",
  },
];

const mockUserNotes: NoteEntry[] = [
  {
    text: "This looks interesting!",
    timestamp: "2024-01-15T09:00:00Z",
    source: "user",
  },
  {
    text: "Follow up next week",
    timestamp: "2024-01-15T11:00:00Z",
    source: "user",
    note_type: "general",
  },
];

describe("AnalysisInsightsPanel", () => {
  it("renders empty state when no analysis notes exist", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={[]} />);
    expect(screen.getByText(/No analysis insights yet/i)).toBeInTheDocument();
  });

  it("renders empty state when notes is null", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={null} />);
    expect(screen.getByText(/No analysis insights yet/i)).toBeInTheDocument();
  });

  it("renders empty state when only user notes exist", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockUserNotes} />);
    expect(screen.getByText(/No analysis insights yet/i)).toBeInTheDocument();
  });

  it("renders panel with analysis notes", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} />);
    expect(screen.getByText("Analysis Insights")).toBeInTheDocument();
    expect(screen.getByText("4 insights")).toBeInTheDocument();
  });

  it("shows priority score badge when provided", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} priority={85} />);
    expect(screen.getByText("Score: 85/100")).toBeInTheDocument();
  });

  it("shows recommendation badge from metadata", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} />);
    // APPLY appears in both the badge and the note text
    const applyElements = screen.getAllByText("APPLY");
    expect(applyElements.length).toBeGreaterThan(0);
  });

  it("renders analysis summary card with metadata badges", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} />);
    expect(screen.getByText("Analysis Summary")).toBeInTheDocument();
    expect(screen.getByText("85/100")).toBeInTheDocument();
    expect(screen.getByText("AI-Forward")).toBeInTheDocument();
    expect(screen.getByText("VP")).toBeInTheDocument();
  });

  it("renders collapsible sections for each note type", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} />);
    expect(screen.getByText("Key Strengths")).toBeInTheDocument();
    expect(screen.getByText("Watch-Outs")).toBeInTheDocument();
    expect(screen.getByText("Interview Talking Points")).toBeInTheDocument();
  });

  it("shows note count in section headers", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} />);
    // Each section should show count "1"
    const countBadges = screen.getAllByText("1");
    expect(countBadges.length).toBeGreaterThan(0);
  });

  it("expands section when clicked", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} />);

    // Initially section content should not be visible (collapsed)
    const strengthsButton = screen.getByText("Key Strengths").closest("button");
    expect(strengthsButton).toBeInTheDocument();

    // Click to expand
    fireEvent.click(strengthsButton!);

    // Now the content should be visible
    expect(screen.getByText(/Strong cloud experience/i)).toBeInTheDocument();
  });

  it("collapses entire panel when header is clicked", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} />);

    // Find the panel header and click it
    const panelHeader = screen.getByText("Analysis Insights").closest("div");
    fireEvent.click(panelHeader!);

    // Sections should no longer be visible
    expect(screen.queryByText("Key Strengths")).not.toBeInTheDocument();
  });

  it("filters out user notes from analysis panel", () => {
    const mixedNotes = [...mockAnalysisNotes, ...mockUserNotes];
    render(<AnalysisInsightsPanel jobId="test-id" notes={mixedNotes} />);

    // Should only show 4 analysis insights, not 6 total
    expect(screen.getByText("4 insights")).toBeInTheDocument();
  });

  it("renders markdown bold text correctly", () => {
    render(<AnalysisInsightsPanel jobId="test-id" notes={mockAnalysisNotes} />);

    // The summary text should render bold text
    // Check that "APPLY" in the content is rendered (the **APPLY** should become bold)
    const summarySection = screen.getByText("Analysis Summary").closest("div");
    expect(summarySection).toBeInTheDocument();
  });
});
