"use client";
import { motion } from "framer-motion";

export default function PenelitiSection() {
  return (
    <section id="peneliti" className="py-16 sm:py-20 px-4 bg-surface">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-2xl sm:text-3xl font-bold text-text">
            Untuk Peneliti
          </h2>
          <p className="mt-2 text-text-secondary max-w-xl mx-auto">
            Detail teknis untuk reproduksibilitas dan verifikasi ilmiah.
          </p>
        </motion.div>

        <div className="mt-8 sm:mt-10 grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-2xl border border-border p-5 sm:p-6 overflow-x-auto"
          >
            <h3 className="font-semibold text-text mb-4">
              Perbandingan Model
            </h3>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 font-medium text-text-secondary">
                    Metrik
                  </th>
                  <th className="text-right py-2 font-medium text-brand">
                    RF
                  </th>
                  <th className="text-right py-2 font-medium text-text-secondary">
                    XGB
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {([
                  ["Accuracy", "99.04%", "98.43%"],
                  ["F1 normal", "0.995", "0.991"],
                  ["F1 severely stunted", "0.989", "0.983"],
                  ["F1 stunted", "0.968", "0.947"],
                  ["F1 tinggi", "0.993", "0.989"],
                  ["Training size", "30.789", "30.789"],
                  ["Artifact size", "17.7 MB", "1.0 MB"],
                ] as [string, string, string][]).map(([metrik, rf, xgb]) => (
                  <tr key={metrik}>
                    <td className="py-2 text-text">{metrik}</td>
                    <td className="py-2 text-right font-medium text-brand">
                      {rf}
                    </td>
                    <td className="py-2 text-right text-text-secondary">
                      {xgb}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>

          <div className="space-y-4 sm:space-y-5">
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="bg-white rounded-2xl border border-border p-5 sm:p-6"
            >
              <h3 className="font-semibold text-text mb-3">Dataset</h3>
              <div className="space-y-2.5 text-sm">
                {([
                  ["Sumber", "Riskesdas 2018"],
                  ["Total sampel", "38.487 (setelah cleaning)"],
                  ["Fitur", "Usia, JK, Tinggi Badan"],
                  ["Standar labeling", "WHO 2023 + Permenkes 2/2020"],
                  ["Train/Test split", "80/20 (stratified)"],
                ] as [string, string][]).map(([label, val]) => (
                  <div key={label} className="flex justify-between items-center">
                    <span className="text-text-secondary">{label}</span>
                    <span className="text-text font-medium text-right">{val}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-white rounded-2xl border border-border p-5 sm:p-6"
            >
              <h3 className="font-semibold text-text mb-3">Infrastruktur</h3>
              <div className="space-y-2.5 text-sm">
                {([
                  ["Backend", "FastAPI + Railway"],
                  ["Frontend", "Next.js 16 + Vercel"],
                  ["Vector DB", "ChromaDB (796 chunks)"],
                  ["LLM", "OpenRouter API"],
                  ["XAI", "SHAP (TreeExplainer)"],
                ] as [string, string][]).map(([label, val]) => (
                  <div key={label} className="flex justify-between items-center">
                    <span className="text-text-secondary">{label}</span>
                    <span className="text-text font-medium text-right">{val}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}