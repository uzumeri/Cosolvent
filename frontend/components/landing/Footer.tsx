import React from 'react';
import Link from 'next/link';
import { Wheat, MoveRight } from 'lucide-react';
import { PGPButton } from '@/components/ui/pgp-button';

const LandingFooter = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-stone-100 border-t border-stone-200">
      <div className="container mx-auto px-4 md:px-6">
        
        {/* Call to Action Block */}
        <div className="py-16 text-center border-b border-stone-200">
            <h2 className="text-4xl font-bold font-serif text-foreground">Ready to streamline your grain trading?</h2>
            <p className="mt-4 max-w-xl mx-auto text-lg text-foreground/70">
                Join our network of forward-thinking producers and global buyers today.
            </p>
            <div className="mt-8 flex justify-center gap-4">
                <PGPButton size="lg" variant="primary">
                    Get Started Now <MoveRight className="w-5 h-5 ml-2" />
                </PGPButton>
            </div>
        </div>

        {/* Links Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 py-16">
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <Wheat className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold text-foreground font-serif">PrairieGrain</span>
            </Link>
            <p className="text-foreground/70 text-sm">
                Directly connecting global buyers with Canada's finest grain producers.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-foreground mb-4">Marketplace</h4>
            <ul className="space-y-3">
              <li><Link href="#" className="text-sm text-foreground/70 hover:text-primary transition-colors">Submit an RFQ</Link></li>
              <li><Link href="#live-offerings" className="text-sm text-foreground/70 hover:text-primary transition-colors">Live Offerings</Link></li>
              <li><Link href="#producers" className="text-sm text-foreground/70 hover:text-primary transition-colors">Browse Producers</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-foreground mb-4">Resources</h4>
            <ul className="space-y-3">
              <li><Link href="#" className="text-sm text-foreground/70 hover:text-primary transition-colors">Logistics Services</Link></li>
              <li><Link href="#" className="text-sm text-foreground/70 hover:text-primary transition-colors">Quality Assurance</Link></li>
              <li><Link href="#" className="text-sm text-foreground/70 hover:text-primary transition-colors">Help Center</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-foreground mb-4">Company</h4>
            <ul className="space-y-3">
              <li><Link href="#" className="text-sm text-foreground/70 hover:text-primary transition-colors">About Us</Link></li>
              <li><Link href="#" className="text-sm text-foreground/70 hover:text-primary transition-colors">Contact</Link></li>
              <li><Link href="#" className="text-sm text-foreground/70 hover:text-primary transition-colors">Careers</Link></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-4 border-t border-stone-200 pt-8 pb-12 flex flex-col sm:flex-row justify-between items-center text-sm text-foreground/60">
          <p>&copy; {currentYear} Prairie Grain Portal Inc. All Rights Reserved.</p>
          <div className="flex gap-4 mt-4 sm:mt-0">
            <Link href="#" className="hover:text-primary transition-colors">Terms of Service</Link>
            <Link href="#" className="hover:text-primary transition-colors">Privacy Policy</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default LandingFooter;