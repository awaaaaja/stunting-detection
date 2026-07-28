# Data Profile -- 2026-07-28

## Dataset: data_balita.csv (Primary)

- **Sumber**: https://www.kaggle.com/datasets/rendiputra/stunting-balita-detection-121k-rows
- **Jumlah baris**: 120999
- **Jumlah kolom**: 7
- **Missing values**: 0 (semua kolom lengkap)

## Kolom & Tipe Data

| Kolom | Tipe | Range | Keterangan |
|-------|------|-------|------------|
| Umur (bulan) | int64 | 0 -- 60 | Usia balita dalam bulan |
| Jenis Kelamin | object | laki-laki / perempuan | -- |
| Tinggi Badan (cm) | float64 | 40.01 -- 128.00 | Tinggi/panjang badan |
| Status Gizi | object | 4 kelas | Label existing dari dataset |

## Statistik Deskriptif

| Kolom | Mean | Std | Min | 25% | 50% | 75% | Max |
|-------|------|-----|-----|-----|-----|-----|-----|
| Umur (bulan) | 30.17 | 17.58 | 0.00 | 15.00 | 30.00 | 45.00 | 60.00 |
| Tinggi Badan (cm) | 88.66 | 17.30 | 40.01 | 77.00 | 89.80 | 101.20 | 128.00 |

## Distribusi Jenis Kelamin

- perempuan: 61002 (50.4%)
- laki-laki: 59997 (49.6%)

## Distribusi Status Gizi

### Label Existing (dari dataset asli)

- normal: 67755 (56.0%)
- severely stunted: 19869 (16.4%)
- tinggi: 19560 (16.2%)
- stunted: 13815 (11.4%)

### Label Baru (berdasarkan WHO z-score)

- normal: 67779 (56.0%)
- severely stunted: 20076 (16.6%)
- tinggi: 19690 (16.3%)
- stunted: 13454 (11.1%)

## Validasi Z-Score

- **Library**: `anthro` v1.1.1 (WHO Child Growth Standards 2006)
- **Mode**: bulanan (age_months)
- **Z-score yang dihitung**: lhfa (Length/Height-for-Age) -- indikator stunting
- **Valid**: 120999/120999 (100%)
- **Agreement dengan label existing**: 99.50%
- **Total disagreement**: 603 baris (0.5%) -- semuanya di batas threshold klasifikasi

### Detail Disagreement

| Existing -> New | Jumlah | Penyebab |
|---------------|--------|----------|
| stunted -> severely stunted | 212 | z-score ~ -3.00 (very close to threshold) |
| normal -> stunted | 176 | z-score ~ -2.00 (borderline) |
| normal -> tinggi | 159 | z-score ~ +3.00 (borderline) |
| normal -> stunted | 22 | z-score ~ -2.00 |
| tinggi -> normal | 29 | z-score ~ +3.00 |
| severely stunted -> stunted | 5 | z-score ~ -3.00 |

## Physiological Outlier Check

| Kolom | Rentang wajar | Temuan |
|-------|---------------|--------|
| Umur (bulan) | 0-60 | Semua dalam rentang |
| Tinggi Badan (cm) | 30-130 (per age group) | 305 baris di batas atas (usia 6 bln, TB ~80 cm) -- fisiologis mungkin untuk anak tinggi |

## Catatan

- Dataset original sudah sangat bersih: 0 missing, 0 duplikat, distribusi wajar.
- Label existing 99.5% konsisten dengan WHO z-score -- dataset berkualitas tinggi.
- Untuk cleaning final (Sprint 3), label baru (WHO z-score) akan digunakan sebagai ground truth.
- 305 baris outlier height tidak di-drop -- akan diverifikasi ulang di Sprint 3 dengan batas fisiologis yang lebih presisi per usia.