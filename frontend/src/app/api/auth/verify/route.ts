import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8005";
const LOCAL_DEV_BYPASS =
  process.env.NODE_ENV !== "production" &&
  process.env.LOCAL_DEV_BYPASS === "true";

export async function GET() {
  if (LOCAL_DEV_BYPASS) {
    return NextResponse.json({ valid: true, bypass: true });
  }

  const cookieStore = await cookies();
  const token = cookieStore.get("auth_token")?.value;

  if (!token) {
    return NextResponse.json({ valid: false }, { status: 401 });
  }

  try {
    // Verify token by making a request to the backend
    const response = await fetch(`${BACKEND_URL}/api/v1/jobs?limit=1`, {
      headers: {
        "X-API-Key": token,
      },
    });

    if (response.ok) {
      return NextResponse.json({ valid: true });
    } else {
      return NextResponse.json({ valid: false }, { status: 401 });
    }
  } catch (error) {
    console.error("Error verifying auth:", error);
    return NextResponse.json({ valid: false }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { apiKey } = await request.json();

    if (LOCAL_DEV_BYPASS) {
      const cookieStore = await cookies();
      cookieStore.set("auth_token", apiKey || "local-dev", {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        maxAge: 60 * 60 * 24 * 30, // 30 days
      });

      return NextResponse.json({ success: true, bypass: true });
    }

    if (!apiKey) {
      return NextResponse.json(
        { error: "API key is required" },
        { status: 400 }
      );
    }

    // Verify the API key against the backend
    const response = await fetch(`${BACKEND_URL}/api/v1/jobs?limit=1`, {
      headers: {
        "X-API-Key": apiKey,
      },
    });

    if (response.ok) {
      // Set the auth cookie
      const cookieStore = await cookies();
      cookieStore.set("auth_token", apiKey, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        sameSite: "lax",
        path: "/",
        maxAge: 60 * 60 * 24 * 30, // 30 days
      });

      return NextResponse.json({ success: true });
    } else {
      return NextResponse.json(
        { error: "Invalid API key" },
        { status: 401 }
      );
    }
  } catch (error) {
    console.error("Error during login:", error);
    return NextResponse.json(
      { error: "Authentication failed" },
      { status: 500 }
    );
  }
}
