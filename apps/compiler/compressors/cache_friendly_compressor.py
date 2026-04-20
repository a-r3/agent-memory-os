"""Future compressor for cache-friendly stable prompt ordering."""

from __future__ import annotations

from typing import Any, Dict

from brain.api.memory_api import MemoryAPI


class CacheFriendlyCompressor:
    """Optimize a context pack for smaller stable sections and better reuse."""

    def __init__(self, memory_api: MemoryAPI) -> None:
        self.memory_api = memory_api

    def compress(self, *, context_pack: Dict[str, Any], max_total_tokens: int) -> Dict[str, Any]:
        """Return an optimized pack and its derived runtime payload."""
        optimized = self.memory_api.optimize_context_pack(
            context_pack,
            max_total_tokens=max_total_tokens,
        )
        return {
            "context_pack": optimized,
            "runtime_payload": self.memory_api.build_runtime_payload(
                agent=optimized["agent"],
                task=optimized["task"],
                context_pack=optimized,
            ),
        }
