"""Re-chunk PNPK Stunting reference text — semantic per section."""
import os, re, json
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"
PNPK_FILE = DOCS_DIR / "pnpk_stunting_referensi.txt"
CHUNK_SIZE = 500
OVERLAP = 50

RAW = PNPK_FILE.read_text(encoding="utf-8")

SECTIONS = []

# Split by BAB headers
bab_pattern = re.compile(r"(BAB [IV]+\s*[-–—]?\s*.+?(?=\n))", re.IGNORECASE)
parts = bab_pattern.split(RAW)

current_bab = None
for p in parts:
    p = p.strip()
    if not p:
        continue
    if re.match(r"^BAB\s+[IV]+\s*[-–—]?\s*\w", p, re.IGNORECASE):
        current_bab = p
    elif current_bab:
        SECTIONS.append((current_bab, p))
        current_bab = None
    else:
        pass  # preamble before BAB I

# Further split each section by sub-headers and into chunks
def smart_chunk(text, source_label, page_num):
    lines = text.split("\n")
    chunks = []
    buffer = ""
    para_start = 1

    for i, line in enumerate(lines):
        line_stripped = line.strip()
        # Check for sub-heading: numbered items like "1. ..." or "## ..." or bold patterns
        is_subhead = bool(re.match(r"^\d+\.\s+[A-Z]", line_stripped)) or line_stripped.startswith("##")
        
        if is_subhead and len(buffer) > 100:
            chunks.append({"text": buffer.strip(), "source": source_label, "page": page_num})
            buffer = line_stripped + "\n"
            para_start = i + 1
        else:
            buffer += line + "\n"

        # Hard cut if buffer exceeds CHUNK_SIZE
        if len(buffer) >= CHUNK_SIZE and len(buffer.split("\n")) > 3:
            chunks.append({"text": buffer.strip(), "source": source_label, "page": page_num})
            # Overlap: keep last 2 lines for context
            overlap_lines = buffer.strip().split("\n")[-3:]
            buffer = "\n".join(overlap_lines) + "\n" if len(overlap_lines[0]) > 20 else ""
            para_start = i + 1

    if buffer.strip():
        chunks.append({"text": buffer.strip(), "source": source_label, "page": page_num})

    return chunks


all_chunks = []
page_counter = 1

for bab_title, content in SECTIONS:
    raw_text = f"{bab_title}\n{content}"
    chunks = smart_chunk(raw_text, "pnpk_stunting_referensi.txt", page_counter)
    for c in chunks:
        # Ensure minimum quality
        if len(c["text"]) >= 100 and c["text"].count(" ") >= 10:
            all_chunks.append(c)
    page_counter += 1

print(f"=== PNPK Re-chunking ===")
print(f"Source file: {PNPK_FILE.name} ({len(RAW)} chars)")
print(f"Sections found: {len(SECTIONS)}")
print(f"Chunks produced: {len(all_chunks)}")

for i, c in enumerate(all_chunks):
    first_line = c["text"].split("\n")[0][:80]
    print(f"  Chunk {i+1}: [{len(c['text']):4d} chars] {first_line}...")

print()
print("Sample chunk 0:")
print(all_chunks[0]["text"][:300])
print("...")
