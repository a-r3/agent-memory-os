"""Smoke tests for the MCP server scaffold and prompt/resource catalogs."""

from mcp.prompts import PROMPTS
from mcp.resources import RESOURCES
from mcp.server import MCPServer


def test_mcp_server_describe_returns_resources_prompts_and_tools() -> None:
    description = MCPServer().describe()
    assert "resources" in description
    assert "prompts" in description
    assert "tools" in description


def test_mcp_catalogs_are_populated() -> None:
    assert "brain://identity/project" in RESOURCES
    assert "build_context_pack" in PROMPTS
