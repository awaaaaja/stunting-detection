"use client";
import { motion } from "framer-motion";

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <motion.div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: "url(/images/hero-baby.jpg)" }}
        initial={{ scale: 1 }}
        whileInView={{ scale: 1.05 }}
        viewport={{ once: true }}
        transition={{ duration: 10, ease: "linear" }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-teal-900/80 via-teal-800/70 to-teal-950/90" />

      <div className="relative z-10 max-w-4xl mx-auto px-4 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight">
            Deteksi Dini Risiko <br />
            <span className="text-teal-300">Stunting pada Balita</span>
          </h1>
        </motion.div>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-6 text-base sm:text-lg text-white/80 max-w-2xl mx-auto leading-relaxed"
        >
          Sistem berbasis Machine Learning, SHAP Explainability, dan RAG &mdash;
          akurat <strong>99.04%</strong>, interpretable, dan berbasis pedoman
          nasional PNPK & WHO.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <a
            href="/dashboard"
            className="w-full sm:w-auto text-center px-8 py-3.5 rounded-xl bg-white text-teal-900 font-semibold text-base hover:bg-teal-50 transition-all shadow-lg hover:shadow-xl active:scale-[0.97]"
          >
            Coba Dashboard Gratis
          </a>
          <button
            onClick={() =>
              document
                .getElementById("metodologi")
                ?.scrollIntoView({ behavior: "smooth" })
            }
            className="w-full sm:w-auto text-center px-8 py-3.5 rounded-xl border-2 border-white/30 text-white font-medium text-base hover:bg-white/10 transition-all active:scale-[0.97]"
          >
            Pelajari Metodologi
          </button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-16 grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 max-w-3xl mx-auto"
        >
          {[
            ["99.04%", "Akurasi Model"],
            ["38.487", "Data Balita"],
            ["4 Kelas", "Klasifikasi"],
            ["100%", "RAG Sukses"],
          ].map(([val, label]) => (
            <div
              key={label}
              className="text-center p-3 rounded-xl bg-white/10 backdrop-blur-sm border border-white/10"
            >
              <div className="text-xl sm:text-2xl font-bold text-white">
                {val}
              </div>
              <div className="text-xs text-white/70 mt-0.5">{label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}