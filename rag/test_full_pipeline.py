from dotenv import load_dotenv
load_dotenv()
import sys, os, pickle, json, urllib.request

sys.path.insert(0, r"D:\Stunting")
os.environ.setdefault("CHROMA_API_KEY", "")
os.environ["CHROMA_TENANT"] = "31e70a65-72b8-429e-bfb7-c7c897f247a9"
os.environ["CHROMA_DATABASE"] = "BALITA"

import pandas as pd
from rag.retrieve import retrieve, format_context

stamp = "20260728"
with open(r"D:\Stunting\model\artifacts\rf_model_" + stamp + ".pkl", "rb") as f:
    model = pickle.load(f)
with open(r"D:\Stunting\model\artifacts\label_encoder_" + stamp + ".pkl", "rb") as f:
    label_encoder = pickle.load(f)
with open(r"D:\Stunting\model\artifacts\shap_explainer_" + stamp + ".pkl", "rb") as f:
    explainer = pickle.load(f)

FEATURE_NAMES = ["Umur (bulan)", "Jenis Kelamin", "Tinggi Badan (cm)"]
CLASS_NAMES = ["normal", "severely stunted", "stunted", "tinggi"]

def predict_single(usia, jk, tinggi):
    jk_encoded = 1 if jk in ("laki-laki", "l") else 0
    X = pd.DataFrame([[usia, jk_encoded, tinggi]], columns=FEATURE_NAMES)
    pred_class = int(model.predict(X)[0])
    pred_proba = model.predict_proba(X)[0].tolist()
    pred_label = label_encoder.inverse_transform([pred_class])[0]
    sv = explainer(X, check_additivity=False)
    shap_features = {}
    for ci, cn in enumerate(CLASS_NAMES):
        shaps = sv.values[0, :, ci]
        base_val = float(sv.base_values[0, ci])
        feats = []
        for fi, fn in enumerate(FEATURE_NAMES):
            feats.append({
                "feature": fn, "value": float(X.iloc[0, fi]),
                "shap_value": round(float(shaps[fi]), 4),
                "abs_shap": round(float(abs(shaps[fi])), 4),
            })
        feats.sort(key=lambda x: x["abs_shap"], reverse=True)
        total_abs = sum(f["abs_shap"] for f in feats)
        for f in feats:
            f["contribution_pct"] = round(f["abs_shap"] / total_abs * 100, 1) if total_abs > 0 else 0
        shap_features[cn] = {"base_value": round(base_val, 4), "features": feats}
    stunting_proba = pred_proba[CLASS_NAMES.index("stunted")] + pred_proba[CLASS_NAMES.index("severely stunted")]
    return {
        "prediction": {
            "class": pred_label, "class_id": pred_class,
            "risk_level": pred_label, "risk_score": round(stunting_proba, 4),
            "probabilities": {cn: round(pred_proba[i], 4) for i, cn in enumerate(CLASS_NAMES)},
        },
        "shap": shap_features[pred_label],
        "shap_per_class": shap_features,
    }

# Test 1: normal case
result = predict_single(36, "perempuan", 95)
result["usia_bulan"] = 36
result["jenis_kelamin"] = "perempuan"
result["tinggi_cm"] = 95
pred = result["prediction"]
print(f"Test 1 - Prediction: {pred['class']} (risk: {pred['risk_score']:.2%})")

# RAG
shap_top = result["shap"]["features"][:3]
feature_desc = "; ".join([
    f"{f['feature']}={f['value']} (kontribusi {f['contribution_pct']}%)"
    for f in shap_top
])
question = (
    f"Balita terdeteksi {pred['class']} dengan skor risiko {pred['risk_score']:.2%}. "
    f"Faktor utama: {feature_desc}. Usia 36 bulan. "
    f"Berikan rekomendasi penanganan berdasarkan pedoman nasional."
)
chunks = retrieve(question, n_results=5)
print(f"Chunks retrieved: {len(chunks)}")

if chunks:
    context = format_context(chunks)
    print(f"Context length: {len(context)} chars")

    prompt_template = """Anda adalah asisten ahli gizi dan kesehatan masyarakat. Gunakan HANYA informasi dari konteks di bawah ini. Jika informasi tidak tersedia, katakan tidak tahu.

Konteks:
{context}

Pertanyaan: {question}"""

    prompt = prompt_template.replace("{context}", context).replace("{question}", question)
    body = json.dumps({
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3, "max_tokens": 512,
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {os.environ["OPENROUTER_API_KEY"]}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        answer = json.loads(resp.read())["choices"][0]["message"]["content"]

    print(f"\n=== Recommendation ===")
    print(answer)
    print(f"\n=== Sources ===")
    for c in chunks:
        print(f"  - {c['source']} (halaman {c['page']})")
else:
    print("No chunks retrieved")

# Test 2: stunting case
print("\n" + "="*50)
result2 = predict_single(24, "laki-laki", 70)
result2["usia_bulan"] = 24
pred2 = result2["prediction"]
print(f"Test 2 - Prediction: {pred2['class']} (risk: {pred2['risk_score']:.2%})")

shap_top2 = result2["shap"]["features"][:3]
feature_desc2 = "; ".join([
    f"{f['feature']}={f['value']} (kontribusi {f['contribution_pct']}%)"
    for f in shap_top2
])
question2 = (
    f"Balita terdeteksi {pred2['class']} dengan skor risiko {pred2['risk_score']:.2%}. "
    f"Faktor utama: {feature_desc2}. Usia 24 bulan. "
    f"Berikan rekomendasi penanganan berdasarkan pedoman nasional."
)
chunks2 = retrieve(question2, n_results=5)
print(f"Chunks retrieved: {len(chunks2)}")
if chunks2:
    context2 = format_context(chunks2)
    prompt2 = prompt_template.replace("{context}", context2).replace("{question}", question2)
    body2 = json.dumps({
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt2}],
        "temperature": 0.3, "max_tokens": 512,
    }).encode()
    req2 = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body2,
        headers={
            "Authorization": f"Bearer {os.environ["OPENROUTER_API_KEY"]}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req2, timeout=30) as resp2:
        answer2 = json.loads(resp2.read())["choices"][0]["message"]["content"]
    print(f"\n=== Recommendation ===")
    print(answer2)
    print(f"\n=== Sources ===")
    for c in chunks2:
        print(f"  - {c['source']} (halaman {c['page']})")
