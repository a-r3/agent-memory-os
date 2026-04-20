"""
Snapshot export and import utilities for Agent Memory OS.

This service provides a minimal operational readiness path for backup and
recovery. It writes structured JSON snapshots into the canonical storage
folders already present in the repository and can load them back into the
in-memory retrieval backend.
"""

from __future__ import annotations

from datetime import datetime, UTC
import json
from pathlib import Path
import re
from typing import Any, Dict, Optional

from brain.models.decision import Decision
from brain.models.entity import Entity
from brain.models.memory_entry import MemoryEntry
from brain.models.session_delta import SessionDelta
from brain.services.retrieval import MemoryRetrievalBackend


class PersistenceService:
    """Export and import corpus snapshots under the canonical storage tree."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        self.base_dir = base_dir or repo_root / "storage"
        self.snapshot_dir = self.base_dir / "snapshots"
        self.export_dir = self.base_dir / "exports"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_snapshot(
        self,
        retrieval_backend: MemoryRetrievalBackend,
        *,
        label: Optional[str] = None,
        export_kind: str = "snapshot",
    ) -> Dict[str, Any]:
        """Write the current in-memory corpus to a JSON file and return metadata."""
        directory = self.snapshot_dir if export_kind == "snapshot" else self.export_dir
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        safe_label = self._safe_label(label or export_kind)
        file_path = directory / f"{timestamp}_{safe_label}.json"

        payload = {
            "version": 1,
            "created_at": datetime.now(UTC).isoformat(),
            "memory_entries": [dict(vars(item)) for item in retrieval_backend.memory_entries],
            "decisions": [dict(vars(item)) for item in retrieval_backend.decisions],
            "session_deltas": [dict(vars(item)) for item in retrieval_backend.session_deltas],
            "entities": [dict(vars(item)) for item in retrieval_backend.entities],
            "links": retrieval_backend.list_links(),
        }
        file_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return {
            "path": str(file_path),
            "export_kind": export_kind,
            "counts": {
                "memory_entries": len(payload["memory_entries"]),
                "decisions": len(payload["decisions"]),
                "session_deltas": len(payload["session_deltas"]),
                "entities": len(payload["entities"]),
                "links": len(payload["links"]),
            },
        }

    def import_snapshot(
        self,
        retrieval_backend: MemoryRetrievalBackend,
        *,
        snapshot_path: str,
        merge: bool = True,
    ) -> Dict[str, Any]:
        """Load a snapshot JSON file into the current in-memory backend."""
        path = Path(snapshot_path)
        payload = json.loads(path.read_text(encoding="utf-8"))

        imported_memory_entries = [MemoryEntry(**item) for item in payload.get("memory_entries", [])]
        imported_decisions = [Decision(**item) for item in payload.get("decisions", [])]
        imported_session_deltas = [SessionDelta(**item) for item in payload.get("session_deltas", [])]
        imported_entities = [Entity(**item) for item in payload.get("entities", [])]
        imported_links = [dict(item) for item in payload.get("links", [])]

        if merge:
            retrieval_backend.memory_entries = self._merge_by_id(retrieval_backend.memory_entries, imported_memory_entries)
            retrieval_backend.decisions = self._merge_by_id(retrieval_backend.decisions, imported_decisions)
            retrieval_backend.session_deltas = self._merge_by_id(retrieval_backend.session_deltas, imported_session_deltas)
            retrieval_backend.entities = self._merge_by_id(retrieval_backend.entities, imported_entities)
            retrieval_backend.links = self._merge_links(retrieval_backend.links, imported_links)
        else:
            retrieval_backend.memory_entries = imported_memory_entries
            retrieval_backend.decisions = imported_decisions
            retrieval_backend.session_deltas = imported_session_deltas
            retrieval_backend.entities = imported_entities
            retrieval_backend.links = imported_links

        return {
            "path": str(path),
            "merge": merge,
            "counts": {
                "memory_entries": len(imported_memory_entries),
                "decisions": len(imported_decisions),
                "session_deltas": len(imported_session_deltas),
                "entities": len(imported_entities),
                "links": len(imported_links),
            },
        }

    def list_snapshot_files(self, *, export_kind: str = "snapshot") -> list[str]:
        """List available snapshot or export files in descending name order."""
        directory = self.snapshot_dir if export_kind == "snapshot" else self.export_dir
        return [str(path) for path in sorted(directory.glob("*.json"), reverse=True)]

    def _merge_by_id(self, existing: list[Any], imported: list[Any]) -> list[Any]:
        merged: dict[str, Any] = {str(vars(item).get("id") or ""): item for item in existing}
        for item in imported:
            merged[str(vars(item).get("id") or "")] = item
        return list(merged.values())

    def _merge_links(self, existing: list[dict[str, str]], imported: list[dict[str, str]]) -> list[dict[str, str]]:
        merged: dict[tuple[str, str, str], dict[str, str]] = {}
        for link in [*existing, *imported]:
            key = (
                str(link.get("source_id") or ""),
                str(link.get("target_id") or ""),
                str(link.get("link_type") or ""),
            )
            merged[key] = link
        return list(merged.values())

    def _safe_label(self, label: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9._-]+", "-", label.strip()).strip("-")
        return cleaned or "snapshot"
