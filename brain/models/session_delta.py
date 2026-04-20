# brain/models/session_delta.py
from datetime import datetime, UTC

class SessionDelta:
    def __init__(self, id: str, session_id: str, task: str,
                 new_facts=None, changed_facts=None, decisions=None,
                 artifacts=None, open_questions=None, next_actions=None,
                 created_at: str = None):
        self.id = id
        self.session_id = session_id
        self.task = task
        self.new_facts = new_facts or []
        self.changed_facts = changed_facts or []
        self.decisions = decisions or []
        self.artifacts = artifacts or []
        self.open_questions = open_questions or []
        self.next_actions = next_actions or []
        self.created_at = created_at or datetime.now(UTC).isoformat()
