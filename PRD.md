# PRD.md — Sistem Deteksi Dini Risiko Stunting (ML + XAI + RAG)

## 1. Latar Belakang & Masalah

Kader posyandu di lapangan melakukan pengukuran antropometri balita (usia, jenis kelamin, berat, tinggi/panjang badan) secara rutin, tapi interpretasi risiko stunting saat ini bergantung pada tabel z-score manual dan pengalaman kader — proses ini rawan salah baca, lambat, dan tidak memberi rekomendasi tindak lanjut yang konsisten dengan pedoman resmi.

Riset ML untuk deteksi stunting di Indonesia sudah banyak (RF/XGBoost dengan akurasi tinggi), tapi mayoritas berhenti di prediksi + SHAP saja tanpa jembatan ke rekomendasi tindak lanjut yang bisa langsung dipakai kader. Sistem chatbot edukasi stunting yang berbasis RAG biasanya berdiri sendiri, terpisah dari model prediktif — user harus tanya manual, bukan otomatis dari hasil prediksi.

## 2. Tujuan Produk

1. Memberi kader posyandu skor risiko stunting balita secara instan dari data antropometri.
2. Menjelaskan **kenapa** skor itu keluar (SHAP) — bukan kotak hitam.
3. Memberi rekomendasi tindak lanjut konkret yang **bersitasi ke pedoman resmi** (RAG), bukan saran generik.
4. Menghasilkan naskah publikasi Sinta 2 sebagai luaran akademik.

## 3. Diferensiasi / Novelty

Kombinasi tiga lapisan — prediksi (RF/XGBoost) + explainability (SHAP) + rekomendasi grounded (RAG) — dalam satu alur end-to-end. Literatur stunting Indonesia saat ini umumnya hanya sampai lapisan pertama atau kedua.

## 4. Target Pengguna

| Persona | Kebutuhan |
|---|---|
| Kader posyandu | Input cepat, output mudah dipahami, bisa dipakai di lapangan dengan koneksi internet tidak stabil |
| Peneliti/pembimbing (evaluator naskah) | Metodologi valid, metrik jelas, sitasi terlacak, tidak ada klaim tanpa dasar |
| Dinas kesehatan (potensial, tidak wajib di MVP) | Data agregat tren risiko per wilayah |

## 5. Ruang Lingkup (Scope)

### 5.1 MVP wajib (in-scope inti)
- Model prediksi risiko stunting (RF/XGBoost) dari data antropometri.
- Layer SHAP untuk menjelaskan fitur dominan tiap prediksi.
- Backend API (FastAPI) dengan endpoint `/predict` dan `/history/{balita_id}`.
- Dashboard kader (Next.js) menampilkan skor, penjelasan, riwayat.

### 5.2 Stretch goal (masuk jika waktu cukup)
- RAG + LLM untuk rekomendasi tindak lanjut bersitasi dari pedoman resmi (Buku Saku SSGI, Pedoman Kemenkes, Perpres 72/2021, WHO Child Growth Standards).
- Mode offline-first (PWA + IndexedDB) untuk form input kader.

### 5.3 Di luar scope (eksplisit tidak dikerjakan)
- Diagnosis medis definitif — sistem ini alat bantu skrining, bukan pengganti tenaga kesehatan.
- Integrasi real-time dengan sistem informasi kesehatan pemerintah (SIGIZI, dsb).
- Aplikasi mobile native (cukup web responsif/PWA).

## 6. Requirement Fungsional

| ID | Requirement | Prioritas |
|---|---|---|
| F1 | Sistem menerima input usia, jenis kelamin, berat, tinggi balita | Wajib |
| F2 | Sistem mengembalikan skor risiko & level risiko (normal/stunting/severely stunted) | Wajib |
| F3 | Sistem menampilkan fitur dominan penyebab skor (SHAP) | Wajib |
| F4 | Sistem menyimpan & menampilkan riwayat pengukuran per balita | Wajib |
| F5 | Sistem memberi rekomendasi tindak lanjut bersitasi pedoman resmi | Stretch |
| F6 | Sistem menolak menjawab dari luar konteks dokumen resmi (anti-halusinasi RAG) | Stretch, tapi wajib kalau F5 dikerjakan |

## 7. Requirement Non-Fungsional

- **Akurasi & validitas ilmiah**: semua formula (z-score, metrik evaluasi) memakai standar resmi (WHO/Permenkes), tidak boleh diformulasi ulang secara ad-hoc.
- **Transparansi data**: setiap keputusan cleaning data terdokumentasi (`DATA_CARD.md`).
- **No data leakage**: test set dipisah sebelum training, tidak disentuh sampai evaluasi akhir.
- **Grounded generation**: rekomendasi dari LLM harus bisa ditelusuri ke chunk dokumen sumber; kalau tidak ada, sistem harus bilang tidak tahu, bukan mengarang.
- **Ketersediaan di lapangan**: idealnya toleran koneksi internet lambat/terputus.
- **Self-hosted**: vector DB dan komponen inti tidak bergantung pada layanan berbayar (ChromaDB/pgvector, bukan Pinecone).

## 8. Metrik Keberhasilan

- Model: accuracy, precision, recall, F1-score, AUC-ROC di test set (bukan training set) — dibandingkan dengan baseline literatur.
- RAG (jika dikerjakan): tingkat relevansi top-k retrieval, hasil spot-check manual grounding (berapa persen rekomendasi yang sitasinya benar-benar valid saat ditelusuri balik).
- Akademik: naskah lolos syarat submisi jurnal Sinta 2.

## 9. Risiko & Mitigasi

| Risiko | Mitigasi |
|---|---|
| Data leakage bikin akurasi palsu tinggi | Split train/test sebelum training, gate review wajib di Fase 2 |
| LLM mengarang rekomendasi (halusinasi) | Prompt grounded ketat + spot-check manual + uji kasus di luar knowledge base |
| Scope RAG terlalu besar untuk timeline KP/skripsi | RAG diposisikan sebagai stretch goal, MVP inti (model+SHAP+dashboard) diprioritaskan dulu |
| Label status gizi di dataset asli tidak akurat | Hitung ulang z-score dari formula resmi, jadikan ground truth baru jika berbeda signifikan |
| Konektivitas lapangan tidak stabil | Pertimbangkan offline-first di frontend (stretch) |

## 10. Timeline Referensi

Mengikuti urutan fase di `PLAN.md` (Fase 0–7). Prioritas realistis kalau waktu terbatas: Fase 0–4 (MVP inti: data → model → SHAP → API) dulu, baru Fase 5 (RAG) kalau waktu masih ada, lalu Fase 6–7.
