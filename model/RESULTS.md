# Model Evaluation Results — Sprint 4

Date: 2026-07-28
Dataset: stunting_clean_20260728.csv (38,487 unique samples)
Train/Test split: 80/20 stratified (30,789 / 7,698)

## Model Comparison

| Metric | Random Forest | XGBoost |
|--------|:---:|:---:|
| Accuracy | **0.9904** | 0.9843 |
| Precision (weighted) | **0.9904** | 0.9843 |
| Recall (weighted) | **0.9904** | 0.9843 |
| F1-Score (weighted) | **0.9904** | 0.9843 |

## Per-Class F1-Score

| Class | Random Forest | XGBoost |
|-------|:---:|:---:|
| normal | **0.9947** | 0.9909 |
| severely stunted | **0.9891** | 0.9832 |
| stunted | **0.9676** | 0.9467 |
| tinggi | **0.9928** | 0.9885 |

## Feature Importance

### Random Forest
| Feature | Importance |
|---------|:---:|
| Tinggi Badan (cm) | **0.6293** |
| Umur (bulan) | 0.3688 |
| Jenis Kelamin | 0.0019 |

### XGBoost
| Feature | Importance |
|---------|:---:|
| Umur (bulan) | **0.4663** |
| Tinggi Badan (cm) | 0.4471 |
| Jenis Kelamin | 0.0866 |

## Notes
- RF selected as primary model for SHAP (Fase 3) due to higher accuracy and F1.
- Accuracy >99% is expected: label is deterministically derived from the same features (age, height) via WHO z-score formula — no data leakage.
- Jenis Kelamin has very low importance for RF because WHO height-for-age standards already account for gender in the reference tables.
- All errors occur at boundary thresholds (+-2SD, +-3SD).

## Visualizations
See `model/visualizations/`:
- `confusion_matrices_YYYYMMDD.png`
- `roc_curves_YYYYMMDD.png`
- `feature_importance_YYYYMMDD.png`
- `model_comparison_YYYYMMDD.png`
- `per_class_metrics_YYYYMMDD.png`

## Artifacts Saved
- `model/artifacts/rf_model_YYYYMMDD.pkl` (Random Forest)
- `model/artifacts/xgb_model_YYYYMMDD.pkl` (XGBoost)
- `model/artifacts/label_encoder_YYYYMMDD.pkl` (LabelEncoder)
