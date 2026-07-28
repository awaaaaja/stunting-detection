from dotenv import load_dotenv
load_dotenv()
import sys, os, json, urllib.request

sys.path.insert(0, r"D:\Stunting")
os.environ.setdefault("CHROMA_API_KEY", "")
os.environ["CHROMA_TENANT"] = "31e70a65-72b8-429e-bfb7-c7c897f247a9"
os.environ["CHROMA_DATABASE"] = "BALITA"

from rag.retrieve import retrieve, format_context

questions = [
    "Apa definisi stunting menurut WHO?",
    "Bagaimana cara diagnosis stunting?",
    "Apa saja pencegahan stunting yang bisa dilakukan?",
    "Bagaimana tata laksana gizi untuk anak stunting?",
    "Apa itu PKMK dan bagaimana cara pemberiannya?",
    "Kapan anak stunting harus dirujuk ke rumah sakit?",
    "Apa saja rekomendasi untuk balita stunting usia 24 bulan dengan TB 70 cm?",
]

print("Retrieval test (without LLM):\n")
for q in questions:
    chunks = retrieve(q, n_results=3)
    print(f"Q: {q}")
    for c in chunks:
        src = f"{c['source']} p.{c['page']}"
        print(f"  [{src}] ({len(c['text'])} chars): {c['text'][:100]}")
    print()
