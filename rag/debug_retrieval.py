from dotenv import load_dotenv
load_dotenv()
import sys, os
sys.path.insert(0, r"D:\Stunting")
os.environ.setdefault("CHROMA_API_KEY", "")
os.environ["CHROMA_TENANT"] = "31e70a65-72b8-429e-bfb7-c7c897f247a9"
os.environ["CHROMA_DATABASE"] = "BALITA"

from rag.retrieve import retrieve

# Check what chunks are retrieved for "pencegahan stunting"
chunks = retrieve("pencegahan stunting", n_results=5)
print(f"=== Query: 'pencegahan stunting' ===")
for i, c in enumerate(chunks):
    print(f"\nChunk {i+1} [{c['source']} p.{c['page']}]")
    print(c['text'][:150])

print("\n" + "="*50)

# Check for "tata laksana gizi"
chunks2 = retrieve("tata laksana gizi stunting", n_results=5)
print(f"\n=== Query: 'tata laksana gizi stunting' ===")
for i, c in enumerate(chunks2):
    print(f"\nChunk {i+1} [{c['source']} p.{c['page']}]")
    print(c['text'][:150])

print("\n" + "="*50)

# Check all IDs from pnpk source
import chromadb
client = chromadb.CloudClient(api_key=os.environ["CHROMA_API_KEY"], tenant=os.environ["CHROMA_TENANT"], database=os.environ.get("CHROMA_DATABASE", "BALITA"))
col = client.get_collection(name='stunting_docs')
all_docs = col.get(limit=1000)
pnpk_chunks = [(doc, meta) for doc, meta in zip(all_docs['documents'], all_docs['metadatas']) 
               if 'pnpk' in meta.get('source', '')]
print(f"\nPNPK chunks in DB: {len(pnpk_chunks)}")
if pnpk_chunks:
    for doc, meta in pnpk_chunks[:3]:
        print(f"  [{meta['source']}] ({len(doc)} chars): {doc[:80]}...")
