import { authClient } from "@/lib/auth-client";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";

export default async function AdminLayout({
	children,
}: {
	children: ReactNode;
}) {
	const session = await authClient.getSession();

	if (!session || !session.data) {
		redirect("/signin");
	}

	// Second, check if the user's role is 'admin'
	if (session.data.user.role !== "admin") {
		redirect("/user");
	}

	// If all checks pass, render the child page
	return <>{children}</>;
}
