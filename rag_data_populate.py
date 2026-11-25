"""Build the handbook FAISS index + chunk metadata. Run once before rag_tool.py."""
import json
from pathlib import Path

import faiss 
import numpy as np

from bedrock_client import EMBEDDING_DIM, embed, embedding_model_id

ROOT = Path(__file__).resolve().parent
HANDBOOK_DIR = ROOT / "data" / "handbook"
INDEX_PATH = ROOT / "data" / "handbook.faiss"
CHUNKS_PATH = ROOT / "data" / "handbook.json"

CHUNK_WORDS = 250
OVERLAP_WORDS = 50

def chunk_words(text, size=CHUNK_WORDS, overlap=OVERLAP_WORDS):
    words = text.split()
    step = size - overlap
    chunks = []
    for start in range(0, len(words), step):
        chunks.append(" ".join(words[start:start + size]))
        if start + size > len(words):
            break
    return chunks

def main():
    files = sorted(HANDBOOK_DIR.glob("*.md"))
    if not files:
        raise SystemExit(f"No .md files found in {HANDBOOK_DIR}")

    model_id = embedding_model_id()

    # Flat list: entry i lines up with FAISS row i, so a search hit
    chunks = []
    for path in files:
        file_chunks = chunk_words(path.read_text(encoding="utf-8"))
        for n, text in enumerate(file_chunks):
            chunks.append({"text": text, "path": path.name, "chunk_in_file": n})
        print(f"{path.name}: {len(file_chunks)} chunks")

    vectors = []
    for i, chunk in enumerate(chunks, 1):
        vectors.append(embed(chunk["text"], model_id))
        print(f"\rEmbedding {i}/{len(chunks)}", end="", flush=True)
    print()

    matrix = np.array(vectors, dtype="float32")
    # Defensive re-normalisation; Titan already returns unit vectors
    faiss.normalize_L2(matrix)
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(matrix)

    faiss.write_index(index, str(INDEX_PATH))
    payload = {"model_id": model_id, "chunks": chunks}
    CHUNKS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {index.ntotal} vectors -> {INDEX_PATH}")
    print(f"Saved {len(chunks)} chunks -> {CHUNKS_PATH}")

if __name__ == "__main__":
    main()