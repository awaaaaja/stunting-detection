import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from datetime import datetime

today = datetime.now().strftime('%Y%m%d')
print(f'Cleaning date: {today}')
print('='*60)

# ============================================================
# 1. Load data with z-scores from Sprint 2
# ============================================================
df = pd.read_csv(f'D:\\Stunting\\data\\processed\\stunting_with_zscore_{today}.csv')
print(f'Loaded: {len(df)} rows, {len(df.columns)} cols')
print(f'Columns: {list(df.columns)}')
print()

# ============================================================
# 2. Check duplicates
# ============================================================
print('='*60)
print('DUPLICATE CHECK')
print('='*60)
dup_mask = df.duplicated(keep='first')
n_dup = dup_mask.sum()
print(f'Exact duplicates (all columns): {n_dup}')
if n_dup > 0:
    print(f'Duplicate rows (first 10):')
    print(df[dup_mask].head(10).to_string())
    df = df[~dup_mask].copy()
    print(f'After drop: {len(df)} rows')

# Also check duplicates on feature columns only (ignoring label)
feat_cols = ['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)']
dup_feat = df.duplicated(subset=feat_cols, keep=False)
n_dup_feat = dup_feat.sum()
print(f'\nRows with duplicate features (same age+gender+height but different label): {n_dup_feat}')
if n_dup_feat > 0:
    # Show some examples
    dup_examples = df[dup_feat].sort_values(by=feat_cols).head(20)
    print(dup_examples[feat_cols + ['Status Gizi', 'Status Gizi WHO', 'z_lhfa']].to_string())
print()

# ============================================================
# 3. Validate physiological outliers using WHO z-score
# ============================================================
print('='*60)
print('PHYSIOLOGICAL OUTLIER VALIDATION (WHO BIV criteria)')
print('='*60)
# WHO considers |z| > 5 as Biologically Implausible Value (BIV) for height-for-age
# Also |z| > 6 is definitely impossible
z = df['z_lhfa']
biv_mask = (z < -6) | (z > 6)
n_biv = biv_mask.sum()
print(f'Biologically Implausible Values (|z| > 6): {n_biv}')

extreme_mask = ((z < -5) & (z >= -6)) | ((z > 5) & (z <= 6))
n_extreme = extreme_mask.sum()
print(f'Extreme values (5 < |z| <= 6): {n_extreme}')

# Show BIV details
if n_biv > 0:
    biv_data = df[biv_mask]
    print(f'\nBIV rows:')
    print(biv_data[['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)', 'Status Gizi WHO', 'z_lhfa']].head(20).to_string())

# Decision: drop BIV (|z| > 6), keep extreme for review
if n_biv > 0:
    print(f'\nDropping {n_biv} BIV rows (|z| > 6)...')
    df = df[~biv_mask].copy()
    print(f'After drop: {len(df)} rows')
print()

# ============================================================
# 4. Feature engineering
# ============================================================
print('='*60)
print('FEATURE ENGINEERING')
print('='*60)

# Encode Jenis Kelamin: laki-laki -> 1, perempuan -> 0
jk_map = {'laki-laki': 1, 'perempuan': 0}
df['Jenis Kelamin'] = df['Jenis Kelamin'].map(jk_map)
print(f'Jenis Kelamin encoded: {jk_map}')
print(f'Value counts:')
print(df['Jenis Kelamin'].value_counts().to_string())
print()

# ============================================================
# 5. Prepare final dataset
# ============================================================
print('='*60)
print('FINAL DATASET PREPARATION')
print('='*60)

# Final columns: features + target
# Target = Status Gizi WHO (WHO z-score based label)
final_cols = ['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)', 'Status Gizi WHO']
df_final = df[final_cols].copy()
df_final = df_final.rename(columns={'Status Gizi WHO': 'Status Gizi'})

print(f'Final shape: {df_final.shape}')
print(f'Final columns: {list(df_final.columns)}')
print(f'Final label distribution:')
print(df_final['Status Gizi'].value_counts())
print()

# ============================================================
# 6. Train/test split (stratified)
# ============================================================
print('='*60)
print('TRAIN/TEST SPLIT (80/20 STRATIFIED)')
print('='*60)

X = df_final[['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)']]
y = df_final['Status Gizi']

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Combine back for saving
train_df = X_train.copy()
train_df['Status Gizi'] = y_train

test_df = X_test.copy()
test_df['Status Gizi'] = y_test

print(f'Train set: {len(train_df)} rows')
print(f'  Label distribution:')
print(f'  {train_df["Status Gizi"].value_counts().to_dict()}')
print(f'  {train_df["Status Gizi"].value_counts(normalize=True).mul(100).round(1).to_dict()}%')
print()
print(f'Test set: {len(test_df)} rows')
print(f'  Label distribution:')
print(f'  {test_df["Status Gizi"].value_counts().to_dict()}')
print(f'  {test_df["Status Gizi"].value_counts(normalize=True).mul(100).round(1).to_dict()}%')
print()

# Verify stratified proportions are preserved
print('Stratification check (class %):')
train_pct = train_df['Status Gizi'].value_counts(normalize=True).sort_index()
test_pct = test_df['Status Gizi'].value_counts(normalize=True).sort_index()
compare = pd.DataFrame({'Train %': train_pct.mul(100).round(2), 'Test %': test_pct.mul(100).round(2)})
print(compare.to_string())

# ============================================================
# 7. Save all outputs
# ============================================================
print('='*60)
print('SAVING OUTPUTS')
print('='*60)

# Full cleaned dataset
clean_path = f'D:\\Stunting\\data\\processed\\stunting_clean_{today}.csv'
df_final.to_csv(clean_path, index=False)
print(f'Full dataset -> {clean_path} ({len(df_final)} rows)')

# Train set
train_path = f'D:\\Stunting\\data\\processed\\stunting_train_{today}.csv'
train_df.to_csv(train_path, index=False)
print(f'Train set -> {train_path} ({len(train_df)} rows)')

# Test set (LOCKED)
test_path = f'D:\\Stunting\\data\\processed\\stunting_test_{today}.csv'
test_df.to_csv(test_path, index=False)
print(f'Test set -> {test_path} ({len(test_df)} rows)')

print()
print('='*60)
print('CLEANING SUMMARY')
print('='*60)
print(f'Original rows: 120999')
print(f'Duplicates dropped: {n_dup}')
print(f'BIV dropped (|z| > 6): {n_biv}')
print(f'Final rows: {len(df_final)}')
print(f'Train rows: {len(train_df)} ({len(train_df)/len(df_final)*100:.1f}%)')
print(f'Test rows: {len(test_df)} ({len(test_df)/len(df_final)*100:.1f}%)')
print()
print('IMPORTANT: Test set is LOCKED. Do NOT touch until final evaluation (Fase 2).')
