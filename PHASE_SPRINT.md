# PHASE_SPRINT.md — Sprint Breakdown

Pemetaan Fase 0–7 (`PLAN.md`) ke sprint kerja mingguan. Estimasi durasi asumsi kerja part-time (bukan full-time) di sela kuliah — sesuaikan kalau ritme kerja beda. Setiap sprint ditutup dengan siklus **Review → Fix → Sempurnakan** penuh sebelum sprint berikutnya dimulai (lihat `AGENTS.md` Bagian 0).

---

## Sprint 0 — Scoping (0.5 minggu)
**Fase terkait**: Fase 0

- [ ] Read: baca ulang PRD.md + riset sebelumnya
- [ ] Thinking: kunci MVP vs stretch goal
- [ ] Build: tulis scope statement 1 halaman
- [ ] Review: cek scope realistis untuk timeline yang tersedia
- [ ] Fix: revisi kalau user minta perubahan
- [ ] Sempurnakan: scope statement final, disimpan, jadi acuan sprint berikutnya

**Exit criteria**: scope disetujui user secara eksplisit.

---

## Sprint 1 — Setup & Akuisisi Data (0.5–1 minggu)
**Fase terkait**: awal Fase 1

- [ ] Read: cek struktur folder standar di AGENTS.md
- [ ] Thinking: rencanakan urutan download & validasi
- [ ] Build: setup folder `data/raw`, `data/processed`, `data/docs`; download dataset utama & sekunder
- [ ] Review: cek file terunduh utuh, ukuran wajar, tidak corrupt
- [ ] Fix: re-download kalau ada masalah
- [ ] Sempurnakan: catat sumber & tanggal unduh di draft `DATA_CARD.md`

**Exit criteria**: dataset mentah ada di `data/raw/`, belum diubah sama sekali.

---

## Sprint 2 — Profiling & Validasi Z-score (1 minggu)
**Fase terkait**: sisa Fase 1

- [ ] Read: baca ulang formula z-score & ambang batas resmi di PLAN.md
- [ ] Thinking: rencanakan library z-score yang dipakai (JANGAN hitung manual)
- [ ] Build: inspeksi skema → `data_profile.md`; hitung ulang z-score; bandingkan ke label asli
- [ ] Review: cek distribusi label wajar secara klinis, cek outlier fisiologis
- [ ] Fix: perbaiki label yang beda signifikan, catat alasannya
- [ ] Sempurnakan: `DATA_CARD.md` lengkap dengan semua keputusan cleaning

**Exit criteria**: `data_profile.md` dan draf `DATA_CARD.md` selesai, siap cleaning final.

---

## Sprint 3 — Cleaning, Feature Engineering, Split (0.5–1 minggu)
**Fase terkait**: penutup Fase 1

- [ ] Read: cek ulang hasil profiling Sprint 2
- [ ] Thinking: tentukan strategi drop vs imputasi missing value
- [ ] Build: cleaning final, feature engineering, split train/test stratified 80/20
- [ ] Review: pastikan test set benar-benar terpisah & belum tersentuh model
- [ ] Fix: perbaiki jika ada kebocoran struktur (index tercampur, dsb.)
- [ ] Sempurnakan: `stunting_clean_YYYYMMDD.csv` final + `DATA_CARD.md` dikunci

**Exit criteria (GATE ke Fase 2)**: dataset bersih + data card lengkap, tidak ada risiko data leakage.

---

## Sprint 4 — Modeling RF/XGBoost (1 minggu)
**Fase terkait**: Fase 2

- [ ] Read: baca ulang rumus metrik evaluasi di PLAN.md
- [ ] Thinking: rencana eksperimen (baseline dulu, baru tuning)
- [ ] Build: training RF & XGBoost, evaluasi di test set
- [ ] Review: cek akurasi tidak mencurigakan tinggi tanpa penjelasan; bandingkan ke literatur
- [ ] Fix: investigasi & perbaiki kalau ada tanda data leakage atau underfit/overfit
- [ ] Sempurnakan: dokumentasikan tabel perbandingan model untuk BAB IV

**Exit criteria (GATE ke Fase 3)**: model tersimpan (`model.pkl`/`.onnx`), metrik final terdokumentasi.

---

## Sprint 5 — SHAP Layer (0.5 minggu)
**Fase terkait**: Fase 3

- [ ] Read: baca ulang konsep Shapley value di PLAN.md
- [ ] Thinking: rencanakan format output SHAP untuk dashboard nanti
- [ ] Build: implementasi `shap.TreeExplainer`, hitung untuk kasus contoh
- [ ] Review: cek fitur dominan masuk akal secara klinis
- [ ] Fix: sesuaikan format output kalau belum konsisten
- [ ] Sempurnakan: fungsi SHAP siap dipanggil dari API

**Exit criteria**: fungsi SHAP menghasilkan fitur terurut valid per prediksi.

---

## Sprint 6 — Backend API (1 minggu)
**Fase terkait**: Fase 4

- [ ] Read: cek ulang kontrak endpoint di PLAN.md
- [ ] Thinking: rencana validasi input & error handling
- [ ] Build: `/predict`, `/history/{balita_id}`, load model+SHAP saat startup
- [ ] Review: test edge case (data tidak lengkap, usia ekstrem, tipe salah)
- [ ] Fix: perbaiki error handling yang bocor/tidak informatif
- [ ] Sempurnakan: logging rapi, response JSON konsisten dengan schema PRD

**Exit criteria (GATE ke Fase 5/6)**: API stabil, teruji edge case, siap dikonsumsi frontend.

---

## Sprint 7 — RAG Knowledge Base (1–1.5 minggu, stretch goal)
**Fase terkait**: Fase 5

- [ ] Read: kumpulkan & baca PDF sumber resmi di `data/docs/`
- [ ] Thinking: rencanakan strategi chunking per sub-bab (bukan per kalimat)
- [ ] Build: ekstraksi teks, chunking, embedding, load ke ChromaDB/pgvector, sambungkan prompt grounded
- [ ] Review: spot-check manual 5+ output ke dokumen sumber; uji kasus di luar knowledge base
- [ ] Fix: perbaiki chunk yang tidak relevan / prompt yang masih bisa "ngarang"
- [ ] Sempurnakan: dokumentasikan bukti grounding untuk BAB III/IV naskah

**Exit criteria**: rekomendasi RAG lolos spot-check grounding, kalau tidak lolos → jangan lanjut ke integrasi, perbaiki dulu.

*Catatan: jika waktu tidak cukup, sprint ini boleh diskip dan dipindah ke "pengembangan lanjutan" BAB V — tapi tetap ditulis lengkap sebagai landasan konseptual di BAB II.*

---

## Sprint 8 — Dashboard Next.js (1 minggu)
**Fase terkait**: Fase 6

- [ ] Read: cek kontrak API final dari Sprint 6–7
- [ ] Thinking: rencana komponen (form, kartu hasil, panel SHAP, panel rekomendasi, riwayat)
- [ ] Build: implementasi semua panel, hubungkan ke backend nyata (bukan mock data)
- [ ] Review: uji dari sisi kader — apakah mudah dipahami tanpa training?
- [ ] Fix: sederhanakan UI yang membingungkan
- [ ] Sempurnakan: polish visual, responsif, siap demo

**Exit criteria**: dashboard fungsional end-to-end dengan backend nyata.

---

## Sprint 9 — Integrasi, Testing, & Naskah (1–1.5 minggu)
**Fase terkait**: Fase 7

- [x] Read: baca ulang seluruh arsitektur & hasil tiap fase
- [x] Thinking: rencana skenario uji (risiko tinggi/rendah/ambigu)
- [x] Build: uji end-to-end (12/12 PASS), kumpulkan hasil evaluasi & contoh output, susun draft naskah
- [x] Review: cek konsistensi klaim di naskah dengan hasil eksperimen aktual (anti-halusinasi berlaku juga untuk penulisan)
- [x] Fix: perbaiki bug & klaim yang tidak akurat
- [x] Sempurnakan: draft naskah Sinta 2 final, siap dikirim ke pembimbing/reviewer

**Exit criteria**: ✅ sistem jalan end-to-end, ✅ naskah siap review manusia.

---

## Ringkasan Timeline

| Sprint | Fase | Estimasi |
|---|---|---|
| 0 | Scoping | 0.5 minggu |
| 1 | Setup & akuisisi data | 0.5–1 minggu |
| 2 | Profiling & z-score | 1 minggu |
| 3 | Cleaning & split | 0.5–1 minggu |
| 4 | Modeling | 1 minggu |
| 5 | SHAP | 0.5 minggu |
| 6 | Backend API | 1 minggu |
| 7 | RAG (stretch) | 1–1.5 minggu |
| 8 | Dashboard | 1 minggu |
| 9 | Integrasi & naskah | 1–1.5 minggu |

**Total tanpa RAG**: ~6–7 minggu. **Total dengan RAG**: ~8–9.5 minggu.
