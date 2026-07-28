"""Ingest clinical chunks to ChromaDB."""
import os, json
from dotenv import load_dotenv
import chromadb

load_dotenv()

COLLECTION_NAME = "stunting_docs"
CHUNKS_FILE = os.path.join(os.path.dirname(__file__), "clinical_chunks.json")

client = chromadb.CloudClient(
    api_key=os.environ["CHROMA_API_KEY"],
    tenant=os.environ["CHROMA_TENANT"],
    database=os.environ.get("CHROMA_DATABASE", "BALITA"),
)

col = client.get_or_create_collection(name=COLLECTION_NAME)

with open(CHUNKS_FILE, encoding="utf-8") as f:
    chunks = json.load(f)

# Generate stable IDs and prepare batch
ids = []
documents = []
metadatas = []

for i, c in enumerate(chunks):
    source_key = c["source"].replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "").replace(",", "")[:40]
    chunk_id = f"clinical_{source_key}_{i:04d}"
    ids.append(chunk_id)
    documents.append(c["text"])
    metadatas.append({
        "source": c["source"],
        "page": c.get("page", 1),
    })

# Upload in batches of 100
batch_size = 100
for start in range(0, len(ids), batch_size):
    end = min(start + batch_size, len(ids))
    col.add(
        ids=ids[start:end],
        documents=documents[start:end],
        metadatas=metadatas[start:end],
    )
    print(f"  Batch {start//batch_size + 1}: {end - start} chunks uploaded")

print(f"\nDone: {len(ids)} clinical chunks ingested")
print(f"Total collection count: {col.count()}")
