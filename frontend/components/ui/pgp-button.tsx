"use client";
import { type VariantProps, cva } from "class-variance-authority";
import React from "react";

const pgpButtonVariants = cva(
	"inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-semibold ring-offset-background transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 transform active:scale-95",
	{
		variants: {
			variant: {
				primary:
					"bg-primary text-primary-foreground shadow-lg shadow-primary/20 hover:bg-primary-hover",
				outline:
					"border border-stone-300 bg-transparent hover:bg-stone-100 text-foreground",
			},
			size: {
				md: "h-10 px-4 py-2",
				lg: "h-12 rounded-lg px-8 text-base",
			},
		},
		defaultVariants: {
			variant: "primary",
			size: "md",
		},
	},
);

export interface PGPButtonProps
	extends React.ButtonHTMLAttributes<HTMLButtonElement>,
		VariantProps<typeof pgpButtonVariants> {}

const PGPButton = React.forwardRef<HTMLButtonElement, PGPButtonProps>(
	({ className, variant, size, ...props }, ref) => {
		return (
			<button
				className={pgpButtonVariants({ variant, size, className })}
				ref={ref}
				{...props}
			/>
		);
	},
);
PGPButton.displayName = "PGPButton";

export { PGPButton };
