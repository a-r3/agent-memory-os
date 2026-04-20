"""Future approval planning for controlled memory writes."""

from __future__ import annotations

from typing import Any, Dict, Optional

from brain.api.memory_api import MemoryAPI


class ApprovalPlanner:
    """Evaluate whether a proposed write should require explicit approval."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()

    def evaluate(self, *, payload_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return a non-destructive approval recommendation."""
        validation = self.memory_api.trust_service.validate_write_payload(
            payload_type=payload_type,
            payload=payload,
        )
        requires_approval = bool(validation["warnings"] or validation["blockers"])
        return {
            "payload_type": payload_type,
            "requires_approval": requires_approval,
            "validation": validation,
        }
