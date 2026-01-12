from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """Basic normalization: normalize whitespace and strip."""
    # Replace Windows newlines and normalize multiple spaces/newlines
    normalized = text.replace("\r\n", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()

