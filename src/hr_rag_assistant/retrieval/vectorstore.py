from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import faiss
import numpy as np

from hr_rag_assistant.types import HRChunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: HRChunk
    score: float  # cosine similarity (higher is better)


class FaissVectorStore:
    """
    Loads a persisted FAISS index + chunk store produced by ingest_hr_docs.py
    and provides similarity search over chunks.

    Assumptions:
    - index is IndexFlatIP
    - vectors were L2-normalized before add
    - queries are L2-normalized before search
    """

    def __init__(self, index_dir: str):
        self.index_dir = Path(index_dir)
        self.index_path = self.index_dir / "index.faiss"
        self.chunks_path = self.index_dir / "chunks.jsonl"
        self.meta_path = self.index_dir / "meta.json"

        if not self.index_path.exists():
            raise FileNotFoundError(f"Missing FAISS index: {self.index_path}")
        if not self.chunks_path.exists():
            raise FileNotFoundError(f"Missing chunks store: {self.chunks_path}")
        if not self.meta_path.exists():
            raise FileNotFoundError(f"Missing meta file: {self.meta_path}")

        self.meta = json.loads(self.meta_path.read_text(encoding="utf-8"))

        # Load FAISS index
        self.index = faiss.read_index(str(self.index_path))

        # Load chunks (order matters: row i corresponds to vector i)
        self.chunks: List[HRChunk] = []
        with self.chunks_path.open("r", encoding="utf-8") as f:
            for line in f:
                row = json.loads(line)
                self.chunks.append(
                    HRChunk(
                        id=row["id"],
                        text=row["text"],
                        metadata=row.get("metadata", {}),
                        source=row["source"],
                        chunk_index=int(row["chunk_index"]),
                        start_char=int(row.get("start_char", 0)),
                        end_char=int(row.get("end_char", 0)),
                    )
                )

        if len(self.chunks) != self.index.ntotal:
            raise RuntimeError(
                f"Index/chunks mismatch: index.ntotal={self.index.ntotal} but chunks={len(self.chunks)}"
            )

        self.dimension = int(self.meta.get("dimension", self.index.d))

    def _normalize_query(self, vector: List[float]) -> np.ndarray:
        x = np.array(vector, dtype="float32").reshape(1, -1)
        if x.shape[1] != self.dimension:
            raise ValueError(f"Query dim {x.shape[1]} != index dim {self.dimension}")
        faiss.normalize_L2(x)
        return x

    def search(self, query_vector: List[float], top_k: int = 5) -> List[RetrievedChunk]:
        if top_k <= 0:
            raise ValueError("top_k must be > 0")

        q = self._normalize_query(query_vector)

        # D: similarity scores, I: indices
        D, I = self.index.search(q, top_k)

        results: List[RetrievedChunk] = []
        for score, idx in zip(D[0].tolist(), I[0].tolist()):
            if idx < 0:
                continue
            results.append(RetrievedChunk(chunk=self.chunks[idx], score=float(score)))

        return results