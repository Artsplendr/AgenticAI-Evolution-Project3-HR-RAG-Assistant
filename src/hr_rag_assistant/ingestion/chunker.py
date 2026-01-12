from __future__ import annotations

from typing import List

from hr_rag_assistant.types import HRChunk, HRDocument


def chunk_document(doc: HRDocument, chunk_size: int, chunk_overlap: int) -> List[HRChunk]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = doc.text
    chunks: List[HRChunk] = []

    start = 0
    idx = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                HRChunk(
                    id=f"{doc.source}::chunk_{idx:04d}",
                    text=chunk_text,
                    source=doc.source,
                    chunk_index=idx,
                    start_char=start,
                    end_char=end,
                    metadata={
                        **doc.metadata,
                        "chunk_index": idx,
                        "start_char": start,
                        "end_char": end,
                    },
                )
            )

        idx += 1

        # ✅ Critical: if we reached the end, stop.
        if end >= len(text):
            break

        # Next start with overlap
        next_start = end - chunk_overlap

        # ✅ Safety guard: ensure the pointer moves forward
        if next_start <= start:
            next_start = end  # no overlap fallback

        start = next_start

    return chunks


def chunk_documents(docs: List[HRDocument], chunk_size: int, chunk_overlap: int) -> List[HRChunk]:
    all_chunks: List[HRChunk] = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc, chunk_size, chunk_overlap))
    return all_chunks