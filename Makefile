# Agent Memory OS development tasks
#
# This Makefile is intentionally conservative and stdlib-friendly. The current
# repository ships importable scaffolds rather than full web servers, so the
# run targets perform smoke imports or lightweight local execution against the
# canonical app facades.

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
COMPOSE ?= docker compose

.PHONY: help install dev-install test test-fast lint format typecheck build clean \
	run-gateway run-compiler run-writeback run-worker-ingest run-worker-compaction \
	run-worker-graph run-worker-recovery run-worker-reporting docker-up docker-down \
	docker-logs pycompile

help:
	@echo "Available targets:"
	@echo "  install               Install the project in editable mode"
	@echo "  dev-install           Install the project with dev dependencies"
	@echo "  test                  Run the full pytest suite"
	@echo "  test-fast             Run a focused integration subset"
	@echo "  pycompile             Compile-check core source files"
	@echo "  lint                  Run Ruff lint checks"
	@echo "  format                Run Ruff formatting"
	@echo "  typecheck             Run mypy against the canonical source tree"
	@echo "  build                 Build source and wheel distributions"
	@echo "  clean                 Remove common Python build artifacts"
	@echo "  run-gateway           Smoke-run the gateway facade"
	@echo "  run-compiler          Smoke-run the compiler facade"
	@echo "  run-writeback         Smoke-run the writeback facade"
	@echo "  run-worker-ingest     Smoke-run the ingest worker"
	@echo "  run-worker-compaction Smoke-run the compaction worker"
	@echo "  run-worker-graph      Smoke-run the graph sync worker"
	@echo "  run-worker-recovery   Smoke-run the recovery worker"
	@echo "  run-worker-reporting  Smoke-run the reporting worker"
	@echo "  docker-up             Start the local Docker Compose stack"
	@echo "  docker-down           Stop the local Docker Compose stack"
	@echo "  docker-logs           Tail Docker Compose service logs"

install:
	$(PIP) install -e .

dev-install:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest

test-fast:
	$(PYTHON) -m pytest \
		tests/test_mcp_integration.py \
		tests/test_phase9_phase10.py \
		tests/test_scaffold_population.py \
		tests/test_future_phase_scaffolds.py

pycompile:
	$(PYTHON) -m compileall brain apps mcp tests

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

typecheck:
	$(PYTHON) -m mypy brain apps mcp

build:
	$(PYTHON) -m build

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type d -name "dist" -prune -exec rm -rf {} +
	find . -type d -name "build" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-gateway:
	$(PYTHON) -c "from apps.gateway.main import create_app; import json; print(json.dumps(create_app().health(), indent=2))"

run-compiler:
	$(PYTHON) -c "from apps.compiler.main import CompilerApp; import json; app=CompilerApp(); result=app.compile_for_task(agent='codex', task='local compiler smoke run', budget_tokens=900); print(json.dumps(result['budget_report'], indent=2))"

run-writeback:
	$(PYTHON) -c "from apps.writeback.main import WritebackApp; app=WritebackApp(); delta_id=app.submit_session_delta({'session_id':'makefile:writeback','task':'local writeback smoke run'}); print(delta_id)"

run-worker-ingest:
	$(PYTHON) -c "from apps.workers.ingest_worker import IngestWorker; worker=IngestWorker(); print('Ingest worker ready:', worker is not None)"

run-worker-compaction:
	$(PYTHON) -c "from apps.workers.compaction_worker import CompactionWorker; import json; print(json.dumps(CompactionWorker().run(), indent=2))"

run-worker-graph:
	$(PYTHON) -c "from apps.workers.graph_sync_worker import GraphSyncWorker; import json; print(json.dumps(GraphSyncWorker().run(root_id='mem-rule-budget', depth=1), indent=2))"

run-worker-recovery:
	$(PYTHON) -c "from apps.workers.recovery_worker import RecoveryWorker; worker=RecoveryWorker(); print('Recovery worker ready:', worker is not None)"

run-worker-reporting:
	$(PYTHON) -c "from apps.workers.reporting_worker import ReportingWorker; import json; print(json.dumps(ReportingWorker().run(), indent=2))"

docker-up:
	$(COMPOSE) up --build -d

docker-down:
	$(COMPOSE) down

docker-logs:
	$(COMPOSE) logs -f --tail=200
