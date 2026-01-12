## HR RAG Assistant Architecture

- Ingestion: `loaders` → `cleaner` → `chunker` → `index_builder` (placeholder persists summary).
- Retrieval: `VectorStore.load_from_index` (placeholder) → `Retriever.similarity_search`.
- Generation: `answerer.synthesize_answer` uses `HR_INSTRUCTION` and formats citations.
- Orchestration: `HRAgent` wires config → retriever → answerer.

### Flow
1) Source docs in `data/raw/`.
2) `scripts/ingest_hr_docs.py` builds/updates `data/indexes/hr_default/`.
3) `scripts/ask_hr.py` queries; retrieved results are synthesized with citations.

