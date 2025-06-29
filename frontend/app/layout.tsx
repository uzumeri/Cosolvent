import type { Metadata } from "next";
import { Geist, Geist_Mono, Inter, Lora, Roboto } from "next/font/google";
import "./globals.css";
import Chatbot from "@/components/chatbot/chatbot";
import { QueryProvider } from "@/lib/query/queryProvider";
import { AuthProvider } from "@/providers/authProvider";

const inter = Inter({
	subsets: ["latin"],
	variable: "--font-sans",
});

const lora = Lora({
	subsets: ["latin"],
	variable: "--font-serif",
	weight: ["400", "500", "600", "700"],
});

const roboto = Roboto({
	variable: "--font-roboto",
	subsets: ["latin"],
});

const geistSans = Geist({
	variable: "--font-geist-sans",
	subsets: ["latin"],
});

const geistMono = Geist_Mono({
	variable: "--font-geist-mono",
	subsets: ["latin"],
});

export const metadata: Metadata = {
	title: "Prairie Grain Portal | Direct Access to Canadian Grain",
	description:
		"Source high-quality, identity-preserved grain directly from verified Canadian Prairie producers. Streamlined logistics and full traceability for global buyers.",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en" className={`${inter.variable} ${lora.variable}`}>
			<body
				className={`${geistSans.variable} ${geistMono.variable} ${roboto.variable} antialiased`}
			>
				<AuthProvider>
					<QueryProvider>
						<Chatbot />
						{children}
					</QueryProvider>
				</AuthProvider>
			</body>
		</html>
	);
}
