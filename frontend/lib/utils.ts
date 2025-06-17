import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export const scrollToBottom = (ref: React.RefObject<HTMLDivElement | null>) => {
	if (ref) {
		ref.current?.scrollIntoView({ behavior: "smooth" });
	}
};
