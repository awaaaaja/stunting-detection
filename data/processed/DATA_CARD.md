# DATA_CARD.md -- Dokumentasi Dataset

## Informasi Dataset

| Field | Detail |
|-------|--------|
| **Nama dataset** | Stunting Balita Detection (121K rows) |
| **Sumber** | https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows |
| **Tanggal unduh** | 2026-07-28 |
| **Metode unduh** | `kagglehub` v1.0.2 (official Kaggle Python library) |
| **Jumlah baris raw** | 120,999 |
| **Jumlah kolom raw** | 4 |
| **Lisensi** | Kaggle Open Data (CC0-like) |

## Skema Original

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `Umur (bulan)` | int64 | Usia balita dalam bulan (0-60) |
| `Jenis Kelamin` | object | laki-laki / perempuan |
| `Tinggi Badan (cm)` | float64 | Tinggi/panjang badan (40.01 - 128.0 cm) |
| `Status Gizi` | object | Label existing: normal, stunted, severely stunted, tinggi |

## Validasi Z-Score

### Metode
- **Library**: `anthro` v1.1.1 -- Python implementation of WHO Child Growth Standards (2006)
- **Indikator**: lhfa (Length/Height-for-Age), indikator utama stunting
- **Mode**: bulanan (age_months)
- **Sumber tabel LMS**: WHO igrowup day-indexed tables (same as SAS/SPSS/Stata official implementation)

### Threshold Klasifikasi (Permenkes No. 2/2020)
| Kategori | Rentang Z-Score |
|-----------|-----------------|
| Severely stunted | Z < -3 SD |
| Stunted | -3 SD <= Z < -2 SD |
| Normal | -2 SD <= Z <= +3 SD |
| Tinggi | Z > +3 SD |

### Hasil Validasi
- **Valid z-score**: 120,999 / 120,999 (100%)
- **Agreement dengan label existing**: 99.50%
- **Disagreement**: 603 baris (0.5%)

### Detail Disagreement
| Existing -> WHO Baru | Jumlah | Penyebab |
|---------------------|--------|----------|
| stunted -> severely stunted | 212 | z-score ~ -3.00 (boundary) |
| normal -> stunted | 176 | z-score ~ -2.00 (boundary) |
| normal -> tinggi | 159 | z-score ~ +3.00 (boundary) |
| normal -> stunted | 22 | z-score ~ -2.00 |
| tinggi -> normal | 29 | z-score ~ +3.00 |
| severely stunted -> stunted | 5 | z-score ~ -3.00 |

**Keputusan**: Label WHO z-score digunakan sebagai ground truth baru karena dihitung dengan library tervalidasi resmi WHO.

## Keputusan Cleaning

### Cleaning Final (Sprint 3)

| Langkah | Detail | Baris Tersisa |
|---------|--------|---------------|
| Original | Dataset mentah dari Kaggle | 120,999 |
| Deduplikasi | Dataset sintetik dengan banyak baris identik; dedup ke unique (age, gender, height) combos | 39,425 |
| BIV removal | Biologically Implausible Values: drop baris dengan \|z_lhfa\| > 6 (WHO standard) — 184 z < -6 + 754 z > 6 | 38,487 |
| Feature engineering | Encode Jenis Kelamin (laki-laki=1, perempuan=0), urut kolom: Umur, JK, TB, Status Gizi | 38,487 |
| Train/test split | 80/20 stratified by label, random_state=42, test set **dikunci** | Train: 30,789 / Test: 7,698 |

### Alasan Keputusan
1. **Deduplikasi**: Dataset bersifat sintetik (121K baris dari ~39K kombinasi unik). Menjaga duplikat akan memberi bobot berlebih pada sampel yang sama. Deduplikasi ke unique feature combinations menghasilkan dataset yang lebih bersih untuk ML.
2. **BIV threshold (|z| > 6)**: Sesuai standar WHO — nilai antropometri di luar ±6 SD dianggap mustahil secara fisiologis dan harus dieksklusi.
3. **Stratified split**: Menjamin proporsi kelas yang sama di train dan test, penting untuk klasifikasi multiclass dengan kelas imbalance (stunting 11.2% vs normal 55.9%).
4. **Test set dikunci (seed=42)**: Tidak boleh disentuh sampai evaluasi akhir Fase 2. Setiap akses sebelum waktunya dicatat sebagai data leakage.

## Dataset Sekunder (Referensi)

| Field | Detail |
|-------|--------|
| **Nama** | Data Stunting Indonesia |
| **Sumber** | https://www.kaggle.com/datasets/dwiiyy/data-stunting-indonesia |
| **Jumlah baris** | 38 (per provinsi) |
| **Kolom** | Provinsi, 2020, 2021, 2022, 2023 (prevalensi stunting %) |
| **Kegunaan** | Sanity check distribusi label hasil cleaning terhadap angka nasional |

## File Output

| File | Deskripsi |
|------|-----------|
| `data/processed/data_profile.md` | Profil statistik lengkap dataset |
| `data/processed/DATA_CARD.md` | Dokumentasi dataset ini |
| `data/processed/stunting_clean_20260728.csv` | Final dataset siap ML (38,487 rows, 4 cols) |
| `data/processed/stunting_train_20260728.csv` | Training set (30,789 rows) |
| `data/processed/stunting_test_20260728.csv` | Test set **LOCKED** (7,698 rows) |
| `data/processed/stunting_with_zscore_20260728.csv` | Intermediate: dataset + z-score WHO + label baru (39,425 rows after dedup) |
