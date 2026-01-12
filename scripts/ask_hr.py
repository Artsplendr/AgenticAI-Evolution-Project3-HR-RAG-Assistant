from __future__ import annotations

import argparse
import os

from hr_rag_assistant.config import get_settings
from hr_rag_assistant.retrieval.retriever import HRRetriever
from hr_rag_assistant.generation.answerer import HRAnswerer
from hr_rag_assistant.generation.citations import format_sources_block


def _print_hits(result, max_chars: int = 350) -> None:
    if not result.results:
        print("\nNo chunks retrieved.")
        return

    print("\n== Retrieved Context ==")
    for i, hit in enumerate(result.results, start=1):
        c = hit.chunk
        snippet = c.text.replace("\n", " ").strip()
        if len(snippet) > max_chars:
            snippet = snippet[:max_chars] + "..."

        print(f"\n[{i}] score={hit.score:.4f}  source={c.source}  id={c.id}")
        print(f"    {snippet}")


def main() -> None:
    parser = argparse.ArgumentParser(description="HR RAG Assistant — Retrieve + Answer (FAISS)")
    parser.add_argument("question", type=str, help="HR question to answer")
    parser.add_argument("--top-k", type=int, default=5, help="Number of chunks to retrieve")
    parser.add_argument("--show-context", action="store_true", help="Print retrieved chunks")
    parser.add_argument("--max-context-chars", type=int, default=None, help="Max characters of context fed to the model")
    parser.add_argument("--temperature", type=float, default=0.0, help="Model temperature")

    args = parser.parse_args()

    s = get_settings()
    chat_model = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
    strict_grounded = os.getenv("STRICT_GROUNDED", "true").strip().lower() in {"1", "true", "yes", "y"}
    max_context_chars = args.max_context_chars if args.max_context_chars is not None else int(
        os.getenv("MAX_CONTEXT_CHARS", "6000")
    )

    print("== HR RAG (FAISS) ==")
    print(f"Using INDEX_DIR: {s.index_dir}")
    print(f"Embedding model: {s.embedding_model}")
    print(f"Chat model:      {chat_model}")
    print(f"Top-K:           {args.top_k}")
    print(f"Strict grounded: {strict_grounded}")
    print(f"Max context:     {max_context_chars} chars")

    # 1) Retrieve
    retriever = HRRetriever(
        index_dir=s.index_dir,
        openai_api_key=s.openai_api_key,
        embedding_model=s.embedding_model,
    )

    retrieval = retriever.retrieve(args.question, top_k=args.top_k)

    print("\nQuestion:")
    print(retrieval.query)

    if args.show_context:
        _print_hits(retrieval)

    # Optional strict gating:
    # If nothing retrieved, or similarity is too low, refuse.
    if strict_grounded:
        if not retrieval.results:
            print("\nAnswer:")
            print("I don't know based on the provided HR documents.")
            print("\nSources:\n- (none)")
            return

    # 2) Answer (grounded)
    answerer = HRAnswerer(openai_api_key=s.openai_api_key, chat_model=chat_model)
    ans = answerer.answer(
        question=retrieval.query,
        hits=retrieval.results,
        max_context_chars=max_context_chars,
        temperature=args.temperature,
    )

    print("\nAnswer:")
    print(ans.answer)

    # 3) Sources (human-facing)
    print("\n" + format_sources_block(retrieval.results))


if __name__ == "__main__":
    main()