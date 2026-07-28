"use client";
import { motion } from "framer-motion";

function CountUp({ value }: { value: string }) {
  const isPct = value.endsWith("%");
  const num = parseFloat(value);
  if (isNaN(num)) return <span className="text-2xl sm:text-3xl font-bold text-text">{value}</span>;
  return (
    <span className="text-2xl sm:text-3xl font-bold text-text">
      {num.toFixed(1)}{isPct ? "%" : ""}
    </span>
  );
}

const stats = [
  { value: "21.6%", label: "Prevalensi Stunting Indonesia (SSGI 2023)" },
  { value: "38.487", label: "Sampel Balita (Riskesdas 2018)" },
  { value: "4", label: "Kelas Klasifikasi (WHO + Permenkes)" },
  { value: "99.5%", label: "Kesesuaian Label dengan Standar WHO" },
];

export default function MasalahSection() {
  return (
    <section id="masalah" className="py-16 sm:py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 lg:gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-2xl sm:text-3xl font-bold text-text">
              Stunting di Indonesia
            </h2>
            <p className="mt-4 text-text-secondary leading-relaxed text-sm sm:text-base">
              Stunting adalah kondisi gagal tumbuh akibat kekurangan gizi kronis
              yang ditandai dengan tinggi badan di bawah standar seusianya.
              Prevalensi stunting Indonesia masih berada di angka{" "}
              <strong>21.6% (SSGI 2023)</strong>, jauh di atas target 14% pada
              2025.
            </p>
            <p className="mt-3 text-text-secondary leading-relaxed text-sm sm:text-base">
              Dampak stunting tidak hanya fisik &mdash; penurunan IQ, risiko
              penyakit degeneratif di masa dewasa, dan kerugian ekonomi jangka
              panjang. Deteksi dini adalah kunci intervensi.
            </p>

            <div className="mt-8 grid grid-cols-2 gap-3 sm:gap-4">
              {stats.map((s) => (
                <div
                  key={s.label}
                  className="p-4 rounded-xl bg-surface-alt border border-border"
                >
                  <CountUp value={s.value} />
                  <p className="text-xs sm:text-sm text-text-secondary mt-1">
                    {s.label}
                  </p>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.6 }}
            className="relative rounded-2xl overflow-hidden shadow-lg"
          >
            <img
              src="/images/posyandu.jpg"
              alt="Posyandu Indonesia"
              className="w-full h-72 sm:h-96 object-cover"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
          </motion.div>
        </div>
      </div>
    </section>
  );
}