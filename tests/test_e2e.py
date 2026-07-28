"""Sprint 9 — End-to-End Test: Sistem Deteksi Dini Risiko Stunting"""
import json
import urllib.request

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0

def test(name, method, path, body=None, expected_status=200):
    global PASS, FAIL
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data,
        headers={"Content-Type": "application/json"} if body else {},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            status = resp.status
            payload = json.loads(resp.read())
        if status == expected_status:
            PASS += 1
            print(f"  PASS [{status}] {name}")
        else:
            FAIL += 1
            print(f"  FAIL [{status}] {name} — expected {expected_status}")
        return payload
    except urllib.error.HTTPError as e:
        status = e.code
        if status == expected_status:
            PASS += 1
            print(f"  PASS [{status}] {name}")
        else:
            FAIL += 1
            body = e.read().decode()[:100]
            print(f"  FAIL [{status}] {name} — expected {expected_status}: {body}")
        return None


print("=" * 60)
print("END-TO-END TEST — Sistem Deteksi Dini Risiko Stunting")
print("=" * 60)

# 1. Health
print("\n[1] Health Check")
h = test("health endpoint", "GET", "/health")
if h:
    assert h["status"] == "ok"
    assert h["model_loaded"] is True
    print(f"    model_loaded={h['model_loaded']}")

# 2. Predict — Normal
print("\n[2] Prediksi — Normal (36 bln, perempuan, 95 cm)")
r = test("normal case", "POST", "/predict", {
    "usia_bulan": 36, "jenis_kelamin": "perempuan",
    "tinggi_cm": 95, "balita_id": "e2e_normal"
})
if r:
    d = r["data"]
    print(f"    class={d['prediction']['class']} risk={d['prediction']['risk_score']:.4f}")
    assert d["prediction"]["class"] == "normal"
    assert d["prediction"]["risk_score"] < 0.5
    assert "shap" in d
    assert "features" in d["shap"]

# 3. Predict — Severely Stunted
print("\n[3] Prediksi — Severely Stunted (24 bln, laki-laki, 70 cm)")
r = test("severely stunted case", "POST", "/predict", {
    "usia_bulan": 24, "jenis_kelamin": "laki-laki",
    "tinggi_cm": 70, "balita_id": "e2e_stunted"
})
if r:
    d = r["data"]
    print(f"    class={d['prediction']['class']} risk={d['prediction']['risk_score']:.4f}")
    assert d["prediction"]["class"] == "severely stunted"
    assert d["prediction"]["risk_score"] > 0.5

# 4. Predict — Stunted (z ~ -2.40 SD → -3SD ≤ z < -2SD)
print("\n[4] Prediksi — Stunted (48 bln, laki-laki, 93 cm)")
r = test("stunted case", "POST", "/predict", {
    "usia_bulan": 48, "jenis_kelamin": "laki-laki",
    "tinggi_cm": 93, "balita_id": "e2e_stunted2"
})
if r:
    d = r["data"]
    cls = d['prediction']['class']
    print(f"    class={cls} risk={d['prediction']['risk_score']:.4f}")
    assert cls == "stunted", f"Expected stunted, got {cls}"

# 5. Predict — Tinggi
print("\n[5] Prediksi — Tinggi (12 bln, perempuan, 85 cm)")
r = test("tinggi case", "POST", "/predict", {
    "usia_bulan": 12, "jenis_kelamin": "perempuan",
    "tinggi_cm": 85, "balita_id": "e2e_tinggi"
})
if r:
    d = r["data"]
    print(f"    class={d['prediction']['class']} risk={d['prediction']['risk_score']:.4f}")

# 6. Edge: usia 0
print("\n[6] Edge Case — Usia 0 bulan")
r = test("age 0", "POST", "/predict", {
    "usia_bulan": 0, "jenis_kelamin": "perempuan", "tinggi_cm": 45
})
if r:
    d = r["data"]
    print(f"    class={d['prediction']['class']}")

# 7. Invalid: usia negatif => 422
print("\n[7] Invalid — Usia negatif")
test("negative age", "POST", "/predict", {
    "usia_bulan": -1, "jenis_kelamin": "laki-laki", "tinggi_cm": 70
}, expected_status=422)

# 8. Invalid: jenis_kelamin salah => 422
print("\n[8] Invalid — JK salah")
test("invalid gender", "POST", "/predict", {
    "usia_bulan": 24, "jenis_kelamin": "xyz", "tinggi_cm": 80
}, expected_status=422)

# 9. History — by ID
print("\n[9] Riwayat — by balita_id")
r = test("history found", "GET", "/history/e2e_normal")
if r:
    assert r["data"]["balita_id"] == "e2e_normal"
    print(f"    records={len(r['data']['records'])}")

# 10. History — 404
print("\n[10] Riwayat — not found")
test("history not found", "GET", "/history/___nonexistent___", expected_status=404)

# 11. History — list all
print("\n[11] Riwayat — list semua")
r = test("list history", "GET", "/history")
if r:
    print(f"    total_balita={len(r['data'])}")

# 12. Rekomendasi — Selalu ada
print("\n[12] Rekomendasi — Selalu ada")
r = test("rekomendasi check", "POST", "/predict", {
    "usia_bulan": 24, "jenis_kelamin": "laki-laki",
    "tinggi_cm": 70, "balita_id": "e2e_rag"
})
if r:
    d = r["data"]
    has_rek = d.get("rekomendasi") is not None
    print(f"    rekomendasi={'yes' if has_rek else 'no'}")
    assert has_rek, "rekomendasi HARUS selalu ada!"
    ans = d["rekomendasi"]["answer"]
    print(f"    answer: {len(ans)} chars | starts: {ans[:60]}...")
    srcs = d["rekomendasi"]["sources"]
    print(f"    sources: {len(srcs)} dokumen")
    assert len(srcs) > 0, "rekomendasi HARUS punya sumber!"

# 13. RAG Stats endpoint
print("\n[13] RAG Stats")
r = test("rag stats", "GET", "/rag-stats")
if r:
    d = r["data"]
    print(f"    total={d['total']} success={d['success']} fallback={d['fallback']}")
    print(f"    success_rate={d['success_rate_pct']}% fallback_rate={d['fallback_rate_pct']}%")
    assert d["total"] > 0
    assert d["success"] + d["fallback"] == d["total"]
    assert d["success"] > 0, f"RAG tidak boleh 0% success (got {d['success_rate_pct']}%)"

print("\n" + "=" * 60)
print(f"HASIL: {PASS} PASS, {FAIL} FAIL dari {PASS+FAIL} test")
if FAIL > 0:
    exit(1)
print("=" * 60)
