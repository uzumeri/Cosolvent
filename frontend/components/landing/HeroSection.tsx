'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { PGPButton } from '@/components/ui/pgp-button';
import { ChevronDown } from 'lucide-react';

const HeroSection = () => {
  return (
    <section className="relative w-full h-screen flex flex-col items-center justify-center text-center overflow-hidden">
      {/* Video Background */}
      <div className="absolute top-0 left-0 w-full h-full -z-10">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-cover"
          // Using a high-quality, royalty-free video of a wheat field
          src="videos/coverr-farming-field-50-1080p.mp4"
        ></video>
        {/* Dark overlay for text readability */}
        <div className="absolute inset-0 bg-black/50"></div>
      </div>

      {/* Content */}
      <motion.div
        className="container relative z-10 px-4 md:px-6"
        initial="hidden"
        animate="visible"
        variants={{
          hidden: {},
          visible: { transition: { staggerChildren: 0.3 } },
        }}
      >
        <motion.h1
          className="text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-7xl font-serif"
          variants={{
            hidden: { opacity: 0, y: 30 },
            visible: { opacity: 1, y: 0, transition: { type: 'spring', duration: 1.5, bounce: 0.4 } },
          }}
        >
          Source Identity-Preserved Canadian Grain
        </motion.h1>
        <motion.p
          className="mt-6 max-w-3xl mx-auto text-lg md:text-xl text-stone-200"
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: 'easeOut' } },
          }}
        >
          Your direct, transparent link to verified Prairie producers for high-quality, containerized grain exports.
        </motion.p>
        <motion.div
          className="mt-10 flex flex-col sm:flex-row justify-center gap-4"
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: 'easeOut' } },
          }}
        >
          <PGPButton size="lg" variant="primary">Submit an RFQ</PGPButton>
          <PGPButton size="lg" variant="outline" className="bg-white/10 border-white/20 text-white backdrop-blur-sm hover:bg-white/20">
            Browse Producer Listings
          </PGPButton>
        </motion.div>
      </motion.div>
      
      {/* Animated Scroll Down Indicator */}
      <motion.div 
        className="absolute bottom-10"
        initial={{ opacity: 0, y: 0 }}
        animate={{ opacity: 1, y: 10 }}
        transition={{ duration: 1.5, repeat: Infinity, repeatType: 'reverse', ease: 'easeInOut' }}
      >
        <ChevronDown className="w-8 h-8 text-white/50" />
      </motion.div>
    </section>
  );
};
export default HeroSection;