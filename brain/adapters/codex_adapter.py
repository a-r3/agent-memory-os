"""
Codex adapter scaffold for Agent Memory OS.

This adapter models the intended agent workflow:

1. request a compact ``context_pack`` from the MCP layer
2. execute the task using compiled context
3. write back a structured session delta
4. register any decisions separately

The implementation here is intentionally minimal. It is importable and runnable,
but execution and writeback are still stubs until real agent/runtime and storage
integrations are added.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from uuid import uuid4

from mcp.tools import MemoryTools


class CodexAdapter:
    """
    Minimal Codex memory-client adapter.

    The adapter depends on ``MemoryTools`` rather than talking directly to the
    compiler or storage. This preserves the architecture boundary where MCP is
    the integration surface and ``ContextCompiler`` remains behind that API.
    """

    agent_name = "codex"

    def __init__(
        self,
        memory_tools: Optional[MemoryTools] = None,
        *,
        budget_tokens: int = 1200,
        memory_scope: Optional[List[str]] = None,
        repo_scope: Optional[List[str]] = None,
    ) -> None:
        self.memory_tools = memory_tools or MemoryTools()
        self.budget_tokens = budget_tokens
        self.memory_scope = memory_scope
        self.repo_scope = repo_scope

    def execute_task(self, task: str, agent_id: str) -> Dict[str, Any]:
        """
        Execute a Codex task using compiled memory context.

        The adapter asks MCP for a ``context_pack`` rather than constructing
        prompt context itself. This keeps token budgeting, status filtering, and
        pack assembly centralized in ``MemoryTools.context_compile`` and the
        underlying ``ContextCompiler``.
        """
        if not isinstance(task, str) or not task.strip():
            raise ValueError("task must be a non-empty string")
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise ValueError("agent_id must be a non-empty string")

        context_pack = self.memory_tools.context_compile(
            agent=self.agent_name,
            task=task,
            budget_tokens=self.budget_tokens,
            memory_scope=self.memory_scope,
            repo_scope=self.repo_scope,
        )
        context_diagnostics = self.memory_tools.context_budget_report(context_pack)
        runtime_payload = self.memory_tools.runtime_payload_preview(
            agent=self.agent_name,
            task=task,
            context_pack=context_pack,
        )

        execution_result = self._run_task_stub(task=task, agent_id=agent_id, context_pack=context_pack)
        session_delta = self._build_session_delta(task=task, agent_id=agent_id, execution_result=execution_result)
        decisions = self._build_decision_payloads(task=task, agent_id=agent_id, execution_result=execution_result)
        writeback = self._writeback(session_delta=session_delta, decisions=decisions)

        return {
            "agent": self.agent_name,
            "agent_id": agent_id,
            "task": task,
            "context_pack": context_pack,
            "context_diagnostics": context_diagnostics,
            "runtime_payload": runtime_payload,
            "execution": execution_result,
            "writeback": writeback,
        }

    def _run_task_stub(self, *, task: str, agent_id: str, context_pack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stub execution hook for future Codex runtime integration.

        Real implementations can replace this with prompt submission, tool use,
        and result parsing. The scaffold returns enough structure to exercise the
        writeback path without embedding any model-specific behavior yet.
        """
        return {
            "status": "pending_implementation",
            "agent_id": agent_id,
            "task": task,
            "summary": "Codex task execution stub ran with compiled context.",
            "consumed_packs": {
                pack_name: len(context_pack.get(pack_name, []))
                for pack_name in ("rules_pack", "identity_pack", "knowledge_pack", "recent_pack", "tools_pack")
            },
            "artifacts": [],
            "decisions": [],
            "open_questions": [
                "Connect Codex runtime invocation to this adapter.",
            ],
            "next_actions": [
                "Replace execution stub with real Codex task orchestration.",
            ],
        }

    def _build_session_delta(
        self,
        *,
        task: str,
        agent_id: str,
        execution_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build a structured delta suitable for ``session_delta_write``."""
        return {
            "id": f"session_delta:{uuid4()}",
            "session_id": f"{self.agent_name}:{agent_id}",
            "task": task,
            "new_facts": [],
            "changed_facts": [],
            "decisions": execution_result.get("decisions", []),
            "artifacts": execution_result.get("artifacts", []),
            "open_questions": execution_result.get("open_questions", []),
            "next_actions": execution_result.get("next_actions", []),
            "created_at": datetime.now(UTC).isoformat(),
        }

    def _build_decision_payloads(
        self,
        *,
        task: str,
        agent_id: str,
        execution_result: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Build MCP decision payloads.

        The scaffold maps any execution-emitted decisions into the MCP contract.
        The default stub emits none, but the method is present so future runtime
        code has an obvious place to translate model outputs into durable records.
        """
        payloads: List[Dict[str, Any]] = []
        for index, decision_text in enumerate(execution_result.get("decisions", []), start=1):
            payloads.append(
                {
                    "id": f"decision:{uuid4()}",
                    "kind": "decision",
                    "title": f"Codex decision {index}",
                    "decision": decision_text,
                    "status": "draft",
                    "rationale": "",
                    "affects": [],
                    "owner": agent_id,
                    "source_refs": [task],
                }
            )
        return payloads

    def _writeback(self, *, session_delta: Dict[str, Any], decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Attempt structured writeback through MCP tools.

        MCP now delegates writeback through the canonical in-memory backend, so
        successful adapter runs should produce real delta and decision ids even
        though task execution itself remains a stub.
        """
        session_delta_result = self._safe_session_delta_write(session_delta)
        decision_results = [self._safe_decision_register(decision) for decision in decisions]
        return {
            "session_delta": session_delta_result,
            "decisions": decision_results,
        }

    def _safe_session_delta_write(self, delta: Dict[str, Any]) -> Dict[str, Any]:
        delta_id = self.memory_tools.session_delta_write(delta)
        return {
            "status": "written",
            "delta_id": delta_id,
        }

    def _safe_decision_register(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        decision_id = self.memory_tools.decision_register(decision)
        return {
            "status": "written",
            "decision_id": decision_id,
        }
