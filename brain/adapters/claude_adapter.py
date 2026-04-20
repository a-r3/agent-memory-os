"""
Claude adapter scaffold for Agent Memory OS.

This adapter mirrors the canonical agent workflow defined in the repository:
compiled context in, task execution, structured delta writeback, and separate
decision registration. The implementation is intentionally light so Claude can
be integrated later without changing the MCP-facing contract.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from uuid import uuid4

from mcp.tools import MemoryTools


class ClaudeAdapter:
    """
    Minimal Claude memory-client adapter.

    The adapter interacts with MCP tools rather than reaching into memory
    services directly. That keeps retrieval, budget enforcement, and context
    compilation centralized in the MCP + ContextCompiler path.
    """

    agent_name = "claude"

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
        Execute a Claude task using MCP-compiled context.

        The adapter requests ``context_pack`` from ``MemoryTools.context_compile``
        so the same budget-aware compiler path is reused across agents. This
        keeps prompt assembly deterministic and makes Claude a memory client
        rather than a memory owner.
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
        Stub execution hook for future Claude runtime integration.

        The scaffold records which packs were supplied so later tests can verify
        that the adapter is consuming MCP-compiled context without needing any
        model-provider integration yet.
        """
        return {
            "status": "pending_implementation",
            "agent_id": agent_id,
            "task": task,
            "summary": "Claude task execution stub ran with compiled context.",
            "consumed_packs": {
                pack_name: len(context_pack.get(pack_name, []))
                for pack_name in ("rules_pack", "identity_pack", "knowledge_pack", "recent_pack", "tools_pack")
            },
            "artifacts": [],
            "decisions": [],
            "open_questions": [
                "Connect Claude runtime invocation to this adapter.",
            ],
            "next_actions": [
                "Replace execution stub with real Claude task orchestration.",
            ],
        }

    def _build_session_delta(
        self,
        *,
        task: str,
        agent_id: str,
        execution_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build a structured delta payload for MCP writeback."""
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
        """Map execution-emitted decisions into MCP decision payloads."""
        payloads: List[Dict[str, Any]] = []
        for index, decision_text in enumerate(execution_result.get("decisions", []), start=1):
            payloads.append(
                {
                    "id": f"decision:{uuid4()}",
                    "kind": "decision",
                    "title": f"Claude decision {index}",
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
        Attempt structured writeback using MCP tools.

        MCP now routes writeback through the canonical in-memory backend, so
        successful adapter runs should return concrete delta and decision ids.
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
