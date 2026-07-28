import Navbar from "@/components/landing/Navbar";
import ScrollProgress from "@/components/landing/ScrollProgress";
import HeroSection from "@/components/landing/HeroSection";
import MasalahSection from "@/components/landing/MasalahSection";
import MetodologiSection from "@/components/landing/MetodologiSection";
import HasilTrainingSection from "@/components/landing/HasilTrainingSection";
import InterpretasiSection from "@/components/landing/InterpretasiSection";
import CaraKerjaSection from "@/components/landing/CaraKerjaSection";
import PenelitiSection from "@/components/landing/PenelitiSection";
import CTASection from "@/components/landing/CTASection";

export default function LandingPage() {
  return (
    <>
      <ScrollProgress />
      <Navbar />
      <HeroSection />
      <MasalahSection />
      <MetodologiSection />
      <HasilTrainingSection />
      <InterpretasiSection />
      <CaraKerjaSection />
      <PenelitiSection />
      <CTASection />
    </>
  );
}