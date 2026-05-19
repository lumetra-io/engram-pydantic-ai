# engram-pydantic-ai

[PydanticAI](https://github.com/pydantic/pydantic-ai) integration for [Engram](https://lumetra.io) — durable memory tools for the Pydantic team's typed-agent framework.

A single `register_engram_tools(agent, bucket=...)` call adds two tools (`engram_store_memory`, `engram_query_memory`) to your PydanticAI `Agent`, bound to a single hosted Engram bucket. The agent gains persistent cross-session memory with hybrid retrieval.

## Install

```bash
pip install lumetra-engram pydantic-ai
```

Vendor `engram_pydantic_ai.py` from this repo (~45 LOC). PyPI release coming.

```bash
export ENGRAM_API_KEY="eng_live_..."
```

## Get an Engram API key

Sign up at <https://lumetra.io> — free tier, no card. You'll see an `eng_live_…` token in your dashboard.

**Don't forget BYOK** — Engram is bring-your-own-key end-to-end for the LLM that does extraction + synthesis. Configure a provider at <https://lumetra.io/models>. DeepSeek is what we recommend. Without one, store/query returns HTTP 412.

## Usage

```python
from pydantic_ai import Agent
from engram_pydantic_ai import register_engram_tools

agent = Agent("openai:gpt-4o-mini", instructions="""
You are a helpful assistant with durable memory. Before answering
questions about prior context, call engram_query_memory. When the
user shares a fact worth remembering, call engram_store_memory.
""")

register_engram_tools(agent, bucket="my-agent")

result = await agent.run("My name is Jacob, please remember that.")
# In a separate process / session:
result = await agent.run("What is my name?")
print(result.output)  # The agent will have called engram_query_memory first.
```

The agent's tool palette now includes:

- `engram_store_memory(content)` — save an atomic fact.
- `engram_query_memory(question)` — hybrid retrieval + synthesized answer.

## Why this beats in-process state

- **Persists across runs and processes.** PydanticAI `Agent` instances are stateless across calls; Engram is hosted and durable.
- **Hybrid retrieval** — BM25 + vector + knowledge graph fusion, not vector-only.
- **Bring-your-own-LLM** for Engram's extraction and synthesis layer (<https://lumetra.io/models>).
- **Per-user / per-session buckets** — call `register_engram_tools(agent, bucket=f"user-{user_id}")` per request.

## Verified

Smoke-tested against live `api.lumetra.io` with PydanticAI's `TestModel` as the LLM (to keep the smoke independent of any paid provider):

- `register_engram_tools(agent, bucket="...")` runs without error.
- Direct client store + query round-trips: 2 memories stored, query "How are tools registered on a PydanticAI agent?" returns `"@agent.tool_plain decorator."` with `memories_found=2`.

For end-to-end agent-loop verification swap `TestModel` for a real model — Engram's `BYOK` provider key is consumed inside Engram for extraction/synthesis; PydanticAI's model client is consumed for the agent loop itself, so they can be (and usually are) different keys.

## License

MIT — Lumetra
