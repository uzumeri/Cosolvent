import { getSession } from "@/lib/api/getSession";
import type { Session } from "@/store/authStore";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";
import { AdminSidebar } from "@/components/admin/AdminSidebar";

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

	if (session.user.role !== "admin") {
		if (session.user.role === "user") {
			redirect("/user");
		}
		redirect("/signin");
	}

	return (
		<div className="flex h-screen bg-slate-950 overflow-hidden">
			<AdminSidebar />
			<main className="flex-1 overflow-y-auto bg-slate-950 text-slate-50 p-8">
				<div className="max-w-6xl mx-auto">
					{children}
				</div>
			</main>
		</div>
	);
}
