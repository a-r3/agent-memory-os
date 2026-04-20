"""Future packer for transport-neutral runtime payloads."""

from __future__ import annotations

from typing import Any, Dict

from brain.api.memory_api import MemoryAPI


class RuntimePayloadPacker:
    """Build a runtime payload from an existing schema-valid context pack."""

    def __init__(self, memory_api: MemoryAPI) -> None:
        self.memory_api = memory_api

    def pack(self, *, agent: str, task: str, context_pack: Dict[str, Any]) -> Dict[str, Any]:
        """Return the canonical runtime payload preview plus trust and budget context."""
        return {
            "runtime_payload": self.memory_api.build_runtime_payload(
                agent=agent,
                task=task,
                context_pack=context_pack,
            ),
            "budget_report": self.memory_api.analyze_context_pack(context_pack),
            "trust_report": self.memory_api.trust_report(types=["memory_entry", "decision"]),
        }
