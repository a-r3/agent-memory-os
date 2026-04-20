"""Gateway route helpers for operational reporting."""

from __future__ import annotations

from typing import Any, Dict

from apps.gateway.main import GatewayApp


def health_route(gateway: GatewayApp) -> Dict[str, Any]:
    """Return the default gateway health payload."""
    return gateway.health()


def trust_route(gateway: GatewayApp) -> Dict[str, Any]:
    """Return the current trust report through the gateway."""
    return gateway.trust_report()
