"""Diagnostic script — cek koneksi ChromaDB Cloud & OpenRouter via .env"""
import os, sys, json, urllib.request
from dotenv import load_dotenv

load_dotenv()

# Test 1: ChromaDB Cloud
print('=== Test ChromaDB Cloud ===')
try:
    import chromadb
    client = chromadb.CloudClient(
        api_key=os.environ['CHROMA_API_KEY'],
        tenant=os.environ['CHROMA_TENANT'],
        database=os.environ.get('CHROMA_DATABASE', 'BALITA'),
    )
    collection = client.get_or_create_collection(name='stunting_docs')
    count = collection.count()
    print('  Koneksi OK! Count: %d chunks' % count)
    if count > 0:
        r = collection.query(query_texts=['stunting child growth'], n_results=1)
        doc = r['documents'][0][0]
        print('  Query OK! Sample: %s...' % doc[:80])
except Exception as e:
    print('  GAGAL: %s' % e)

# Test 2: OpenRouter
print()
print('=== Test OpenRouter ===')
try:
    api_key = os.environ['OPENROUTER_API_KEY']
    body = json.dumps({
        'model': 'openai/gpt-4o-mini',
        'messages': [{'role': 'user', 'content': 'Katakan Halo dalam 3 kata'}],
        'temperature': 0.3,
        'max_tokens': 20,
    }).encode()
    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=body,
        headers={
            'Authorization': 'Bearer %s' % api_key,
            'Content-Type': 'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read())
    print('  Response: %s' % result['choices'][0]['message']['content'])
except Exception as e:
    print('  GAGAL: %s' % e)
