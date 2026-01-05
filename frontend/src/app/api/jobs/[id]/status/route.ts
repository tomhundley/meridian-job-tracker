import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

async function getAuthToken() {
  const cookieStore = await cookies();
  return cookieStore.get("auth_token")?.value;
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getAuthToken();
  if (!token) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { id } = await params;

  try {
    const body = await request.json();
    const response = await fetch(`${BACKEND_URL}/api/v1/jobs/${id}/status`, {
      method: "PATCH",
      headers: {
        "X-API-Key": token,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error updating job status:", error);
    return NextResponse.json(
      { error: "Failed to update job status" },
      { status: 500 }
    );
  }
}
