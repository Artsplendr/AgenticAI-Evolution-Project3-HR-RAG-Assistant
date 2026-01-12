from __future__ import annotations

import logging
import os


def get_logger(name: str | None = None) -> logging.Logger:
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name if name else "hr_rag_assistant")
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

