"""Minimal integration tests for the Agent Memory OS MVP path."""

from brain.adapters.claude_adapter import ClaudeAdapter
from brain.adapters.codex_adapter import CodexAdapter
from brain.adapters.generic_adapter import GenericAdapter
from brain.services.retrieval import MemoryRetrievalBackend
from mcp.tools import MemoryTools


def test_context_compile_returns_schema_shaped_pack() -> None:
    tools = MemoryTools(retrieval_backend=MemoryRetrievalBackend())

    context_pack = tools.context_compile(
        agent="codex",
        task="compile context for MCP integration test",
        budget_tokens=700,
        memory_scope=["rule", "identity", "procedure"],
    )

    assert set(context_pack.keys()) == {
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
    assert context_pack["agent"] == "codex"
    assert isinstance(context_pack["limits"]["max_total_tokens"], int)
    assert isinstance(context_pack["rules_pack"], list)


def test_adapters_execute_and_write_back_to_in_memory_backend() -> None:
    retrieval_backend = MemoryRetrievalBackend()
    tools = MemoryTools(retrieval_backend=retrieval_backend)

    baseline_delta_count = len(retrieval_backend.session_deltas)

    codex_result = CodexAdapter(memory_tools=tools).execute_task(
        "prepare codex adapter integration test",
        "codex-test",
    )
    claude_result = ClaudeAdapter(memory_tools=tools).execute_task(
        "prepare claude adapter integration test",
        "claude-test",
    )
    generic_result = GenericAdapter("generic-runtime", memory_tools=tools).execute_task(
        "prepare generic adapter integration test",
        "generic-test",
    )

    assert codex_result["execution"]["status"] == "pending_implementation"
    assert claude_result["execution"]["status"] == "pending_implementation"
    assert generic_result["execution"]["status"] == "pending_implementation"
    assert codex_result["writeback"]["session_delta"]["status"] == "written"
    assert claude_result["writeback"]["session_delta"]["status"] == "written"
    assert generic_result["writeback"]["session_delta"]["status"] == "written"
    assert len(retrieval_backend.session_deltas) == baseline_delta_count + 3
