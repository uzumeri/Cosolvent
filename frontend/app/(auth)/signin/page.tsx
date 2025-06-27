"use client";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PGPButton } from "@/components/ui/pgp-button";
import { useSession } from "@/lib/auth-client";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { z } from "zod";
import { signIn, type signInSchema } from "./signin";

type SignInStatus = "idle" | "loading" | "success" | "error";

export default function SignInPage() {
	const router = useRouter();
	const { refetch, data } = useSession();
	const [status, setStatus] = useState<SignInStatus>("idle");
	const [callbackUrl, setCallbackUrl] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [formData, setFormData] = useState<z.infer<typeof signInSchema>>({
		email: "",
		password: "",
		callbackUrl: null,
	});

	const handleFormChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		setFormData({ ...formData, [event.target.name]: event.target.value });
	};

	const handleFormSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		setError(null);
		setStatus("loading");

		if (callbackUrl) {
			formData.callbackUrl = callbackUrl;
		}

		const result = await signIn(formData);

		if (result?.error) {
			setError(result.error);
			setStatus("error");
			return;
		}

		refetch();
		setStatus("success");
		setFormData({
			email: "",
			password: "",
			callbackUrl: null,
		});
	};

	// Get callbackUrl from window.location.search
	useEffect(() => {
		if (typeof window !== "undefined") {
			const params = new URLSearchParams(window.location.search);
			const url = params.get("callbackUrl");
			setCallbackUrl(url);
		}
	}, []);

	useEffect(() => {
		if (status === "success") {
			if (callbackUrl) {
				router.push(callbackUrl);
			}

			if (data?.user.role === "admin") {
				router.push("/admin");
			}

			router.push("/user");
		}
	}, [status, router.push, data, callbackUrl]);

	return (
		// This is the new glassmorphism container
		<motion.div
			className="w-full max-w-md text-white rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg"
			initial={{ opacity: 0, y: 20 }}
			animate={{ opacity: 1, y: 0 }}
			transition={{ duration: 0.7, ease: "easeOut" }}
		>
			<div className="text-center">
				<h1 className="text-4xl font-bold font-serif">Welcome Back</h1>
				<p className="mt-3 text-lg text-stone-300">
					Sign in to access the marketplace.
				</p>
			</div>

			<form onSubmit={handleFormSubmit} className="mt-8 space-y-6">
				{error && (
					<div className="bg-red-500/20 border border-red-500/50 text-red-300 text-sm rounded-lg p-3 text-center">
						{error}
					</div>
				)}
				<div className="space-y-2">
					<Label htmlFor="email" className="text-stone-300">
						Email Address
					</Label>
					<Input
						id="email"
						name="email"
						type="email"
						onChange={handleFormChange}
						value={formData.email}
						placeholder="you@company.com"
						required
						className="bg-white/5 border-white/20 text-white placeholder:text-stone-400 focus-visible:ring-primary/50"
					/>
				</div>
				<div className="space-y-2">
					<div className="flex items-center justify-between">
						<Label htmlFor="password" className="text-stone-300">
							Password
						</Label>
						<Link
							href="#"
							className="text-sm text-primary/80 hover:text-primary font-medium transition-colors"
						>
							Forgot Password?
						</Link>
					</div>
					<Input
						id="password"
						name="password"
						type="password"
						onChange={handleFormChange}
						value={formData.password}
						required
						className="bg-white/5 border-white/20 text-white placeholder:text-stone-400 focus-visible:ring-primary/50"
					/>
				</div>
				<PGPButton
					type="submit"
					className="w-full"
					size="lg"
					disabled={status === "loading"}
				>
					Sign In
				</PGPButton>
			</form>

			<div className="mt-8 text-center text-sm">
				<p className="text-stone-300">
					Don't have an account?{" "}
					<Link
						href="/signup"
						className="font-semibold text-white hover:underline"
					>
						Sign Up
					</Link>
				</p>
			</div>
		</motion.div>
	);
}
