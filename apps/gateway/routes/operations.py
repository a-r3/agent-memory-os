"""Future operational route helpers."""

from __future__ import annotations

from typing import Any, Dict

from apps.gateway.main import GatewayApp


def operations_report_route(gateway: GatewayApp) -> Dict[str, Any]:
    """Return a consolidated operational report through the gateway."""
    return {
        "health": gateway.health(),
        "trust": gateway.trust_report(),
        "tiers": gateway.memory_tools.memory_tier_report(),
        "snapshots": gateway.memory_tools.memory_snapshot_list(export_kind="snapshot"),
    }
