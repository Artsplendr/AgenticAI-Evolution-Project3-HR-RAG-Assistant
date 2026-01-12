from __future__ import annotations

from dataclasses import dataclass
from typing import List

from openai import OpenAI

from hr_rag_assistant.retrieval.prompts import HR_SYSTEM_PROMPT, HR_USER_PROMPT_TEMPLATE
from hr_rag_assistant.retrieval.vectorstore import RetrievedChunk


@dataclass(frozen=True)
class AnswerResult:
    question: str
    answer: str
    used_context_chars: int
    model: str


def build_context(hits: List[RetrievedChunk], max_context_chars: int = 6000) -> str:
    """
    Build a context string that is readable and citation-friendly.
    We include source + chunk id headers so the model can reference them,
    and to keep human debugging easy.
    """
    parts: List[str] = []
    used = 0

    for hit in hits:
        c = hit.chunk
        header = f"[SOURCE: {c.source} | CHUNK: chunk_{c.chunk_index:04d} | SCORE: {hit.score:.4f}]"
        body = c.text.strip()

        block = header + "\n" + body + "\n"
        if used + len(block) > max_context_chars:
            # add a truncated final block if there's room
            remaining = max_context_chars - used
            if remaining > len(header) + 20:
                parts.append((header + "\n" + body)[:remaining] + "\n")
                used = max_context_chars
            break

        parts.append(block)
        used += len(block)

    return "".join(parts)


class HRAnswerer:
    def __init__(self, *, openai_api_key: str, chat_model: str):
        self.oai = OpenAI(api_key=openai_api_key)
        self.chat_model = chat_model

    def answer(
        self,
        *,
        question: str,
        hits: List[RetrievedChunk],
        max_context_chars: int = 6000,
        temperature: float = 0.0,
    ) -> AnswerResult:
        question = question.strip()
        if not question:
            raise ValueError("Question is empty.")

        context = build_context(hits, max_context_chars=max_context_chars)

        user_prompt = HR_USER_PROMPT_TEMPLATE.format(question=question, context=context)

        resp = self.oai.chat.completions.create(
            model=self.chat_model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": HR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = (resp.choices[0].message.content or "").strip()

        return AnswerResult(
            question=question,
            answer=text,
            used_context_chars=len(context),
            model=self.chat_model,
        )