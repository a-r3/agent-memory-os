"""
Compatibility wrapper for the MVP retrieval backend.

The canonical in-memory retrieval service now lives in
``brain.services.retrieval``. This module remains as a thin alias so any
earlier imports continue to work while the repository transitions to the new
path.
"""

from brain.services.retrieval import MemoryRetrievalBackend


class MemoryRetrievalStub(MemoryRetrievalBackend):
    """Backward-compatible alias for the canonical MVP retrieval backend."""


__all__ = ["MemoryRetrievalStub"]
