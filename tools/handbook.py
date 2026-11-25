"""Cosine-similarity search over a FAISS index whose name matches the tool name."""
import json
import sys
from pathlib import Path

import faiss
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
sys.path.insert(0, str(ROOT))

from bedrock_client import embed

TOP_K = 1

TOOL_SPEC = {
    "toolSpec": {
        "name": "handbook",
        "description": (
            "Search the NoVaOps employee handbook (policies, benefits, PTO, titles, "
            "rituals, devices, severance, internal systems, carrer, etc.). Use ONLY for "
            "questions about NovaOps the company. Do not use for chit-chat or general knowledge."
        ),
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A self-contained search query describing what to find in the handbook."
                    }
                },
                "required": ["query"]
            }
        }
    }
}

_CACHE = {}

class DataNotReadyError(Exception):
    pass

def _load(name):
    if name in _CACHE:
        return _CACHE[name]

    index_path = DATA_DIR / f"{name}.faiss"
    chunks_path = DATA_DIR / f"{name}.json"
    if not index_path.exists() or not chunks_path.exists():
        raise DataNotReadyError(f"Missing {index_path.name} or {chunks_path.name}")

    try:
        payload = json.loads(chunks_path.read_text(encoding="utf-8"))
        chunks, model_id = payload["chunks"], payload["model_id"]
    except (ValueError, KeyError, TypeError) as exc:
        raise DataNotReadyError(f"{index_path.name} and {chunks_path.name} is not in the expected format") from exc

    index = faiss.read_index(str(index_path))
    if index.ntotal != len(chunks):
        raise DataNotReadyError(f"{index_path.name} and {chunks_path.name} are out of sync")

    _CACHE[name] = (index, chunks, model_id)

    return _CACHE[name]

def search(tool_name, query, top_k=TOP_K):
    """Return [(chunk_in_file, file_name, chunk_text, score), ...] best-first"""
    index, chunks, model_id = _load(tool_name)

    # Embed the query with the same model that build the index, or scores are meaningless.
    query_vec = np.array([embed(query, model_id)], dtype="float32")
    # before:  [3, 4]          length = √(3² + 4²) = 5
    # after:   [3/5, 4/5] = [0.6, 0.8]   length = √(0.36 + 0.64) = 1
    faiss.normalize_L2(query_vec)
    # On unit vectors, IndexFlatIP inner product == cosine similarity.
    scores, ids = index.search(query_vec, top_k)
    # "chunk_in_file" is the index of this chunk in the file
    # "path" is the file name
    # "text" is the chunk text
    return [
        (chunks[i]["chunk_in_file"], chunks[i]["path"], chunks[i]["text"], float(s))
        for i, s in zip(ids[0], scores[0])
        if i != -1
    ]

def format_results(results):
    """Reader all top-k rows (with scores) as text, the LLM judges which are relevant."""
    return "\n\n".join(
        f"[source: {path} | chunk {n} | cosine {score:.3f}]\n{text}"
        for n, path, text, score in results
    )