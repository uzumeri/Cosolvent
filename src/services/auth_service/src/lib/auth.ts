import env from "@/config/env";
import { betterAuth } from "better-auth";
import { mongodbAdapter } from "better-auth/adapters/mongodb";
import { connectToDB } from "./db";
import { admin, openAPI } from "better-auth/plugins";
import { beforeSignUp } from "@/hooks/createAuth";

const db = await connectToDB();

export const auth = betterAuth({
	secret: env.BETTER_AUTH_SECRET,
	database: mongodbAdapter(db),
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
