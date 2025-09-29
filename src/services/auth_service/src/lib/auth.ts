import env from "@/config/env";
import { betterAuth } from "better-auth";
import { admin, openAPI } from "better-auth/plugins";
import { beforeSignUp } from "@/hooks/createAuth";
import { Pool } from "pg";

export const auth = betterAuth({
	secret: env.BETTER_AUTH_SECRET,
	database: new Pool({ connectionString: env.DATABASE_URL }),
	trustedOrigins: [env.FRONTEND_URL],
	emailAndPassword: {
		enabled: true,
	},
	user: {
		additionalFields: {
			userType: {
				type: "string",
				input: true,
			},
		},
	},
	hooks: {
		before: beforeSignUp(),
	},
	plugins: [openAPI(), admin()],
});
