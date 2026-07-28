from dotenv import load_dotenv
load_dotenv()
import chromadb

client = chromadb.CloudClient(
    api_key=os.environ["CHROMA_API_KEY"],
    tenant=os.environ["CHROMA_TENANT"],
    database=os.environ.get("CHROMA_DATABASE", "BALITA"),
)
col = client.get_collection(name="stunting_docs")

data = col.get()
ids = data["ids"]
docs = data["documents"]
print(f"Total chunks: {len(ids)}")
print()

# stats
total_chars = sum(len(d) for d in docs)
avg_chars = total_chars / len(docs) if docs else 0
short_count = sum(1 for d in docs if len(d) < 50)
print(f"Total chars: {total_chars:,}")
print(f"Avg chars/chunk: {avg_chars:.0f}")
print(f"Chunks < 50 chars: {short_count}")
print()

# sample some chunks
sources = set()
for doc, meta in zip(docs, data["metadatas"]):
    sources.add(meta["source"])
print(f"Sources: {sorted(sources)}")
print()

# show some longer chunks
long_chunks = [(doc, meta) for doc, meta in zip(docs, data["metadatas"]) if len(doc) > 100]
print(f"Chunks > 100 chars: {len(long_chunks)}")
for doc, meta in long_chunks[:3]:
    print(f"\n  [{meta['source']} p.{meta['page']}] ({len(doc)} chars)")
    print(f"  {doc[:200]}")
