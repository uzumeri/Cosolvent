'use client';
import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Link from 'next/link';
import { PGPButton } from '@/components/ui/pgp-button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import SignUpStepper from '@/components/auth/SignUpStepper';
import { Check, User, Building } from 'lucide-react';

const steps = ["Account", "Profile", "Finish"];
type Role = 'buyer' | 'producer' | null;

export default function SignUpPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [role, setRole] = useState<Role>(null);

  const handleNext = () => setCurrentStep(prev => prev < steps.length - 1 ? prev + 1 : prev);
  const handlePrev = () => setCurrentStep(prev => prev > 0 ? prev - 1 : prev);

  const motionVariants = {
    initial: { opacity: 0, y: 30 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -30 },
  };

  const inputStyles = "bg-white/5 border-white/20 text-white placeholder:text-stone-400 focus-visible:ring-primary/50";

  // The return statement is now corrected (no stray '>')
  return (
    // The entire component is wrapped in the new glassmorphism container
    <motion.div
      className="w-full max-w-2xl text-white rounded-2xl border border-white/10 bg-white/5 p-8 shadow-2xl backdrop-blur-lg"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: 'easeOut' }}
    >
        <div className="text-center">
            <div className="w-full flex justify-center mb-8">
                <SignUpStepper currentStep={currentStep} steps={steps} />
            </div>
            <AnimatePresence mode="wait">
                <motion.div key={`title-${currentStep}`} variants={motionVariants} initial="initial" animate="animate" exit="exit" transition={{ duration: 0.3 }}>
                    <h1 className="text-4xl md:text-5xl font-bold font-serif">
                        {currentStep === 0 && "Create Your Account"}
                        {currentStep === 1 && "Tell Us About Yourself"}
                        {currentStep === 2 && "You're All Set!"}
                    </h1>
                    <p className="mt-3 text-lg text-stone-300">
                        {currentStep === 0 && "Step 1: Let's start with the basics."}
                        {currentStep === 1 && "Step 2: Are you here to buy or sell?"}
                        {currentStep === 2 && "A verification link has been sent to your email."}
                    </p>
                </motion.div>
            </AnimatePresence>
        </div>

        <div className="mt-10">
            <AnimatePresence mode="wait">
                <motion.div
                    key={`content-${currentStep}`}
                    variants={motionVariants}
                    initial="initial"
                    animate="animate"
                    exit="exit"
                    transition={{ duration: 0.3 }}
                    className="space-y-6"
                >
                    {currentStep === 0 && (
                        <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); handleNext(); }}>
                            <div className="space-y-2"><Label className="text-stone-300">Email Address</Label><Input type="email" required className={inputStyles} /></div>
                            <div className="space-y-2"><Label className="text-stone-300">Password</Label><Input type="password" required className={inputStyles} /></div>
                            <div className="space-y-2"><Label className="text-stone-300">Confirm Password</Label><Input type="password" required className={inputStyles} /></div>
                            <PGPButton type="submit" className="w-full" size="lg">Continue</PGPButton>
                        </form>
                    )}

                    {currentStep === 1 && (
                        <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); handleNext(); }}>
                            <div className="space-y-2"><Label className="text-stone-300">Select Your Role</Label><div className="grid grid-cols-2 gap-4"><RoleCard icon={<User />} title="I'm a Buyer" description="Source quality grain" selected={role === 'buyer'} onClick={() => setRole('buyer')} /><RoleCard icon={<Building />} title="I'm a Producer" description="Sell your harvest" selected={role === 'producer'} onClick={() => setRole('producer')} /></div></div>
                            <div className="space-y-2"><Label className="text-stone-300">Full Name</Label><Input required className={inputStyles} /></div>
                            <div className="space-y-2"><Label className="text-stone-300">Company Name (Optional)</Label><Input className={inputStyles} /></div>
                            <div className="flex gap-4"><PGPButton type="button" variant="outline" onClick={handlePrev} className="w-full text-white border-white/50 hover:bg-white/10">Back</PGPButton><PGPButton type="submit" className="w-full">Continue</PGPButton></div>
                        </form>
                    )}

                    {currentStep === 2 && (
                        <div className="text-center">
                            <div className="flex justify-center mb-4"><div className="h-16 w-16 bg-green-500/20 text-green-300 rounded-full flex items-center justify-center border border-green-400"><Check className="h-8 w-8" /></div></div>
                            <p className="text-stone-300 mb-6">Please check your inbox to complete your registration and gain access to the marketplace.</p>
                            <Link href="/login"><PGPButton className="w-full sm:w-1/2 mx-auto" size="lg">Go to Login</PGPButton></Link>
                        </div>
                    )}
                </motion.div>
            </AnimatePresence>
        </div>

        <div className="mt-8 text-center text-sm">
            <p className="text-stone-300">
                Already have an account?{' '}
                <Link href="/login" className="font-semibold text-white hover:underline">
                    Log In
                </Link>
            </p>
        </div>
    </motion.div>
  );
}

// Helper component for Role Selection Cards
const RoleCard = ({ icon, title, description, selected, onClick }: { icon: React.ReactNode, title: string, description: string, selected: boolean, onClick: () => void }) => (
    <div onClick={onClick} className={`p-4 rounded-lg cursor-pointer transition-all duration-200 text-left ${selected ? 'border-2 border-primary bg-primary/10 shadow-lg' : 'border border-white/20 bg-white/5 hover:bg-white/10'}`}>
        <div className={`mb-2 h-10 w-10 flex items-center justify-center rounded-full transition-colors ${selected ? 'bg-primary text-primary-foreground' : 'bg-white/10 text-white'}`}>
            {icon}
        </div>
        <h3 className="font-semibold text-white">{title}</h3>
        <p className="text-sm text-stone-300">{description}</p>
    </div>
);