# Operations Guide for Agent Memory OS

## Purpose

This document describes how to run, validate, and maintain the repository in a
local development environment while preserving the canonical memory-centric
architecture.

## Startup Sequence

1. Copy `.env.example` to `.env` and adjust local values as needed.
2. Install the project with:
   - `make dev-install`
3. Run focused smoke checks with:
   - `make test-fast`
4. Optionally start the Docker development stack with:
   - `make docker-up`

## Canonical Runtime Surfaces

- `mcp/tools.py` exposes the stable tool surface used by adapters.
- `brain/api/memory_api.py` is the canonical internal memory facade.
- `apps/gateway/main.py` and `apps/compiler/main.py` are application-level
  facades built on top of the canonical API.
- `apps/workers/` contains background-oriented smoke-safe worker scaffolds.

## Validation

Recommended local checks:

- `make pycompile`
- `make test-fast`
- `make lint`

## Snapshot and Recovery Flow

The persistence service and related scaffolds support:

- snapshot export
- snapshot import
- reporting and operational review

Snapshots and export manifests live under:

- `storage/snapshots/`
- `storage/exports/`
- `storage/archives/`

## Safety Rules

- Do not bypass MCP or the Memory API for memory mutations.
- Do not store raw chat history as canonical memory.
- Do not store secrets or PII in general-purpose memory.
- Keep writeback delta-based and traceable.

## Future Operational Work

Future phases extend this guide with:

- approval gates
- policy audit automation
- recovery drills
- export and archive playbooks
