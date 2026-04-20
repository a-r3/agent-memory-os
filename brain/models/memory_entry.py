# brain/models/memory_entry.py
from typing import List, Optional
from datetime import datetime, UTC

class MemoryEntry:
    def __init__(self, id: str, kind: str, title: str,
                 summary_short: str, status: str,
                 created_at: Optional[str] = None, updated_at: Optional[str] = None,
                 summary_full: Optional[str] = None,
                 tags: Optional[List[str]] = None,
                 entity_refs: Optional[List[str]] = None,
                 source_refs: Optional[List[str]] = None,
                 confidence: Optional[float] = None):
        self.id = id
        self.kind = kind
        self.title = title
        self.summary_short = summary_short
        self.summary_full = summary_full
        self.status = status
        self.tags = tags or []
        self.entity_refs = entity_refs or []
        self.source_refs = source_refs or []
        self.confidence = confidence
        self.created_at = created_at or datetime.now(UTC).isoformat()
        self.updated_at = updated_at or datetime.now(UTC).isoformat()
