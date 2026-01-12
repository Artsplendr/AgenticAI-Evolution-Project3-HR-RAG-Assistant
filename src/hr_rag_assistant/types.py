from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

@dataclass(frozen=True)
class HRDocument:
    source: str
    text: str
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class HRChunk:
    id: str
    text: str
    metadata: Dict[str, Any]
    source: str
    chunk_index: int
    start_char: int
    end_char: int