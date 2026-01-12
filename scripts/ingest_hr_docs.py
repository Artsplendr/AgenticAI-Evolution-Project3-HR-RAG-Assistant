from __future__ import annotations

from hr_rag_assistant.config import get_settings
from hr_rag_assistant.ingestion.loaders import load_documents
from hr_rag_assistant.ingestion.cleaner import clean_text
from hr_rag_assistant.ingestion.chunker import chunk_documents
from hr_rag_assistant.ingestion.index_builder import build_and_persist_faiss_index


def main() -> None:
    s = get_settings()

    print("== HR RAG Ingestion (FAISS) ==")
    print(f"Raw docs dir : {s.raw_data_dir}")
    print(f"Index dir    : {s.index_dir}")
    print(f"Chunk size   : {s.chunk_size}")
    print(f"Overlap      : {s.chunk_overlap}")
    print(f"Embeddings   : {s.embedding_model}")

    # 1) Load docs
    docs = load_documents(s.raw_data_dir)
    print(f"\nLoaded documents: {len(docs)}")

    # 2) Clean text
    cleaned_docs = []
    for d in docs:
        cleaned_docs.append(
            type(d)(
                source=d.source,
                text=clean_text(d.text),
                metadata=d.metadata,
            )
        )

    total_chars = sum(len(d.text) for d in cleaned_docs)
    print(f"Total cleaned chars: {total_chars:,}")
    print(">>> CLEANING DONE, STARTING CHUNKING")
    

    # 3) Chunk
    chunks = chunk_documents(
        cleaned_docs,
        chunk_size=s.chunk_size,
        chunk_overlap=s.chunk_overlap,
    )
    print(f"Chunks created: {len(chunks)}")

    if not chunks:
        raise RuntimeError("No chunks created. Check your documents and chunk settings.")

    avg_len = sum(len(c.text) for c in chunks) / len(chunks)
    print(f"Avg chunk length: {avg_len:.1f} chars")
    print(f"Example chunk id: {chunks[0].id}")

    # 4) Build + persist FAISS index
    print("\nBuilding FAISS index (calling embeddings)...")
    build_and_persist_faiss_index(
        chunks=chunks,
        index_dir=s.index_dir,
        openai_api_key=s.openai_api_key,
        embedding_model=s.embedding_model,
    )

    print("\n✅ Done.")
    print(f"Saved: {s.index_dir}/index.faiss")
    print(f"Saved: {s.index_dir}/chunks.jsonl")
    print(f"Saved: {s.index_dir}/meta.json")



if __name__ == "__main__":
    main()

print(">>> FILE END REACHED")
