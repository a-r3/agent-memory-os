# ADR-0001: Canonical Shared Memory

## Status
Approved

## Context

Multiple AI agents are expected to operate over the same projects, tasks, and evolving knowledge base.

Without a shared canonical memory layer, the system drifts toward:

- fragmented knowledge
- repeated re-explanation
- conflicting agent assumptions
- duplicated summaries
- weak continuity across sessions

In that model, each agent becomes the temporary owner of memory, and continuity depends too heavily on prompt history.

That is not acceptable for a long-lived multi-agent system.

## Decision

Agent Memory OS will use a single shared memory kernel as the canonical source of durable memory for all agents.

Agents do not own memory.  
Agents are clients of memory.

## Consequences

### Positive
- continuity improves across sessions and agents
- knowledge duplication is reduced
- memory governance becomes centralized
- decisions, facts, and rules can be stored structurally
- agent replacement becomes easier

### Negative
- architecture becomes more deliberate
- memory writeback must be governed carefully
- a central memory model must be maintained
- poor schema design could affect many integrations

## Notes

This decision is foundational and should be assumed by all later architecture and implementation work.
