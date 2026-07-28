import os
from dotenv import load_dotenv
import chromadb

load_dotenv()

COLLECTION_NAME = "stunting_docs"
N_RESULTS = 5

# Clinical sources are preferred over policy PDFs
CLINICAL_PREFIXES = [
    "PNPK Stunting",
    "PNPK Stunting Detail",
    "WHO Guideline",
    "WHO Stunting Brief",
    "Juknis PMT Lokal",
    "IPC Guidelines",
    "Pedoman Intervensi",
    "pnpk_stunting_referensi",
]

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.CloudClient(
            api_key=os.environ["CHROMA_API_KEY"],
            tenant=os.environ["CHROMA_TENANT"],
            database=os.environ.get("CHROMA_DATABASE", "BALITA"),
        )
        _collection = _client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def _is_clinical(source: str) -> bool:
    for prefix in CLINICAL_PREFIXES:
        if source.startswith(prefix):
            return True
    return False


def retrieve(query: str, n_results: int = N_RESULTS, min_chars: int = 100) -> list[dict]:
    col = _get_collection()
    # Expand Indonesian query with English keywords for better embedding match
    expanded = query.lower()
    query_map = {
        "stunting": "stunting child growth",
        "gizi": "nutrition nutritional",
        "tata laksana": "management treatment therapy",
        "pencegahan": "prevention preventive",
        "diagnosis": "diagnosis diagnostic assessment",
        "definisi": "definition",
        "pkak": "pkak medical food",
        "pdk": "pdk special dietary",
        "rujuk": "referral reference hospital",
        "asi": "breastfeeding breast milk exclusive",
        "mpasi": "complementary feeding",
        "pmt": "supplementary feeding",
        "balita": "toddler underfive children",
        "protein": "protein animal",
        "vitamin": "vitamin supplementation",
        "imunisasi": "immunization vaccination",
        "posyandu": "posyandu health post",
        "puskesmas": "puskesmas health center",
        "rsud": "hospital referral",
    }
    for id_word, en_words in query_map.items():
        if id_word in expanded:
            expanded += " " + en_words

    # Pull more candidates to overcome dedup
    results = col.query(query_texts=[expanded], n_results=n_results * 8)
    clinical: list[dict] = []
    policy: list[dict] = []
    seen_texts: set = set()

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        text = doc.strip()
        if len(text) < min_chars:
            continue
        if text.count(" ") < 10 and len(text) < 200:
            continue

        # Dedup by text prefix (first 100 chars) instead of source+page
        dedup_key = text[:100]
        if dedup_key in seen_texts:
            continue
        seen_texts.add(dedup_key)

        entry = {"text": doc, "source": meta["source"], "page": meta["page"]}
        if _is_clinical(meta["source"]):
            clinical.append(entry)
        else:
            policy.append(entry)

    # Interleave: clinical first, then fill with policy
    out = clinical[:n_results]
    if len(out) < n_results:
        needed = n_results - len(out)
        out.extend(policy[:needed])
    return out


def format_context(chunks: list[dict]) -> str:
    parts = []
    seen = set()
    for c in chunks:
        key = (c["source"], c["page"])
        if key not in seen:
            seen.add(key)
        parts.append(f"[Sumber: {c['source']}, Halaman {c['page']}]\n{c['text']}")
    return "\n\n---\n\n".join(parts)
