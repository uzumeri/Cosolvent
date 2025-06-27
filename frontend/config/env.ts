import { z } from "zod";

const EnvSchema = z.object({
	NODE_ENV: z
		.enum(["development", "test", "production"])
		.default("development"),
	NEXT_PUBLIC_API_BASE_URL: z.string().url(),
	NEXT_PUBLIC_APP_URL: z.string().url(),
});

const parsed = EnvSchema.safeParse({
	NODE_ENV: process.env.NODE_ENV,
	NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
	NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
});

if (!parsed.success) {
	console.error("Invalid environment variables:");
	console.error(JSON.stringify(parsed.error.flatten().fieldErrors, null, 2));
	throw new Error("Invalid environment variables");
}

const env = parsed.data;

export type Env = typeof env;
export default env;
