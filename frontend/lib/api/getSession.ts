import type { Session } from "@/store/authStore";
import type { ReadonlyRequestCookies } from "next/dist/server/web/spec-extension/adapters/request-cookies";

const INTERNAL_API_BASE_URL = process.env.INTERNAL_API_BASE_URL || "http://localhost";

export const getSession = async (
	cookies: ReadonlyRequestCookies,
): Promise<Session> => {
	const sessionToken = cookies.get("better-auth.session_token")?.value;

	if (!sessionToken) {
		throw new Error("Session token not found");
	}

	const response = await fetch(`${INTERNAL_API_BASE_URL}/api/auth/get-session`, {
		headers: {
			cookie: `better-auth.session_token=${sessionToken}`,
		},
	});

	if (!response.ok) {
		throw new Error(`Session validation failed: ${response.status}`);
	}

	return response.json();
};
