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
    "Sistem deteksi dini risiko stunting pada balita berbasis ML + XAI. Masukkan data balita untuk prediksi, analisis SHAP, dan rekomendasi.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="id" className={`${inter.variable} h-full`}>
      <body className="h-full font-sans" style={{ fontFamily: "var(--font-inter)" }}>
        {children}
      </body>
    </html>
  );
}
