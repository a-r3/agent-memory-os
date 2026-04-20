"""
Budget planning and diagnostics for compiled context packs.

This service extends the existing token-budget discipline with reusable
planning and analysis helpers. It does not change the canonical
``context_pack`` schema; instead, it provides diagnostics that can be exposed
through ``MemoryAPI`` and MCP as a separate tool path.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
import re
from typing import Any, Callable, Mapping, Optional


@dataclass(frozen=True)
class BudgetPlan:
    """Resolved token budget split for one compilation request."""

    max_total_tokens: int
    max_output_tokens: int
    max_input_tokens: int
    reserved_output_ratio: float


class BudgetingService:
    """Plan and inspect token budgets without changing compiler output shape."""

    def __init__(
        self,
        *,
        reserved_output_ratio: float = 0.35,
        minimum_output_tokens: int = 256,
        minimum_input_tokens: int = 128,
        token_estimator: Optional[Callable[[str], int]] = None,
    ) -> None:
        self.reserved_output_ratio = reserved_output_ratio
        self.minimum_output_tokens = minimum_output_tokens
        self.minimum_input_tokens = minimum_input_tokens
        self.token_estimator = token_estimator or self.estimate_tokens

    def resolve_budget(self, *, budget_tokens: int, requested_output_tokens: Optional[int] = None) -> BudgetPlan:
        """Resolve input/output budget limits using the same policy as the compiler."""
        if budget_tokens <= 0:
            raise ValueError("budget_tokens must be positive")

        if requested_output_tokens is not None:
            if requested_output_tokens <= 0:
                raise ValueError("requested_output_tokens must be positive when provided")
            max_output_tokens = min(requested_output_tokens, budget_tokens)
        else:
            derived = int(budget_tokens * self.reserved_output_ratio)
            max_output_tokens = max(self.minimum_output_tokens, min(derived, budget_tokens))

        max_input_tokens = max(self.minimum_input_tokens, budget_tokens - max_output_tokens)
        return BudgetPlan(
            max_total_tokens=budget_tokens,
            max_output_tokens=max_output_tokens,
            max_input_tokens=max_input_tokens,
            reserved_output_ratio=self.reserved_output_ratio,
        )

    def analyze_context_pack(self, context_pack: Mapping[str, Any]) -> dict[str, Any]:
        """
        Estimate token usage for a compiled context pack.

        The returned diagnostics are separate from the canonical pack so schema
        compliance is preserved while agents and tests still gain visibility
        into cost control behavior.
        """
        limits = dict(context_pack.get("limits") or {})
        max_total_tokens = int(limits.get("max_total_tokens") or 0)
        max_output_tokens = int(limits.get("max_output_tokens") or 0)
        max_input_tokens = max(0, max_total_tokens - max_output_tokens)

        pack_tokens = {
            pack_name: sum(self.token_estimator(item) for item in context_pack.get(pack_name, []) if isinstance(item, str))
            for pack_name in ("rules_pack", "identity_pack", "knowledge_pack", "recent_pack", "tools_pack")
        }
        total_input_tokens = sum(pack_tokens.values())
        recommendations: list[str] = []

        if max_input_tokens and total_input_tokens > max_input_tokens:
            recommendations.append("trim_context_candidates")
        if pack_tokens.get("knowledge_pack", 0) > max(1, total_input_tokens // 2):
            recommendations.append("compress_knowledge_pack_first")
        if pack_tokens.get("recent_pack", 0) > pack_tokens.get("rules_pack", 0) + pack_tokens.get("identity_pack", 0):
            recommendations.append("prefer_recent_delta_summaries_over_raw_volume")

        return {
            "within_input_budget": total_input_tokens <= max_input_tokens if max_input_tokens else True,
            "max_total_tokens": max_total_tokens,
            "max_output_tokens": max_output_tokens,
            "max_input_tokens": max_input_tokens,
            "estimated_input_tokens": total_input_tokens,
            "pack_tokens": pack_tokens,
            "remaining_input_tokens": max(0, max_input_tokens - total_input_tokens),
            "recommendations": recommendations,
        }

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Approximate tokens conservatively without external tokenizer dependencies."""
        if not text:
            return 0
        compact = re.sub(r"\s+", " ", text.strip())
        if not compact:
            return 0
        return max(1, ceil(len(compact) / 4))
