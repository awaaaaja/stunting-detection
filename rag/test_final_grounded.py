from dotenv import load_dotenv
load_dotenv()
import sys, os, json, urllib.request
sys.path.insert(0, r"D:\Stunting")
os.environ.setdefault("CHROMA_API_KEY", "")
os.environ["CHROMA_TENANT"] = "31e70a65-72b8-429e-bfb7-c7c897f247a9"
os.environ["CHROMA_DATABASE"] = "BALITA"
from rag.retrieve import retrieve, format_context

questions = [
    "Jelaskan tata laksana gizi untuk anak stunting.",
    "Apa definisi stunting?",
    "Apa saja pencegahan stunting yang bisa dilakukan menurut PNPK?",
]

for q in questions:
    chunks = retrieve(q, n_results=3)
    if not chunks:
        print("Q: " + q + "\nA: No chunks\n")
        continue
    context = format_context(chunks)
    prompt = "Anda adalah asisten ahli gizi dan kesehatan masyarakat. Gunakan HANYA informasi dari konteks di bawah ini. Jika informasi tidak tersedia, katakan tidak tahu.\n\nKonteks:\n" + context + "\n\nPertanyaan: " + q

    body = json.dumps({
        "model": "openai/gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3, "max_tokens": 512,
    }).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {os.environ["OPENROUTER_API_KEY"]}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        answer = json.loads(resp.read())["choices"][0]["message"]["content"]

    print("Q: " + q)
    print("A: " + answer)
    print("Sumber:")
    for c in chunks:
        print("  - " + c["source"] + " (halaman " + str(c["page"]) + ")")
    print()
