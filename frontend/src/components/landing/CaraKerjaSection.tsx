"use client";
import { motion } from "framer-motion";

const STEPS = [
  {
    icon: "📝",
    title: "Input Data",
    desc: "Usia (0–60 bln), Jenis Kelamin, Tinggi Badan (20–150 cm)",
  },
  {
    icon: "📊",
    title: "Normalisasi Z-Score",
    desc: "Hitung TB/U berdasarkan standar WHO 2023 — deteksi −3SD hingga +3SD",
  },
  {
    icon: "🤖",
    title: "Prediksi Random Forest",
    desc: "Klasifikasi 4 kelas dengan confidence score. Akurasi 99.04%",
  },
  {
    icon: "🔍",
    title: "Analisis SHAP",
    desc: "Feature attribution: fitur mana yang paling memengaruhi prediksi",
  },
  {
    icon: "💡",
    title: "Rekomendasi RAG",
    desc: "Rekomendasi grounded dari 796 chunk dokumen PNPK, WHO, Juknis PMT",
  },
];

export default function CaraKerjaSection() {
  return (
    <section id="cara-kerja" className="py-16 sm:py-20 px-4 bg-white">
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-2xl sm:text-3xl font-bold text-text">
            Cara Kerja
          </h2>
          <p className="mt-2 text-text-secondary">
            Dari input hingga rekomendasi dalam 5 langkah.
          </p>
        </motion.div>

        <div className="mt-10 sm:mt-12 space-y-0">
          {STEPS.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="flex gap-4 sm:gap-6"
            >
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-brand/10 flex items-center justify-center text-lg sm:text-xl shrink-0">
                  {step.icon}
                </div>
                {i < STEPS.length - 1 && (
                  <div className="w-0.5 h-full min-h-[48px] sm:min-h-[60px] bg-border" />
                )}
              </div>
              <div className="pb-8 sm:pb-10">
                <h3 className="text-base sm:text-lg font-semibold text-text">
                  {step.title}
                </h3>
                <p className="mt-1 text-sm text-text-secondary">{step.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}