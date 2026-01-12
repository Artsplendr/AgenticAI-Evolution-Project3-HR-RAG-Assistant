from __future__ import annotations

from pathlib import Path

import pytest

from src.hr_rag_assistant.ingestion.chunker import chunk_text


def test_chunker_basic_and_overlap() -> None:
    text = " ".join([f"word{i}" for i in range(0, 1500)])
    chunks = chunk_text(text, chunk_size=200, overlap=50, source_path=Path("sample.md"))
    assert len(chunks) > 1
    # Ensure metadata present and monotonic chunk ids
    for i, ch in enumerate(chunks):
        assert ch.source_path.name == "sample.md"
        assert ch.chunk_id == f"chunk-{i}"
        assert ch.start_char < ch.end_char
        assert ch.text
    # Overlap implies that the second chunk starts before the first ended
    assert chunks[1].start_char < chunks[0].end_char


def test_chunker_invalid_args() -> None:
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("hello", overlap=-1)

