"""Smoke tests for compiler app scaffolds and canonical context compilation."""

from apps.compiler.main import CompilerApp
from brain.api.context import ContextAPI
from brain.api.memory_api import MemoryAPI


def test_compiler_app_returns_context_pack_and_runtime_payload() -> None:
    app = CompilerApp()
    result = app.compile_for_task(agent="codex", task="compiler smoke test", budget_tokens=800)

    assert "context_pack" in result
    assert "runtime_payload" in result
    assert result["context_pack"]["agent"] == "codex"


def test_context_api_compiles_schema_shaped_pack() -> None:
    context_api = ContextAPI(MemoryAPI())
    context_pack = context_api.compile(agent="claude", task="context api smoke test", budget_tokens=700)

    assert context_pack["agent"] == "claude"
    assert "limits" in context_pack
