## Decisions

- Chunking: 600 words with 80-word overlap (simple, robust starter).
- Top-K: default 4 results.
- Vector store: placeholder; swap for a real embeddings DB (FAISS, Chroma, etc.).
- Paths: controlled by env (`HR_RAW_DIR`, `HR_INDEX_DIR`) with sensible defaults.
- Instruction: strict "answer only from HR policy context" to avoid hallucinations.

