from __future__ import annotations

from typing import Iterable, List, Set, Tuple

from hr_rag_assistant.retrieval.vectorstore import RetrievedChunk


def unique_sources(hits: Iterable[RetrievedChunk], max_sources: int = 10) -> List[str]:
    """
    Return a de-duplicated list of sources like:
      remote_work_policy.md :: chunk_0002
    """
    seen: Set[Tuple[str, int]] = set()
    out: List[str] = []

    for hit in hits:
        c = hit.chunk
        key = (c.source, c.chunk_index)
        if key in seen:
            continue
        seen.add(key)
        out.append(f"{c.source} :: chunk_{c.chunk_index:04d}")
        if len(out) >= max_sources:
            break

    return out


def format_sources_block(hits: Iterable[RetrievedChunk], max_sources: int = 10) -> str:
    srcs = unique_sources(hits, max_sources=max_sources)
    if not srcs:
        return "Sources:\n- (none)"
    return "Sources:\n" + "\n".join(f"- {s}" for s in srcs)