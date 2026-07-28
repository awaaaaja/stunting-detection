import pickle
import json
import os
import logging
import traceback
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

import uvicorn
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

load_dotenv()

# ---------------------------------------------------------------------------
# Project root (cross-platform, works on Render)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# RAG Stats tracking (must be before RAG_AVAILABLE block)
# ---------------------------------------------------------------------------
_rag_stats = {"success": 0, "fallback": 0, "total": 0, "rag_available": False}

RAG_AVAILABLE = False
try:
    import sys as _sys
    _sys.path.insert(0, str(PROJECT_ROOT))
    from rag.retrieve import retrieve as _rag_retrieve, format_context as _rag_format
    RAG_AVAILABLE = True
    _rag_stats["rag_available"] = True
except Exception:
    _rag_stats["rag_available"] = False

from rag.rekomendasi_fallback import get_rekomendasi_hybrid, get_rekomendasi_rule

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ARTIFACT_DIR = PROJECT_ROOT / "model" / "artifacts"
FEATURE_NAMES = ['Umur (bulan)', 'Jenis Kelamin', 'Tinggi Badan (cm)']
CLASS_NAMES = ['normal', 'severely stunted', 'stunted', 'tinggi']

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global model/shap objects (loaded at startup)
# ---------------------------------------------------------------------------
model = None
label_encoder = None
explainer = None


def load_artifacts():
    global model, label_encoder, explainer
    stamp = '20260728'
    log.info('Loading model artifacts...')
    with open(ARTIFACT_DIR / f'rf_model_{stamp}.pkl', 'rb') as f:
        model = pickle.load(f)
    with open(ARTIFACT_DIR / f'label_encoder_{stamp}.pkl', 'rb') as f:
        label_encoder = pickle.load(f)
    with open(ARTIFACT_DIR / f'shap_explainer_{stamp}.pkl', 'rb') as f:
        explainer = pickle.load(f)
    log.info('All artifacts loaded.')


# ---------------------------------------------------------------------------
# History storage (SQLite)
# ---------------------------------------------------------------------------
from backend.history_db import save_prediction, get_history, list_balita


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------
class PredictInput(BaseModel):
    usia_bulan: int = Field(..., ge=0, le=60, description='Usia balita dalam bulan (0-60)')
    jenis_kelamin: str = Field(..., description='Jenis kelamin: laki-laki atau perempuan')
    tinggi_cm: float = Field(..., gt=20, lt=150, description='Tinggi badan dalam cm')
    balita_id: Optional[str] = Field(None, description='ID balita untuk riwayat')

    @field_validator('jenis_kelamin')
    @classmethod
    def validate_gender(cls, v):
        v_lower = v.lower().strip()
        if v_lower not in ('laki-laki', 'perempuan', 'l', 'p'):
            raise ValueError('jenis_kelamin harus "laki-laki" atau "perempuan"')
        return v_lower


class PredictOutput(BaseModel):
    status: str = 'success'
    data: dict


# ---------------------------------------------------------------------------
# Prediction helper
# ---------------------------------------------------------------------------
def predict_single(usia: int, jk: str, tinggi: float):
    # Map gender to model encoding
    jk_encoded = 1 if jk in ('laki-laki', 'l') else 0
    X = pd.DataFrame([[usia, jk_encoded, tinggi]], columns=FEATURE_NAMES)

    # Predict
    pred_class = int(model.predict(X)[0])
    pred_proba = model.predict_proba(X)[0].tolist()
    pred_label = label_encoder.inverse_transform([pred_class])[0]

    # SHAP
    sv = explainer(X, check_additivity=False)

    shap_features = {}
    for ci, cn in enumerate(CLASS_NAMES):
        shaps = sv.values[0, :, ci]
        base_val = float(sv.base_values[0, ci])
        feats = []
        for fi, fn in enumerate(FEATURE_NAMES):
            feats.append({
                'feature': fn,
                'value': float(X.iloc[0, fi]),
                'shap_value': round(float(shaps[fi]), 4),
                'abs_shap': round(float(abs(shaps[fi])), 4),
            })
        feats.sort(key=lambda x: x['abs_shap'], reverse=True)
        total_abs = sum(f['abs_shap'] for f in feats)
        for f in feats:
            f['contribution_pct'] = round(f['abs_shap'] / total_abs * 100, 1) if total_abs > 0 else 0

        shap_features[cn] = {'base_value': round(base_val, 4), 'features': feats}

    # Risk score = probability of stunting (stunted + severely stunted)
    stunting_proba = pred_proba[CLASS_NAMES.index('stunted')] + pred_proba[CLASS_NAMES.index('severely stunted')]

    result = {
        'prediction': {
            'class': pred_label,
            'class_id': pred_class,
            'risk_level': pred_label,
            'risk_score': round(stunting_proba, 4),
            'probabilities': {cn: round(pred_proba[i], 4) for i, cn in enumerate(CLASS_NAMES)},
        },
        'shap': shap_features[pred_label],
        'shap_per_class': shap_features,
    }
    return result


# ---------------------------------------------------------------------------
# RAG Recommendation (optional — graceful fallback)
# ---------------------------------------------------------------------------
RAG_PROMPT_TEMPLATE = """Anda adalah asisten ahli gizi dan kesehatan masyarakat yang membantu memberikan rekomendasi berbasis bukti untuk pencegahan dan penanganan stunting pada balita di Indonesia.

Gunakan HANYA informasi dari konteks di bawah ini untuk menjawab pertanyaan.
Jika informasi tidak tersedia di konteks, katakan "Tidak ada informasi yang cukup dalam dokumen sumber untuk menjawab pertanyaan ini."

Konteks:
{context}

Pertanyaan: {question}"""


def _call_openrouter(prompt: str) -> str:
    import urllib.request, json as _json

    api_key = os.environ["OPENROUTER_API_KEY"]
    body = _json.dumps({
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 512,
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = _json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


def generate_rekomendasi(result: dict) -> dict:
    global _rag_stats
    pred = result["prediction"]
    shap_top = result["shap"]["features"][:3]
    feature_desc = "; ".join([f"{f['feature']}={f['value']} (kontribusi {f['contribution_pct']}%)" for f in shap_top])
    usia = result.get("usia_bulan", 0)

    rag_result = None
    _rag_stats["total"] += 1

    if RAG_AVAILABLE:
        question = (
            f"Balita terdeteksi {pred['class']} dengan skor risiko {pred['risk_score']:.2%}. "
            f"Faktor utama: {feature_desc}. "
            f"Usia {usia} bulan. "
            f"Berikan rekomendasi penanganan berdasarkan pedoman nasional."
        )
        try:
            chunks = _rag_retrieve(question, n_results=5)
            if chunks and any(len(c["text"].strip()) >= 20 for c in chunks):
                context = _rag_format(chunks)
                prompt = RAG_PROMPT_TEMPLATE.replace("{context}", context).replace("{question}", question)
                answer = _call_openrouter(prompt)
                if answer and len(answer) > 20:
                    rag_result = {
                        "answer": answer,
                        "sources": [{"source": c["source"], "page": c["page"]} for c in chunks],
                    }
                    logging.info(
                        "RAG ok: %d chunks, %d ctx chars, %d ans chars",
                        len(chunks), len(context), len(answer),
                    )
        except Exception as _e:
            logging.warning("RAG LLM call failed: %s", str(_e)[:200])

    result_hybrid = get_rekomendasi_hybrid(
        prediction_class=pred["class"],
        risk_score=pred["risk_score"],
        feature_desc=feature_desc,
        usia=usia,
        rag_result=rag_result,
    )

    if rag_result is not None:
        _rag_stats["success"] += 1
    else:
        _rag_stats["fallback"] += 1

    return result_hybrid


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title='Sistem Deteksi Dini Risiko Stunting',
    description='ML + XAI + RAG untuk deteksi risiko stunting balita',
    version='1.0.0',
)

# CORS — allow Vercel frontend + development
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def startup():
    load_artifacts()


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'model_loaded': model is not None,
        'explainer_loaded': explainer is not None,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }


@app.post('/predict', response_model=PredictOutput)
def predict(input_data: PredictInput):
    try:
        result = predict_single(
            usia=input_data.usia_bulan,
            jk=input_data.jenis_kelamin,
            tinggi=input_data.tinggi_cm,
        )

        # Add metadata
        timestamp = datetime.now(timezone.utc).isoformat()
        result['timestamp'] = timestamp
        result['usia_bulan'] = input_data.usia_bulan
        result['jenis_kelamin'] = input_data.jenis_kelamin
        result['tinggi_cm'] = input_data.tinggi_cm
        if input_data.balita_id:
            result['balita_id'] = input_data.balita_id

        # Save to SQLite
        if input_data.balita_id:
            save_prediction({
                "balita_id": input_data.balita_id,
                "usia_bulan": input_data.usia_bulan,
                "jenis_kelamin": input_data.jenis_kelamin,
                "tinggi_cm": input_data.tinggi_cm,
                "prediction": result['prediction']['class'],
                "risk_score": result['prediction']['risk_score'],
                "shap": result['shap'],
                "rekomendasi": {},
            })
            log.info(f'Prediction saved for balita_id={input_data.balita_id}')

        # RAG recommendation
        rag_result = generate_rekomendasi(result)
        result["rekomendasi"] = rag_result

        log.info(f'Predict: usia={input_data.usia_bulan}, jk={input_data.jenis_kelamin}, '
                 f'tinggi={input_data.tinggi_cm:.1f} -> {result["prediction"]["class"]}'
                 f' | RAG: {"yes" if rag_result else "no"}')

        return PredictOutput(data=result)

    except Exception as e:
        log.error(f'Prediction failed: {e}', exc_info=True)
        raise HTTPException(status_code=500, detail=f'Prediction failed: {str(e)}')


@app.get('/history/{balita_id}')
def get_history_ep(balita_id: str):
    records = get_history(balita_id)
    if not records:
        raise HTTPException(status_code=404, detail=f'Balita ID {balita_id} not found')
    return {
        'status': 'success',
        'data': {
            'balita_id': balita_id,
            'records': records,
        },
    }


@app.get('/history')
def list_history_ep():
    summary = list_balita()
    return {'status': 'success', 'data': summary}


# ---------------------------------------------------------------------------
# RAG Stats endpoint
# ---------------------------------------------------------------------------
@app.get('/rag-stats')
def get_rag_stats():
    return {
        'status': 'success',
        'data': {
            **_rag_stats,
            'success_rate_pct': round(_rag_stats['success'] / _rag_stats['total'] * 100, 1) if _rag_stats['total'] > 0 else 0,
            'fallback_rate_pct': round(_rag_stats['fallback'] / _rag_stats['total'] * 100, 1) if _rag_stats['total'] > 0 else 0,
        },
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)