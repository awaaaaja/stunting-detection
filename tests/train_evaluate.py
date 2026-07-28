import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, label_binarize
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, classification_report, confusion_matrix,
                             roc_curve, auc)
import xgboost as xgb
import pickle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

today = datetime.now().strftime('%Y%m%d')
out_dir = 'D:\\Stunting\\model\\artifacts'
os.makedirs(out_dir, exist_ok=True)
viz_dir = 'D:\\Stunting\\model\\visualizations'
os.makedirs(viz_dir, exist_ok=True)

sns.set_style('whitegrid')
plt.rcParams['figure.dpi'] = 120

print('='*60)
print('SPRINT 4 — MODEL TRAINING & EVALUATION')
print('='*60)

# ============================================================
# 1. Load data
# ============================================================
print('\n--- Loading Data ---')
train = pd.read_csv('D:\\Stunting\\data\\processed\\stunting_train_20260728.csv')
test = pd.read_csv('D:\\Stunting\\data\\processed\\stunting_test_20260728.csv')

feature_cols = ['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)']
target_col = 'Status Gizi'

X_train = train[feature_cols]
y_train_str = train[target_col]
X_test = test[feature_cols]
y_test_str = test[target_col]

# Encode labels
le = LabelEncoder()
y_train = le.fit_transform(y_train_str)
y_test = le.transform(y_test_str)
class_names = le.classes_
n_classes = len(class_names)

print(f'Classes: {list(class_names)}')
print(f'Train: {X_train.shape}, Test: {X_test.shape}')
print(f'Train class distribution: {dict(zip(class_names, np.bincount(y_train)))}')
print(f'Test class distribution: {dict(zip(class_names, np.bincount(y_test)))}')

# ============================================================
# 2. Train Random Forest
# ============================================================
print('\n--- Training Random Forest ---')
rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
y_prob_rf = rf.predict_proba(X_test)

acc_rf = accuracy_score(y_test, y_pred_rf)
prec_rf = precision_score(y_test, y_pred_rf, average='weighted')
rec_rf = recall_score(y_test, y_pred_rf, average='weighted')
f1_rf = f1_score(y_test, y_pred_rf, average='weighted')

print(f'RF Accuracy:  {acc_rf:.4f}')
print(f'RF Precision: {prec_rf:.4f}')
print(f'RF Recall:    {rec_rf:.4f}')
print(f'RF F1-Score:  {f1_rf:.4f}')
print()
print('RF Classification Report:')
print(classification_report(y_test, y_pred_rf, target_names=class_names))

rf_cm = confusion_matrix(y_test, y_pred_rf)
print(f'RF Confusion Matrix:\n{rf_cm}')

# ============================================================
# 3. Train XGBoost
# ============================================================
print('\n--- Training XGBoost ---')
xgb_model = xgb.XGBClassifier(
    n_estimators=100, random_state=42, n_jobs=-1,
    eval_metric='mlogloss', use_label_encoder=False
)
xgb_model.fit(X_train, y_train)
y_pred_xgb = xgb_model.predict(X_test)
y_prob_xgb = xgb_model.predict_proba(X_test)

acc_xgb = accuracy_score(y_test, y_pred_xgb)
prec_xgb = precision_score(y_test, y_pred_xgb, average='weighted')
rec_xgb = recall_score(y_test, y_pred_xgb, average='weighted')
f1_xgb = f1_score(y_test, y_pred_xgb, average='weighted')

print(f'XGB Accuracy:  {acc_xgb:.4f}')
print(f'XGB Precision: {prec_xgb:.4f}')
print(f'XGB Recall:    {rec_xgb:.4f}')
print(f'XGB F1-Score:  {f1_xgb:.4f}')
print()
print('XGB Classification Report:')
print(classification_report(y_test, y_pred_xgb, target_names=class_names))

xgb_cm = confusion_matrix(y_test, y_pred_xgb)
print(f'XGB Confusion Matrix:\n{xgb_cm}')

# ============================================================
# 4. Save models
# ============================================================
print('\n--- Saving Models ---')
with open(f'{out_dir}/rf_model_{today}.pkl', 'wb') as f:
    pickle.dump(rf, f)
with open(f'{out_dir}/xgb_model_{today}.pkl', 'wb') as f:
    pickle.dump(xgb_model, f)
with open(f'{out_dir}/label_encoder_{today}.pkl', 'wb') as f:
    pickle.dump(le, f)
print(f'RF model saved: rf_model_{today}.pkl')
print(f'XGB model saved: xgb_model_{today}.pkl')
print(f'Label encoder saved: label_encoder_{today}.pkl')

# ============================================================
# 5. VISUALIZATIONS
# ============================================================
print('\n--- Generating Visualizations ---')

# --- 5a. Confusion Matrices ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, cm, model_name, title in [
    (axes[0], rf_cm, 'Random Forest', 'RF Confusion Matrix'),
    (axes[1], xgb_cm, 'XGBoost', 'XGBoost Confusion Matrix')
]:
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')

plt.tight_layout()
plt.savefig(f'{viz_dir}/confusion_matrices_{today}.png', bbox_inches='tight', dpi=150)
plt.close()
print('  confusion_matrices.png saved')

# --- 5b. ROC Curves ---
y_test_bin = label_binarize(y_test, classes=range(n_classes))

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, y_prob, model_name in [
    (axes[0], y_prob_rf, 'Random Forest'),
    (axes[1], y_prob_xgb, 'XGBoost')
]:
    for i in range(n_classes):
        fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, lw=2, label=f'{class_names[i]} (AUC={roc_auc:.3f})')
    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(f'{model_name} — ROC Curves (OvR)', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)

plt.tight_layout()
plt.savefig(f'{viz_dir}/roc_curves_{today}.png', bbox_inches='tight', dpi=150)
plt.close()
print('  roc_curves.png saved')

# --- 5c. Feature Importance ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, model, model_name in [
    (axes[0], rf, 'Random Forest'),
    (axes[1], xgb_model, 'XGBoost')
]:
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(importances)))
    ax.barh(range(len(importances)), importances[indices][::-1],
            color=colors[::-1], edgecolor='navy', linewidth=0.5)
    ax.set_yticks(range(len(importances)))
    ax.set_yticklabels([feature_cols[i] for i in indices[::-1]])
    ax.set_xlabel('Importance')
    ax.set_title(f'{model_name} — Feature Importance', fontsize=12, fontweight='bold')
    for i, v in enumerate(importances[indices][::-1]):
        ax.text(v + 0.01, i, f'{v:.3f}', va='center', fontsize=10)

plt.tight_layout()
plt.savefig(f'{viz_dir}/feature_importance_{today}.png', bbox_inches='tight', dpi=150)
plt.close()
print('  feature_importance.png saved')

# --- 5d. Model Comparison Bar Chart ---
metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
rf_scores = [acc_rf, prec_rf, rec_rf, f1_rf]
xgb_scores = [acc_xgb, prec_xgb, rec_xgb, f1_xgb]

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(metrics))
width = 0.35

bars1 = ax.bar(x - width/2, rf_scores, width, label='Random Forest',
               color='#2E86AB', edgecolor='white', linewidth=0.5)
bars2 = ax.bar(x + width/2, xgb_scores, width, label='XGBoost',
               color='#A23B72', edgecolor='white', linewidth=0.5)

ax.set_ylabel('Score')
ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylim(0, 1.0)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 0.01,
                f'{h:.4f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(f'{viz_dir}/model_comparison_{today}.png', bbox_inches='tight', dpi=150)
plt.close()
print('  model_comparison.png saved')

# --- 5e. Per-Class Metrics Heatmap ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, y_pred, model_name in [
    (axes[0], y_pred_rf, 'Random Forest'),
    (axes[1], y_pred_xgb, 'XGBoost')
]:
    report = classification_report(y_test, y_pred, target_names=class_names,
                                    output_dict=True)
    report_df = pd.DataFrame(report).iloc[:-1, :3]
    sns.heatmap(report_df, annot=True, fmt='.3f', cmap='YlOrRd',
                ax=ax, linewidths=0.5, cbar_kws={'shrink': 0.8})
    ax.set_title(f'{model_name} — Per-Class Metrics', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{viz_dir}/per_class_metrics_{today}.png', bbox_inches='tight', dpi=150)
plt.close()
print('  per_class_metrics.png saved')

# ============================================================
# 6. Summary table for documentation
# ============================================================
print('\n' + '='*60)
print('FINAL RESULTS — MODEL COMPARISON')
print('='*60)
print(f'{"Metric":<15} {"Random Forest":<18} {"XGBoost":<18}')
print('-'*51)
print(f'{"Accuracy":<15} {acc_rf:<18.4f} {acc_xgb:<18.4f}')
print(f'{"Precision":<15} {prec_rf:<18.4f} {prec_xgb:<18.4f}')
print(f'{"Recall":<15} {rec_rf:<18.4f} {rec_xgb:<18.4f}')
print(f'{"F1-Score":<15} {f1_rf:<18.4f} {f1_xgb:<18.4f}')
print('-'*51)

# Per-class F1
print('\nPer-Class F1-Score:')
rf_f1_per = f1_score(y_test, y_pred_rf, average=None)
xgb_f1_per = f1_score(y_test, y_pred_xgb, average=None)
for i, name in enumerate(class_names):
    print(f'  {name:<20} RF={rf_f1_per[i]:.4f}    XGB={xgb_f1_per[i]:.4f}')

# RF feature importance
print('\nRandom Forest Feature Importances:')
for name, imp in sorted(zip(feature_cols, rf.feature_importances_),
                         key=lambda x: x[1], reverse=True):
    print(f'  {name}: {imp:.4f}')

print('\nXGBoost Feature Importances:')
for name, imp in sorted(zip(feature_cols, xgb_model.feature_importances_),
                         key=lambda x: x[1], reverse=True):
    print(f'  {name}: {imp:.4f}')

print(f'\nModels saved to: {out_dir}/')
print(f'Visualizations saved to: {viz_dir}/')
print('\nDone.')
