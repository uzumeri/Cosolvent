import env from "@/config/env";
import { betterAuth } from "better-auth";
import { mongodbAdapter } from "better-auth/adapters/mongodb";
import { connectToDB } from "./db";
import { admin, openAPI } from "better-auth/plugins";

const db = await connectToDB();

export const auth = betterAuth({
	secret: env.BETTER_AUTH_SECRET,
	database: mongodbAdapter(db),
	emailAndPassword: {
		enabled: true,
	},
	plugins: [openAPI(),admin()],
});
