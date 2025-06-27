import { getSession } from "@/lib/api/getSession";
import type { Session } from "@/store/authStore";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";

export default async function AdminLayout({
	children,
}: {
	children: ReactNode;
}) {
	let session: Session;

	try {
		session = await getSession(await cookies());
	} catch (error) {
		// Session token missing or invalid
		redirect("/signin");
	}

	if (session.user.role === "admin") {
		return <>{children}</>;
	}

	if (session.user.role === "user") {
		redirect("/user");
	}

	redirect("/signin");
}
