"""
trip_llm.py
───────────
The one place where Trip Buddy picks its AI model. Every lesson imports make_llm() from here.

We use Groq: it has a FREE tier (no credit card) and speaks the same API as OpenAI,
so we keep using LangChain's ChatOpenAI and only change the address and the key.

Setup
    1. Get a free key at https://console.groq.com/keys
    2. cp .env.example .env   and paste it as GROQ_API_KEY

Want another provider? Any OpenAI-compatible service works. Set these in .env:
    LLM_BASE_URL   e.g. http://localhost:11434/v1 for Ollama (local, no key needed)
    LLM_MODEL      a model on that service that supports tool calling
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")   # free on Groq, supports tool calling
API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")

# ── Token limits (save your free Groq quota) ──────────────────────────────────
# MAX_TOKENS  most tokens the model may produce in ONE reply (thinking + answer)
# MAX_STEPS   most model calls per question in the agent loop (each tool round = 1 step)
MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1000"))
MAX_STEPS = int(os.getenv("LLM_MAX_STEPS", "6"))


def make_llm() -> ChatOpenAI:
    """Return a chat model. temperature=0 keeps answers steady between runs."""
    if not API_KEY and "localhost" not in BASE_URL:
        raise SystemExit(
            "No API key found. Get a free one at https://console.groq.com/keys "
            "and put GROQ_API_KEY=... in your .env file."
        )
    extra = {}
    if "gpt-oss" in MODEL:
        # gpt-oss "thinks" before answering; low effort = fewer thinking tokens
        extra["reasoning_effort"] = "low"
    return ChatOpenAI(model=MODEL, base_url=BASE_URL, api_key=API_KEY or "not-needed",
                      temperature=0, max_tokens=MAX_TOKENS, **extra)
