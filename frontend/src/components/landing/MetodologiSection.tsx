"use client";
import { useState } from "react";
import { motion } from "framer-motion";

const CARDS = [
  {
    title: "Random Forest Classifier",
    badge: "99.04% Akurasi",
    icon: "🌳",
    short:
      "Ensemble learning dengan 100 decision trees untuk klasifikasi 4 kelas status gizi berbasis z-score WHO.",
    detail:
      "Hyperparameter: criterion=gini, max_depth=None, random_state=42. Per-class F1: normal=0.995, severely stunted=0.989, stunted=0.968, tinggi=0.993. Fitur dominan: Tinggi Badan (62.93%). SMOTE digunakan untuk menangani imbalance kelas stunted (10.6%).",
  },
  {
    title: "SHAP Explainability",
    badge: "Interpretable AI",
    icon: "🔍",
    short:
      "SHAP (SHapley Additive Explanations) untuk menjelaskan kontribusi tiap fitur terhadap hasil prediksi secara individual.",
    detail:
      "Kontribusi fitur bervariasi per kelas: TB = 48.2%–76.5%, Umur = 22.4%–45.6%, Jenis Kelamin = 1.1%–6.2%. Visualisasi waterfall plot menunjukkan faktor dominan tiap prediksi secara transparan.",
  },
  {
    title: "RAG Recommender",
    badge: "Berbasis PNPK + WHO",
    icon: "📄",
    short:
      "Retrieval-Augmented Generation dari 796 chunk dokumen klinis — rekomendasi grounded, bukan generik.",
    detail:
      "Sumber: PNPK 2023, WHO Child Growth Standards 2023, Juknis PMT Lokal Kemkes 2025, IPC Guidelines, Pedoman Intervensi Stunting Terintegrasi. 100% sukses rate setelah integrasi 53 chunk klinis prioritas.",
  },
];

export default function MetodologiSection() {
  const [expanded, setExpanded] = useState<number | null>(null);

  return (
    <section id="metodologi" className="py-16 sm:py-20 px-4 bg-surface">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-2xl sm:text-3xl font-bold text-text">
            Metodologi
          </h2>
          <p className="mt-2 text-text-secondary max-w-xl mx-auto">
            Tiga pilar utama sistem &mdash; akurasi ML, transparansi XAI, dan
            rekomendasi berbasis bukti.
          </p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-80px" }}
          variants={{
            hidden: {},
            visible: { transition: { staggerChildren: 0.15 } },
          }}
          className="mt-10 sm:mt-12 grid grid-cols-1 md:grid-cols-3 gap-5 sm:gap-6"
        >
          {CARDS.map((card, i) => (
            <motion.div
              key={card.title}
              variants={{
                hidden: { opacity: 0, y: 40 },
                visible: {
                  opacity: 1,
                  y: 0,
                  transition: { duration: 0.6 },
                },
              }}
              whileHover={{ y: -4 }}
              className="bg-white rounded-2xl border border-border p-5 sm:p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
              onClick={() =>
                setExpanded(expanded === i ? null : i)
              }
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl">{card.icon}</span>
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-brand/10 text-brand whitespace-nowrap">
                  {card.badge}
                </span>
              </div>
              <h3 className="text-base sm:text-lg font-semibold text-text">
                {card.title}
              </h3>
              <p className="mt-2 text-sm text-text-secondary leading-relaxed">
                {card.short}
              </p>

              <motion.div
                initial={false}
                animate={{
                  height: expanded === i ? "auto" : 0,
                  opacity: expanded === i ? 1 : 0,
                }}
                transition={{ duration: 0.3 }}
                className="overflow-hidden"
              >
                <div className="mt-3 pt-3 border-t border-border text-sm text-text-secondary leading-relaxed">
                  {card.detail}
                </div>
              </motion.div>

              <p className="mt-3 text-xs text-muted">
                {expanded === i ? "Tap untuk tutup" : "Tap untuk detail"}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}