import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "StuntingDetect — Deteksi Dini Risiko Stunting",
  description:
    "Sistem berbasis ML (Random Forest 99.04%), SHAP Explainability, dan RAG berbasis PNPK & WHO untuk klasifikasi risiko stunting pada balita. Dibangun dari 38.487 sampel Riskesdas 2018.",
  openGraph: {
    title: "StuntingDetect",
    description:
      "Deteksi dini risiko stunting dengan AI — akurat, interpretable, berbasis pedoman nasional.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id" className={`${inter.variable} h-full`}>
      <body
        className="h-full font-sans antialiased"
        style={{ fontFamily: "var(--font-inter)" }}
      >
        {children}
      </body>
    </html>
  );
}