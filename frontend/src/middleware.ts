import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const authToken = request.cookies.get("auth_token")?.value;
  const { pathname } = request.nextUrl;
  const localDevBypass =
    process.env.NODE_ENV !== "production" &&
    process.env.LOCAL_DEV_BYPASS === "true";

  if (localDevBypass) {
    if (pathname === "/login") {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
    return NextResponse.next();
  }

  // Public paths that don't require auth
  const publicPaths = ["/login", "/api/auth/verify"];
  const isPublicPath = publicPaths.some((path) => pathname.startsWith(path));

  // Allow public paths
  if (isPublicPath) {
    // If already logged in and trying to access login, redirect to dashboard
    if (pathname === "/login" && authToken) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }
    return NextResponse.next();
  }

  // Redirect to login if no auth token
  if (!authToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
