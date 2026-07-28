from dotenv import load_dotenv
load_dotenv()
import sys, os, json, urllib.request
sys.path.insert(0, r"D:\Stunting")
os.environ.setdefault("CHROMA_API_KEY", "")
os.environ["CHROMA_TENANT"] = "31e70a65-72b8-429e-bfb7-c7c897f247a9"
os.environ["CHROMA_DATABASE"] = "BALITA"
from rag.retrieve import retrieve, format_context

for q in [
    "tata laksana gizi anak stunting",
    "pencegahan stunting pada balita",
    "definisi stunting",
    "kapan harus rujuk ke rumah sakit",
]:
    chunks = retrieve(q, n_results=3)
    print("Q: " + q)
    print("  Chunks: " + str(len(chunks)))
    for c in chunks:
        src = c["source"]
        txt = c["text"][:80]
        print("    [" + src + "] (" + str(len(c["text"])) + "c): " + txt + "...")
    print()
