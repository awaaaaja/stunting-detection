import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from datetime import datetime

today = datetime.now().strftime('%Y%m%d')
print('='*60)
print(f'CLEANING & SPLIT v2 — {today}')
print('='*60)

# ============================================================
# 1. Load
# ============================================================
df = pd.read_csv('D:\\Stunting\\data\\processed\\stunting_with_zscore_20260728.csv')
print(f'Loaded: {len(df)} rows')

# ============================================================
# 2. Deduplicate to unique feature combinations
# ============================================================
print('\n--- STEP 1: Deduplication ---')
feat_cols = ['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)']
# Use the first occurrence of each unique feature combination
df_dedup = df.drop_duplicates(subset=feat_cols, keep='first').copy()
print(f'Before dedup: {len(df)} rows')
print(f'After dedup:  {len(df_dedup)} rows')
print(f'Dropped:      {len(df) - len(df_dedup)} rows (synthetic repeats)')

# ============================================================
# 3. BIV removal (|z| > 6)
# ============================================================
print('\n--- STEP 2: Biologically Implausible Values ---')
z = df_dedup['z_lhfa']
biv_low = (z < -6).sum()
biv_high = (z > 6).sum()
print(f'BIV low (z < -6):  {biv_low}')
print(f'BIV high (z > 6): {biv_high}')

df_clean = df_dedup[(z >= -6) & (z <= 6)].copy()
print(f'After BIV removal: {len(df_clean)} rows')
print(f'Dropped: {len(df_dedup) - len(df_clean)} rows')

# Show BIV examples
biv_rows = df_dedup[~((z >= -6) & (z <= 6))]
if len(biv_rows) > 0:
    print('\nBIV examples:')
    print(biv_rows[feat_cols + ['Status Gizi WHO', 'z_lhfa']].head(10).to_string())

# ============================================================
# 4. Feature engineering
# ============================================================
print('\n--- STEP 3: Feature Engineering ---')
jk_map = {'laki-laki': 1, 'perempuan': 0}
df_clean['Jenis Kelamin'] = df_clean['Jenis Kelamin'].map(jk_map)
print(f'Gender encoded: {jk_map}')

# Final dataset columns
df_final = df_clean[['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)', 'Status Gizi WHO']].copy()
df_final = df_final.rename(columns={'Status Gizi WHO': 'Status Gizi'})

print(f'\nFinal shape: {len(df_final)} rows')
print(f'Final label distribution:')
label_dist = df_final['Status Gizi'].value_counts()
for k, v in label_dist.items():
    print(f'  {k}: {v} ({v/len(df_final)*100:.1f}%)')

# ============================================================
# 5. Train/test split (80/20 stratified)
# ============================================================
print('\n--- STEP 4: Train/Test Split ---')
X = df_final[['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)']]
y = df_final['Status Gizi']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

train_df = X_train.copy()
train_df['Status Gizi'] = y_train
test_df = X_test.copy()
test_df['Status Gizi'] = y_test

print(f'Train: {len(train_df)} rows ({len(train_df)/len(df_final)*100:.1f}%)')
print(f'Test:  {len(test_df)} rows ({len(test_df)/len(df_final)*100:.1f}%)')

# Verify stratification
print('\nLabel distribution comparison:')
train_pct = train_df['Status Gizi'].value_counts(normalize=True).mul(100).round(1)
test_pct = test_df['Status Gizi'].value_counts(normalize=True).mul(100).round(1)
compare = pd.DataFrame({'Train %': train_pct, 'Test %': test_pct})
print(compare.to_string())

# Show test set info for locking
print('\n--- TEST SET LOCKED ---')
print('This test set must NOT be touched until final Fase 2 evaluation.')
print(f'Test set path: D:\\Stunting\\data\\processed\\stunting_test_{today}.csv')
print(f'Test set size: {len(test_df)} rows')
print(f'Random seed: 42 (documented)')

# ============================================================
# 6. Save
# ============================================================
print('\n--- STEP 5: Saving Outputs ---')
clean_path = f'D:\\Stunting\\data\\processed\\stunting_clean_{today}.csv'
df_final.to_csv(clean_path, index=False)
print(f'Full dataset -> {clean_path} ({len(df_final)} rows)')

train_path = f'D:\\Stunting\\data\\processed\\stunting_train_{today}.csv'
train_df.to_csv(train_path, index=False)
print(f'Train set -> {train_path} ({len(train_df)} rows)')

test_path = f'D:\\Stunting\\data\\processed\\stunting_test_{today}.csv'
test_df.to_csv(test_path, index=False)
print(f'Test set -> {test_path} ({len(test_df)} rows)')

print('\n' + '='*60)
print('CLEANING COMPLETE')
print('='*60)
