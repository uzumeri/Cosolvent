"use client";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { PGPButton } from "@/components/ui/pgp-button";
import { motion } from "framer-motion";
import Link from "next/link";

export default function SignInPage() {
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
					Log in to access the marketplace.
				</p>
			</div>

			<form className="mt-8 space-y-6">
				<div className="space-y-2">
					<Label htmlFor="email" className="text-stone-300">
						Email Address
					</Label>
					<Input
						id="email"
						type="email"
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
						type="password"
						required
						className="bg-white/5 border-white/20 text-white placeholder:text-stone-400 focus-visible:ring-primary/50"
					/>
				</div>
				<PGPButton type="submit" className="w-full" size="lg">
					Log In
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
