"""Tests for post-Phase-7 trust checks and budgeting diagnostics."""

from brain.adapters.codex_adapter import CodexAdapter
from brain.api.memory_api import MemoryAPI
from brain.services.retrieval import MemoryRetrievalBackend
from mcp.tools import MemoryTools


def test_memory_api_blocks_secret_like_memory_write() -> None:
    api = MemoryAPI(retrieval_backend=MemoryRetrievalBackend())

    try:
        api.write_memory_entry(
            {
                "kind": "rule",
                "title": "Do not store secrets",
                "summary_short": "token = sk-ABCDEFGHIJKLMNOPQRSTUV012345",
                "status": "approved",
                "source_refs": ["security.md"],
            }
        )
    except ValueError as exc:
        assert "blocked" in str(exc)
    else:
        raise AssertionError("secret-like payload should be blocked")


def test_mcp_exposes_budget_and_trust_reports() -> None:
    tools = MemoryTools(retrieval_backend=MemoryRetrievalBackend())

    context_pack = tools.context_compile(
        agent="codex",
        task="inspect budget diagnostics for context assembly",
        budget_tokens=720,
        memory_scope=["rule", "identity", "procedure"],
    )
    budget_report = tools.context_budget_report(context_pack)
    trust_report = tools.memory_trust_report(types=["memory_entry", "decision"])
    health_report = tools.memory_health_report()

    assert budget_report["max_total_tokens"] == 720
    assert "pack_tokens" in budget_report
    assert "trust_levels" in trust_report
    assert "link_validation" in health_report


def test_adapter_returns_context_diagnostics_from_mcp() -> None:
    tools = MemoryTools(retrieval_backend=MemoryRetrievalBackend())

    result = CodexAdapter(memory_tools=tools).execute_task(
        "prepare adapter context diagnostics",
        "codex-diagnostics",
    )

    assert result["context_diagnostics"]["max_total_tokens"] == result["context_pack"]["limits"]["max_total_tokens"]
    assert "pack_tokens" in result["context_diagnostics"]
