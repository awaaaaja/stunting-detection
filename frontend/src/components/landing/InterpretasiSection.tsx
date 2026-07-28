"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const SLIDES = [
  {
    class: "Normal",
    img: "/images/shap_waterfall_normal.png",
    desc: "TB=95cm, Usia=36bln, Perempuan — SHAP baseline 0.173, TB (−0.423) dan Umur (−0.401) mendorong kuat ke arah normal. Risk score: 0%. Pertumbuhan optimal.",
    color: "bg-emerald-50 border-emerald-200 text-emerald-700",
  },
  {
    class: "Stunted",
    img: "/images/shap_waterfall_stunted.png",
    desc: "TB=93cm, Usia=48bln, Laki-laki — TB (+0.512, 58.3%) dan Umur (+0.350, 39.8%) mendorong ke arah stunting. Berada di threshold −2SD, SHAP menunjukkan kontribusi hampir seimbang.",
    color: "bg-amber-50 border-amber-200 text-amber-700",
  },
  {
    class: "Severely Stunted",
    img: "/images/shap_waterfall_severely.png",
    desc: "TB=70cm, Usia=24bln, Laki-laki — TB mendominasi (76.5%, SHAP +0.679). Risk score: 100%. Kondisi darurat gizi yang memerlukan rujukan segera.",
    color: "bg-rose-50 border-rose-200 text-rose-700",
  },
  {
    class: "Tinggi",
    img: "/images/shap_waterfall_tinggi.png",
    desc: "TB=85cm, Usia=12bln, Perempuan — TB (−0.557, 61.2%) dan Umur (−0.340, 37.4%) mendorong ke arah tinggi. Risk score: 0%. Pertumbuhan di atas rata-rata normal.",
    color: "bg-sky-50 border-sky-200 text-sky-700",
  },
];

export default function InterpretasiSection() {
  const [active, setActive] = useState(0);

  const prev = () => setActive((active - 1 + SLIDES.length) % SLIDES.length);
  const next = () => setActive((active + 1) % SLIDES.length);

  return (
    <section id="interpretasi" className="py-16 sm:py-20 px-4 bg-surface">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-2xl sm:text-3xl font-bold text-text">
            Interpretasi per Kelas
          </h2>
          <p className="mt-2 text-text-secondary max-w-xl mx-auto">
            Visualisasi SHAP Waterfall &mdash; bagaimana tiap fitur mempengaruhi
            prediksi.
          </p>
        </motion.div>

        <div className="mt-8 sm:mt-10 max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={active}
              initial={{ opacity: 0, x: 60 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -60 }}
              transition={{ duration: 0.35 }}
              className="space-y-4"
            >
              <div
                className={`inline-flex px-4 py-1.5 rounded-full text-sm font-medium ${SLIDES[active].color}`}
              >
                {SLIDES[active].class}
              </div>

              <div className="rounded-2xl overflow-hidden border border-border bg-white">
                <img
                  src={SLIDES[active].img}
                  alt={SLIDES[active].class}
                  className="w-full h-auto object-contain max-h-[500px]"
                />
              </div>

              <p className="text-sm text-text-secondary leading-relaxed p-4 sm:p-5 rounded-xl bg-white border border-border">
                {SLIDES[active].desc}
              </p>
            </motion.div>
          </AnimatePresence>

          <div className="mt-6 flex items-center justify-center gap-4">
            <button
              onClick={prev}
              className="p-2.5 rounded-full bg-white border border-border hover:bg-surface-alt active:scale-90 transition-all"
              aria-label="Sebelumnya"
            >
              <svg className="w-5 h-5 text-text" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <div className="flex gap-2">
              {SLIDES.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setActive(i)}
                  className={`w-2.5 h-2.5 rounded-full transition-all ${
                    i === active ? "bg-brand scale-125" : "bg-border hover:bg-muted"
                  }`}
                  aria-label={`Slide ${i + 1}`}
                />
              ))}
            </div>

            <button
              onClick={next}
              className="p-2.5 rounded-full bg-white border border-border hover:bg-surface-alt active:scale-90 transition-all"
              aria-label="Selanjutnya"
            >
              <svg className="w-5 h-5 text-text" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}