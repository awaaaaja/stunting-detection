import pandas as pd
import numpy as np

df = pd.read_csv('D:\\Stunting\\data\\processed\\stunting_with_zscore_20260728.csv')
print(f'Total rows: {len(df)}')
print(f'Total columns: {len(df.columns)}')
print(f'Columns: {list(df.columns)}')
print()

# Check unique combinations of features only
feat_cols = ['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)']
unique_feat = df.drop_duplicates(subset=feat_cols)
print(f'Unique feature combinations: {len(unique_feat)}')

# Check unique combinations of features + z-score
unique_feat_z = df.drop_duplicates(subset=feat_cols + ['z_lhfa'])
print(f'Unique feature+z combinations: {len(unique_feat_z)}')

# Check unique combinations of features + label
unique_feat_label = df.drop_duplicates(subset=feat_cols + ['Status Gizi WHO'])
print(f'Unique feature+label combinations: {len(unique_feat_label)}')

# Unique everything
unique_all = df.drop_duplicates()
print(f'Unique all columns: {len(unique_all)}')
print()

# Distribution of duplicates
print('Duplicate frequency distribution:')
freq = df.groupby(feat_cols).size()
print(f'Feature combos appearing: ')
print(f'  1 time: {(freq == 1).sum()}')
print(f'  2-5 times: {((freq >= 2) & (freq <= 5)).sum()}')
print(f'  6-10 times: {((freq >= 6) & (freq <= 10)).sum()}')
print(f'  11-50 times: {((freq >= 11) & (freq <= 50)).sum()}')
print(f'  >50 times: {(freq > 50).sum()}')
print(f'  Max frequency: {freq.max()}')
print()

# Is this synthetic/repeated data?
# Check sample of highly duplicated combinations
high_freq = freq[freq > 50].head(10)
print('Sample of highly duplicated feature combos (frequency > 50):')
for idx, count in high_freq.items():
    subset = df[(df['Umur (bulan)'] == idx[0]) & (df['Jenis Kelamin'] == idx[1]) & (df['Tinggi Badan (cm)'] == idx[2])]
    print(f'  Age={idx[0]}, Gender={idx[1]}, Height={idx[2]}: freq={count}, labels={subset["Status Gizi WHO"].unique()}, z_range=[{subset["z_lhfa"].min():.4f}, {subset["z_lhfa"].max():.4f}]')

# Check: are duplicates because of floating point in z-score?
print('\nFloating point precision check:')
z_unique = df['z_lhfa'].nunique()
print(f'Unique z_lhfa values: {z_unique} out of {len(df)}')
print(f'Unique heights: {df["Tinggi Badan (cm)"].nunique()} out of {len(df)}')

# Check: how many unique (age, gender, rounded_height) combos?
df['height_rounded'] = df['Tinggi Badan (cm)'].round(1)
unique_rounded = df.drop_duplicates(subset=['Umur (bulan)', 'Jenis Kelamin', 'height_rounded']).shape[0]
print(f'\nUnique (age, gender, height_1dp) combos: {unique_rounded}')
unique_rounded_int = df.drop_duplicates(subset=['Umur (bulan)', 'Jenis Kelamin', df['Tinggi Badan (cm)'].round(0)]).shape[0]
print(f'Unique (age, gender, height_int) combos: {unique_rounded_int}')

# What does the original duplicate count look like WITHOUT z-score column?
dup_no_z = df[feat_cols + ['Status Gizi']].duplicated(keep='first').sum()
print(f'\nDuplicates (feat + original label, no z): {dup_no_z}')

dup_who = df[feat_cols + ['Status Gizi WHO']].duplicated(keep='first').sum()
print(f'Duplicates (feat + WHO label, no z): {dup_who}')
