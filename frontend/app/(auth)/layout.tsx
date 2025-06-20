import Link from "next/link";
import { Wheat } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen w-full flex flex-col">
      {/* Video Background & Overlay - SAME AS HERO */}
      <div className="absolute top-0 left-0 w-full h-full -z-10">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
          src="/videos/coverr-farming-field-50-1080p.mp4" // From your project structure
        ></video>
        <div className="absolute inset-0 bg-black/60"></div>
      </div>

      {/* Minimal Header with Logo */}
      <header className="relative z-20 flex-shrink-0">
        <div className="container mx-auto px-4 md:px-6">
          <div className="flex h-20 items-center">
            <Link href="/" className="flex items-center gap-2">
                <Wheat className="h-8 w-8 text-primary" />
                <span className="text-2xl font-bold text-white font-serif">PrairieGrain</span>
            </Link>
          </div>
        </div>
      </header>
      
      {/* Centered Content Area */}
      <main className="relative z-20 flex flex-grow items-center justify-center py-12 px-4">
        {children}
      </main>
    </div>
  );
}