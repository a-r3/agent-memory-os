"""Future worker for policy, trust, and hygiene auditing."""

from __future__ import annotations

from typing import Dict, Optional

from brain.api.memory_api import MemoryAPI


class PolicyAuditWorker:
    """Bundle policy-relevant trust, hygiene, and tiering signals."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def run(self) -> Dict[str, object]:
        """Return a consolidated audit bundle."""
        return {
            "trust": self.memory_api.trust_report(),
            "health": self.memory_api.memory_health_report(),
            "tiers": self.memory_api.memory_tier_report(),
        }
