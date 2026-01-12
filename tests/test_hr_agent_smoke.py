from __future__ import annotations

from src.hr_rag_assistant.agent import HRAgent
from src.hr_rag_assistant.config import load_config
from src.hr_rag_assistant.retrieval.prompts import HR_INSTRUCTION


def test_hr_agent_smoke() -> None:
    config = load_config()
    agent = HRAgent(config=config)
    res = agent.ask("How many PTO days do I get?")
    assert hasattr(res, "answer")
    assert hasattr(res, "citations")
    assert isinstance(res.answer, str)
    assert isinstance(res.citations, list)
    # In placeholder mode, answer should include the instruction prefix
    assert HR_INSTRUCTION.split(".")[0] in res.answer

