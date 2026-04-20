"""Decision-focused compatibility helpers over the canonical memory API."""

from __future__ import annotations

from typing import Any, Dict, Optional

from brain.api.memory_api import MemoryAPI


class DecisionsAPI:
    """Focused decision access wrapper that preserves the canonical API path."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def register(self, decision: Dict[str, Any]) -> str:
        """Register a decision through the canonical memory API."""
        return self.memory_api.register_decision(decision)
