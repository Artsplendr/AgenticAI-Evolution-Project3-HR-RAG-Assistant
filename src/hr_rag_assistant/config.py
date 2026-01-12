from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    embedding_model: str
    raw_data_dir: str
    index_dir: str
    chunk_size: int
    chunk_overlap: int


def get_settings() -> Settings:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Set it in your .env file.")

    return Settings(
        openai_api_key=api_key,
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        raw_data_dir=os.getenv("RAW_DATA_DIR", "./data/raw"),
        index_dir=os.getenv("INDEX_DIR", "./data/indexes/hr_default"),
        chunk_size=int(os.getenv("CHUNK_SIZE", "900")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "150")),
    )