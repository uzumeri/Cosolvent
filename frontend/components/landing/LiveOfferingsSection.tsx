'use client';
import React from 'react';
import { motion } from 'framer-motion';
import { PGPCard } from '../ui/pgp-card';
import { PGPButton } from '../ui/pgp-button';
import { Tag, Scale, MapPin } from 'lucide-react';

const offerings = [
    { crop: '#1 CWRS Wheat', protein: '14.5%', tonnage: 250, origin: 'Rosetown, SK' },
    { crop: 'No. 2 Canada Canola', oilContent: '45%', tonnage: 500, origin: 'Lethbridge, AB' },
    { crop: 'Laird No. 1 Lentils', tonnage: 150, origin: 'Moose Jaw, SK' },
    { crop: 'Organic Malting Barley', tonnage: 100, origin: 'Virden, MB' }
];

const LiveOfferingsSection = () => {
    return (
        <section id="live-offerings" className="py-24 sm:py-32 bg-white border-y border-stone-200">
            <div className="container mx-auto px-4 md:px-6">
                <motion.div
                    className="text-center mb-16"
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8 }}
                >
                    <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">Live Producer Offerings</h2>
                    <p className="mt-4 max-w-2xl mx-auto text-lg text-foreground/70">
                       Browse current, ready-to-ship grain lots available directly from our verified producers.
                    </p>
                </motion.div>
                
                <div className="max-w-5xl mx-auto">
                    {/* Table Header */}
                    <div className="hidden md:grid grid-cols-6 gap-4 px-6 mb-4 text-sm font-semibold text-foreground/60 tracking-wider uppercase">
                        <div className="col-span-3"><span>Crop & Details</span></div>
                        <div className="text-right"><span>Tonnage (MT)</span></div>
                        <div className="text-right"><span>Origin</span></div>
                        <div className="text-right"><span>Action</span></div>
                    </div>

                    {/* Offerings List */}
                    <motion.div 
                        className="space-y-4"
                        variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true, amount: 0.2 }}
                    >
                        {offerings.map((lot, index) => (
                            <motion.div
                                key={index}
                                variants={{
                                    hidden: { opacity: 0, y: 20 },
                                    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
                                }}
                            >
                                <PGPCard className="transition-all duration-300 hover:shadow-xl hover:border-primary/50">
                                    <div className="grid grid-cols-2 md:grid-cols-6 items-center gap-4 p-4">
                                        {/* Main Info */}
                                        <div className="col-span-2 md:col-span-3">
                                            <h3 className="text-lg font-semibold text-foreground">{lot.crop}</h3>
                                            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-foreground/60 mt-1">
                                                {lot.protein && <span className="flex items-center gap-1.5"><Tag className="h-4 w-4" />Protein: {lot.protein}</span>}
                                                {lot.oilContent && <span className="flex items-center gap-1.5"><Tag className="h-4 w-4" />Oil: {lot.oilContent}</span>}
                                            </div>
                                        </div>

                                        {/* Tonnage */}
                                        <div className="text-right font-medium">{lot.tonnage}</div>

                                        {/* Origin */}
                                        <div className="text-right text-sm text-foreground/70">{lot.origin}</div>

                                        {/* Action Button */}
                                        <div className="col-span-2 md:col-span-1 text-right">
                                            <PGPButton variant='primary'>Request Quote</PGPButton>
                                        </div>
                                    </div>
                                </PGPCard>
                            </motion.div>
                        ))}
                    </motion.div>
                </div>
            </div>
        </section>
    );
};
export default LiveOfferingsSection;