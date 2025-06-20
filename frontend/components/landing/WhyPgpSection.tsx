'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { PGPCard, PGPCardContent, PGPCardHeader, PGPCardTitle } from '@/components/ui/pgp-card';
import { ShieldCheck, Truck, DatabaseZap, Handshake, Wheat } from 'lucide-react';

// Main feature card on the left
const mainFeature = {
  title: 'Direct. Transparent. Traceable.',
  description: 'PrairieGrain was built on a simple idea: to create the most efficient and trustworthy path from the producer’s bin to the global buyer’s destination. We leverage technology to remove intermediaries, providing clear communication and unprecedented visibility into the supply chain.'
};

// Supporting features on the right
const supportingFeatures = [
  { icon: <Handshake />, title: 'Direct Producer Access', description: 'Negotiate directly with our network of verified Canadian Prairie producers.' },
  { icon: <ShieldCheck />, title: 'Assured Crop Quality', description: 'Access detailed crop data, from protein levels to grade, before you commit.' },
  { icon: <DatabaseZap />, title: 'Full Lot Traceability', description: 'Track your grain from the farm to the port for complete peace of mind.' },
  { icon: <Truck />, title: 'Streamlined Logistics', description: 'We handle the complexities of transport, documentation, and freight forwarding.' },
];

const WhyPgpSection = () => {
  return (
    <section id="features" className="py-24 sm:py-32 bg-background">
      <div className="container mx-auto px-4 md:px-6">
        {/* Section Header */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            Why Source Through PrairieGrain?
          </h2>
          <p className="mt-4 max-w-2xl mx-auto text-lg text-foreground/70">
            We provide the tools and trust necessary for modern agricultural trade.
          </p>
        </motion.div>

        {/* Asymmetrical Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Main Feature */}
          <motion.div
            className="lg:col-span-1"
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, amount: 0.3 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          >
            <PGPCard className="h-full p-6 bg-gradient-to-br from-stone-50 to-white shadow-xl">
              <PGPCardHeader>
                <div className="bg-primary/10 text-primary h-12 w-12 rounded-lg flex items-center justify-center mb-4">
                  <Wheat className="h-6 w-6" />
                </div>
                <PGPCardTitle className="text-2xl font-semibold">{mainFeature.title}</PGPCardTitle>
              </PGPCardHeader>
              <PGPCardContent>
                <p className="text-foreground/80">{mainFeature.description}</p>
              </PGPCardContent>
            </PGPCard>
          </motion.div>

          {/* Right Column: Supporting Features */}
          <motion.div 
            className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-8"
            variants={{
              visible: { transition: { staggerChildren: 0.2 } }
            }}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
          >
            {supportingFeatures.map((feature, i) => (
              <motion.div
                key={i}
                variants={{
                  hidden: { opacity: 0, y: 20 },
                  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
                }}
              >
                <PGPCard className="h-full transform hover:-translate-y-1 transition-transform duration-300 hover:shadow-lg">
                  <PGPCardHeader className="flex-row items-start gap-4">
                    <div className="flex-shrink-0 bg-primary/10 text-primary h-10 w-10 rounded-lg flex items-center justify-center">
                      {React.cloneElement(feature.icon, { className: 'h-5 w-5' })}
                    </div>
                    <div>
                      <PGPCardTitle className="text-lg">{feature.title}</PGPCardTitle>
                      <p className="mt-1 text-sm text-foreground/70">{feature.description}</p>
                    </div>
                  </PGPCardHeader>
                </PGPCard>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default WhyPgpSection;