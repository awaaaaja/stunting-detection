# Scope Statement — Sistem Deteksi Dini Risiko Stunting (ML + XAI + RAG)

## 1. Visi Produk
Memberi kader posyandu sistem skrining risiko stunting yang cepat (input → skor dalam detik), transparan (SHAP menjelaskan kenapa), dan actionable (rekomendasi grounded ke pedoman resmi).

## 2. MVP Wajib (In-Scope Inti) — Prioritaskan, tidak bisa ditawar
| Komponen | Output |
|---|---|
| **Data** (Fase 1) | Dataset bersih & tervalidasi z-score WHO, train/test split 80/20 stratified |
| **Model** (Fase 2) | Random Forest & XGBoost terlatih, evaluasi di test set |
| **SHAP** (Fase 3) | Fitur dominan per prediksi, terurut kontribusi |
| **Backend API** (Fase 4) | `POST /predict` dan `GET /history/{balita_id}` |
| **Dashboard** (Fase 6) | Form input, kartu skor + level risiko, panel SHAP, riwayat |
| **Naskah** (Fase 7) | Draft publikasi Sinta 2 |

## 3. Stretch Goal (Hanya Jika Waktu Cukup)
- **RAG + LLM** (Fase 5): Rekomendasi tindak lanjut bersitasi dari Buku Saku SSGI, Pedoman Kemenkes, Perpres 72/2021, WHO Child Growth Standards — dengan prompt grounded ketat.
- **Offline-first PWA** di frontend untuk toleransi koneksi lapangan.

## 4. Di Luar Scope (Eksplisit Tidak Dikerjakan)
- Diagnosis medis definitif — sistem ini alat bantu skrining, bukan pengganti tenaga kesehatan.
- Integrasi real-time dengan SIGIZI atau sistem informasi pemerintah lainnya.
- Aplikasi mobile native — cukup web responsif / PWA.

## 5. Prinsip Arsitektur
- **Self-hosted**: semua komponen (termasuk vector DB untuk RAG) tidak bergantung layanan berbayar.
- **Grounded generation**: rekomendasi dari LLM harus bersitasi ke chunk dokumen sumber; jika informasi tidak ditemukan, sistem harus bilang "tidak tahu".
- **No data leakage**: test set dipisah sebelum training, tidak disentuh sampai evaluasi akhir.

## 6. Timeline
| Sprint | Fase | Estimasi |
|---|---|---|
| 0 | Scoping | 0.5 minggu |
| 1–3 | Data (akuisisi → profiling → cleaning & split) | 2–3 minggu |
| 4 | Modeling RF/XGBoost | 1 minggu |
| 5 | SHAP layer | 0.5 minggu |
| 6 | Backend API | 1 minggu |
| 7 | RAG (stretch) | 1–1.5 minggu |
| 8 | Dashboard | 1 minggu |
| 9 | Integrasi & naskah | 1–1.5 minggu |
| **Total tanpa RAG** | **~6–7 minggu** | |
| **Total dengan RAG** | **~8–9.5 minggu** | |

## 7. Risiko & Mitigasi
| Risiko | Mitigasi |
|---|---|
| Data leakage → akurasi palsu | Gate review Fase 2: jika >99%, investigasi |
| LLM halusinasi | Prompt grounded ketat + spot-check manual |
| Scope RAG melebar | RAG = stretch goal, dikerjakan hanya jika MVP inti selesai |
| Label asli dataset tidak akurat | Hitung ulang z-score dari library WHO, jadikan ground truth baru |
