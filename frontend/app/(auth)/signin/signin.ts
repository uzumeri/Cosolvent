import env from "@/config/env";
import { authClient } from "@/lib/auth-client";
import { z } from "zod";

export const signInSchema = z.object({
	email: z.string().email("Invalid email address."),
	password: z.string().min(8, "Password must be at least 8 characters."),
	callbackUrl: z.string().url("Invalid callback URL.").nullable(),
});

type ActionResponse = { error: string | null; success: boolean };

export async function signIn(
	formData: z.infer<typeof signInSchema>,
): Promise<ActionResponse> {
	// Check for null values first
	if (!formData.email || !formData.password) {
		return { error: "Email and password are required.", success: false };
	}

	// Validate form input with Zod
	const parseResult = signInSchema.safeParse(formData);

	if (!parseResult.success) {
		const errorMessage = parseResult.error.errors
			.map((e) => e.message)
			.join(", ");
		return { error: errorMessage, success: false };
	}

	const { email, password, callbackUrl } = parseResult.data;

	if (callbackUrl) {
		try {
			const parsedUrl = new URL(callbackUrl);
			if (env.NEXT_PUBLIC_APP_URL !== parsedUrl.origin) {
				return { error: "Invalid callback URL origin.", success: false };
			}
		} catch {
			return { error: "Malformed callback URL.", success: false };
		}
	}

	const result = await authClient.signIn.email({ email, password });
	console.log(result);

	if (result.error) {
		return { error: "Invalid email or password.", success: false };
	}

	return { error: null, success: true };
}
