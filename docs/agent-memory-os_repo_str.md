agent-memory-os/
├── README.md
├── AGENTS.md
├── .env.example
├── Makefile
├── pyproject.toml
├── docker-compose.yml
├── apps/
│   ├── gateway/
│   │   ├── main.py
│   │   ├── routes/
│   │   └── mcp/
│   ├── compiler/
│   │   ├── main.py
│   │   ├── planners/
│   │   ├── packers/
│   │   └── compressors/
│   ├── writeback/
│   │   ├── main.py
│   │   ├── merge.py
│   │   ├── dedupe.py
│   │   └── promotion.py
│   └── workers/
│       ├── ingest_worker.py
│       ├── compaction_worker.py
│       └── graph_sync_worker.py
├── brain/
│   ├── api/
│   │   ├── memory.py
│   │   ├── decisions.py
│   │   ├── context.py
│   │   ├── search.py
│   │   └── entities.py
│   ├── models/
│   │   ├── memory_entry.py
│   │   ├── decision.py
│   │   ├── event.py
│   │   ├── entity.py
│   │   └── session_delta.py
│   ├── services/
│   │   ├── retrieval.py
│   │   ├── ranking.py
│   │   ├── linking.py
│   │   ├── summarization.py
│   │   ├── trust.py
│   │   └── budgeting.py
│   └── adapters/
│       ├── codex_adapter.py
│       ├── claude_adapter.py
│       └── generic_adapter.py
├── storage/
│   ├── docs/
│   │   ├── identity/
│   │   ├── rules/
│   │   ├── procedures/
│   │   ├── decisions/
│   │   ├── entities/
│   │   └── sessions/
│   ├── snapshots/
│   ├── exports/
│   └── archives/
├── schemas/
│   ├── memory_entry.schema.json
│   ├── decision.schema.json
│   ├── event.schema.json
│   ├── entity.schema.json
│   ├── session_delta.schema.json
│   └── context_pack.schema.json
├── prompts/
│   ├── compiler/
│   ├── summarizer/
│   ├── planner/
│   └── validators/
├── mcp/
│   ├── server.py
│   ├── resources.py
│   ├── tools.py
│   └── prompts.py
├── adapters/
│   ├── codex/
│   │   ├── config.template.toml
│   │   └── instructions.md
│   ├── claude/
│   │   ├── CLAUDE.template.md
│   │   └── skills/
│   └── generic/
│       └── client_examples/
├── tests/
│   ├── test_memory_api.py
│   ├── test_compiler.py
│   ├── test_dedupe.py
│   ├── test_graph_links.py
│   └── test_mcp_server.py
└── docs/
    ├── architecture.md
    ├── operations.md
    ├── security.md
    ├── token_budgeting.md
    └── rollout_plan.md
