'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { FilePlus2, Users, Handshake, Search, Award, Truck } from 'lucide-react';
import { PGPCard, PGPCardContent } from '@/components/ui/pgp-card';

const steps = [
    { side: 'buyer', icon: <FilePlus2 />, title: "Submit Your RFQ", description: "Post your detailed grain requirements—crop, grade, specs, and volume. It's free and takes minutes." },
    { side: 'producer', icon: <Search />, title: "Find Global RFQs", description: "Access a live list of quotation requests from qualified global buyers that match your offerings." },
    { side: 'buyer', icon: <Users />, title: "Receive Direct Offers", description: "Verified producers submit competitive, transparent offers directly to you. No intermediaries." },
    { side: 'producer', icon: <Award />, title: "Submit Your Offer", description: "Showcase your quality, price, and terms directly to the buyer. Highlight your certifications." },
    { side: 'buyer', icon: <Handshake />, title: "Award & Ship", description: "Accept the best offer. We coordinate the logistics, from container stuffing to final delivery." },
    { side: 'producer', icon: <Truck />, title: "Fulfill & Get Paid", description: "Once accepted, deliver to the designated container terminal and get paid securely via PGP." },
];

const HowItWorksSection = () => {
    return (
        <section id="process" className="py-24 sm:py-32 bg-white border-y border-stone-200">
            <div className="container mx-auto px-4 md:px-6">
                <motion.div
                    className="text-center mb-20"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8 }}
                >
                    <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">A Clear Path for Everyone</h2>
                    <p className="mt-4 max-w-2xl mx-auto text-lg text-foreground/70">
                        Our process is designed for transparency and efficiency for both sides of the marketplace.
                    </p>
                </motion.div>

                <div className="relative max-w-4xl mx-auto">
                    {/* The Timeline */}
                    <motion.div 
                        className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-stone-200"
                        initial={{ height: 0 }}
                        whileInView={{ height: "100%" }}
                        viewport={{ once: true, amount: 0.2 }}
                        transition={{ duration: 2, ease: 'easeOut' }}
                    />

                    {/* Steps */}
                    <div className="space-y-12">
                        {steps.map((step, index) => {
                            const isBuyer = step.side === 'buyer';
                            const cardVariants = {
                                hidden: { opacity: 0, x: isBuyer ? -50 : 50 },
                                visible: { opacity: 1, x: 0, transition: { duration: 0.6, ease: 'easeOut' } }
                            };

                            return (
                                <div key={index} className="relative flex justify-center items-center">
                                    <motion.div
                                        className={`w-full md:w-[calc(50%-2rem)] ${isBuyer ? 'md:mr-auto' : 'md:ml-auto md:text-right'}`}
                                        variants={cardVariants}
                                        initial="hidden"
                                        whileInView="visible"
                                        viewport={{ once: true, amount: 0.5 }}
                                    >
                                        <PGPCard className={`shadow-lg text-left ${isBuyer ? 'border-l-4 border-primary' : 'border-r-4 border-stone-400'}`}>
                                            <PGPCardContent className="p-6">
                                                <div className="flex items-start gap-4">
                                                    <div className={`flex-shrink-0 h-10 w-10 rounded-full flex items-center justify-center ${isBuyer ? 'bg-primary/10 text-primary' : 'bg-stone-100 text-stone-500'}`}>
                                                        {React.cloneElement(step.icon, { className: 'w-5 h-5' })}
                                                    </div>
                                                    <div>
                                                        <h3 className="font-semibold text-lg text-foreground">{step.title}</h3>
                                                        <p className="text-sm text-foreground/70 mt-1">{step.description}</p>
                                                    </div>
                                                </div>
                                            </PGPCardContent>
                                        </PGPCard>
                                    </motion.div>
                                    {/* Timeline Circle */}
                                    <motion.div 
                                        className={`absolute left-1/2 -translate-x-1/2 h-4 w-4 rounded-full border-2 border-stone-200 bg-background`}
                                        initial={{ scale: 0 }}
                                        whileInView={{ scale: 1 }}
                                        viewport={{ once: true, amount: 0.5 }}
                                        transition={{ duration: 0.5, delay: 0.2 }}
                                    />
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
        </section>
    );
};

export default HowItWorksSection;