import pandas as pd
import numpy as np
from anthro import compute, batch
import json

# ============================================================
# 1. Load dataset
# ============================================================
df = pd.read_csv('D:\\Stunting\\data\\raw\\data_balita.csv')
print(f'Dataset shape: {df.shape}')
print(f'Columns: {list(df.columns)}')

# ============================================================
# 2. Profile data
# ============================================================
print('\n' + '='*60)
print('DATA PROFILE')
print('='*60)

print(f'\nMissing values:\n{df.isnull().sum()}')

num_cols = ['Umur (bulan)', 'Tinggi Badan (cm)']
for c in num_cols:
    print(f'\n--- {c} ---')
    print(f'  Mean:   {df[c].mean():.4f}')
    print(f'  Std:    {df[c].std():.4f}')
    print(f'  Min:    {df[c].min():.4f}')
    print(f'  25%:    {df[c].quantile(0.25):.4f}')
    print(f'  50%:    {df[c].quantile(0.50):.4f}')
    print(f'  75%:    {df[c].quantile(0.75):.4f}')
    print(f'  Max:    {df[c].max():.4f}')

print(f'\n--- Jenis Kelamin ---')
jk_map = df['Jenis Kelamin'].value_counts()
for k, v in jk_map.items():
    print(f'  {k}: {v} ({v/len(df)*100:.1f}%)')

print(f'\n--- Status Gizi (existing label) ---')
sg_map = df['Status Gizi'].value_counts()
for k, v in sg_map.items():
    print(f'  {k}: {v} ({v/len(df)*100:.1f}%)')

# ============================================================
# 3. Check for physiological outliers
# ============================================================
print('\n' + '='*60)
print('PHYSIOLOGICAL OUTLIER CHECK')
print('='*60)

# Reasonable ranges for 0-60 month Indonesian children (approximate)
# Height range per age: very rough check
outlier_height = df[
    ((df['Umur (bulan)'] == 0) & ((df['Tinggi Badan (cm)'] < 30) | (df['Tinggi Badan (cm)'] > 70))) |
    ((df['Umur (bulan)'] >= 1) & (df['Umur (bulan)'] <= 6) & ((df['Tinggi Badan (cm)'] < 35) | (df['Tinggi Badan (cm)'] > 80))) |
    ((df['Umur (bulan)'] >= 7) & (df['Umur (bulan)'] <= 12) & ((df['Tinggi Badan (cm)'] < 40) | (df['Tinggi Badan (cm)'] > 90))) |
    ((df['Umur (bulan)'] >= 13) & (df['Umur (bulan)'] <= 24) & ((df['Tinggi Badan (cm)'] < 50) | (df['Tinggi Badan (cm)'] > 100))) |
    ((df['Umur (bulan)'] >= 25) & (df['Umur (bulan)'] <= 36) & ((df['Tinggi Badan (cm)'] < 60) | (df['Tinggi Badan (cm)'] > 110))) |
    ((df['Umur (bulan)'] >= 37) & (df['Umur (bulan)'] <= 48) & ((df['Tinggi Badan (cm)'] < 70) | (df['Tinggi Badan (cm)'] > 120))) |
    ((df['Umur (bulan)'] >= 49) & (df['Umur (bulan)'] <= 60) & ((df['Tinggi Badan (cm)'] < 75) | (df['Tinggi Badan (cm)'] > 130)))
]
print(f'Rows with potentially outlier height: {len(outlier_height)}')
if len(outlier_height) > 0:
    print(outlier_height.head(20).to_string())

# ============================================================
# 4. Calculate z-scores using WHO Anthro library
# ============================================================
print('\n' + '='*60)
print('Z-SCORE CALCULATION (WHO Anthro)')
print('='*60)

# Map gender: 'laki-laki' -> 'm', 'perempuan' -> 'f'
sex_map = {'laki-laki': 'm', 'perempuan': 'f'}
df['sex'] = df['Jenis Kelamin'].map(sex_map)

# Prepare batch input for anthro
# Use month mode since we have age in months
batch_input = []
for _, row in df.iterrows():
    batch_input.append({
        'sex': row['sex'],
        'age_months': row['Umur (bulan)'],
        'height_cm': row['Tinggi Badan (cm)'],
    })

# Process in chunks of 1000 to avoid memory issues
chunk_size = 1000
results = []
for i in range(0, len(batch_input), chunk_size):
    chunk = batch_input[i:i+chunk_size]
    chunk_results = batch(chunk, default_mode='month')
    results.extend(chunk_results)
    if (i // chunk_size) % 10 == 0:
        print(f'  Processed {i+len(chunk)}/{len(batch_input)} rows...')

print(f'  Total processed: {len(results)} rows')

# ============================================================
# 5. Extract z-scores and compare with existing labels
# ============================================================
print('\n' + '='*60)
print('CLASSIFICATION COMPARISON')
print('='*60)

# anthro uses: 'Severely stunted', 'Moderately stunted', 'Normal' for lhfa
# Our dataset uses: 'severely stunted', 'stunted', 'normal', 'tinggi'

z_scores = [r['z_lhfa'] for r in results]
classifications = [r['lhfa'] for r in results]

# Handle missing/error results
valid_mask = [isinstance(z, (int, float)) for z in z_scores]
print(f'Valid z-scores: {sum(valid_mask)}/{len(valid_mask)}')
print(f'Invalid/missing z-scores: {sum(1 for v in valid_mask if not v)}')

# Create new classification based on WHO thresholds
new_labels = []
for z in z_scores:
    if not isinstance(z, (int, float)):
        new_labels.append(None)
    elif z < -3:
        new_labels.append('severely stunted')
    elif z < -2:
        new_labels.append('stunted')
    elif z <= 3:
        new_labels.append('normal')
    else:
        new_labels.append('tinggi')

df['z_lhfa'] = z_scores
df['new_label'] = new_labels
df['anthro_class'] = classifications

# Comparison
valid_df = df[valid_mask].copy()
print(f'\nNew label distribution (WHO z-score based):')
print(valid_df['new_label'].value_counts())

print(f'\nExisting label distribution:')
print(valid_df['Status Gizi'].value_counts())

print(f'\nCross-tabulation (new vs existing):')
ct = pd.crosstab(valid_df['Status Gizi'], valid_df['new_label'], margins=True)
print(ct)

# Agreement rate
agreement = valid_df['Status Gizi'] == valid_df['new_label']
print(f'\nAgreement rate: {agreement.sum()}/{len(valid_df)} = {agreement.mean()*100:.2f}%')

# Where they disagree
disagree = valid_df[valid_df['Status Gizi'] != valid_df['new_label']]
print(f'\nDisagreement samples (first 20):')
print(disagree[['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)', 'Status Gizi', 'new_label', 'z_lhfa']].head(20).to_string())

print(f'\nDisagreement by existing label:')
print(disagree['Status Gizi'].value_counts())

print(f'\nDisagreement by new label:')
print(disagree['new_label'].value_counts())
