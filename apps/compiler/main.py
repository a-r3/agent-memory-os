"""
Compiler application scaffold for Agent Memory OS.

This module wraps the canonical ``MemoryAPI`` compilation and optimization
paths, giving later transports or worker processes a single importable entry
point for context planning, packing, and compression.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from apps.compiler.compressors.token_compressor import TokenCompressor
from apps.compiler.packers.context_packer import ContextPacker
from apps.compiler.planners.scope_planner import ScopePlanner
from brain.api.memory_api import MemoryAPI


class CompilerApp:
    """High-level context compiler facade built on canonical services."""

    def __init__(self, memory_api: Optional[MemoryAPI] = None) -> None:
        self.memory_api = memory_api or MemoryAPI()
        self.scope_planner = ScopePlanner(self.memory_api)
        self.context_packer = ContextPacker(self.memory_api)
        self.token_compressor = TokenCompressor(self.memory_api)

    def compile_for_task(self, *, agent: str, task: str, budget_tokens: int) -> Dict[str, Any]:
        """Plan scopes, compile a context pack, and attach diagnostics."""
        plan = self.scope_planner.plan(task)
        packed = self.context_packer.pack(
            agent=agent,
            task=task,
            budget_tokens=budget_tokens,
            memory_scope=plan["memory_scope"],
            repo_scope=plan["repo_scope"],
        )
        packed["runtime_payload"] = self.memory_api.build_runtime_payload(
            agent=agent,
            task=task,
            context_pack=packed["context_pack"],
        )
        return packed

    def compress_existing_pack(self, context_pack: Dict[str, Any], max_total_tokens: int) -> Dict[str, Any]:
        """Apply deterministic compression to an existing context pack."""
        return self.token_compressor.compress(context_pack, max_total_tokens=max_total_tokens)
