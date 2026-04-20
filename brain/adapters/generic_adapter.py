"""
Generic adapter scaffold for Agent Memory OS.

This adapter exists to preserve the architecture rule that agents are replaceable
memory clients. It follows the same workflow as the Codex and Claude adapters:

1. request a compiled context pack through MCP
2. execute a task using that compact context
3. write back a structured session delta
4. register any decisions separately

The adapter does not implement provider-specific runtime logic. It is a thin
contract for future automation runtimes, orchestration layers, and custom
integrations.
"""

from __future__ import annotations

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
from uuid import uuid4

from mcp.tools import MemoryTools


class GenericAdapter:
    """Minimal generic memory-client adapter."""

    def __init__(
        self,
        agent_name: str = "generic",
        memory_tools: Optional[MemoryTools] = None,
        *,
        budget_tokens: int = 1200,
        memory_scope: Optional[List[str]] = None,
        repo_scope: Optional[List[str]] = None,
    ) -> None:
        if not isinstance(agent_name, str) or not agent_name.strip():
            raise ValueError("agent_name must be a non-empty string")
        self.agent_name = agent_name.strip()
        self.memory_tools = memory_tools or MemoryTools()
        self.budget_tokens = budget_tokens
        self.memory_scope = memory_scope
        self.repo_scope = repo_scope

    def execute_task(self, task: str, agent_id: str) -> Dict[str, Any]:
        """Execute a task using MCP-compiled context and structured writeback."""
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

        return {
            "agent": self.agent_name,
            "agent_id": agent_id,
            "task": task,
            "context_pack": context_pack,
            "context_diagnostics": context_diagnostics,
            "runtime_payload": runtime_payload,
            "execution": execution_result,
            "writeback": {
                "session_delta": self._safe_session_delta_write(session_delta),
                "decisions": [self._safe_decision_register(decision) for decision in decisions],
            },
        }

    def _run_task_stub(self, *, task: str, agent_id: str, context_pack: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder execution hook for future non-provider-specific runtimes."""
        return {
            "status": "pending_implementation",
            "agent_id": agent_id,
            "task": task,
            "summary": f"{self.agent_name} task execution stub ran with compiled context.",
            "consumed_packs": {
                pack_name: len(context_pack.get(pack_name, []))
                for pack_name in ("rules_pack", "identity_pack", "knowledge_pack", "recent_pack", "tools_pack")
            },
            "artifacts": [],
            "decisions": [],
            "open_questions": ["Connect runtime-specific execution to the generic adapter."],
            "next_actions": ["Replace execution stub with orchestration-specific logic."],
        }

    def _build_session_delta(
        self,
        *,
        task: str,
        agent_id: str,
        execution_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build a structured session delta payload for MCP writeback."""
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
        """Map execution-emitted decision strings into MCP decision payloads."""
        payloads: List[Dict[str, Any]] = []
        for index, decision_text in enumerate(execution_result.get("decisions", []), start=1):
            payloads.append(
                {
                    "id": f"decision:{uuid4()}",
                    "kind": "decision",
                    "title": f"{self.agent_name} decision {index}",
                    "decision": decision_text,
                    "status": "draft",
                    "rationale": "",
                    "affects": [],
                    "owner": agent_id,
                    "source_refs": [task],
                }
            )
        return payloads

    def _safe_session_delta_write(self, delta: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "written",
            "delta_id": self.memory_tools.session_delta_write(delta),
        }

    def _safe_decision_register(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "written",
            "decision_id": self.memory_tools.decision_register(decision),
        }
