from __future__ import annotations

from src.hr_rag_assistant.retrieval.retriever import Retriever
from src.hr_rag_assistant.retrieval.vectorstore import VectorStore


def test_retriever_with_empty_store_returns_no_results() -> None:
    store = VectorStore(chunks=[])
    retriever = Retriever(store)
    results = retriever.retrieve("What is the PTO policy?", top_k=3)
    assert isinstance(results, list)
    assert len(results) == 0

