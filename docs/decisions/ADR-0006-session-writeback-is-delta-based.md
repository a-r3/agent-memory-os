# ADR-0006: Session Writeback Is Delta-Based

## Status
Approved

## Context

Naive memory systems often write oversized summaries after every session.

This leads to:

- repeated information
- bloated storage
- duplicate facts
- noisy retrieval
- rising maintenance complexity

The system needs a more disciplined method for preserving session outcomes.

## Decision

Agent Memory OS will write session outcomes back as structured deltas rather than full-history summaries.

A session delta should focus on:

- new facts
- changed facts
- decisions
- artifacts
- open questions
- next actions

## Consequences

### Positive
- writeback remains compact
- memory redundancy is reduced
- later promotion becomes easier
- episodic continuity is preserved without transcript bloat

### Negative
- delta design must be consistent
- some narrative richness is intentionally reduced
- later reconstruction may require combining delta records with other artifacts

## Notes

Delta-based writeback is essential for long-lived memory hygiene.
