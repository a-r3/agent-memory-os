"""Token-budget compression helpers for compiled context packs."""

from __future__ import annotations

from typing import Any, Dict

from brain.api.memory_api import MemoryAPI


class TokenCompressor:
    """Compress compiled context packs while preserving schema compliance."""

    def __init__(self, memory_api: MemoryAPI) -> None:
        self.memory_api = memory_api

    def compress(self, context_pack: Dict[str, Any], *, max_total_tokens: int) -> Dict[str, Any]:
        """Return an optimized pack plus updated diagnostics."""
        optimized = self.memory_api.optimize_context_pack(
            context_pack,
            max_total_tokens=max_total_tokens,
        )
        return {
            "context_pack": optimized,
            "budget_report": self.memory_api.analyze_context_pack(optimized),
        }
