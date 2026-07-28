"""Search Semantic Scholar for stunting papers — no login needed."""
import requests, json, time, os
from pathlib import Path

BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
QUERIES = [
    "stunting management children Indonesia",
    "stunting prevention intervention toddlers Indonesia",
    "tata laksana stunting balita",
    "child growth malnutrition Indonesia treatment",
    "stunting risk factors child health developing countries",
]

papers = []
seen_titles = set()

for q in QUERIES:
    try:
        r = requests.get(BASE, params={
            "query": q,
            "limit": 10,
            "fields": "title,abstract,year,authors,openAccessPdf,externalIds,venue",
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            for p in data.get("data", []):
                title = p.get("title", "").strip()
                if title and title not in seen_titles and len(title) > 20:
                    seen_titles.add(title)
                    papers.append({
                        "title": title,
                        "abstract": p.get("abstract", "") or "",
                        "year": p.get("year"),
                        "venue": p.get("venue", ""),
                        "pdf_url": p.get("openAccessPdf", {}).get("url") if p.get("openAccessPdf") else None,
                        "doi": p.get("externalIds", {}).get("DOI") if p.get("externalIds") else None,
                    })
        time.sleep(1)  # rate limit
    except Exception as e:
        print(f"  Query failed [{q[:30]}]: {e}")

print(f"=== Semantic Scholar ===")
print(f"Total papers: {len(papers)}")
for i, p in enumerate(papers):
    has_abstract = "yes" if len(p["abstract"]) > 50 else "no"
    has_pdf = "yes" if p["pdf_url"] else "no"
    print(f"  {i+1}. [{p['year']}] {p['title'][:70]}... | abstract={has_abstract} pdf={has_pdf}")

OUT = Path(__file__).parent / "scholar_results.json"
OUT.write_text(json.dumps(papers, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nSaved to {OUT.name}")
