"""Context packing helpers for the compiler app."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from brain.api.memory_api import MemoryAPI


class ContextPacker:
    """Wrap canonical context compilation and diagnostics."""

    def __init__(self, memory_api: MemoryAPI) -> None:
        self.memory_api = memory_api

    def pack(
        self,
        *,
        agent: str,
        task: str,
        budget_tokens: int,
        memory_scope: Optional[Sequence[str]] = None,
        repo_scope: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """Compile and validate a context pack with budget analysis."""
        context_pack = self.memory_api.compile_context(
            agent=agent,
            task=task,
            budget_tokens=budget_tokens,
            memory_scope=memory_scope,
            repo_scope=repo_scope,
        )
        return {
            "context_pack": context_pack,
            "budget_report": self.memory_api.analyze_context_pack(context_pack),
        }
