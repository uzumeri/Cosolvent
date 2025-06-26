import { create } from "zustand";

export enum UserType {
	SELLER = "SELLER",
	BUYER = "BUYER",
	FARMER = "FARMER",
	SERVICE_PROVIDER = "SERVICE_PROVIDER",
}

export interface Session {
	user: {
		id: string;
		name: string;
		email: string;
		emailVerified: boolean;
		role: "admin" | "user";
		userType: UserType;
	};
	session: {
		id: string;
		expiresAt: string;
		token: string;
		createdAt: string;
		updatedAt: string;
		ipAddress: string;
		userAgent: string;
	};
}

// state's shape
interface AuthState {
	session: Session | null;
	role: "admin" | "user" | null;
	userType: UserType | null;
	isPending: boolean;
	error: Error | null;
	// Action to update, set, or clear the session
	setSession: (session: Session | null) => void;
	setPending: (isPending: boolean) => void;
	setError: (error: Error | null) => void;
	clearSession: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
	// Initial state
	session: null,
	role: null,
	userType: null,
	isPending: true, // Start in a pending state until we check the session
	error: null,

	// --- Actions ---

	setSession: (sessionData) =>
		set({
			session: sessionData,
			role: sessionData?.user?.role ?? null,
			userType: sessionData?.user?.userType ?? null,
			isPending: false,
			error: null,
		}),

	setPending: (isPending) => set({ isPending }),

	setError: (error) => set({ error, isPending: false }),

	// Action for logging out
	clearSession: () =>
		set({
			session: null,
			role: null,
			userType: null,
			isPending: false,
		}),
}));
