# AGENTS.md — Sistem Deteksi Dini Risiko Stunting (ML + XAI + RAG)

Dokumen ini adalah instruksi kerja wajib untuk AI coding agent (opencode/jcode/Claude Code/Cursor, dll) yang mengerjakan project ini. Agent HARUS membaca dan mengikuti dokumen ini sebelum menyentuh kode apapun.

Referensi silang: `PRD.md` (kenapa & untuk siapa), `PLAN.md` (roadmap fase), `LOG.md` (jejak keputusan — buat/append jika belum ada).

---

## 0. Prinsip Inti — WAJIB, Tidak Bisa Ditawar

**Tidak ada fase, task, atau sub-task yang boleh langsung "build" tanpa melewati siklus 6 langkah berikut, secara berurutan, tanpa lompat:**

```
READ → THINKING → BUILD → REVIEW → FIX → SEMPURNAKAN → (baru lanjut task berikutnya)
```

Agent dilarang keras menyingkat siklus ini menjadi "baca sekilas lalu langsung ngoding". Setiap pelanggaran siklus ini dianggap kegagalan eksekusi, bukan sekadar kekurangan gaya kerja.

### 0.1 Definisi tiap langkah

**1. READ (Baca)**
- Baca ulang dokumen relevan: `PRD.md`, `PLAN.md`, bagian fase yang sedang dikerjakan, `DATA_CARD.md` (jika sudah ada), kode/file yang akan diubah.
- Baca file yang SUDAH ADA di folder terkait sebelum menulis file baru — jangan asumsikan struktur, verifikasi dengan `ls`/`view`.
- Kalau ada dependency ke fase sebelumnya (misal Fase 2 butuh output Fase 1), buka dan periksa output fase sebelumnya secara langsung — jangan percaya begitu saja bahwa fase sebelumnya "pasti sudah beres".
- Output langkah ini: pemahaman eksplisit tentang apa yang ada sekarang, sebelum mengubah apapun.

**2. THINKING (Berpikir)**
- Tulis (dalam bentuk komentar rencana singkat, bukan langsung kode) apa yang akan dilakukan, kenapa pendekatan ini dipilih, dan risiko/edge case apa yang mungkin muncul.
- Untuk keputusan yang menyangkut validitas ilmiah (formula z-score, metrik evaluasi, threshold klasifikasi) — WAJIB cek ulang terhadap sumber resmi yang tercantum di `PLAN.md`, JANGAN andalkan ingatan/pola umum.
- Kalau ada ambiguitas yang berdampak besar (misalnya struktur skema database, pilihan library inti), berhenti dan tanyakan ke user alih-alih menebak.
- Output langkah ini: rencana konkret, termasuk urutan langkah teknis dan kriteria "selesai" untuk task ini.

**3. BUILD (Bangun)**
- Eksekusi rencana dari langkah Thinking. Tidak menambah scope di luar rencana tanpa alasan kuat (hindari scope creep diam-diam).
- Ikuti struktur folder dan konvensi kode di Bagian 2 dan 3 dokumen ini.
- Commit kecil dan bertahap lebih baik daripada satu perubahan besar tak terlacak.

**4. REVIEW (Tinjau)**
- Baca ulang HASIL build — bukan cuma "apakah script jalan tanpa error", tapi apakah output-nya masuk akal secara substantif.
- Untuk data: cek profil data hasil (jumlah baris, rentang nilai, distribusi label) — apakah wajar secara klinis?
- Untuk model: cek metrik di test set, bukan training set. Akurasi terlalu tinggi (misal >99%) adalah RED FLAG kebocoran data, bukan prestasi — investigasi dulu sebelum lanjut.
- Untuk RAG/LLM: cek apakah rekomendasi yang keluar benar-benar mengutip dari chunk yang di-retrieve, bukan mengarang. Lakukan spot-check manual ke dokumen sumber.
- Untuk kode: baca ulang diff/file yang baru ditulis, cek konsistensi dengan konvensi project.

**5. FIX (Perbaiki)**
- Perbaiki semua temuan dari Review sebelum melanjutkan. Jangan menunda "nanti aja diperbaiki belakangan" kecuali sudah dicatat eksplisit di `LOG.md` sebagai known issue dengan alasan penundaan.
- Kalau Fix mengubah asumsi besar (misal ternyata z-score dataset asli salah dan harus dihitung ulang semua), agent WAJIB mundur ke langkah THINKING lagi untuk task ini, bukan tempel patch cepat.

**6. SEMPURNAKAN (Poles)**
- Setelah fungsional dan benar, rapikan: dokumentasi inline, penamaan variabel, docstring, hapus kode debug/print, pastikan file config konsisten.
- Update `DATA_CARD.md` / `LOG.md` / bagian relevan di `PLAN.md` untuk mencatat apa yang baru selesai dan keputusan penting apa yang diambil.
- **Baru setelah langkah ini selesai**, agent boleh lanjut ke task/fase berikutnya.

### 0.2 Gate antar-fase

Sebelum mulai fase baru (misal dari Fase 1 ke Fase 2), agent WAJIB:
1. Konfirmasi "Target/Hasil" fase sebelumnya (lihat `PLAN.md`) benar-benar terpenuhi dan bisa ditunjukkan filenya.
2. Tidak mulai Fase 2 (modeling) kalau `data/processed/stunting_clean.csv` dan `DATA_CARD.md` dari Fase 1 belum ada/lengkap.
3. Tidak mulai Fase 4 (API) sebelum model dan SHAP explainer dari Fase 2–3 benar-benar bisa di-load dan menghasilkan output valid.
4. Kalau ragu apakah gate terpenuhi, laporkan ke user dengan status jelas — jangan lanjut diam-diam dengan asumsi "kemungkinan sudah cukup".

---

## 1. Anti-Halusinasi — Aturan Ketat untuk Klaim Ilmiah & Teknis

Karena project ini akhirnya jadi naskah publikasi Sinta 2, klaim yang salah/mengarang punya konsekuensi nyata. Agent WAJIB:

1. **Jangan mengarang sitasi.** Nama penulis, judul jurnal, tahun terbit, atau angka statistik HARUS berasal dari dokumen yang benar-benar dibaca/diberikan (PDF, dataset, atau hasil web_search dengan URL yang bisa diverifikasi). Kalau tidak yakin sumbernya, katakan tidak tahu — jangan menebak format yang "kedengarannya benar".
2. **Formula ilmiah tidak boleh direka ulang dari ingatan.** Z-score, metrik evaluasi (accuracy/precision/recall/F1/AUC), dan formula SHAP sudah didokumentasikan lengkap di `PLAN.md` — pakai itu sebagai rujukan tunggal, jangan improvisasi varian lain.
3. **Untuk komponen RAG**, prompt LLM WAJIB mengandung instruksi eksplisit: "gunakan HANYA informasi dari konteks yang diberikan" dan "jika informasi tidak ada di konteks, katakan tidak tahu". Ini bukan opsional.
4. **Setiap klaim numerik dari hasil eksperimen** (akurasi model, prevalensi, dsb.) harus bisa ditelusuri balik ke file/log spesifik yang menghasilkannya. Jangan laporkan angka tanpa jejak sumbernya.
5. **Untuk klaim teknis soal library/API** (saat coding), verifikasi ke dokumentasi resmi sebelum dipakai — jangan asumsikan nama fungsi/parameter dari ingatan pola umum, terutama untuk library yang jarang dipakai (shap, chromadb, dsb).

---

## 2. Struktur Folder Project

```
project-root/
├── AGENTS.md              # dokumen ini
├── PRD.md                 # requirement produk
├── PLAN.md                # roadmap & detail teknis per fase
├── LOG.md                 # jejak keputusan & progres (append-only, kronologis)
├── data/
│   ├── raw/                # file mentah, JANGAN pernah diubah/ditimpa
│   │   └── secondary/       # dataset pembanding
│   ├── processed/           # hasil cleaning, versi bertanggal
│   │   ├── data_profile.md
│   │   ├── DATA_CARD.md
│   │   └── stunting_clean_YYYYMMDD.csv
│   └── docs/                # PDF pedoman resmi untuk RAG (Fase 5)
├── model/
│   ├── train.py
│   ├── evaluate.py
│   └── artifacts/           # model.pkl / model.onnx tersimpan
├── explainability/
│   └── shap_explainer.py
├── rag/
│   ├── ingest.py            # chunking + embedding + load ke vector DB
│   ├── retrieve.py
│   └── prompt_templates/
├── backend/                 # FastAPI
│   ├── main.py
│   ├── routers/
│   └── schemas/
├── frontend/                 # Next.js
└── tests/
```

Aturan: `data/raw/` bersifat read-only secara konvensi (bukan hanya secara teknis) — kalau butuh versi baru, buat file baru di `data/processed/`, jangan menimpa raw.

---

## 3. Konvensi Kode & Kerja

- **Python**: PEP8, type hints untuk fungsi publik, docstring gaya Google untuk fungsi non-trivial.
- **Commit message**: `[Fase-X] deskripsi singkat` (contoh: `[Fase-1] validasi z-score & cleaning dataset utama`).
- **Tidak retrain model per-request** di backend — load sekali saat startup.
- **Test set tidak boleh disentuh** sebelum tahap evaluasi akhir Fase 2 — pelanggaran ini dicatat sebagai data leakage, bukan kesalahan kecil.
- **Setiap keputusan cleaning/imputasi data** harus didokumentasikan di `DATA_CARD.md` dengan alasannya — bukan cuma dilakukan diam-diam di kode.
- **File config/env**: gunakan `.env` untuk kredensial, jangan hardcode API key di kode.

---

## 4. Definisi "Selesai" per Fase (ringkas — detail penuh di PLAN.md)

| Fase | Definisi Selesai |
|---|---|
| 0 — Scoping | Scope statement 1 halaman disetujui user |
| 1 — Data | `stunting_clean_*.csv` + `DATA_CARD.md` + `data_profile.md` lengkap, z-score tervalidasi ulang |
| 2 — Modeling | Model RF & XGBoost terlatih, dievaluasi di test set, hasil terdokumentasi |
| 3 — SHAP | Fungsi/endpoint SHAP menghasilkan fitur terurut per prediksi, sudah dicek masuk akal klinis |
| 4 — Backend API | `/predict` dan `/history/{id}` jalan, teruji termasuk edge case |
| 5 — RAG | Retrieval teruji relevan, LLM grounded (lolos spot-check manual), sitasi konkret |
| 6 — Dashboard | Semua panel (skor, SHAP, rekomendasi, riwayat) terhubung ke backend nyata |
| 7 — Integrasi & naskah | End-to-end jalan, draft naskah Sinta 2 siap review |

---

## 5. Kapan Agent Harus Berhenti dan Bertanya ke User

- Ambiguitas skema database atau keputusan arsitektur yang sulit diubah belakangan.
- Ditemukan diskrepansi antara asumsi awal dan data nyata (contoh kasus sebelumnya: modul purchasing yang diasumsikan ternyata tidak ada di skema asli).
- Akurasi model mencurigakan (terlalu tinggi/rendah) tanpa penjelasan jelas.
- RAG menghasilkan jawaban yang tidak bisa ditelusuri ke chunk manapun.
- Scope fase mulai melebar jauh dari yang didefinisikan di `PLAN.md`.

Dalam semua kasus di atas, agent melaporkan temuan secara spesifik (bukan "ada masalah", tapi "ditemukan X, kemungkinan penyebab Y, opsi A/B") dan menunggu arahan sebelum lanjut.
