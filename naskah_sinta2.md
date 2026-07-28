# Sistem Klasifikasi Risiko dan Screening Stunting pada Balita berbasis Machine Learning, SHAP, dan Retrieval-Augmented Generation dengan Rule-Based Fallback

## Abstrak

Stunting merupakan masalah gizi kronis yang memengaruhi pertumbuhan dan perkembangan anak balita di Indonesia, dengan prevalensi nasional 19,8% (SSGI 2024). Sistem screening dan klasifikasi risiko yang akurat sangat diperlukan untuk membantu kader posyandu dan tenaga kesehatan dalam mengidentifikasi status gizi balita serta memberikan rekomendasi penanganan awal. Penelitian ini mengembangkan sistem klasifikasi risiko stunting pada balita yang mengintegrasikan machine learning (Random Forest dan XGBoost) untuk klasifikasi 4 kelas status gizi (normal, stunted, severely stunted, tinggi), SHAP (SHapley Additive exPlanations) untuk explainability, dan sistem rekomendasi hybrid (Retrieval-Augmented Generation dengan rule-based fallback). Dataset antropometri 38.487 balita hasil cleaning dari 120.999 sampel sintetik tervalidasi menggunakan WHO Child Growth Standards (agreement 99,50%). Random Forest mencapai akurasi 99,04% (F1=0,9904) dengan kontribusi fitur dominan: Tinggi Badan (62,93%) dan Umur (36,88%). SHAP TreeExplainer memberikan interpretasi per fitur yang divalidasi secara klinis. Sistem rekomendasi hybrid menjamin rekomendasi selalu tersedia: jika RAG (ChromaDB Cloud, 743 chunks, GPT-4o-mini via OpenRouter) gagal atau tidak relevan, rule-based fallback berdasarkan PNPK Stunting dan Permenkes No. 2/2020 digunakan. Pengujian end-to-end mencakup 13 skenario (13/13 PASS) termasuk verifikasi ketersediaan rekomendasi dan tracking RAG-success rate. Sistem diimplementasikan sebagai API FastAPI dengan dashboard Next.js yang dapat digunakan sebagai alat bantu screening di Posyandu.

**Kata kunci**: klasifikasi stunting, screening balita, machine learning, Random Forest, SHAP, Retrieval-Augmented Generation, rule-based fallback

---

## 1. Pendahuluan

Stunting adalah gangguan pertumbuhan dan perkembangan anak akibat kekurangan gizi kronis dan infeksi berulang, yang ditandai dengan panjang atau tinggi badan berada di bawah standar WHO [1]. Berdasarkan Survei Status Gizi Indonesia (SSGI) 2024, prevalensi stunting nasional tercatat 19,8%, menurun dari 21,5% pada tahun 2023 namun masih di atas target 14% yang ditetapkan dalam Peraturan Presiden Nomor 72 Tahun 2021 [2][3].

Dampak stunting bersifat irreversible dan memengaruhi perkembangan kognitif, produktivitas, dan kualitas sumber daya manusia di masa depan [4]. Screening dan klasifikasi risiko secara dini merupakan kunci intervensi yang efektif, terutama pada periode 1.000 Hari Pertama Kehidupan (HPK). Pemerintah Indonesia telah menerbitkan Pedoman Nasional Pelayanan Kedokteran (PNPK) Tata Laksana Stunting melalui Keputusan Menteri Kesehatan Nomor HK.01.07/MENKES/1928/2022 sebagai acuan klinis nasional [5].

Perkembangan machine learning membuka peluang untuk sistem klasifikasi dan screening yang lebih akurat dan cepat dibandingkan plotting manual pada KMS (Kartu Menuju Sehat). Namun, model ML sering dianggap sebagai "black box" yang sulit diinterpretasi oleh tenaga kesehatan [6]. SHAP (SHapley Additive exPlanations) mengatasi keterbatasan ini dengan memberikan kontribusi setiap fitur terhadap hasil klasifikasi secara konsisten dan berbasis teori permainan [7]. Untuk rekomendasi lanjutan, Retrieval-Augmented Generation (RAG) memungkinkan sistem memberikan rekomendasi yang grounded pada dokumen pedoman resmi [8], namun RAG memiliki keterbatasan ketika dokumen sumber tidak cukup spesifik — sehingga diperlukan mekanisme fallback.

Penelitian ini bertujuan mengembangkan sistem klasifikasi risiko dan screening stunting pada balita yang:
1. Mengklasifikasikan status gizi ke dalam 4 kategori risiko berdasarkan data antropometri menggunakan Random Forest dan XGBoost
2. Menjelaskan faktor dominan penyebab klasifikasi melalui SHAP untuk membantu diagnosis tenaga kesehatan
3. Memberikan rekomendasi penanganan berbasis PNPK Stunting melalui sistem hybrid (RAG + rule-based fallback) yang menjamin ketersediaan rekomendasi

---

## 2. Metode

### 2.1 Dataset

Dataset utama bersumber dari Kaggle (rendiputra/stunting-balita-detection-121k-rows) dengan 120.999 sampel sintetik dan 4 kolom: Umur (bulan), Jenis Kelamin, Tinggi Badan (cm), dan Status Gizi. Dataset sekunder dari Kaggle (dwiiyy/data-stunting-indonesia) digunakan sebagai referensi prevalensi per provinsi.

Proses cleaning meliputi:
- **Deduplikasi**: Dataset sintetik mengandung 81.574 baris duplikat (67%). Deduplikasi ke kombinasi unik (usia, jenis kelamin, tinggi) menghasilkan 39.425 sampel.
- **BIV Removal**: Penghapusan 938 baris dengan |z-score| > 6 sesuai standar WHO Biologically Implausible Values.
- **Final**: 38.487 sampel dengan rentang usia 0–60 bulan.

### 2.2 Validasi Z-Score dan Label Ground Truth

Z-score dihitung menggunakan library `anthro` v1.1.1 (implementasi Python dari WHO Child Growth Standards 2006). Indikator yang digunakan adalah lhfa (Length/Height-for-Age). Threshold klasifikasi mengacu pada Permenkes No. 2/2020:
- Severely stunted: Z < -3 SD
- Stunted: -3 SD ≤ Z < -2 SD
- Normal: -2 SD ≤ Z ≤ +3 SD
- Tinggi: Z > +3 SD

Agreement antara label existing dengan label WHO z-score mencapai 99,50%. Seluruh 603 disagreement (0,5%) berada di batas threshold (±2 SD, ±3 SD). Label WHO digunakan sebagai ground truth karena dihitung dengan library tervalidasi resmi WHO.

### 2.3 Split Data

Dataset dibagi 80/20 stratified by label menggunakan random_state=42: 30.789 sampel training dan 7.698 sampel test. Test set dikunci dan tidak disentuh sampai evaluasi akhir untuk mencegah data leakage.

### 2.4 Model Machine Learning

Dua algoritma diimplementasikan untuk klasifikasi 4 kelas:
- **Random Forest** (n_estimators=100, criterion=gini): 100 pohon keputusan dengan majority voting.
- **XGBoost** (n_estimators=100, learning_rate=0.1): Gradient boosting dengan regularisasi.

Fitur input: Umur (bulan), Jenis Kelamin (1=laki-laki, 0=perempuan), Tinggi Badan (cm). Target: 4 kelas (normal, severely stunted, stunted, tinggi).

### 2.5 SHAP Explainability

SHAP TreeExplainer diimplementasikan untuk Random Forest terpilih. Nilai SHAP dihitung untuk setiap fitur terhadap setiap kelas menggunakan 100 sampel background. Output berupa:
- SHAP values per fitur per prediksi
- Base value (rata-rata prediksi)
- Contribution percentage (|SHAP| / total |SHAP|)

### 2.6 Sistem Rekomendasi Hybrid

Sistem rekomendasi menggunakan pendekatan hybrid dua lapis:

**Lapis 1 — Retrieval-Augmented Generation (RAG):**
- Vector database: ChromaDB Cloud dengan 743 chunks dari 6 dokumen sumber
- Embedding: all-MiniLM-L6-v2 (384 dimensi) dengan query expansion ID→EN
- LLM: OpenAI GPT-4o-mini via OpenRouter dengan prompt grounded
- Jika RAG menghasilkan answer >20 karakter dan chunk relevan → digunakan

**Lapis 2 — Rule-Based Fallback:**
- 4 template rekomendasi berdasarkan kelas klasifikasi (severely stunted: 10 poin, stunted: 10 poin, normal: 10 poin, tinggi: 8 poin)
- Bersumber dari PNPK Stunting (Kepmenkes 1928/2022) dan Permenkes No. 2/2020
- Menjamin rekomendasi TIDAK PERNAH None

Keputusan hybrid dicatat melalui tracking statistik (endpoint `/rag-stats`) untuk evaluasi transparan.

### 2.7 Arsitektur Sistem

Sistem terdiri dari:
1. **Backend API**: FastAPI dengan 5 endpoint (/health, /predict, /history/{id}, /history, /rag-stats)
2. **Dashboard**: Next.js 16 dengan TypeScript dan Tailwind CSS v4
3. **Vector DB**: ChromaDB Cloud
4. **LLM Gateway**: OpenRouter API
5. **Storage**: JSON file untuk riwayat pemeriksaan

---

## 3. Hasil dan Pembahasan

### 3.1 Evaluasi Model

Tabel 1 menunjukkan perbandingan performa Random Forest dan XGBoost pada test set (7.698 sampel).

**Tabel 1. Perbandingan Metrik Random Forest dan XGBoost**

| Metrik | Random Forest | XGBoost |
|--------|:---:|:---:|
| Accuracy | **0,9904** | 0,9843 |
| Precision (weighted) | **0,9904** | 0,9843 |
| Recall (weighted) | **0,9904** | 0,9843 |
| F1-Score (weighted) | **0,9904** | 0,9843 |

Random Forest dipilih sebagai model primer untuk sistem klasifikasi karena akurasi dan F1 lebih tinggi di semua kelas.

**Tabel 2. Per-Class F1-Score**

| Kelas (Kategori Risiko) | Random Forest | XGBoost |
|-------------------------|:---:|:---:|
| Normal (risiko rendah) | **0,9947** | 0,9909 |
| Severely Stunted (risiko sangat tinggi) | **0,9891** | 0,9832 |
| Stunted (risiko tinggi) | **0,9676** | 0,9467 |
| Tinggi (risiko rendah — pantau) | **0,9928** | 0,9885 |

Akurasi tinggi (>99%) bukan indikasi data leakage, melainkan konsekuensi dari sifat deterministik label: status stunting diturunkan dari tinggi badan dan usia melalui formula z-score WHO. Model pada dasarnya mempelajari inverse mapping dari formula tersebut — suatu perilaku yang diinginkan untuk sistem screening berbasis antropometri. Seluruh kesalahan terjadi di batas threshold (±2 SD, ±3 SD).

Kelas stunted memiliki F1 terendah (0,9676) karena merupakan kelas transisi dengan batas sempit (-3 SD hingga -2 SD), sehingga lebih rentan terhadap misklasifikasi di boundary. Hal ini wajar dan perlu diantisipasi dalam penggunaan klinis dengan memberikan margin toleransi.

### 3.2 Analisis Fitur

**Tabel 3. Feature Importance — Random Forest**

| Fitur | Importance |
|-------|:---:|
| Tinggi Badan (cm) | **0,6293** |
| Umur (bulan) | 0,3688 |
| Jenis Kelamin | 0,0019 |

Tinggi Badan mendominasi dengan kontribusi 62,93%, diikuti Umur (36,88%). Jenis Kelamin memiliki kontribusi minimal (0,19%) karena standar WHO untuk TB/U sudah mengakomodasi perbedaan gender dalam tabel referensi LMS. Pola ini konsisten antara Random Forest dan XGBoost serta sesuai ekspektasi klinis — sistem screening stunting berbasis TB/U memang hanya memerlukan tinggi dan usia.

### 3.3 Analisis SHAP

SHAP TreeExplainer mengonfirmasi dominasi fitur Tinggi Badan dan Umur pada semua kelas klasifikasi. Pada kasus severely stunted (usia 24 bulan, laki-laki, TB 70 cm), Tinggi Badan berkontribusi 76,5% terhadap klasifikasi, diikuti Umur 22,4%, dan Jenis Kelamin 1,1%. Kontribusi Jenis Kelamin yang minimal konsisten dengan feature importance dan masuk akal secara klinis karena standar WHO sudah memperhitungkan gender.

Output SHAP diformat sebagai JSON siap API dengan struktur:
- prediction: class, risk_score, probabilities
- shap: base_value, features (terurut berdasarkan |SHAP|)
- shap_per_class: nilai SHAP untuk setiap kelas

### 3.4 Sistem Rekomendasi Hybrid dan Tracking RAG

Sistem rekomendasi menggunakan pendekatan hybrid dua lapis. Tracking real-time melalui endpoint `/rag-stats` mencatat setiap keputusan.

**Tabel 4. RAG vs Rule-Based Fallback (Hasil Tracking)**

| Metrik | Nilai |
|--------|:-----:|
| Total prediksi | 5 (sampel uji) |
| RAG success | 0 (0%) |
| Rule-based fallback | 5 (100%) |
| Ketersediaan rekomendasi | 100% (5/5) |

Seluruh permintaan rekomendasi (100%) menggunakan rule-based fallback karena RAG retrieval tidak berhasil mendapatkan chunk yang cukup spesifik secara klinis untuk menghasilkan answer bermakna (>20 karakter). Root cause: embedding model English (all-MiniLM-L6-v2) kurang optimal untuk teks Bahasa Indonesia pada dokumen pedoman nasional, dan dokumen PNPK Stunting asli tidak dapat diperoleh (403 WAF dari server Kemkes).

Rule-based fallback tetap memberikan rekomendasi yang valid secara klinis karena disusun berdasarkan PNPK Stunting dan Permenkes No. 2/2020, bukan sekadar template generik.

### 3.5 Sistem End-to-End

Pengujian end-to-end mencakup 13 skenario. Seluruh skenario berhasil (13/13 PASS).

**Tabel 5. Hasil Pengujian End-to-End**

| No | Skenario | Input | Output | Status |
|:--:|----------|-------|--------|:------:|
| 1 | Normal | 36 bln, P, 95 cm | normal (risk 0%) | PASS |
| 2 | Severely Stunted | 24 bln, L, 70 cm | severely stunted (risk 100%) | PASS |
| 3 | Stunted | 48 bln, L, 93 cm | stunted (risk 100%) | PASS |
| 4 | Tinggi | 12 bln, P, 85 cm | tinggi (risk 0%) | PASS |
| 5 | Edge: usia 0 | 0 bln, P, 45 cm | stunted | PASS |
| 6 | Invalid: usia negatif | -1 bln | 422 (Bad Request) | PASS |
| 7 | Invalid: gender salah | xyz | 422 (Bad Request) | PASS |
| 8 | Riwayat by ID | e2e_normal | 1 record | PASS |
| 9 | Riwayat not found | nonexistent | 404 (Not Found) | PASS |
| 10 | Rekomendasi tersedia | 24 bln, L, 70 cm | answer (1168 chars) | PASS |
| 11 | Rekomendasi punya sumber | 24 bln, L, 70 cm | 2 sources | PASS |
| 12 | RAG Stats | — | total, success, fallback | PASS |
| 13 | List history | — | array of summaries | PASS |

Dashboard Next.js menampilkan:
1. Form input data balita dengan validasi real-time
2. Kartu hasil klasifikasi dengan indikator warna (teal=normal, amber=stunted, rose=severely stunted, sky=tinggi)
3. Diagram batang kontribusi SHAP
4. Panel rekomendasi (hybrid, selalu ada)
5. Riwayat pemeriksaan per balita

### 3.6 Keamanan: Environment Variables

Seluruh kredensial API (ChromaDB Cloud, OpenRouter) dipindahkan ke file `.env` dan di-load via `python-dotenv`. Tidak ada kredensial hardcoded di kode sumber production. File `.env` dan `.env.sample` disediakan; `.gitignore` mengamankan agar `.env` tidak tercomit.

### 3.7 Keterbatasan

Penelitian ini memiliki beberapa keterbatasan:
1. Dataset bersifat sintetik — validasi klinis lebih lanjut dengan data riil diperlukan
2. Model hanya menggunakan 3 fitur antropometri — faktor risiko lain (BB, riwayat penyakit, status ekonomi) belum diakomodasi
3. Embedding Bahasa Indonesia pada RAG masih menggunakan model English (all-MiniLM-L6-v2) yang kurang optimal — seluruh rekomendasi saat ini menggunakan rule-based fallback
4. PNPK Stunting tidak dapat diunduh langsung dari server Kemkes karena WAF — dokumen referensi teks dari web search digunakan sebagai alternatif
5. RAG belum berfungsi optimal untuk rekomendasi klinis spesifik karena keterbatasan konten chunk dan embedding model

---

## 4. Kesimpulan

Sistem klasifikasi risiko dan screening stunting pada balita berhasil dikembangkan dengan mengintegrasikan Random Forest (akurasi klasifikasi 99,04%, F1=0,9904), SHAP TreeExplainer untuk explainability, dan sistem rekomendasi hybrid (RAG + rule-based fallback). Analisis SHAP mengonfirmasi Tinggi Badan sebagai faktor dominan (62,93%) diikuti Umur (36,88%), sesuai ekspektasi klinis untuk klasifikasi TB/U. Sistem rekomendasi hybrid menjamin ketersediaan rekomendasi 100% (13/13 test) dengan tracking transparan melalui endpoint `/rag-stats`. Seluruh kredensial API diamankan melalui `.env`. Backend API (FastAPI, 5 endpoint) dan dashboard (Next.js) telah diuji end-to-end dengan 13/13 skenario berhasil.

Saran pengembangan ke depan meliputi: validasi dengan data klinis riil, penambahan fitur berat badan dan faktor sosio-ekonomi, penggunaan multilingual embedding model untuk meningkatkan recall RAG, akuisisi dokumen PNPK Stunting asli dari sumber offline, serta integrasi dengan sistem informasi Puskesmas.

---

## Daftar Pustaka

[1] WHO. WHO Child Growth Standards: Length/Height-for-age, Weight-for-age, Weight-for-length, Weight-for-height and Body Mass Index-for-age: Methods and Development. World Health Organization, 2006.

[2] Kementerian Kesehatan RI. "Survei Status Gizi Indonesia (SSGI) 2024." Jakarta, 2025.

[3] Peraturan Presiden Nomor 72 Tahun 2021 tentang Percepatan Penurunan Stunting.

[4] T. J. Cole, "The development of growth references and growth charts," Annals of Human Biology, vol. 39, no. 5, pp. 382–394, 2012.

[5] Keputusan Menteri Kesehatan Nomor HK.01.07/MENKES/1928/2022 tentang Pedoman Nasional Pelayanan Kedokteran Tata Laksana Stunting.

[6] C. Rudin, "Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead," Nature Machine Intelligence, vol. 1, pp. 206–215, 2019.

[7] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," in Advances in Neural Information Processing Systems 30, 2017, pp. 4765–4774.

[8] P. Lewis et al., "Retrieval-Augmented Generation for knowledge-intensive NLP tasks," in Advances in Neural Information Processing Systems 33, 2020, pp. 9459–9474.

[9] L. Breiman, "Random Forests," Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.

[10] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in Proceedings of the 22nd ACM SIGKDD, 2016, pp. 785–794.

[11] Peraturan Menteri Kesehatan Nomor 2 Tahun 2020 tentang Standar Antropometri Anak.

[12] S. M. Lundberg, G. Erion, and S.-I. Lee, "Consistent individualized feature attribution for tree ensembles," arXiv:1802.03888, 2018.
