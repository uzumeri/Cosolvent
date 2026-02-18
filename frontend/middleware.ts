import { getSessionCookie } from "better-auth/cookies";
import { type NextRequest, NextResponse } from "next/server";

export async function middleware(request: NextRequest) {
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
