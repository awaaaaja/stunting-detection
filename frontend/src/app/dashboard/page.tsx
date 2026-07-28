"use client";

import { useState, useCallback, useRef } from "react";
import { predict, listHistory } from "@/lib/api";
import type { PredictResponse, HistorySummary } from "@/lib/types";
import ReactMarkdown from "react-markdown";

export default function Dashboard() {
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<HistorySummary[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const resultRef = useRef<HTMLDivElement>(null);

  const [usia, setUsia] = useState("");
  const [jk, setJk] = useState("");
  const [tinggi, setTinggi] = useState("");
  const [balitaId, setBalitaId] = useState("");

  const usiaErr = usia !== "" && (Number(usia) < 0 || Number(usia) > 60);
  const tinggiErr = tinggi !== "" && (Number(tinggi) < 20 || Number(tinggi) > 150);
  const jkErr = jk !== "" && !["laki-laki", "perempuan"].includes(jk);

  const canSubmit = usia !== "" && tinggi !== "" && jk !== "" && !usiaErr && !tinggiErr && !jkErr;

  const handleSubmit = useCallback(async () => {
    if (!canSubmit) return;
    setLoading(true);
    setError(null);
    setShowHistory(false);
    try {
      const res = await predict({
        usia_bulan: Number(usia),
        jenis_kelamin: jk,
        tinggi_cm: Number(tinggi),
        balita_id: balitaId || undefined,
      });
      setResult(res.data);
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Gagal memproses prediksi");
    } finally {
      setLoading(false);
    }
  }, [canSubmit, usia, jk, tinggi, balitaId]);

  const loadHistory = useCallback(async () => {
    try {
      const res = await listHistory();
      setHistory(res.data);
      setShowHistory(true);
    } catch {
      setError("Gagal memuat riwayat");
    }
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && canSubmit && !loading) handleSubmit();
  };

  return (
    <div className="min-h-full flex flex-col">
      <header className="sticky top-0 z-40 bg-white border-b border-border">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand flex items-center justify-center text-white text-sm font-bold">
              SD
            </div>
            <div className="leading-tight">
              <span className="font-semibold text-text">StuntingDetect</span>
              <span className="hidden sm:inline text-muted text-sm ml-2">Deteksi Dini Risiko Stunting</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <a href="/" className="btn-ghost text-sm">Beranda</a>
            <button onClick={loadHistory} className="btn-ghost text-sm">Riwayat</button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6 space-y-6">
        <div className="text-center mb-2">
          <h1 className="text-2xl font-bold text-text sm:text-3xl">
            Deteksi Risiko Stunting
          </h1>
          <p className="text-text-secondary mt-1 max-w-lg mx-auto">
            Masukkan data antropometri balita untuk mendapatkan prediksi, analisis SHAP, dan rekomendasi berbasis pedoman nasional.
          </p>
        </div>

        <div className="card max-w-2xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="label">Usia (bulan)</label>
              <input
                type="number"
                value={usia}
                onChange={(e) => setUsia(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="0–60"
                min={0}
                max={60}
                className={`input-field ${usiaErr ? "ring-2 ring-danger/30 border-danger" : ""}`}
              />
              {usiaErr && <p className="text-xs text-danger mt-1">Rentang 0–60 bulan</p>}
            </div>

            <div>
              <label className="label">Jenis Kelamin</label>
              <select
                value={jk}
                onChange={(e) => setJk(e.target.value)}
                className={`input-field ${jkErr ? "ring-2 ring-danger/30 border-danger" : ""}`}
              >
                <option value="">Pilih</option>
                <option value="laki-laki">Laki-laki</option>
                <option value="perempuan">Perempuan</option>
              </select>
              {jkErr && <p className="text-xs text-danger mt-1">Pilih jenis kelamin</p>}
            </div>

            <div>
              <label className="label">Tinggi Badan (cm)</label>
              <input
                type="number"
                value={tinggi}
                onChange={(e) => setTinggi(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="20–150"
                step={0.1}
                min={20}
                max={150}
                className={`input-field ${tinggiErr ? "ring-2 ring-danger/30 border-danger" : ""}`}
              />
              {tinggiErr && <p className="text-xs text-danger mt-1">Rentang 20–150 cm</p>}
            </div>
          </div>

          <div className="mt-4">
            <label className="label">ID Balita (opsional)</label>
            <input
              type="text"
              value={balitaId}
              onChange={(e) => setBalitaId(e.target.value)}
              placeholder="Misal: B001, A0123"
              className="input-field max-w-xs"
            />
          </div>

          <div className="mt-5 flex items-center gap-3">
            <button
              onClick={handleSubmit}
              disabled={!canSubmit || loading}
              className="btn-primary"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Memproses...
                </>
              ) : (
                "Deteksi Sekarang"
              )}
            </button>
            {result && (
              <button onClick={() => { setResult(null); setError(null); }} className="btn-ghost">
                Hapus
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="max-w-2xl mx-auto card border-danger/30 bg-danger/5">
            <div className="flex items-start gap-3">
              <span className="text-danger text-lg leading-none mt-0.5">&#9888;</span>
              <div>
                <p className="font-medium text-danger text-sm">{error}</p>
                <p className="text-text-secondary text-xs mt-1">Coba periksa koneksi ke server atau ulangi.</p>
              </div>
            </div>
          </div>
        )}

        {result && (
          <div ref={resultRef} className="space-y-5 animate-fade-in">
            <ResultPanel result={result} />
          </div>
        )}

        {showHistory && (
          <HistoryPanel
            history={history}
            onClose={() => setShowHistory(false)}
            onSelect={(id) => { setBalitaId(id); setShowHistory(false); }}
          />
        )}

        {!result && !error && (
          <div className="max-w-lg mx-auto text-center py-12">
            <div className="w-16 h-16 rounded-full bg-brand/10 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-brand" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
              </svg>
            </div>
            <h3 className="font-medium text-text">Belum ada data</h3>
            <p className="text-text-secondary text-sm mt-1">Masukkan data balita di atas untuk memulai deteksi.</p>
          </div>
        )}
      </main>
    </div>
  );
}

function ResultPanel({ result }: { result: PredictResponse }) {
  const pred = result.prediction;
  const colorMap: Record<string, { bg: string; text: string; bar: string; label: string }> = {
    normal: { bg: "bg-emerald-50 border-emerald-200", text: "text-emerald-700", bar: "bg-emerald-500", label: "Normal" },
    stunted: { bg: "bg-amber-50 border-amber-200", text: "text-amber-700", bar: "bg-amber-500", label: "Stunting" },
    "severely stunted": { bg: "bg-rose-50 border-rose-200", text: "text-rose-700", bar: "bg-rose-500", label: "Severely Stunted" },
    tinggi: { bg: "bg-sky-50 border-sky-200", text: "text-sky-700", bar: "bg-sky-500", label: "Tinggi" },
  };
  const colors = colorMap[pred.class] || colorMap.normal;

  return (
    <>
      <div className={`max-w-2xl mx-auto card ${colors.bg} ${colors.text}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider opacity-70">Status Gizi</p>
            <h2 className="text-2xl font-bold mt-0.5">{colors.label}</h2>
            <p className="text-sm mt-1 opacity-80">
              Risiko stunting: <span className="font-semibold">{(pred.risk_score * 100).toFixed(1)}%</span>
            </p>
          </div>
          <div className={`w-16 h-16 rounded-full flex items-center justify-center text-lg font-bold ${colors.bg} border-2 ${colors.text}`}
               style={{ borderColor: "currentColor" }}>
            {(pred.risk_score * 100).toFixed(0)}
          </div>
        </div>

        <div className="mt-4 space-y-1.5">
          {["normal", "stunted", "severely stunted", "tinggi"].map((cls) => {
            const prob = pred.probabilities[cls] ?? 0;
            const pct = (prob * 100).toFixed(1);
            const clsColors = colorMap[cls] || colorMap.normal;
            return (
              <div key={cls} className="flex items-center gap-3">
                <span className="text-xs w-28 text-text-secondary shrink-0">{clsColors.label}</span>
                <div className="flex-1 h-2 rounded-full bg-black/5 overflow-hidden">
                  <div
                    className={`shap-bar ${clsColors.bar}`}
                    style={{ width: `${prob * 100}%` }}
                  />
                </div>
                <span className="text-xs text-text-secondary w-10 text-right tabular-nums">{pct}%</span>
              </div>
            );
          })}
        </div>
      </div>

      <div className="max-w-2xl mx-auto card">
        <h3 className="font-semibold text-text mb-4">Faktor Dominan</h3>
        <div className="space-y-3">
          {result.shap.features.map((f, i) => {
            const pct = f.contribution_pct;
            const isPositive = f.shap_value > 0;
            return (
              <div key={f.feature} className="animate-fade-in" style={{ animationDelay: `${i * 80}ms` } as React.CSSProperties}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="font-medium text-text">{f.feature}</span>
                  <span className="text-text-secondary tabular-nums">{f.value} {f.feature === "Tinggi Badan (cm)" ? "cm" : f.feature === "Umur (bulan)" ? "bln" : ""}</span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-2.5 rounded-full bg-surface-alt overflow-hidden">
                    <div
                      className={`shap-bar ${isPositive ? "bg-brand" : "bg-warning"}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="text-xs text-text-secondary w-16 text-right tabular-nums">{pct}%</span>
                </div>
              </div>
            );
          })}
        </div>
        <p className="text-xs text-muted mt-3">
          Persentase kontribusi tiap fitur terhadap hasil prediksi. Nilai positif (teal) = mendorong ke arah stunting.
        </p>
      </div>

      <div className="max-w-2xl mx-auto card">
        <div className="flex items-center gap-2 mb-3">
          <svg className="w-5 h-5 text-brand" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />
          </svg>
          <h3 className="font-semibold text-text">Rekomendasi</h3>
        </div>
        <div className="text-sm text-text-secondary leading-relaxed prose prose-sm max-w-none prose-headings:text-text prose-strong:text-text">
          <ReactMarkdown>{result.rekomendasi.answer}</ReactMarkdown>
        </div>
        {result.rekomendasi.sources.length > 0 && (
          <details className="mt-3">
            <summary className="text-xs text-muted cursor-pointer hover:text-text-secondary transition-colors">
              Sumber ({result.rekomendasi.sources.length})
            </summary>
            <ul className="mt-2 space-y-1">
              {result.rekomendasi.sources.map((s, i) => (
                <li key={i} className="text-xs text-muted">
                  {s.source}{s.page != null ? ` — Halaman ${s.page}` : ""}
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>

      <div className="max-w-2xl mx-auto">
        <details className="card">
          <summary className="text-sm font-medium text-text-secondary cursor-pointer">
            Detail Pemeriksaan
          </summary>
          <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
            {[
              ["Usia", `${result.usia_bulan} bulan`],
              ["Jenis Kelamin", result.jenis_kelamin],
              ["Tinggi Badan", `${result.tinggi_cm} cm`],
              ["Waktu", new Date(result.timestamp).toLocaleString("id-ID")],
            ].map(([l, v]) => (
              <div key={l}>
                <p className="text-muted text-xs">{l}</p>
                <p className="font-medium text-text">{v}</p>
              </div>
            ))}
          </div>
        </details>
      </div>
    </>
  );
}

function HistoryPanel({
  history,
  onClose,
  onSelect,
}: {
  history: HistorySummary[];
  onClose: () => void;
  onSelect: (id: string) => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/30 backdrop-blur-sm">
      <div className="card w-full max-w-lg mx-4 max-h-[70vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-text">Riwayat Pemeriksaan</h3>
          <button onClick={onClose} className="btn-ghost p-1">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        {history.length === 0 ? (
          <div className="text-center py-8 text-muted text-sm">Belum ada riwayat.</div>
        ) : (
          <div className="space-y-2">
            {history.map((h) => (
              <button
                key={h.balita_id}
                onClick={() => onSelect(h.balita_id)}
                className="w-full text-left p-3 rounded-lg hover:bg-surface-alt transition-colors border border-border"
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium text-text text-sm">{h.balita_id}</span>
                  <span className={`badge ${h.last_prediction === "normal" || h.last_prediction === "tinggi" ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700"}`}>
                    {h.last_prediction}
                  </span>
                </div>
                <div className="flex items-center gap-3 mt-1 text-xs text-muted">
                  <span>{h.total_records} pemeriksaan</span>
                  {h.last_checked && <span>{new Date(h.last_checked).toLocaleDateString("id-ID")}</span>}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}