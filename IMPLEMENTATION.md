# Implementation Guide

**Version**: 0.2.0
**Last updated**: 2026-03-17
**Design reference**: [README.md](README.md)

This document describes how to set up, build, deploy, and test the
pytest-framework project. It is the operational companion to the README.

---

## Changelog

| Version | Date | Description |
|---|---|---|
| 0.2.0 | 2026-03-17 | Restructured: framework/sut/tests separation; Makefile; env generator |
| 0.1.0 | 2026-03-17 | Initial implementation guide |

---

## Architecture boundary

The project separates three concerns:

| Directory | Role | Swappable |
|---|---|---|
| `framework/` | Testing infrastructure: log tracker, notification service, registry, CI/CD workflows | No (core) |
| `sut/` | System under test: the mock twitter clone | Yes (replace with any containerized app) |
| `tests/` | Test suite: e2e, integration, unit tests against the SUT | Adapts to the SUT |

The top-level `docker-compose.yml` includes both
`framework/docker-compose.framework.yml` and
`sut/twitter-clone/docker-compose.sut.yml`. To swap the SUT, replace the
include path and adjust test fixtures in `tests/conftest.py`.

---

## Prerequisites

| Tool | Minimum version | Purpose |
|---|---|---|
| Docker Engine | 24.x | Container runtime |
| Docker Compose | 2.20+ | Multi-container orchestration |
| Python | 3.11+ | Backend, tests, linter |
| Node.js | 20 LTS | Frontend build (future) |
| Git | 2.x | Version control |
| Make | any | Build/deploy/test commands |

Optional:

* `ruff` (`pip install ruff`) for local linting
* `playwright` (`pip install playwright && playwright install`) for local
  E2E tests

---

## Bootstrap

```
make bootstrap
```

This runs `scripts/generate_env.sh` which:

1. Generates a random 32-byte hex JWT secret
2. Writes a `.env` file with all required variables and defaults
3. Creates the `data/` directory

The `.env` file is gitignored. Re-running with `--force` overwrites
without prompting.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `APP_DB_PATH` | `./data/app.db` | SUT application database |
| `LOG_DB_PATH` | `./data/logs.db` | Log tracker database |
| `JWT_SECRET` | (generated) | Secret key for JWT signing |
| `JWT_EXPIRY_SECONDS` | `3600` | Token expiry duration |
| `LOG_MAX_LINE_BYTES` | `16384` | Max log line size (16KB) |
| `LOG_STORAGE_CAP_MB` | `256` | Log storage cap before FIFO eviction |
| `REGISTRY_PORT` | `5001` | Local Docker Registry host port |

The two SQLite files are deliberately separate. `app.db` is owned by the
SUT backend. `logs.db` is owned by the framework log tracker. This
isolation prevents a runaway log table from affecting the application.

---

## Container inventory

| Container | Image | Port | Layer |
|---|---|---|---|
| frontend | `sut/twitter-clone/frontend/Dockerfile` | 3000 | SUT |
| backend | `sut/twitter-clone/backend/Dockerfile` | 8000 | SUT |
| log-tracker | `framework/log-tracker/Dockerfile` | 8001 | Framework |
| notification | `framework/notification-service/Dockerfile` | 8002 | Framework |
| registry | `registry:2` | 5001 | Framework |

The "Layer" column makes the boundary explicit. SUT containers can be
replaced without touching framework containers.

---

## Build and deploy

```
make build       # Build all images
make up          # Start all services (runs bootstrap if needed)
make down        # Stop and remove containers
make restart     # Rebuild and restart everything
make status      # Show container health
make logs        # Tail container logs
make clean       # Stop containers, remove database files
```

### Health endpoints

Each service exposes a health or readiness endpoint used by Docker
Compose healthchecks and by the CI pipeline before running tests:

| Service | Endpoint |
|---|---|
| Backend | `GET /health` |
| Frontend | HTTP 200 on root |
| Log tracker | `GET /version` |
| Notification | `GET /health` |
| Registry | `GET /v2/` |

---

## Linting

```
make lint
```

Runs `ruff check .` across the entire project. Configuration lives in
`pyproject.toml` (to be created when ruff rules are finalized).

---

## Running tests

```
make test          # All levels
make test-unit     # Unit tests only
make test-int      # Integration tests only
make test-e2e      # E2E tests only
```

### E2E tests

Require a running deployment. Use Playwright to drive the frontend.
In CI, run inside the official Playwright Docker image
(`mcr.microsoft.com/playwright/python`).

### Integration tests

Hit the backend API directly using HTTPX. Require backend and database
to be running. Do not require the frontend.

### Unit tests

Run in isolation with no external dependencies.

### Test configuration

Base URLs are set via environment variables in `tests/conftest.py`:

| Variable | Default | Used by |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | Integration, E2E |
| `FRONTEND_URL` | `http://localhost:3000` | E2E |
| `LOG_TRACKER_URL` | `http://localhost:8001` | Integration |

---

## CI/CD workflows

Workflow definitions go in `framework/workflows/` and are symlinked or
copied to `.github/workflows/` when GitHub is configured.

### lint.yml

* **Trigger**: Every push
* **Steps**: Checkout, install ruff, `ruff check .`

### ci.yml

* **Trigger**: Push to non-draft pull request branch
* **Steps**:
    1. Checkout
    2. `make bootstrap`
    3. `make build`
    4. `make up`
    5. Wait for health checks
    6. `make test-unit`
    7. `make test-int`
    8. `make test-e2e`
    9. Upload results to log tracker
    10. `make down`

---

## Log Tracker specification

### Endpoints

* `POST /logs` -- accepts JSON log data
* `GET /logs` -- retrieves log lines filtered by time range
* `GET /info` -- capabilities, limits, image checksum, uptime
* `GET /version` -- semver version as JSON

### Input format

Accepts JSON in two forms:

* List of strings (stored as simple log lines)
* List of objects with `metadata` (dict) and `line` (string) keys

### Storage

* Dedicated SQLite file (`logs.db`), separate from SUT database
* Metadata is stored but not exposed on retrieval in v1

### Retrieval

* Time range only (start/end as ISO8601 query parameters)
* Uses insertion time when log content has no parseable timestamp
* Returns log line text only

### Limits and retention

* 16KB maximum per log line
* Total storage cap with FIFO eviction (oldest removed first)

### Concurrency

SQLite serializes writes. Concurrent submissions queue. In production,
a message queue (RabbitMQ, Redis Streams) would buffer writes.

### Future capabilities (not in v1)

* Regex search via reverse indexing or backend delegation
* Metadata retrieval on read
* Advanced query filters

---

## Known limitations

* **SQLite write serialization**: Both databases serialize writes.
  Acceptable for toy setup. PostgreSQL + message queue for production.

* **No log search**: Time-range only in v1. Reverse indexing or
  Elasticsearch for production.

* **No metadata on read**: Stored but not returned. Future endpoint
  or query parameter.

* **No internal service auth**: Log tracker and notification service
  accept unauthenticated requests. Mutual TLS or API keys for
  production.

* **Single-host only**: No horizontal scaling in this configuration.

* **Frontend is a placeholder**: Static HTML served by nginx. React
  build pipeline not yet implemented.

---

## References

* [README.md](README.md) -- Architecture, selected stack, quick start
* [Docker Compose docs](https://docs.docker.com/compose/)
* [FastAPI docs](https://fastapi.tiangolo.com/)
* [Playwright for Python](https://playwright.dev/python/)
* [ruff](https://docs.astral.sh/ruff/)
* [registry:2](https://hub.docker.com/_/registry)
