import os
import glob
from dotenv import load_dotenv
import chromadb
import pdfplumber
import tiktoken

load_dotenv()

PDF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "docs")
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
COLLECTION_NAME = "stunting_docs"
ENCODING_MODEL = "cl100k_base"

chroma_client = chromadb.CloudClient(
    api_key=os.environ["CHROMA_API_KEY"],
    tenant=os.environ["CHROMA_TENANT"],
    database=os.environ.get("CHROMA_DATABASE", "BALITA"),
)

enc = tiktoken.get_encoding(ENCODING_MODEL)


def extract_text(pdf_path):
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({"page": i + 1, "text": text.strip()})
    return pages


def chunk_text(text, source, page):
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + CHUNK_SIZE
        chunk_tokens = tokens[start:end]
        chunk_text = enc.decode(chunk_tokens)
        chunk_id = f"{source}_p{page}_{start}"
        chunks.append({
            "id": chunk_id,
            "text": chunk_text,
            "metadata": {
                "source": source,
                "page": page,
                "chunk_start": start,
            }
        })
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def main():
    pdf_files = glob.glob(os.path.join(PDF_DIR, "*.pdf"))
    print(f"Ditemukan {len(pdf_files)} PDF")

    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

    all_ids = []
    all_documents = []
    all_metadatas = []
    total_chunks = 0

    for pdf_path in sorted(pdf_files):
        fname = os.path.basename(pdf_path)
        print(f"  Memproses {fname}...", end=" ")
        pages = extract_text(pdf_path)
        print(f"{len(pages)} halaman", end=" ")
        file_chunks = 0
        for page in pages:
            chunks = chunk_text(page["text"], fname, page["page"])
            for c in chunks:
                all_ids.append(c["id"])
                all_documents.append(c["text"])
                all_metadatas.append(c["metadata"])
                file_chunks += 1
        total_chunks += file_chunks
        print(f"-> {file_chunks} chunks")

    if all_ids:
        batch_size = 100
        for i in range(0, len(all_ids), batch_size):
            batch_end = min(i + batch_size, len(all_ids))
            collection.add(
                ids=all_ids[i:batch_end],
                documents=all_documents[i:batch_end],
                metadatas=all_metadatas[i:batch_end],
            )
            print(f"    Batch {i//batch_size + 1}: {batch_end - i} chunks pushed")

    print(f"\nSelesai: {total_chunks} chunks dari {len(pdf_files)} PDF -> koleksi '{COLLECTION_NAME}'")


if __name__ == "__main__":
    main()
