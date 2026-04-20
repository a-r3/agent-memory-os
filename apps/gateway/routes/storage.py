"""Future-phase storage and persistence route helpers."""

from __future__ import annotations

from typing import Any, Dict

from apps.gateway.main import GatewayApp


def snapshot_export_route(gateway: GatewayApp, *, label: str | None = None) -> Dict[str, Any]:
    """Export a snapshot through the gateway's canonical MCP-backed path."""
    return gateway.memory_tools.memory_snapshot_export(label=label, export_kind="snapshot")


def snapshot_import_route(gateway: GatewayApp, *, snapshot_path: str, merge: bool = True) -> Dict[str, Any]:
    """Import a snapshot through the gateway's canonical MCP-backed path."""
    return gateway.memory_tools.memory_snapshot_import(snapshot_path=snapshot_path, merge=merge)


def snapshot_list_route(gateway: GatewayApp) -> list[str]:
    """List available snapshots through the gateway's canonical MCP-backed path."""
    return gateway.memory_tools.memory_snapshot_list(export_kind="snapshot")
