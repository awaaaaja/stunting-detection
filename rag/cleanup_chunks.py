from dotenv import load_dotenv
load_dotenv()
import sys, os
sys.path.insert(0, r"D:\Stunting")
os.environ.setdefault("CHROMA_API_KEY", "")
os.environ["CHROMA_TENANT"] = "31e70a65-72b8-429e-bfb7-c7c897f247a9"
os.environ["CHROMA_DATABASE"] = "BALITA"

import chromadb
client = chromadb.CloudClient(api_key=os.environ["CHROMA_API_KEY"], tenant=os.environ["CHROMA_TENANT"], database=os.environ.get("CHROMA_DATABASE", "BALITA"))
col = client.get_collection(name='stunting_docs')

# Get all
all_data = client._get('stunting_docs', limit=745)
ids = all_data['ids']
docs = all_data['documents']
metas = all_data['metadatas']

print(f"Total: {len(ids)}")
# Find short chunks
short = [(i, d, m['source']) for i, (d, m) in enumerate(zip(docs, metas)) if len(d) < 50]
print(f"Short chunks (<50 chars): {len(short)}")
for idx, d, src in short[:10]:
    print(f"  [{src}] ({len(d)}c): '{d[:40]}'")
