'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { PGPButton } from '@/components/ui/pgp-button';
import { Wheat } from 'lucide-react';

const LandingHeader = () => {
  const [scrolled, setScrolled] = useState(false);

  // Effect to detect scroll
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };

    window.addEventListener('scroll', handleScroll);
    // Cleanup function to remove the event listener
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <header 
      className={`fixed top-0 z-50 w-full transition-all duration-300 ease-in-out ${scrolled ? 'bg-background/70 backdrop-blur-lg border-b border-stone-200 shadow-sm' : 'bg-transparent'}`}
    >
      <div className="container mx-auto flex h-20 items-center justify-between px-4 md:px-6">
        <Link href="/" className="flex items-center gap-2">
          <Wheat className="h-8 w-8 text-primary" />
          <span className={`text-2xl font-bold font-serif transition-colors ${scrolled ? 'text-foreground' : 'text-white'}`}>
            PrairieGrain
          </span>
        </Link>
        <nav className="hidden items-center gap-8 md:flex">
          <Link href="#features" className={`text-base font-medium transition-colors ${scrolled ? 'text-foreground/70 hover:text-foreground' : 'text-stone-300 hover:text-white'}`}>
            Why PGP?
          </Link>
          <Link href="#live-offerings" className={`text-base font-medium transition-colors ${scrolled ? 'text-foreground/70 hover:text-foreground' : 'text-stone-300 hover:text-white'}`}>
            Live Offerings
          </Link>
          <Link href="#producers" className={`text-base font-medium transition-colors ${scrolled ? 'text-foreground/70 hover:text-foreground' : 'text-stone-300 hover:text-white'}`}>
            Producers
          </Link>
        </nav>
        <div className="flex items-center gap-2">
          <PGPButton 
            variant="outline" 
            size="md"
            className={!scrolled ? 'text-white border-white/50 hover:bg-white/10' : ''}
          >
            Log In
          </PGPButton>
          <PGPButton variant="primary" size="md">
            Sign Up
          </PGPButton>
        </div>
      </div>
    </header>
  );
};

export default LandingHeader;