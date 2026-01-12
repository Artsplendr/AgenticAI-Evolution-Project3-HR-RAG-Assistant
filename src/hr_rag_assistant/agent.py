from __future__ import annotations

from typing import Optional

from src.hr_rag_assistant.config import Config
from src.hr_rag_assistant.generation.answerer import synthesize_answer
from src.hr_rag_assistant.logging import get_logger
from src.hr_rag_assistant.retrieval.retriever import Retriever
from src.hr_rag_assistant.retrieval.vectorstore import VectorStore
from src.hr_rag_assistant.types import AnswerResult


class HRAgent:
    def __init__(self, config: Config, logger=None) -> None:
        self.config = config
        self.logger = logger or get_logger(__name__)
        self._store = VectorStore.load_from_index(config.index_dir)
        self._retriever = Retriever(self._store)

    def ask(self, question: str, top_k: int = 4) -> AnswerResult:
        self.logger.info("Question: %s", question)
        retrieved = self._retriever.retrieve(question, top_k=top_k)
        answer = synthesize_answer(question, retrieved)
        return answer

