import LandingFooter from "@/components/landing/Footer";
import LandingHeader from "@/components/landing/Header";
import HeroSection from "@/components/landing/HeroSection";
import HowItWorksSection from "@/components/landing/HowItWorksSection";
import LiveOfferingsSection from "@/components/landing/LiveOfferingsSection";
import ProducersSection from "@/components/landing/ProducersSection";
import WhyPgpSection from "@/components/landing/WhyPgpSection";

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
