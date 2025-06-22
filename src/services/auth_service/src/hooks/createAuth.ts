import { allowedUserTypes, isValidUserType } from "@/models/user";
import { APIError } from "better-auth/api";
import { createAuthMiddleware } from "better-auth/plugins";

type AuthContext = {
	path: string;
	body: {
		name?: string;
		email?: string;
		password?: string;
		userType?: string;
	};
};

export const beforeSignUp = () => {
	return createAuthMiddleware(async (ctx: AuthContext) => {
		if (ctx.path !== "/sign-up/email") {
			return;
		}

		const { userType } = ctx.body || {};

		if (!isValidUserType(userType)) {
			throw new APIError("BAD_REQUEST", {
				message: `Invalid or missing userType. Must be one of these values: ${allowedUserTypes.join(", ")}`,
			});
		}
	});
};
