"""Smoke tests for dedupe and archive planning scaffolds."""

from apps.writeback.archive import ArchivePlanner
from apps.writeback.dedupe import DedupeService
from brain.api.memory_api import MemoryAPI


def test_dedupe_service_returns_duplicate_report_shape() -> None:
    report = DedupeService(MemoryAPI()).duplicate_report()
    assert "duplicate_candidate_groups" in report
    assert "duplicate_candidates" in report


def test_archive_planner_returns_archive_plan_shape() -> None:
    plan = ArchivePlanner(MemoryAPI()).build_archive_plan()
    assert "duplicate_candidates" in plan
    assert "cold_count" in plan
