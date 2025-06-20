'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { PGPCard, PGPCardContent, PGPCardHeader, PGPCardTitle } from '../ui/pgp-card';
import { PGPButton } from '../ui/pgp-button';
import { BadgeCheck, MapPin } from 'lucide-react';
import Image from 'next/image';

const producers = [
  { name: 'Clearwater Organics', location: 'Saskatchewan', image: '/images/producer-1.jpg', certs: ['Pro-Cert Organic', 'Non-GMO Project'] },
  { name: 'Durum King Farms', location: 'Alberta', image: '/images/producer-2.jpg', certs: ['CSGA Certified Seed', 'HACCP Certified'] },
  { name: 'Prairie Pulses Inc.', location: 'Manitoba', image: '/images/producer-3.jpg', certs: ['GlobalG.A.P.', 'ISO 22000'] },
];

const containerVariants = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.2 } }
};

const cardVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 100, duration: 0.8 } }
};

const ProducersSection = () => {
  return (
    <section id="producers" className="py-24 sm:py-32 bg-background">
      <div className="container mx-auto px-4 md:px-6">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Meet Our Verified Producers
          </h2>
          <p className="mt-4 max-w-2xl mx-auto text-lg text-foreground/70">
            The foundation of our marketplace is a network of Canada's most reputable and quality-driven operations.
          </p>
        </motion.div>
        
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
        >
          {producers.map((producer) => (
            <motion.div key={producer.name} variants={cardVariants}>
              <PGPCard className="overflow-hidden h-full flex flex-col text-left group">
                <div className="overflow-hidden relative">
                  <Image src={producer.image} alt={producer.name} width={400} height={250} className="w-full h-56 object-cover group-hover:scale-105 transition-transform duration-500 ease-in-out" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/0"></div>
                  <div className="absolute top-4 right-4 flex items-center gap-1.5 text-xs bg-primary text-primary-foreground font-bold px-3 py-1.5 rounded-full">
                    <BadgeCheck className="h-4 w-4"/>PGP Verified
                  </div>
                </div>
                
                <PGPCardHeader>
                    <PGPCardTitle className="text-2xl font-serif">{producer.name}</PGPCardTitle>
                    <p className="text-sm text-foreground/70 flex items-center gap-1.5 mt-1">
                        <MapPin className="h-4 w-4" /> {producer.location}
                    </p>
                </PGPCardHeader>

                <PGPCardContent className="flex flex-col flex-grow">
                  <div className="flex-grow">
                      <p className="text-sm font-semibold text-foreground/80 mb-2">Key Certifications:</p>
                      <div className="flex flex-wrap gap-2">
                          {producer.certs.map(cert => (
                              <span key={cert} className="text-xs font-medium bg-stone-100 text-foreground/80 px-2 py-1 rounded-full border border-stone-200">{cert}</span>
                          ))}
                      </div>
                  </div>
                  <PGPButton variant="outline" className="mt-6 w-full group-hover:bg-primary group-hover:text-primary-foreground group-hover:border-primary transition-all duration-300">
                    View Profile
                  </PGPButton>
                </PGPCardContent>
              </PGPCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
};

export default ProducersSection;