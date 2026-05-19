"""
engram_pydantic_ai — durable memory tools for PydanticAI agents.

Returns a registrar that adds two Engram-backed tools (`engram_store_memory`,
`engram_query_memory`) to any PydanticAI Agent, bound to a single bucket.

Usage:

    from pydantic_ai import Agent
    from engram_pydantic_ai import register_engram_tools

    agent = Agent("openai:gpt-4o-mini", instructions="...")
    register_engram_tools(agent, bucket="my-agent")
"""

from __future__ import annotations

import os
from typing import Optional

from pydantic_ai import Agent
from lumetra_engram import EngramClient


def register_engram_tools(
    agent: Agent,
    bucket: str,
    *,
    client: Optional[EngramClient] = None,
) -> EngramClient:
    """Register Engram-backed memory tools on `agent`. Returns the client
    so callers can also drive Engram directly outside of the agent loop.
    """
    c = client or EngramClient(api_key=os.environ.get("ENGRAM_API_KEY"))

    @agent.tool_plain
    def engram_store_memory(content: str) -> str:
        """Save an atomic fact to durable memory the agent can recall later.

        Args:
            content: One declarative fact, e.g. "User prefers dark mode."
        """
        r = c.store_memory(content, bucket)
        return f"stored {r.get('memory_id', '(unknown)')}"

    @agent.tool_plain
    def engram_query_memory(question: str) -> str:
        """Semantic + graph search over stored memories. Returns a
        synthesized answer that cites the relevant memories.
        """
        r = c.query(question, buckets=[bucket])
        ans = r.get("answer") or ""
        return ans.split("FINAL ANSWER:")[-1].strip() or "No memories found."

    return c
