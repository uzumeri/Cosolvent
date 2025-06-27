import env from "@/config/env";
import { createAuthClient } from "better-auth/react";
import { nextCookies } from "better-auth/next-js";
import { adminClient, inferAdditionalFields } from "better-auth/client/plugins";

export const authClient = createAuthClient({
	baseURL: `${env.NEXT_PUBLIC_API_BASE_URL}/auth/api/auth`,
	plugins: [
		nextCookies(),
		adminClient(),
		inferAdditionalFields({
			user: {
				userType: {
					type: "string",
					input: true,
				},
			},
		}),
	],
});

export const { useSession } = authClient;
