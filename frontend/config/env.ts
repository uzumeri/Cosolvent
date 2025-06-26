import path from "node:path";
import { config } from "dotenv";
import { expand } from "dotenv-expand";
import { z } from "zod";

expand(
	config({
		path: path.resolve(
			process.cwd(),
			process.env.NODE_ENV === "test" ? ".env.test" : ".env",
		),
	}),
);

const EnvSchema = z.object({
	NODE_ENV: z
		.enum(["development", "test", "production"])
		.default("development"),
	NEXT_PUBLIC_API_BASE_URL: z.string().default("http://localhost/"),
});

// Validate env vars
const parsed = EnvSchema.safeParse(process.env);

if (!parsed.success) {
	console.error("Invalid environment variables:");
	console.error(JSON.stringify(parsed.error.flatten().fieldErrors, null, 2));
	process.exit(1);
}

const env = parsed.data;

export type Env = typeof env;
export default env;
