import type { Session } from "@/store/authStore";
import type { ReadonlyRequestCookies } from "next/dist/server/web/spec-extension/adapters/request-cookies";
import axiosInstance from "./axios";

export const getSession = async (
	cookies: ReadonlyRequestCookies,
): Promise<Session> => {
	const sessionToken = cookies.get("better-auth.session_token")?.value;

	if (!sessionToken) {
		throw new Error("Session token not found");
	}

	const response = await axiosInstance.get<Session>("/api/auth/get-session", {
		headers: {
			cookie: `better-auth.session_token=${sessionToken}`,
		},
	});

	return response.data;
};
