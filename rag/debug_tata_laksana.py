from dotenv import load_dotenv
load_dotenv()
import sys, os
sys.path.insert(0, r"D:\Stunting")
os.environ.setdefault("CHROMA_API_KEY", "")
os.environ["CHROMA_TENANT"] = "31e70a65-72b8-429e-bfb7-c7c897f247a9"
os.environ["CHROMA_DATABASE"] = "BALITA"

from rag.retrieve import retrieve

q = "tata laksana gizi anak stunting"
chunks = retrieve(q, n_results=5)
for i, c in enumerate(chunks):
    print(f"Chunk {i+1} [{c['source']} p.{c['page']}] ({len(c['text'])} chars)")
    print(c['text'][:200])
    print()
