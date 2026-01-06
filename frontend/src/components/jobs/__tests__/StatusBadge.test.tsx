import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusBadge } from "../StatusBadge";

describe("StatusBadge", () => {
  it("renders the mapped label", () => {
    render(<StatusBadge status="applied" />);
    expect(screen.getByText("Applied")).toBeInTheDocument();
  });

  it("falls back to raw status for unknown values", () => {
    render(<StatusBadge status="custom_status" />);
    expect(screen.getByText("custom_status")).toBeInTheDocument();
  });
});
