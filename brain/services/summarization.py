"""
Deterministic summarization and compression helpers for Agent Memory OS.

This service supports later-phase optimization work without changing the
canonical ``context_pack`` schema. It provides:

- stable compression of already compiled context packs
- cache-friendly runtime payload assembly for adapters

The implementation stays heuristic and dependency-free so it remains suitable
for local testing and predictable smoke runs.
"""

from __future__ import annotations

from hashlib import sha256
from typing import Any, Callable, Dict, List, Mapping, Optional

from brain.services.context_compiler import estimate_tokens, trim_text_to_token_budget


COMPRESS_PRIORITY = (
    "tools_pack",
    "recent_pack",
    "knowledge_pack",
    "identity_pack",
    "rules_pack",
)

PAYLOAD_PACK_ORDER = (
    "rules_pack",
    "identity_pack",
    "knowledge_pack",
    "recent_pack",
    "tools_pack",
)


class SummarizationService:
    """Compression and runtime payload helpers for Phase 9+ optimization work."""

    def __init__(self, token_estimator: Optional[Callable[[str], int]] = None) -> None:
        self.token_estimator = token_estimator or estimate_tokens

    def compress_context_pack(
        self,
        context_pack: Mapping[str, Any],
        *,
        max_total_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Return a schema-shaped compressed copy of a context pack.

        Compression works from lowest-priority pack to highest-priority pack so
        stable reusable guidance is preserved as long as possible.
        """
        compressed = {
            "id": context_pack["id"],
            "agent": context_pack["agent"],
            "task": context_pack["task"],
            "rules_pack": list(context_pack.get("rules_pack", [])),
            "identity_pack": list(context_pack.get("identity_pack", [])),
            "knowledge_pack": list(context_pack.get("knowledge_pack", [])),
            "recent_pack": list(context_pack.get("recent_pack", [])),
            "tools_pack": list(context_pack.get("tools_pack", [])),
            "limits": dict(context_pack.get("limits") or {}),
        }

        resolved_max_total_tokens = int(max_total_tokens or compressed["limits"].get("max_total_tokens") or 0)
        resolved_max_output_tokens = int(compressed["limits"].get("max_output_tokens") or 0)
        if resolved_max_total_tokens > 0:
            compressed["limits"]["max_total_tokens"] = resolved_max_total_tokens

        input_budget = max(0, resolved_max_total_tokens - resolved_max_output_tokens)
        if input_budget <= 0:
            return compressed

        while self._estimate_pack_tokens(compressed) > input_budget:
            changed = False
            for pack_name in COMPRESS_PRIORITY:
                pack_items = compressed[pack_name]
                if not pack_items:
                    continue
                largest_index = max(range(len(pack_items)), key=lambda idx: self.token_estimator(pack_items[idx]))
                original = pack_items[largest_index]
                original_tokens = self.token_estimator(original)
                if original_tokens <= 1:
                    pack_items.pop(largest_index)
                    changed = True
                    break

                target_tokens = max(1, original_tokens // 2)
                trimmed = trim_text_to_token_budget(original, target_tokens, estimator=self.token_estimator)
                if trimmed and trimmed != original:
                    pack_items[largest_index] = trimmed
                else:
                    pack_items.pop(largest_index)
                changed = True
                if self._estimate_pack_tokens(compressed) <= input_budget:
                    break
            if not changed:
                break

        return compressed

    def build_runtime_payload(
        self,
        *,
        agent: str,
        task: str,
        context_pack: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """
        Build a cache-friendly runtime payload for adapter execution.

        The payload is stable in ordering and separates reusable context from
        task-local content so future real runtimes can reuse the same assembly
        contract without each adapter rebuilding prompt text independently.
        """
        sections: List[Dict[str, Any]] = []
        for pack_name in PAYLOAD_PACK_ORDER:
            items = [item for item in context_pack.get(pack_name, []) if isinstance(item, str)]
            if not items:
                continue
            sections.append(
                {
                    "name": pack_name,
                    "items": items,
                    "estimated_tokens": sum(self.token_estimator(item) for item in items),
                }
            )

        stable_cache_material = "\n".join(
            "\n".join(context_pack.get(pack_name, []))
            for pack_name in ("rules_pack", "identity_pack", "tools_pack")
        )
        runtime_prompt = "\n\n".join(
            [f"[{section['name']}]\n" + "\n".join(section["items"]) for section in sections]
            + [f"[task]\n{task}"]
        )

        return {
            "agent": agent,
            "task": task,
            "sections": sections,
            "cache_key": sha256(stable_cache_material.encode("utf-8")).hexdigest(),
            "estimated_tokens": self.token_estimator(runtime_prompt),
            "prompt": runtime_prompt,
        }

    def _estimate_pack_tokens(self, context_pack: Mapping[str, Any]) -> int:
        return sum(
            self.token_estimator(item)
            for pack_name in PAYLOAD_PACK_ORDER
            for item in context_pack.get(pack_name, [])
            if isinstance(item, str)
        )
