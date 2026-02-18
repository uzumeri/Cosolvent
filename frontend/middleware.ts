import { getSessionCookie } from "better-auth/cookies";
import { type NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
	// Debug: log all cookies
	const allCookies = request.cookies.getAll();
	console.log("[Middleware] Path:", request.nextUrl.pathname);
	console.log("[Middleware] Cookies:", JSON.stringify(allCookies.map(c => c.name)));

	// getCookieCache is the recommended way to quickly check for a session
	const session = getSessionCookie(request);
	console.log("[Middleware] Session cookie found:", !!session);

	if (!session) {
		const callbackUrl = encodeURIComponent(request.url);
		return NextResponse.redirect(
			new URL(`/signin?callbackUrl=${callbackUrl}`, request.url),
		);
	}

	return NextResponse.next();
}

export const config = {
	matcher: ["/user/:path*", "/admin/:path*"],
};
