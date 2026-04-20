"""Context-focused compatibility helpers over the canonical memory API."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from brain.api.memory_api import MemoryAPI


class ContextAPI:
    """Focused context API wrapper for compiler-facing callers."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def compile(
        self,
        *,
        agent: str,
        task: str,
        budget_tokens: int,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """Compile a schema-shaped context pack through the canonical API."""
        return self.memory_api.compile_context(
            agent=agent,
            task=task,
            budget_tokens=budget_tokens,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
