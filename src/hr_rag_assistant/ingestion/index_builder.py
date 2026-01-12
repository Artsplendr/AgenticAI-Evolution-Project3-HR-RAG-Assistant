from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

import faiss
from openai import OpenAI

from hr_rag_assistant.types import HRChunk


def _batched(items: List[str], batch_size: int):
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


def build_and_persist_faiss_index(
    *,
    chunks: List[HRChunk],
    index_dir: str,
    openai_api_key: str,
    embedding_model: str,
    batch_size: int = 128,
) -> None:
    """
    Builds a FAISS index (cosine similarity via normalized vectors + Inner Product)
    and persists:
      - index.faiss
      - chunks.jsonl (id, text, metadata for citations)
      - meta.json (embedding_model, dim, counts)
    """
    if not chunks:
        raise ValueError("No chunks provided for indexing.")

    os.makedirs(index_dir, exist_ok=True)
    index_dir_path = Path(index_dir)

    index_path = index_dir_path / "index.faiss"
    chunks_path = index_dir_path / "chunks.jsonl"
    meta_path = index_dir_path / "meta.json"

    oai = OpenAI(api_key=openai_api_key)

    # 1) Embed chunks
    all_vectors: List[List[float]] = []
    all_ids: List[str] = []

    texts = [c.text for c in chunks]
    ids = [c.id for c in chunks]

    for id_batch, text_batch in zip(_batched(ids, batch_size), _batched(texts, batch_size)):
        emb = oai.embeddings.create(model=embedding_model, input=text_batch)
        vectors = [e.embedding for e in emb.data]
        all_vectors.extend(vectors)
        all_ids.extend(id_batch)

    if not all_vectors:
        raise RuntimeError("Embedding returned no vectors.")

    dim = len(all_vectors[0])

    # 2) Build FAISS index
    # We use cosine similarity by L2-normalizing vectors and using Inner Product.
    import numpy as np

    x = np.array(all_vectors, dtype="float32")
    faiss.normalize_L2(x)

    index = faiss.IndexFlatIP(dim)  # Inner Product
    index.add(x)

    # 3) Persist FAISS index
    faiss.write_index(index, str(index_path))

    # 4) Persist chunk store for citations + lookup
    # We store chunks in the same order as vectors were added to FAISS.
    # Retrieval later will return indices -> map to these rows.
    with chunks_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            row = {
                "id": c.id,
                "source": c.source,
                "chunk_index": c.chunk_index,
                "start_char": c.start_char,
                "end_char": c.end_char,
                "text": c.text,
                "metadata": c.metadata,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # 5) Persist meta
    meta = {
        "embedding_model": embedding_model,
        "dimension": dim,
        "num_chunks": len(chunks),
        "faiss_index": "IndexFlatIP",
        "similarity": "cosine (via normalized vectors + inner product)",
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")