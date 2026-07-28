"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const TABS = [
  {
    id: "confusion",
    label: "Confusion Matrix",
    img: "/images/confusion_matrices.png",
    caption:
      "Model mengklasifikasikan 7.630 dari 7.698 sampel test dengan benar (99.14%). Hanya 68 error — seluruhnya di batas threshold z-score (−2SD dan −3SD). False positive severely stunted: 0. Kelas tinggi (Z > +3SD): 100% tepat tanpa error.",
  },
  {
    id: "roc",
    label: "ROC Curve",
    img: "/images/roc_curves.png",
    caption:
      "AUC rata-rata 0.998 — model hampir sempurna dalam membedakan antar kelas di semua threshold. Kurva ROC keempat kelas mendekati sudut kiri-atas, menunjukkan discriminability sangat tinggi.",
  },
  {
    id: "importance",
    label: "Feature Importance",
    img: "/images/feature_importance.png",
    caption:
      "Tinggi Badan adalah fitur paling dominan (62.93%), diikuti Umur (36.88%). Jenis Kelamin kontribusi minimal (0.19%) — konsisten dengan literatur bahwa TB/U adalah indikator utama stunting.",
  },
  {
    id: "perclass",
    label: "Per-Class Metrics",
    img: "/images/per_class_metrics.png",
    caption:
      "F1-score merata di semua kelas: normal=0.995, severely stunted=0.989, stunted=0.968, tinggi=0.993. Kinerja terendah di kelas stunted (batas −2SD) — konsisten dengan kompleksitas klasifikasi di zona threshold.",
  },
  {
    id: "comparison",
    label: "Model Comparison",
    img: "/images/model_comparison.png",
    caption:
      "Random Forest (99.04%) unggul tipis dari XGBoost (98.43%) — selisih +0.61%. RF dipilih sebagai model produksi karena: (1) lebih stabil di per-class F1, (2) lebih interpretable (feature importance bawaan), (3) performa lebih baik di kelas minoritas stunted.",
  },
];

export default function HasilTrainingSection() {
  const [active, setActive] = useState(0);

  return (
    <section id="hasil" className="py-16 sm:py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-2xl sm:text-3xl font-bold text-text">
            Hasil Training Model
          </h2>
          <p className="mt-2 text-text-secondary max-w-xl mx-auto">
            Evaluasi Random Forest pada test set (20% data = 7.698 sampel).
          </p>
        </motion.div>

        <div className="mt-8 sm:mt-10 flex gap-2 overflow-x-auto pb-2 -mx-4 px-4 snap-x snap-mandatory md:justify-center md:mx-0 md:px-0 scrollbar-hide">
          {TABS.map((tab, i) => (
            <button
              key={tab.id}
              onClick={() => setActive(i)}
              className={`snap-start shrink-0 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all active:scale-95 ${
                active === i
                  ? "bg-brand text-white"
                  : "bg-surface-alt text-text-secondary hover:bg-border"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={active}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="mt-6 sm:mt-8"
          >
            <div className="rounded-2xl overflow-hidden border border-border bg-surface-alt">
              <img
                src={TABS[active].img}
                alt={TABS[active].label}
                className="w-full h-auto object-contain max-h-[500px]"
              />
            </div>
            <div className="mt-4 p-4 sm:p-5 rounded-xl bg-surface-alt border border-border">
              <p className="text-sm text-text-secondary leading-relaxed">
                {TABS[active].caption}
              </p>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  );
}