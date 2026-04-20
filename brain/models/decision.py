# brain/models/decision.py
from datetime import datetime, UTC

class Decision:
    def __init__(self, id: str, kind: str, title: str, decision: str,
                 status: str, created_at: str = None, updated_at: str = None,
                 rationale: str = "", affects: list = None, owner: str = "",
                 source_refs: list = None):
        self.id = id
        self.kind = kind
        self.title = title
        self.decision = decision
        self.rationale = rationale
        self.affects = affects or []
        self.owner = owner
        self.source_refs = source_refs or []
        self.status = status
        self.created_at = created_at or datetime.now(UTC).isoformat()
        self.updated_at = updated_at or datetime.now(UTC).isoformat()
