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

function getAuthHeaders(token: string | undefined): Record<string, string> | null {
  if (token) {
    return { "X-API-Key": token };
  }
  if (LOCAL_DEV_BYPASS) {
    return {};
  }
  return null;
}

export async function GET(request: NextRequest) {
  const token = await getAuthToken();
  const authHeaders = getAuthHeaders(token);
  if (!authHeaders) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const { searchParams } = new URL(request.url);
  const type = searchParams.get("type") || "user";

  try {
    const response = await fetch(
      `${BACKEND_URL}/api/v1/decline-reasons/${type}`,
      {
        headers: authHeaders,
      }
    );

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Error fetching decline reasons:", error);
    return NextResponse.json(
      { error: "Failed to fetch decline reasons" },
      { status: 500 }
    );
  }
}
