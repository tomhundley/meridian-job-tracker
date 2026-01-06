import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { DeclineReasonsPicker } from "../DeclineReasonsPicker";
import useSWR from "swr";

vi.mock("swr", () => ({
  default: vi.fn(),
}));

const mockUseSWR = useSWR as unknown as ReturnType<typeof vi.fn>;

const mockUserDeclineReasons = {
  categories: [
    {
      name: "compensation",
      display_name: "Compensation",
      reasons: [
        { code: "salary_too_low", display_name: "Salary below expectations", category: "compensation", description: null },
        { code: "benefits_inadequate", display_name: "Benefits not competitive", category: "compensation", description: null },
      ],
    },
    {
      name: "location",
      display_name: "Location & Remote",
      reasons: [
        { code: "not_remote", display_name: "Not fully remote", category: "location", description: null },
      ],
    },
  ],
};

const mockCompanyDeclineReasons = {
  categories: [
    {
      name: "candidate_selection",
      display_name: "Candidate Selection",
      reasons: [
        { code: "selected_other", display_name: "Selected another candidate", category: "candidate_selection", description: null },
      ],
    },
    {
      name: "experience_skills",
      display_name: "Experience & Skills",
      reasons: [
        { code: "insufficient_experience", display_name: "Not enough experience", category: "experience_skills", description: null },
        { code: "failed_technical", display_name: "Did not pass technical assessment", category: "experience_skills", description: null },
      ],
    },
  ],
};

describe("DeclineReasonsPicker", () => {
  beforeEach(() => {
    mockUseSWR.mockReset();
  });

  it("renders loading state", () => {
    mockUseSWR.mockReturnValue({ data: undefined, error: undefined, isLoading: true });
    render(
      <DeclineReasonsPicker type="user" selectedReasons={[]} onChange={() => {}} />
    );
    expect(screen.getByText("Loading reasons...")).toBeInTheDocument();
  });

  it("renders error state", () => {
    mockUseSWR.mockReturnValue({ data: undefined, error: new Error("boom"), isLoading: false });
    render(
      <DeclineReasonsPicker type="user" selectedReasons={[]} onChange={() => {}} />
    );
    expect(screen.getByText("Failed to load decline reasons")).toBeInTheDocument();
  });

  it("renders user decline reasons with correct title", () => {
    mockUseSWR.mockReturnValue({ data: mockUserDeclineReasons, error: undefined, isLoading: false });
    render(
      <DeclineReasonsPicker type="user" selectedReasons={[]} onChange={() => {}} />
    );
    expect(screen.getByText("Why did you pass?")).toBeInTheDocument();
    expect(screen.getByText("Compensation")).toBeInTheDocument();
    expect(screen.getByText("Location & Remote")).toBeInTheDocument();
  });

  it("renders company decline reasons with correct title", () => {
    mockUseSWR.mockReturnValue({ data: mockCompanyDeclineReasons, error: undefined, isLoading: false });
    render(
      <DeclineReasonsPicker type="company" selectedReasons={[]} onChange={() => {}} />
    );
    expect(screen.getByText("Why did they decline?")).toBeInTheDocument();
    expect(screen.getByText("Candidate Selection")).toBeInTheDocument();
    expect(screen.getByText("Experience & Skills")).toBeInTheDocument();
  });

  it("expands category when clicked", () => {
    mockUseSWR.mockReturnValue({ data: mockUserDeclineReasons, error: undefined, isLoading: false });
    render(
      <DeclineReasonsPicker type="user" selectedReasons={[]} onChange={() => {}} />
    );

    // Initially, reasons should not be visible
    expect(screen.queryByText("Salary below expectations")).not.toBeInTheDocument();

    // Click to expand
    fireEvent.click(screen.getByText("Compensation"));

    // Now reasons should be visible
    expect(screen.getByText("Salary below expectations")).toBeInTheDocument();
    expect(screen.getByText("Benefits not competitive")).toBeInTheDocument();
  });

  it("calls onChange when reason is selected", () => {
    mockUseSWR.mockReturnValue({ data: mockUserDeclineReasons, error: undefined, isLoading: false });
    const onChange = vi.fn();
    render(
      <DeclineReasonsPicker type="user" selectedReasons={[]} onChange={onChange} />
    );

    // Expand category
    fireEvent.click(screen.getByText("Compensation"));

    // Click checkbox
    const checkbox = screen.getByRole("checkbox", { name: /Salary below expectations/i });
    fireEvent.click(checkbox);

    expect(onChange).toHaveBeenCalledWith(["salary_too_low"]);
  });

  it("calls onChange when reason is deselected", () => {
    mockUseSWR.mockReturnValue({ data: mockUserDeclineReasons, error: undefined, isLoading: false });
    const onChange = vi.fn();
    render(
      <DeclineReasonsPicker
        type="user"
        selectedReasons={["salary_too_low"]}
        onChange={onChange}
      />
    );

    // Category should auto-expand because it has a selected reason
    // Click checkbox to deselect
    const checkbox = screen.getByRole("checkbox", { name: /Salary below expectations/i });
    fireEvent.click(checkbox);

    expect(onChange).toHaveBeenCalledWith([]);
  });

  it("shows selected count badge on category", () => {
    mockUseSWR.mockReturnValue({ data: mockUserDeclineReasons, error: undefined, isLoading: false });
    render(
      <DeclineReasonsPicker
        type="user"
        selectedReasons={["salary_too_low", "benefits_inadequate"]}
        onChange={() => {}}
      />
    );

    // Should show "2" badge on Compensation category
    expect(screen.getByText("2")).toBeInTheDocument();
  });

  it("shows selected reasons as chips", () => {
    mockUseSWR.mockReturnValue({ data: mockUserDeclineReasons, error: undefined, isLoading: false });
    render(
      <DeclineReasonsPicker
        type="user"
        selectedReasons={["salary_too_low"]}
        onChange={() => {}}
      />
    );

    // Should show the selected reason as a chip (outside the category)
    const chips = screen.getAllByText("Salary below expectations");
    expect(chips.length).toBeGreaterThanOrEqual(1);
  });

  it("disables interactions when disabled prop is true", () => {
    mockUseSWR.mockReturnValue({ data: mockUserDeclineReasons, error: undefined, isLoading: false });
    const onChange = vi.fn();
    render(
      <DeclineReasonsPicker
        type="user"
        selectedReasons={["salary_too_low"]}
        onChange={onChange}
        disabled
      />
    );

    // Category should auto-expand because it has a selected reason
    // Checkbox should be disabled
    const checkbox = screen.getByRole("checkbox", { name: /Salary below expectations/i });
    expect(checkbox).toBeDisabled();

    // Clicking should not call onChange
    fireEvent.click(checkbox);
    expect(onChange).not.toHaveBeenCalled();
  });

  it("auto-expands categories with selected reasons", () => {
    mockUseSWR.mockReturnValue({ data: mockUserDeclineReasons, error: undefined, isLoading: false });
    render(
      <DeclineReasonsPicker
        type="user"
        selectedReasons={["not_remote"]}
        onChange={() => {}}
      />
    );

    // Location category should be auto-expanded because it has a selected reason
    // There will be multiple "Not fully remote" texts (checkbox label + chip)
    const elements = screen.getAllByText("Not fully remote");
    expect(elements.length).toBeGreaterThanOrEqual(1);
    // Verify there's a checkbox (meaning category is expanded)
    expect(screen.getByRole("checkbox", { name: /Not fully remote/i })).toBeInTheDocument();
  });
});
