"""Canonical event model for Agent Memory OS."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Dict, Optional


class Event:
    """
    Structured event record for audit and episodic continuity.

    Events are not injected directly into prompt context. They remain a durable
    execution log that can later support traceability, debugging, and replay.
    """

    def __init__(
        self,
        id: str,
        kind: str,
        agent: str,
        action: str,
        *,
        task_id: str = "",
        inputs: Optional[Dict[str, Any]] = None,
        outputs: Optional[Dict[str, Any]] = None,
        status: str = "success",
        created_at: Optional[str] = None,
    ) -> None:
        self.id = id
        self.kind = kind
        self.agent = agent
        self.action = action
        self.task_id = task_id
        self.inputs = inputs or {}
        self.outputs = outputs or {}
        self.status = status
        self.created_at = created_at or datetime.now(UTC).isoformat()
