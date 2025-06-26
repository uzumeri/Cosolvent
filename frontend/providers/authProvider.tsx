"use client";

import { useEffect } from "react";
import { useSession } from "@/lib/auth-client";
import { type Session, useAuthStore } from "@/store/authStore";

export function AuthProvider({ children }: { children: React.ReactNode }) {
	const { data: session, isPending } = useSession();
	const { setSession, setPending } = useAuthStore();

	useEffect(() => {
		setPending(isPending);

		if (!isPending) {
			setSession(session as Session | null);
		}
	}, [session, isPending, setSession, setPending]);

	return <>{children}</>;
}
