import pandas as pd

train = pd.read_csv('D:\\Stunting\\data\\processed\\stunting_train_20260728.csv')
test = pd.read_csv('D:\\Stunting\\data\\processed\\stunting_test_20260728.csv')

umur_col = 'Umur (bulan)'
jk_col = 'Jenis Kelamin'
tb_col = 'Tinggi Badan (cm)'
sg_col = 'Status Gizi'

# Check overlap
train_tuples = set(zip(train[umur_col], train[jk_col], train[tb_col]))
test_tuples = set(zip(test[umur_col], test[jk_col], test[tb_col]))
overlap = train_tuples & test_tuples
print(f'Train rows: {len(train)}')
print(f'Test rows: {len(test)}')
print(f'Overlap (data leakage): {len(overlap)} rows')
if len(overlap) == 0:
    print('No data leakage -- test set is completely isolated.')
else:
    print('WARNING: DATA LEAKAGE DETECTED!')

# No duplicates within sets
dup_train = train.duplicated().sum()
dup_test = test.duplicated().sum()
print(f'Duplicates in train: {dup_train}')
print(f'Duplicates in test: {dup_test}')

# Label distribution
print()
print('Train label %:')
print(train[sg_col].value_counts(normalize=True).mul(100).round(1))
print()
print('Test label %:')
print(test[sg_col].value_counts(normalize=True).mul(100).round(1))

# Feature ranges
print()
print(f'Train - age months: {train[umur_col].min()}-{train[umur_col].max()}')
print(f'Test  - age months: {test[umur_col].min()}-{test[umur_col].max()}')
print(f'Train - height: {train[tb_col].min():.1f}-{train[tb_col].max():.1f}')
print(f'Test  - height: {test[tb_col].min():.1f}-{test[tb_col].max():.1f}')
print(f'Train - gender: {train[jk_col].unique()}')
print(f'Test  - gender: {test[jk_col].unique()}')

print()
print('Test set is LOCKED. Do not modify.')
