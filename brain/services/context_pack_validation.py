"""
Validation helpers for ``context_pack`` payloads.

The MVP currently validates schema compliance without introducing a runtime
dependency on external JSON Schema libraries. This module centralizes that
logic so MCP and future tools can enforce the same contract consistently.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ContextPackValidator:
    """
    Minimal validator for ``schemas/context_pack.schema.json``.

    The validator loads the repository schema for traceability, then performs
    the concrete structural checks needed by the current MVP implementation.
    """

    def __init__(self, schema_path: Path | None = None) -> None:
        self.schema_path = schema_path or Path(__file__).resolve().parents[2] / "schemas" / "context_pack.schema.json"
        self.schema = json.loads(self.schema_path.read_text(encoding="utf-8"))

    def validate(self, context_pack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a context pack against the current schema contract.

        The schema marks some packs as optional. The implementation requires
        them to exist as arrays so agent consumers always receive a stable
        output shape.
        """
        required_keys = {
            "id",
            "agent",
            "task",
            "rules_pack",
            "identity_pack",
            "knowledge_pack",
            "recent_pack",
            "tools_pack",
            "limits",
        }
        if set(context_pack.keys()) != required_keys:
            raise ValueError(
                "context_pack keys do not match the implementation contract: "
                f"{sorted(context_pack.keys())}"
            )

        for field_name in ("id", "agent", "task"):
            value = context_pack.get(field_name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"context_pack.{field_name} must be a non-empty string")

        for pack_name in ("rules_pack", "identity_pack", "knowledge_pack", "recent_pack", "tools_pack"):
            pack = context_pack.get(pack_name)
            if not isinstance(pack, list) or not all(isinstance(item, str) for item in pack):
                raise ValueError(f"context_pack.{pack_name} must be a list[str]")

        limits = context_pack.get("limits")
        if not isinstance(limits, dict):
            raise ValueError("context_pack.limits must be an object")
        if set(limits.keys()) != {"max_total_tokens", "max_output_tokens"}:
            raise ValueError("context_pack.limits must contain max_total_tokens and max_output_tokens")
        if not isinstance(limits["max_total_tokens"], int) or limits["max_total_tokens"] <= 0:
            raise ValueError("context_pack.limits.max_total_tokens must be a positive integer")
        if not isinstance(limits["max_output_tokens"], int) or limits["max_output_tokens"] <= 0:
            raise ValueError("context_pack.limits.max_output_tokens must be a positive integer")
        if limits["max_output_tokens"] > limits["max_total_tokens"]:
            raise ValueError("context_pack.limits.max_output_tokens cannot exceed max_total_tokens")

        return context_pack
