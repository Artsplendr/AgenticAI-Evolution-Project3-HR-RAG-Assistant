from __future__ import annotations

from dataclasses import dataclass
from typing import List

from openai import OpenAI

from hr_rag_assistant.retrieval.vectorstore import FaissVectorStore, RetrievedChunk


@dataclass(frozen=True)
class RetrievalResult:
    query: str
    top_k: int
    results: List[RetrievedChunk]


class HRRetriever:
    def __init__(
        self,
        *,
        index_dir: str,
        openai_api_key: str,
        embedding_model: str,
    ):
        self.store = FaissVectorStore(index_dir=index_dir)
        self.oai = OpenAI(api_key=openai_api_key)
        self.embedding_model = embedding_model

    def retrieve(self, query: str, top_k: int = 5) -> RetrievalResult:
        query = query.strip()
        if not query:
            raise ValueError("Query is empty.")

        emb = self.oai.embeddings.create(model=self.embedding_model, input=[query])
        query_vec = emb.data[0].embedding

        hits = self.store.search(query_vec, top_k=top_k)
        return RetrievalResult(query=query, top_k=top_k, results=hits)