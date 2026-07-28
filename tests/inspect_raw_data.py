import pandas as pd

# Primary dataset deeper inspection
df1 = pd.read_csv('D:\\Stunting\\data\\raw\\data_balita.csv')
print('=== PRIMARY DATASET INSPECTION ===')
print(f'Shape: {df1.shape}')
print(f'Columns: {list(df1.columns)}')
print(f'Null values:\n{df1.isnull().sum()}')
print()
print(f'Status Gizi unique values: {df1["Status Gizi"].unique()}')
print(f'Status Gizi value counts:\n{df1["Status Gizi"].value_counts()}')
print()
print(f'Jenis Kelamin unique: {df1["Jenis Kelamin"].unique()}')
print(f'Jenis Kelamin value counts:\n{df1["Jenis Kelamin"].value_counts()}')
print()
umur_col = 'Umur (bulan)'
tb_col = 'Tinggi Badan (cm)'
print(f'Umur range: {df1[umur_col].min()} - {df1[umur_col].max()} bulan')
print(f'Tinggi Badan range: {df1[tb_col].min()} - {df1[tb_col].max()} cm')
print(f'Tinggi Badan mean: {df1[tb_col].mean():.2f} cm')
print()
print('Sample rows (first 10):')
print(df1.head(10).to_string())
print()

# Secondary dataset - might need semicolon separator
print('=== SECONDARY DATASET ===')
df2_raw = pd.read_csv('D:\\Stunting\\data\\raw\\secondary\\Data Stunting Indonesia.csv')
print(f'Raw shape: {df2_raw.shape}')
print(f'Raw columns: {list(df2_raw.columns)}')
print(f'Raw content:')
print(df2_raw.to_string())
print()
print(f'Trying sep=";":')
df2 = pd.read_csv('D:\\Stunting\\data\\raw\\secondary\\Data Stunting Indonesia.csv', sep=';')
print(f'Shape: {df2.shape}')
print(f'Columns: {list(df2.columns)}')
print(df2.to_string())
