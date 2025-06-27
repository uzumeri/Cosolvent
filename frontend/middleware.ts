import { type NextRequest, NextResponse } from "next/server";
import { getSessionCookie } from "better-auth/cookies";

export async function middleware(request: NextRequest) {
	// getCookieCache is the recommended way to quickly check for a session
	const session = getSessionCookie(request);

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
