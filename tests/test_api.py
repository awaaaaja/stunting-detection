import requests
import json

BASE = 'http://localhost:8000'
pass_count = 0
fail_count = 0

def test(name, method, path, expected_status, data=None):
    global pass_count, fail_count
    url = f'{BASE}{path}'
    try:
        if method == 'GET':
            r = requests.get(url, timeout=10)
        else:
            r = requests.post(url, json=data, timeout=10)

        if r.status_code == expected_status:
            print(f'  PASS [{r.status_code}] {name}')
            pass_count += 1
        else:
            print(f'  FAIL [{r.status_code}] {name} (expected {expected_status})')
            print(f'    Response: {r.text[:300]}')
            fail_count += 1
        return r
    except Exception as e:
        print(f'  ERROR {name}: {e}')
        fail_count += 1
        return None


print('='*60)
print('API TEST SUITE')
print('='*60)

# 1. Health
print('\n--- 1. Health Check ---')
r = test('Health', 'GET', '/health', 200)
if r:
    print(f'    Response: model_loaded={r.json().get("model_loaded")}')

# 2. Predict - normal case
print('\n--- 2. Predict (normal) ---')
r = test('Predict normal', 'POST', '/predict', 200, {
    'usia_bulan': 36,
    'jenis_kelamin': 'laki-laki',
    'tinggi_cm': 96.0,
    'balita_id': 'test-001'
})
if r:
    data = r.json()['data']
    pred = data['prediction']
    print(f'    Class: {pred["class"]} (risk_score={pred["risk_score"]})')
    print(f'    SHAP features:')
    for f in data['shap']['features']:
        print(f'      {f["feature"]}: {f["shap_value"]} ({f["contribution_pct"]}%)')

# 3. Predict - stunted case
print('\n--- 3. Predict (stunted) ---')
r = test('Predict stunted', 'POST', '/predict', 200, {
    'usia_bulan': 24,
    'jenis_kelamin': 'perempuan',
    'tinggi_cm': 75.0,
    'balita_id': 'test-002'
})
if r:
    data = r.json()['data']
    pred = data['prediction']
    print(f'    Class: {pred["class"]} (risk_score={pred["risk_score"]})')

# 4. Predict - severely stunted
print('\n--- 4. Predict (severely stunted) ---')
r = test('Predict severely stunted', 'POST', '/predict', 200, {
    'usia_bulan': 12,
    'jenis_kelamin': 'laki-laki',
    'tinggi_cm': 55.0,
    'balita_id': 'test-003'
})
if r:
    data = r.json()['data']
    pred = data['prediction']
    print(f'    Class: {pred["class"]} (risk_score={pred["risk_score"]})')

# 5. Predict - tinggi (tall)
print('\n--- 5. Predict (tinggi) ---')
r = test('Predict tinggi', 'POST', '/predict', 200, {
    'usia_bulan': 6,
    'jenis_kelamin': 'laki-laki',
    'tinggi_cm': 72.0,
    'balita_id': 'test-004'
})
if r:
    data = r.json()['data']
    pred = data['prediction']
    print(f'    Class: {pred["class"]} (risk_score={pred["risk_score"]})')

# 6. Edge case: invalid gender
print('\n--- 6. Edge: Invalid Gender ---')
test('Invalid gender', 'POST', '/predict', 422, {
    'usia_bulan': 24,
    'jenis_kelamin': 'unknown',
    'tinggi_cm': 85.0,
})

# 7. Edge case: age out of range
print('\n--- 7. Edge: Age out of range ---')
test('Age too high', 'POST', '/predict', 422, {
    'usia_bulan': 100,
    'jenis_kelamin': 'laki-laki',
    'tinggi_cm': 85.0,
})

# 8. Edge case: height too low
print('\n--- 8. Edge: Height too low ---')
test('Height too low', 'POST', '/predict', 422, {
    'usia_bulan': 24,
    'jenis_kelamin': 'laki-laki',
    'tinggi_cm': 5.0,
})

# 9. Edge case: missing field
print('\n--- 9. Edge: Missing field ---')
test('Missing field', 'POST', '/predict', 422, {
    'usia_bulan': 24,
    'tinggi_cm': 85.0,
})

# 10. History by balita_id
print('\n--- 10. History by ID ---')
r = test('History test-001', 'GET', '/history/test-001', 200)
if r:
    data = r.json()['data']
    print(f'    Records: {len(data["records"])}')
    print(f'    Latest: {data["records"][-1]["prediction"]["class"]}')

# 11. History - not found
print('\n--- 11. History ID not found ---')
test('History not found', 'GET', '/history/nonexistent', 404)

# 12. List all history
print('\n--- 12. List History ---')
r = test('List history', 'GET', '/history', 200)
if r:
    data = r.json()['data']
    print(f'    Total balita: {len(data)}')
    for b in data:
        print(f'      {b["balita_id"]}: {b["total_records"]} records, last={b["last_prediction"]}')

# Summary
print('\n' + '='*60)
print(f'RESULTS: {pass_count} passed, {fail_count} failed')
print('='*60)
