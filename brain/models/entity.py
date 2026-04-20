# brain/models/entity.py
from datetime import datetime, UTC

class Entity:
    def __init__(self, id: str, kind: str, name: str,
                 description: str = "", links: dict = None,
                 created_at: str = None, updated_at: str = None):
        self.id = id
        self.kind = kind
        self.name = name
        self.description = description
        self.links = links or {"depends_on": [], "used_by": []}
        self.created_at = created_at or datetime.now(UTC).isoformat()
        self.updated_at = updated_at or datetime.now(UTC).isoformat()
