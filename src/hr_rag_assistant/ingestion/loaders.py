from __future__ import annotations

from pathlib import Path
from typing import List

from hr_rag_assistant.types import HRDocument

SUPPORTED_EXTS = {".md", ".txt"}


def load_documents(raw_dir: str) -> List[HRDocument]:
    base = Path(raw_dir)
    if not base.exists():
        raise FileNotFoundError(f"RAW_DATA_DIR not found: {base.resolve()}")

    docs: List[HRDocument] = []
    for path in sorted(base.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTS:
            text = path.read_text(encoding="utf-8", errors="ignore")
            docs.append(
                HRDocument(
                    source=path.name,
                    text=text,
                    metadata={
                        "source": path.name,
                        "path": str(path.relative_to(base)),
                        "ext": path.suffix.lower(),
                    },
                )
            )

    if not docs:
        raise RuntimeError(f"No .md/.txt documents found in {base.resolve()}")

    return docs