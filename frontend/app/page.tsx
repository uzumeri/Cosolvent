import LandingHeader from '@/components/landing/Header';
import LandingFooter from '@/components/landing/Footer';
import HeroSection from '@/components/landing/HeroSection';
import WhyPgpSection from '@/components/landing/WhyPgpSection';
import ProducersSection from '@/components/landing/ProducersSection';
import HowItWorksSection from '@/components/landing/HowItWorksSection';
import LiveOfferingsSection from '@/components/landing/LiveOfferingsSection';

export default function HomePage() {
  return (
    <>
      <LandingHeader />
      <main>
        <HeroSection />
        <WhyPgpSection />
        <LiveOfferingsSection />
        <ProducersSection />
        <HowItWorksSection />
      </main>
      <LandingFooter />
    </>
  );
}