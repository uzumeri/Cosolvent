import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}

export const scrollToRef = (
	ref: React.RefObject<HTMLDivElement | null>,
	options?: ScrollIntoViewOptions,
) => {
	const option = options ?? { behavior: "smooth" };
	if (ref) {
		ref.current?.scrollIntoView(option);
	}
};
