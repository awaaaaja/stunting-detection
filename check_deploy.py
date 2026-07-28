"""Check deployment health."""
import requests, sys, json

BASE = "https://considerate-magic-production-749c.up.railway.app"
FRONT = "https://frontend-one-drab-gw3ah1e6mq.vercel.app"

errors = []

def check(label, status, detail=""):
    ok = status == "PASS"
    status_str = "PASS" if ok else "FAIL"
    print(f"  [{status_str}] {label}" + (f" | {detail}" if detail else ""))
    if not ok:
        errors.append(label)
    return ok

print("=== BACKEND CHECKS ===")

try:
    r = requests.get(f"{BASE}/health", timeout=15)
    d = r.json()
    check("Health endpoint", "PASS" if r.status_code == 200 else "FAIL",
          f"status={d.get('status')} model_loaded={d.get('model_loaded')}")
except Exception as e:
    check("Health endpoint", "FAIL", str(e)[:100])

try:
    r2 = requests.post(f"{BASE}/predict", json={
        "usia_bulan": 24, "jenis_kelamin": "laki-laki",
        "tinggi_cm": 70, "balita_id": "cek_koneksi"
    }, timeout=40)
    d2 = r2.json()["data"]
    check("Predict severely stunted", "PASS" if r2.status_code == 200 else "FAIL",
          f'class={d2["prediction"]["class"]} risk={d2["prediction"]["risk_score"]}')
    ans = d2["rekomendasi"]["answer"]
    src = len(d2["rekomendasi"]["sources"])
    check("RAG rekomendasi", "PASS" if len(ans) > 100 else "FAIL",
          f"{len(ans)} chars, {src} sources")
except Exception as e:
    check("Predict/RAG", "FAIL", str(e)[:100])

try:
    r3 = requests.get(f"{BASE}/history/cek_koneksi", timeout=10)
    d3 = r3.json()["data"]
    check("History by ID", "PASS" if r3.status_code == 200 else "FAIL",
          f'records={len(d3["records"])}')
except Exception as e:
    check("History by ID", "FAIL", str(e)[:80])

try:
    r4 = requests.get(f"{BASE}/rag-stats", timeout=10)
    s = r4.json()["data"]
    check("RAG Stats", "PASS" if s["success"] > 0 else "FAIL",
          f'success={s["success"]} fallback={s["fallback"]} rate={s["success_rate_pct"]}%')
except Exception as e:
    check("RAG Stats", "FAIL", str(e)[:80])

try:
    r5 = requests.options(f"{BASE}/predict", timeout=10)
    cors = r5.headers.get("Access-Control-Allow-Origin", "MISSING")
    check("CORS headers", "PASS" if cors != "MISSING" else "FAIL", cors)
except Exception as e:
    check("CORS headers", "FAIL", str(e)[:80])

print()
print("=== FRONTEND CHECKS ===")

try:
    r6 = requests.get(FRONT, timeout=15)
    check("Frontend loads", "PASS" if r6.status_code == 200 else "FAIL",
          f'{r6.status_code} | {len(r6.text)} chars')
    has_content = "Sistem" in r6.text or "Stunting" in r6.text or "Deteksi" in r6.text
    check("Content present", "PASS" if has_content else "FAIL")
except Exception as e:
    check("Frontend loads", "FAIL", str(e)[:80])

print()
print(f"=== RAILWAY STATUS ===")
import subprocess
result = subprocess.run(
    ["railway", "service", "status", "--service", "considerate-magic"],
    capture_output=True, text=True, timeout=10,
    cwd="D:\\Stunting"
)
print(result.stdout.strip() if result.stdout else "  (status via CLI)")

print()
if errors:
    print(f"❌ {len(errors)} FAIL: {', '.join(errors)}")
else:
    print("✅ SEMUA PASS — server aman, bisa diakses publik")