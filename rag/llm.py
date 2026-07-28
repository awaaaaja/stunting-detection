import os
import json
from pathlib import Path
from dotenv import load_dotenv

from rag.retrieve import retrieve, format_context

load_dotenv()

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
MODEL = "openai/gpt-4o-mini"

PROMPT_TEMPLATE = Path(__file__).parent / "prompt_templates" / "rekomendasi_stunting.txt"


def build_prompt(question: str, context: str) -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    return template.replace("{context}", context).replace("{question}", question)


def query_llm(prompt: str) -> str:
    import urllib.request

    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 512,
    }).encode()

    req = urllib.request.Request(
        f"{OPENROUTER_BASE}/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())

    return result["choices"][0]["message"]["content"]


def generate_rekomendasi(question: str, balita_data: dict | None = None) -> dict:
    context_chunks = retrieve(question, n_results=5)

    if balita_data:
        data_context = (
            f"Data balita: "
            f"Usia={balita_data.get('age_months')} bulan, "
            f"TB={balita_data.get('height_cm')} cm, "
            f"BB={balita_data.get('weight_kg')} kg, "
            f"Jenis Kelamin={balita_data.get('gender')}, "
            f"TB/U z-score={balita_data.get('height_for_age_z')}, "
            f"Status={balita_data.get('stunting_status')}"
        )
        question = f"{question}\n\n{data_context}"

    prompt = build_prompt(question, format_context(context_chunks))
    response = query_llm(prompt)

    return {
        "question": question,
        "answer": response,
        "sources": [
            {"source": c["source"], "page": c["page"]}
            for c in context_chunks
        ],
    }


if __name__ == "__main__":
    result = generate_rekomendasi("Apa saja pencegahan stunting yang bisa dilakukan?")
    print(f"=== Question ===\n{result['question']}")
    print(f"\n=== Answer ===\n{result['answer']}")
    print(f"\n=== Sources ===")
    for s in result["sources"]:
        print(f"  - {s['source']} (halaman {s['page']})")
