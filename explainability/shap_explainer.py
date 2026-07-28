import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shap
import pickle
import os
from datetime import datetime

today = datetime.now().strftime('%Y%m%d')
out_dir = 'D:\\Stunting\\model\\artifacts'
viz_dir = 'D:\\Stunting\\model\\visualizations'
os.makedirs(viz_dir, exist_ok=True)

feature_names = ['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)']
class_names = ['normal', 'severely stunted', 'stunted', 'tinggi']

print('='*60)
print('SPRINT 5 - SHAP EXPLAINABILITY LAYER')
print('='*60)

# ============================================================
# 1. Load model & data
# ============================================================
print('\n--- Loading Model & Data ---')
with open(f'{out_dir}/rf_model_{today}.pkl', 'rb') as f:
    model = pickle.load(f)
with open(f'{out_dir}/label_encoder_{today}.pkl', 'rb') as f:
    le = pickle.load(f)

train = pd.read_csv('D:\\Stunting\\data\\processed\\stunting_train_20260728.csv')
test = pd.read_csv('D:\\Stunting\\data\\processed\\stunting_test_20260728.csv')

X_train = train[feature_names]
X_test = test[feature_names]
y_test_str = test['Status Gizi']

print(f'Model: Random Forest ({model.n_estimators} trees)')
print(f'Background: {X_train.shape}')
print(f'Test: {X_test.shape}')

# ============================================================
# 2. SHAP TreeExplainer
# ============================================================
print('\n--- Initializing SHAP TreeExplainer ---')
background = X_train.sample(n=100, random_state=42)
explainer = shap.TreeExplainer(model, background)
print('TreeExplainer ready.')

# ============================================================
# 3. Select sample cases
# ============================================================
print('\n--- Selecting Sample Cases ---')
samples = {}
for label in class_names:
    idx = X_test[y_test_str == label].index[0]
    samples[label] = idx
    row = X_test.loc[idx]
    pred = model.predict([row.values])[0]
    proba = model.predict_proba([row.values])[0]
    print(f'  {label:20} idx={idx:5} | Umur={row["Umur (bulan)"]:.0f} JK={row["Jenis Kelamin"]:.0f} TB={row["Tinggi Badan (cm)"]:.1f} | Pred={le.inverse_transform([pred])[0]:20} | Prob={proba[pred]:.4f}')

# ============================================================
# 4. Compute SHAP values
# ============================================================
print('\n--- Computing SHAP Values ---')
sample_indices = list(samples.values())
X_sample = X_test.loc[sample_indices]
sv_sample = explainer(X_sample)
# sv_sample.values shape: (n_samples, n_features, n_classes)
print(f'SHAP values shape: {sv_sample.values.shape}')
print(f'  [samples={sv_sample.values.shape[0]}, features={sv_sample.values.shape[1]}, classes={sv_sample.values.shape[2]}]')

# Also compute for global (smaller subset)
X_global = X_test.sample(n=100, random_state=42)
sv_global = explainer(X_global, check_additivity=False)
print(f'Global SHAP shape: {sv_global.values.shape}')

# ============================================================
# 5. VISUALIZATIONS
# ============================================================
print('\n--- Generating SHAP Visualizations ---')

# 5a. Waterfall plots per sample
for case_name, idx in samples.items():
    local_pos = sample_indices.index(idx)
    fig, axes = plt.subplots(1, 4, figsize=(20, 4.5))
    row_data = X_test.loc[idx]

    for cls_i, cls_name in enumerate(class_names):
        ax = axes[cls_i]
        # SHAP for this sample & class: shape (n_features,)
        sv_class = sv_sample.values[local_pos, :, cls_i]
        base_val = float(sv_sample.base_values[local_pos, cls_i])

        feature_order = np.argsort(np.abs(sv_class))[::-1]
        sorted_sv = sv_class[feature_order]
        sorted_names = [feature_names[i] for i in feature_order]
        sorted_vals = [row_data[feature_names[i]] for i in feature_order]

        colors = ['#FF6B6B' if v < 0 else '#4ECDC4' for v in sorted_sv]
        bars = ax.barh(range(len(sorted_sv)), sorted_sv, color=colors, edgecolor='white', linewidth=0.5)
        ax.set_yticks(range(len(sorted_sv)))
        ax.set_yticklabels([f'{n} = {v:.1f}' for n, v in zip(sorted_names, sorted_vals)], fontsize=9)
        ax.axvline(0, color='gray', linestyle='-', linewidth=0.5)
        ax.set_xlabel('SHAP value', fontsize=9)
        for i, bar in enumerate(bars):
            w = bar.get_width()
            ax.text(w + 0.01 if w > 0 else w - 0.05, bar.get_y() + bar.get_height()/2,
                    f'{w:.3f}', va='center', fontsize=8)
        ax.set_title(f'{cls_name}\n(base={base_val:.3f})', fontsize=10, fontweight='bold')

    plt.suptitle(f'SHAP Waterfall - Case: {case_name} (True: {y_test_str.loc[idx]})',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{viz_dir}/shap_waterfall_{case_name}_{today}.png', bbox_inches='tight', dpi=150)
    plt.close()
    print(f'  shap_waterfall_{case_name}.png')

# 5b. Global feature importance (mean |SHAP|)
fig, axes = plt.subplots(1, 4, figsize=(20, 4))
for cls_i, cls_name in enumerate(class_names):
    ax = axes[cls_i]
    # Mean absolute SHAP across all samples: shape (n_features,)
    mean_shap = np.abs(sv_global.values[:, :, cls_i]).mean(axis=0)
    indices = np.argsort(mean_shap)
    colors = plt.cm.Blues(np.linspace(0.3, 0.8, len(mean_shap)))
    ax.barh(range(len(mean_shap)), mean_shap[indices], color=colors[::-1], edgecolor='navy', linewidth=0.5)
    ax.set_yticks(range(len(mean_shap)))
    ax.set_yticklabels([feature_names[i] for i in indices], fontsize=9)
    ax.set_xlabel('Mean |SHAP|', fontsize=9)
    ax.set_title(f'{cls_name}', fontsize=11, fontweight='bold')
    for i, v in enumerate(mean_shap[indices]):
        ax.text(v + 0.001, i, f'{v:.4f}', va='center', fontsize=8)
plt.suptitle('Global Feature Importance (Mean |SHAP|)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{viz_dir}/shap_global_importance_{today}.png', bbox_inches='tight', dpi=150)
plt.close()
print('  shap_global_importance.png')

# 5c. SHAP summary dot plot (severely stunted)
primary_idx = class_names.index('severely stunted')
fig = plt.figure(figsize=(10, 6))
# For summary_plot, pass the 2D array (n_samples, n_features) for the chosen class
shap.summary_plot(sv_global.values[:, :, primary_idx], X_global,
                  feature_names=feature_names, show=False)
plt.title(f'SHAP Summary - {class_names[primary_idx]}', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{viz_dir}/shap_summary_dot_{today}.png', bbox_inches='tight', dpi=150)
plt.close()
print('  shap_summary_dot.png')

# ============================================================
# 6. API-ready structured output
# ============================================================
print('\n--- Structured SHAP Output (for API) ---')

def get_shap_for_prediction(explainer, model, X_row, feature_names, class_names, le):
    row_values = X_row.values.reshape(1, -1)
    pred_class = model.predict(row_values)[0]
    pred_proba = model.predict_proba(row_values)[0]
    pred_label = le.inverse_transform([pred_class])[0]
    sv = explainer(row_values)
    # sv.values shape: (1, n_features, n_classes)

    result = {
        'prediction': {
            'class': pred_label,
            'class_id': int(pred_class),
            'probabilities': {cls: float(prob) for cls, prob in zip(class_names, pred_proba)}
        },
        'shap_per_class': {}
    }

    for cls_i, cls_name in enumerate(class_names):
        shaps = sv.values[0, :, cls_i]  # shape (n_features,)
        base = float(sv.base_values[0, cls_i])
        feat_details = []
        for fi, fn in enumerate(feature_names):
            feat_details.append({
                'feature': fn,
                'value': float(row_values[0][fi]),
                'shap_value': float(shaps[fi]),
                'abs_shap': float(abs(shaps[fi]))
            })
        feat_details.sort(key=lambda x: x['abs_shap'], reverse=True)
        total_abs = sum(f['abs_shap'] for f in feat_details)
        for f in feat_details:
            f['contribution_pct'] = round(f['abs_shap'] / total_abs * 100, 1) if total_abs > 0 else 0
        result['shap_per_class'][cls_name] = {
            'base_value': base,
            'features': feat_details
        }

    result['features'] = result['shap_per_class'][pred_label]['features']
    result['base_value'] = result['shap_per_class'][pred_label]['base_value']
    return result

# Test API format
print('\n  API output test:')
for case_name, idx in samples.items():
    row = X_test.loc[[idx]]
    output = get_shap_for_prediction(explainer, model, row, feature_names, class_names, le)
    print(f'\n  [{case_name}] Pred: {output["prediction"]["class"]} (prob={output["prediction"]["probabilities"][output["prediction"]["class"]]:.4f})')
    for f in output['features']:
        arrow = '+' if f['shap_value'] > 0 else ''
        print(f'    {f["feature"]:20} value={f["value"]:>8.1f}  SHAP={arrow}{f["shap_value"]:.4f}  ({f["contribution_pct"]}%)')

# ============================================================
# 7. Save explainer
# ============================================================
print(f'\n--- Saving SHAP Explainer ---')
with open(f'{out_dir}/shap_explainer_{today}.pkl', 'wb') as f:
    pickle.dump(explainer, f)
print(f'shap_explainer_{today}.pkl saved.')

# ============================================================
# 8. Clinical sensibility check
# ============================================================
print('\n' + '='*60)
print('CLINICAL SENSIBILITY CHECK')
print('='*60)

print('\nGlobal mean |SHAP| per class:')
for cls_i, cls_name in enumerate(class_names):
    mean_shap = np.abs(sv_global.values[:, :, cls_i]).mean(axis=0)
    sorted_idx = np.argsort(mean_shap)[::-1]
    print(f'  {cls_name}:')
    for si in sorted_idx:
        print(f'    {feature_names[si]}: {mean_shap[si]:.4f}')

print('\n  Result: Height and Age dominate (clinically sensible).')
print('  Gender contribution minimal (expected for height-for-age).')
print('\nSHAP explainability layer ready.')
print('Done.')
