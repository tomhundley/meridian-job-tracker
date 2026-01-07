import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { JobsTable } from "../JobsTable";
import useSWRInfinite from "swr/infinite";

vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("swr/infinite", () => ({
  default: vi.fn(),
}));

const mockUseSWRInfinite = useSWRInfinite as unknown as ReturnType<typeof vi.fn>;

const createMockJob = (overrides = {}) => ({
  id: "job-1",
  title: "Engineer",
  company: "Acme",
  location: "Remote",
  work_location_type: "remote",
  status: "applied",
  priority: 80,
  created_at: new Date("2024-01-01").toISOString(),
  updated_at: new Date("2024-01-01").toISOString(),
  applied_at: null,
  posted_at: null,
  salary_min: null,
  salary_max: null,
  salary_currency: null,
  employment_type: null,
  contact_count: 0,
  is_easy_apply: false,
  is_favorite: false,
  is_perfect_fit: false,
  is_ai_forward: false,
  ...overrides,
});

describe("JobsTable", () => {
  beforeEach(() => {
    mockUseSWRInfinite.mockReset();
  });

  it("renders loading state", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: undefined,
      error: undefined,
      isLoading: true,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    render(<JobsTable />);
    expect(screen.getByText("Loading jobs...")).toBeInTheDocument();
  });

  it("renders error state", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: undefined,
      error: new Error("boom"),
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    render(<JobsTable />);
    expect(screen.getByText("Failed to load jobs")).toBeInTheDocument();
  });

  it("renders empty state", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{ items: [], total: 0, total_pages: 0 }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    render(<JobsTable />);
    expect(screen.getByText("No jobs found. Add your first job to get started.")).toBeInTheDocument();
    expect(screen.getByText("Add Job")).toBeInTheDocument();
  });

  it("renders job rows", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{ items: [createMockJob()], total: 1, total_pages: 1 }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    render(<JobsTable />);
    expect(screen.getByText("Engineer")).toBeInTheDocument();
    expect(screen.getByText("Acme")).toBeInTheDocument();
    // Remote appears in both location column and work_location_type badge
    expect(screen.getAllByText("Remote")).toHaveLength(2);
  });

  it("renders favorite icon when job is favorited", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{ items: [createMockJob({ is_favorite: true })], total: 1, total_pages: 1 }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    const { container } = render(<JobsTable />);
    // Heart icon should be rendered with fill-red-400 class when favorited
    const heartIcon = container.querySelector(".fill-red-400");
    expect(heartIcon).toBeInTheDocument();
  });

  it("does not render favorite icon when job is not favorited", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{ items: [createMockJob({ is_favorite: false })], total: 1, total_pages: 1 }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    const { container } = render(<JobsTable />);
    // Heart icon with fill should not be rendered
    const heartIcon = container.querySelector(".fill-red-400");
    expect(heartIcon).not.toBeInTheDocument();
  });

  it("renders easy apply icon when enabled", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{ items: [createMockJob({ is_easy_apply: true })], total: 1, total_pages: 1 }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    const { container } = render(<JobsTable />);
    const zapIcon = container.querySelector(".text-green-400");
    expect(zapIcon).toBeInTheDocument();
  });

  it("renders perfect fit icon when enabled", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{ items: [createMockJob({ is_perfect_fit: true })], total: 1, total_pages: 1 }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    const { container } = render(<JobsTable />);
    const targetIcon = container.querySelector(".text-purple-400");
    expect(targetIcon).toBeInTheDocument();
  });

  it("renders AI forward icon when enabled", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{ items: [createMockJob({ is_ai_forward: true })], total: 1, total_pages: 1 }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    const { container } = render(<JobsTable />);
    const sparklesIcon = container.querySelector(".text-cyan-400");
    expect(sparklesIcon).toBeInTheDocument();
  });

  it("renders all preference icons together", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{
        items: [
          createMockJob({
            is_favorite: true,
            is_easy_apply: true,
            is_perfect_fit: true,
            is_ai_forward: true,
          }),
        ],
        total: 1,
        total_pages: 1,
      }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    const { container } = render(<JobsTable />);
    expect(container.querySelector(".fill-red-400")).toBeInTheDocument(); // favorite
    expect(container.querySelector(".text-green-400")).toBeInTheDocument(); // easy apply
    expect(container.querySelector(".text-purple-400")).toBeInTheDocument(); // perfect fit
    expect(container.querySelector(".text-cyan-400")).toBeInTheDocument(); // ai forward
  });

  it("displays total job count", () => {
    mockUseSWRInfinite.mockReturnValue({
      data: [{ items: [createMockJob()], total: 62, total_pages: 2 }],
      error: undefined,
      isLoading: false,
      isValidating: false,
      size: 1,
      setSize: vi.fn(),
      mutate: vi.fn(),
    });
    render(<JobsTable />);
    expect(screen.getByText("1")).toBeInTheDocument(); // showing
    expect(screen.getByText("62")).toBeInTheDocument(); // total
  });
});
