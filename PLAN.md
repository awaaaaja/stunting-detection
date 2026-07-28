# PLAN.md — Roadmap Teknis: Sistem Deteksi Dini Risiko Stunting

Dokumen acuan teknis. Setiap fase di sini WAJIB dikerjakan dengan siklus Read→Thinking→Build→Review→Fix→Sempurnakan sesuai `AGENTS.md`. Gate antar-fase juga diatur di sana — jangan lompat fase.

---

## Fase 0 — Scoping & Requirement Lock

**Tujuan**: kunci scope MVP supaya tidak melebar tanpa kendali.

- [ ] Baca ulang `PRD.md` dan seluruh dokumen riset/arsitektur sebelumnya.
- [ ] Kunci: RF/XGBoost + SHAP + dashboard = wajib. RAG = stretch goal.
- [ ] Tulis scope statement 1 halaman, minta konfirmasi user.

**Target/Hasil**: dokumen scope disetujui, jadi acuan semua fase berikutnya.

---

## Fase 1 — Kumpulkan & Validasi Data Training

**Sumber data:**
- Dataset utama (121K baris): https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows
- Dataset sekunder/pembanding: https://www.kaggle.com/datasets/dwiiyy/data-stunting-indonesia
- Data agregat resmi per wilayah: https://katalog.data.go.id/dataset/?tags=Stunting
- Sanity check angka nasional (SSGI 2024): https://www.badankebijakan.kemkes.go.id/survei-status-gizi-indonesia-ssgi-2024/
- Formula & ambang batas resmi (Permenkes No. 2/2020): https://kesprimkom.kemkes.go.id/assets/uploads/contents/others/2020permenkes02.pdf

**Rumus z-score (WHO Child Growth Standards / Permenkes No. 2/2020):**
```
Z = (Nilai ukur individu − Median populasi rujukan) / Standar deviasi populasi rujukan
```
TB/U dan BB/U memakai metode LMS (Lambda-Mu-Sigma) — **JANGAN hitung manual dari nol**, pakai library tervalidasi (`zscorer` di R, atau implementasi WHO Anthro di Python).

**Ambang batas klasifikasi (baku, tidak boleh diubah):**
- Normal: −2 SD ≤ Z ≤ +3 SD
- Stunting (pendek): Z < −2 SD
- Severely stunted (sangat pendek): Z < −3 SD

**Langkah kerja:**
1. Setup folder: `data/raw/`, `data/processed/`, `data/docs/`
2. Unduh: `kaggle datasets download -d rendiputra/stunting-balita-detection-121k-rows -p data/raw/ --unzip`; simpan dataset sekunder di `data/raw/secondary/`
3. Inspeksi skema — jumlah baris, kolom, tipe data, missing value, rentang nilai/outlier → `data/processed/data_profile.md`
4. Hitung ulang z-score dengan library resmi, validasi terhadap label yang sudah ada di dataset; kalau beda signifikan, catat dan pakai hasil hitungan ulang sebagai ground truth
5. Bersihkan data — duplikat, missing value (dokumentasikan drop vs imputasi + alasan), outlier fisiologis tidak mungkin
6. Feature engineering dasar — usia ke satuan bulan, encode jenis kelamin, urutan kolom fitur konsisten
7. Split train/test 80/20 (atau 70/30), stratified by label, **sebelum** model dilatih — tidak boleh disentuh lagi sampai evaluasi akhir
8. Dokumentasikan sebagai `data/processed/DATA_CARD.md`: sumber, tanggal unduh, jumlah baris sebelum/sesudah cleaning, daftar keputusan cleaning, hasil validasi z-score

**Target/Hasil**: `stunting_clean_YYYYMMDD.csv` bersih & tervalidasi + `DATA_CARD.md` lengkap. Siap training tanpa risiko data leakage.

**Review checklist wajib sebelum lanjut Fase 2:**
- [ ] Tidak ada baris dengan usia/tinggi/berat fisiologis mustahil
- [ ] Distribusi label (normal/stunting/severely stunted) masuk akal dibanding SSGI nasional
- [ ] Test set benar-benar terpisah dan belum disentuh

---

## Fase 2 — Modeling: RF/XGBoost + Evaluasi

**Rumus metrik evaluasi:**
```
Accuracy  = (TP + TN) / (TP + TN + FP + FN)
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1-score  = 2 × (Precision × Recall) / (Precision + Recall)
AUC-ROC   = luas area di bawah kurva True Positive Rate vs False Positive Rate
```

**Langkah kerja:**
1. Load data hasil Fase 1
2. Latih Random Forest dan XGBoost terpisah
3. Evaluasi di **test set** — hitung semua metrik di atas
4. Bandingkan dua model, pilih terbaik atau laporkan keduanya
5. Tuning hyperparameter kalau performa kurang (grid/random search)
6. Dokumentasikan hasil untuk BAB IV naskah

**Target/Hasil**: `model.pkl`/`model.onnx` tersimpan, tabel perbandingan performa RF vs XGBoost.

**Review checklist wajib:**
- [ ] Metrik dihitung di test set, bukan training set
- [ ] Akurasi >99% → investigasi kebocoran data dulu sebelum diterima sebagai hasil valid
- [ ] Hasil dibandingkan ke literatur pembanding, bukan diterima mentah-mentah

---

## Fase 3 — SHAP Explainability Layer

**Konsep rumus (Shapley value):**
```
φᵢ = Σ [ |S|! × (|F| − |S| − 1)! / |F|! ] × [ f(S ∪ {i}) − f(S) ]
```
φᵢ = kontribusi fitur i, F = himpunan semua fitur, S = subset fitur tanpa i.

**Langkah kerja:**
1. Load model terlatih dari Fase 2
2. Implementasi `shap.TreeExplainer(model)`
3. Hitung SHAP value untuk beberapa kasus contoh
4. Cek fitur dominan masuk akal secara klinis (bandingkan literatur — status gizi & usia biasanya dominan)
5. Siapkan format output SHAP untuk dashboard

**Target/Hasil**: fungsi/endpoint yang menghasilkan daftar fitur terurut kontribusi per prediksi individual.

---

## Fase 4 — Backend API (FastAPI)

**Endpoint utama:**
```
POST /predict
  input: { usia_bulan, jenis_kelamin, berat_kg, tinggi_cm }
  output: { risk_score, risk_level, top_features, recommendations }

GET /history/{balita_id}
  output: riwayat pengukuran dan prediksi balita tersebut
```

**Langkah kerja:**
1. Setup FastAPI, load model & SHAP explainer sekali saat startup
2. Implementasi `/predict` — validasi input, jalankan model + SHAP
3. Test edge case (data tidak lengkap, usia ekstrem)
4. Error handling + logging

**Target/Hasil**: API mengembalikan skor risiko + penjelasan SHAP dalam JSON konsisten.

---

## Fase 5 — Index Knowledge Base RAG (Stretch Goal)

**Dokumen sumber:**
- Permenkes No. 2/2020: https://kesprimkom.kemkes.go.id/assets/uploads/contents/others/2020permenkes02.pdf
- Perpres No. 72/2021: https://peraturan.bpk.go.id/Download/168225/Perpres%20Nomor%2072%20Tahun%202021.pdf
- Buku KIA 2024: https://kesprimkom.kemkes.go.id/assets/uploads/contents/others/Buku_KIA_2024.pdf
- WHO Child Growth Standards: https://www.who.int/tools/child-growth-standards/standards/length-height-for-age
- Ringkasan 5 Pilar Stranas: https://stunting.go.id/perpres-nomor-72-tahun-2021-tentang-percepatan-penurunan-stunting/

**Langkah kerja:**
1. Kumpulkan PDF ke `data/docs/`
2. Ekstraksi teks (`pdfplumber`/`unstructured`)
3. Chunking per sub-bab/pasal, 300–500 token, overlap 50 token
4. Embedding tiap chunk (`multilingual-e5-base`)
5. Simpan ke ChromaDB/pgvector dengan metadata sumber (nama dokumen, halaman/pasal)
6. Uji retrieval: query fitur SHAP dominan → cek relevansi top-k
7. Sambungkan ke LLM dengan prompt grounded (lihat template di bawah)

**Prompt template LLM (wajib, jangan diubah esensinya):**
```
System: Kamu adalah asisten yang membantu kader posyandu menyusun
rekomendasi tindak lanjut stunting. Gunakan HANYA informasi dari
konteks yang diberikan. Jika informasi tidak ada di konteks,
katakan tidak tahu — jangan menebak atau mengarang.
Sertakan sumber di akhir tiap poin.

Context: {retrieved_chunks}

Data kasus:
- Skor risiko: {risk_score}
- Faktor dominan (SHAP): {top_features}

Susun 2-3 rekomendasi tindak lanjut singkat untuk kader,
masing-masing dengan sitasi sumber pedoman.
```

**Target/Hasil**: fungsi retrieval mengembalikan rekomendasi bersitasi, terbukti grounded lewat spot-check manual.

**Review checklist wajib (anti-halusinasi):**
- [ ] Tiap rekomendasi punya sitasi sumber konkret (dokumen + halaman/bab)
- [ ] Spot-check manual: ambil 5+ output, telusuri balik ke PDF sumber, cocok atau tidak
- [ ] Uji kasus di luar knowledge base — sistem harus bilang tidak tahu, bukan menjawab percaya diri

---

## Fase 6 — Web App / Dashboard (Next.js)

**Komponen utama:**
- Form input data balita (offline-first/PWA kalau memungkinkan)
- Kartu hasil: skor risiko, level risiko
- Panel penjelasan: fitur dominan SHAP
- Panel rekomendasi: hasil RAG + sitasi
- Riwayat pengukuran per balita

**Target/Hasil**: dashboard terhubung ke backend Fase 4, bisa dipakai kader tanpa training panjang.

---

## Fase 7 — Integrasi End-to-End, Testing, & Siapkan Naskah

**Langkah kerja:**
1. Uji alur penuh input → output sesuai arsitektur
2. Susun skenario uji: risiko tinggi, rendah, data ambigu
3. Kumpulkan hasil evaluasi + contoh output sebagai bahan BAB IV
4. Perbaiki bug ditemukan
5. Susun draft naskah Sinta 2, lengkap diagram arsitektur & tabel evaluasi

**Target/Hasil**: sistem jalan end-to-end, draft naskah siap direview.

---

## Alat Bantu Development: Graphify

Skill AI coding agent yang memetakan seluruh isi folder project (kode, PDF, dataset, skema) jadi knowledge graph yang bisa di-query — bukan pengganti RAG end-user, murni alat bantu agent saat development supaya tidak grep manual berulang. Jalankan `/graphify` begitu struktur folder Fase 1 sudah ada (idealnya setelah PDF Fase 5 juga masuk ke `data/docs/`).
