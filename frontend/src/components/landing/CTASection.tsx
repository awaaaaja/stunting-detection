"use client";
import { motion } from "framer-motion";

export default function CTASection() {
  return (
    <section className="py-16 sm:py-20 px-4 bg-gradient-to-br from-teal-700 via-teal-600 to-teal-800">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="max-w-2xl mx-auto text-center"
      >
        <div className="w-16 h-16 rounded-2xl bg-white/20 flex items-center justify-center mx-auto">
          <span className="text-3xl">🩺</span>
        </div>
        <h2 className="mt-6 text-2xl sm:text-3xl font-bold text-white">
          Siap Melakukan Deteksi?
        </h2>
        <p className="mt-3 text-teal-100/80 max-w-lg mx-auto text-sm sm:text-base">
          Masukkan data antropometri balita &mdash; dapatkan prediksi, analisis
          SHAP, dan rekomendasi berbasis pedoman nasional dalam hitungan detik.
        </p>
        <motion.a
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          href="/dashboard"
          className="inline-block mt-8 px-8 sm:px-10 py-4 rounded-xl bg-white text-teal-800 font-semibold text-base sm:text-lg shadow-xl hover:shadow-2xl transition-shadow"
        >
          Coba Dashboard Gratis &rarr;
        </motion.a>
      </motion.div>

      <div className="mt-12 sm:mt-16 pt-8 border-t border-white/10 max-w-4xl mx-auto">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-teal-100/60">
          <span>&copy; 2026 StuntingDetect</span>
          <div className="flex gap-6">
            <a href="https://github.com/awaaaaja/stunting-detection" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">
              GitHub
            </a>
            <a href="/dashboard" className="hover:text-white transition-colors">
              Dashboard
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}