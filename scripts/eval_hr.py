#!/usr/bin/env python
from __future__ import annotations

import argparse
from typing import List, Tuple

from src.hr_rag_assistant.agent import HRAgent
from src.hr_rag_assistant.config import load_config
from src.hr_rag_assistant.logging import get_logger


def small_eval_suite() -> List[Tuple[str, str]]:
    # (question, must_contain_substring)
    return [
        ("How many PTO days do I get?", "PTO"),
        ("What are core hours for remote work?", "Core"),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Tiny eval harness for HR Q&A.")
    _ = parser.parse_args()

    logger = get_logger(__name__)
    config = load_config()
    agent = HRAgent(config=config, logger=logger)

    tests = small_eval_suite()
    total = len(tests)
    passed = 0
    for q, must in tests:
        res = agent.ask(q)
        ok = must.lower() in res.answer.lower()
        passed += int(ok)
        print(f"Q: {q}\nA: {res.answer}\n-> contains '{must}': {ok}\n")

    print(f"Passed {passed}/{total}")


if __name__ == "__main__":
    main()

