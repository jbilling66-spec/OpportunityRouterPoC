"""Model config. Claude as the reasoning engine; a separate (ideally stronger) judge for evals."""
from __future__ import annotations
from langchain_anthropic import ChatAnthropic

AGENT_MODEL = "claude-sonnet-4-6"
JUDGE_MODEL = "claude-sonnet-4-6"  # bump to claude-opus-4-8 for a tougher grader

def get_agent_llm(temperature: float = 0.0) -> ChatAnthropic:
    return ChatAnthropic(model=AGENT_MODEL, temperature=temperature, max_tokens=2000)

def get_judge_llm() -> ChatAnthropic:
    return ChatAnthropic(model=JUDGE_MODEL, temperature=0.0, max_tokens=1000)
