import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { JobsTable } from "../JobsTable";
import useSWR from "swr";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("swr", () => ({
  default: vi.fn(),
}));

const mockUseSWR = useSWR as unknown as ReturnType<typeof vi.fn>;

describe("JobsTable", () => {
  beforeEach(() => {
    mockUseSWR.mockReset();
  });

  it("renders loading state", () => {
    mockUseSWR.mockReturnValue({ data: undefined, error: undefined, isLoading: true });
    render(<JobsTable />);
    expect(screen.getByText("Loading jobs...")).toBeInTheDocument();
  });

  it("renders error state", () => {
    mockUseSWR.mockReturnValue({ data: undefined, error: new Error("boom"), isLoading: false });
    render(<JobsTable />);
    expect(screen.getByText("Failed to load jobs")).toBeInTheDocument();
  });

  it("renders empty state", () => {
    mockUseSWR.mockReturnValue({ data: { items: [] }, error: undefined, isLoading: false });
    render(<JobsTable />);
    expect(screen.getByText("No jobs found. Add your first job to get started.")).toBeInTheDocument();
    expect(screen.getByText("Add Job")).toBeInTheDocument();
  });

  it("renders job rows", () => {
    mockUseSWR.mockReturnValue({
      data: {
        items: [
          {
            id: "job-1",
            title: "Engineer",
            company: "Acme",
            location: "Remote",
            status: "applied",
            priority: 80,
            created_at: new Date("2024-01-01").toISOString(),
            applied_at: null,
          },
        ],
      },
      error: undefined,
      isLoading: false,
    });
    render(<JobsTable />);
    expect(screen.getByText("Engineer")).toBeInTheDocument();
    expect(screen.getByText("Acme")).toBeInTheDocument();
    expect(screen.getByText("Remote")).toBeInTheDocument();
  });
});
