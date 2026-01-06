import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8005";
const LOCAL_DEV_BYPASS =
  process.env.NODE_ENV !== "production" &&
  process.env.LOCAL_DEV_BYPASS === "true";

async function getAuthToken() {
  const cookieStore = await cookies();
  return cookieStore.get("auth_token")?.value;
}

function getAuthHeaders(token: string | undefined) {
  if (token) {
    return { "X-API-Key": token };
  }
  if (LOCAL_DEV_BYPASS) {
    return {};
  }
  return null;
}

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getAuthToken();
  const authHeaders = getAuthHeaders(token);
  if (!authHeaders) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { id } = await params;

  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/jobs/${id}`, {
      headers: {
        ...authHeaders,
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error fetching job:", error);
    return NextResponse.json(
      { error: "Failed to fetch job" },
      { status: 500 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getAuthToken();
  const authHeaders = getAuthHeaders(token);
  if (!authHeaders) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { id } = await params;

  try {
    const body = await request.json();
    const response = await fetch(`${BACKEND_URL}/api/v1/jobs/${id}`, {
      method: "PATCH",
      headers: {
        ...authHeaders,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error updating job:", error);
    return NextResponse.json(
      { error: "Failed to update job" },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const token = await getAuthToken();
  const authHeaders = getAuthHeaders(token);
  if (!authHeaders) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { id } = await params;

  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/jobs/${id}`, {
      method: "DELETE",
      headers: {
        ...authHeaders,
      },
    });

    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error deleting job:", error);
    return NextResponse.json(
      { error: "Failed to delete job" },
      { status: 500 }
    );
  }
}
