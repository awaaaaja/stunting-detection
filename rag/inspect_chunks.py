from dotenv import load_dotenv
load_dotenv()
import chromadb

client = chromadb.CloudClient(
    api_key=os.environ["CHROMA_API_KEY"],
    tenant=os.environ["CHROMA_TENANT"],
    database=os.environ.get("CHROMA_DATABASE", "BALITA"),
)
col = client.get_collection(name="stunting_docs")

q = "percepatan penurunan stunting"
results = col.query(query_texts=[q], n_results=3)
for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
    print(f"=== Result {i+1} [{meta['source']} p.{meta['page']}] ===")
    print(doc[:500])
    print()
