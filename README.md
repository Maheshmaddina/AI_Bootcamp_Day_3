# Trip Buddy: AI Bootcamp Day 3

A trip-planning AI agent for a group of friends, built up step by step over 15 lessons:
SQLite → embeddings → ChromaDB → LLM chains → RAG → tool calling → multi-chain → full agent →
MCP → memory → A2A (agent-to-agent).

The AI model is **free**: [Groq](https://console.groq.com/keys) (`openai/gpt-oss-120b`), called through
LangChain's `ChatOpenAI`. Model and token limits live in one place: [`trip_llm.py`](trip_llm.py).

## Setup

```bash
uv sync                    # installs the exact versions from uv.lock
cp .env.example .env       # then paste your free Groq key as GROQ_API_KEY
```

## Lessons

| File | What it teaches | Needs key |
|---|---|---|
| `trip_01_sqlite_basics.py` | SQLite tables, JOIN, `sqlite3.Row` | no |
| `trip_02_embeddings_basics.py` | Sentence embeddings and cosine similarity | no |
| `trip_03_chromadb_retrieval.py` | Vector DB search with metadata filters | no |
| `trip_04_llm_chain.py` | Prompt template, LCEL `prompt \| llm \| parser` | yes |
| `trip_05_rag_chain.py` | Retrieve → augment → generate | yes |
| `trip_06_tool_calling.py` | `@tool`, `bind_tools`, the tool loop | yes |
| `trip_07_multi_chain.py` | Compute with a tool, then chain two LLM steps | yes |
| `trip_08_full_agent.py` | Full ReAct agent with a Gradio chat UI | yes |
| `trip_09_mcp_client_demo.py` | MCP protocol step by step (no AI) | no |
| `trip_10_mcp_agent.py` | Agent whose tools come from an MCP server | yes |
| `trip_11_memory_types.py` | Short-term, semantic, episodic, procedural memory | no |
| `trip_12_memory_pipeline.py` | Extract → classify → consolidate → store → recall | yes |
| `trip_13_memory_agent.py` | Agent that remembers your group | yes |
| `trip_14_a2a_client_demo.py` | Talk to another agent over A2A by hand | yes* |
| `trip_15_a2a_agent.py` | Agent using MCP tools and an A2A guide agent | yes* |

Supporting files: `trip_mcp_server.py` (MCP server), `trip_guide_agent.py` (A2A Local Guide agent),
`trip_memory.py` (memory system), `trip_llm.py` (model settings).

\* Start the guide agent first in a second terminal: `uv run trip_guide_agent.py`

Run any lesson with `uv run <file>`. Chat apps open at http://127.0.0.1:7860.

## Deploying (AWS, free plan)

- `Dockerfile` + `start.sh` package lesson 15 (agent + MCP server + guide agent) in one container on port 8080.
  Set `GROQ_API_KEY`, and `APP_USER` / `APP_PASSWORD` to require a login.
- It runs on an EC2 `t4g.small` behind Caddy (free HTTPS), turns itself off after 30 idle minutes,
  and [`aws/wake_lambda.py`](aws/wake_lambda.py) is the wake-up link that starts it again
  (it refuses once the monthly AWS budget is used up).
