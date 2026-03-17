# Implementation Guide

**Version**: 0.1.0
**Last updated**: 2026-03-17
**Design reference**: [README.md](README.md)

This document describes how to set up, build, deploy, and test the
pytest-framework-example project. It is the operational companion to the
README, which contains architecture rationale and design decisions.

---

## Changelog

| Version | Date | Description |
|---|---|---|
| 0.1.0 | 2026-03-17 | Initial implementation guide; selected stack documented |

---

## Prerequisites

The following must be installed on the host machine.

| Tool | Minimum version | Purpose |
|---|---|---|
| Docker Engine | 24.x | Container runtime for all services |
| Docker Compose | 2.20+ | Multi-container orchestration |
| Node.js | 20 LTS | Frontend build toolchain |
| Python | 3.11+ | Backend API, test runner, linter |
| Git | 2.x | Version control |

Optional but recommended:

* `ruff` (installable via `pip install ruff`) for local linting before push
* `playwright` Python package for local E2E test execution

---

## Project structure

```
pytest-framework/
|-- README.md                  # Architecture and design decisions
|-- IMPLEMENTATION.md          # This file
|-- docker-compose.yml         # Orchestrates all services
|-- .github/
|   |-- workflows/
|       |-- lint.yml           # Linting pipeline (ruff)
|       |-- ci.yml             # Build, deploy, test pipeline
|-- frontend/
|   |-- Dockerfile
|   |-- package.json
|   |-- tsconfig.json
|   |-- src/
|-- backend/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- app/
|       |-- main.py            # FastAPI entry point
|       |-- models.py
|       |-- auth.py
|       |-- validators.py
|-- log-tracker/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- app/
|       |-- main.py            # Log tracker API entry point
|       |-- db.py              # SQLite operations
|-- notification-service/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- app/
|       |-- main.py            # Notification stub entry point
|-- tests/
|   |-- conftest.py            # Shared pytest fixtures
|   |-- e2e/                   # Playwright E2E tests
|   |-- integration/           # API-level tests (HTTPX)
|   |-- unit/                  # Isolated logic tests
|-- data/
|   |-- app.db                 # Application SQLite database (gitignored)
|   |-- logs.db                # Log tracker SQLite database (gitignored)
```

---

## Container inventory

All services run as Docker containers orchestrated by Docker Compose.

| Container | Image | Port | Purpose |
|---|---|---|---|
| frontend | Built from `frontend/Dockerfile` | 3000 | React/TypeScript SPA |
| backend | Built from `backend/Dockerfile` | 8000 | FastAPI REST API |
| log-tracker | Built from `log-tracker/Dockerfile` | 8001 | Custom log API |
| notification | Built from `notification-service/Dockerfile` | 8002 | Notification stub API |
| registry | `registry:2` | 5000 | Local Docker Registry |

---

## Configuration

### Environment variables

Environment variables are managed via a `.env` file at the project root.
This file is gitignored.

| Variable | Default | Description |
|---|---|---|
| `APP_DB_PATH` | `./data/app.db` | Path to application SQLite file |
| `LOG_DB_PATH` | `./data/logs.db` | Path to log tracker SQLite file |
| `JWT_SECRET` | (none, required) | Secret key for JWT signing |
| `JWT_EXPIRY_SECONDS` | `3600` | Token expiry duration |
| `LOG_MAX_LINE_BYTES` | `16384` | Maximum log line size (16KB) |
| `LOG_STORAGE_CAP_MB` | `256` | Total log storage cap before FIFO eviction |
| `REGISTRY_PORT` | `5000` | Local Docker Registry port |

### Docker Compose

The `docker-compose.yml` file defines all containers, networks, and volume
mounts. The application database and log tracker database are stored in the
`data/` directory, mounted as volumes into their respective containers.

The two SQLite files are deliberately separate:

* `app.db` - owned by the backend container
* `logs.db` - owned by the log-tracker container

This isolation ensures a runaway log table cannot affect the application
database, and simplifies future backend swaps for the log tracker.

---

## Build

### Local build

```
docker compose build
```

This builds all custom images (frontend, backend, log-tracker, notification).
The `registry:2` image is pulled from Docker Hub.

### CI build (GitHub Actions)

The `ci.yml` workflow:

1. Checks out the repository
2. Builds all images via `docker compose build`
3. Tags and pushes images to the local Docker Registry
4. Proceeds to deploy and test stages

---

## Deploy

### Local deployment

```
docker compose up -d
```

Starts all containers in detached mode. The frontend is accessible at
`http://localhost:3000`, the backend API at `http://localhost:8000`.

### Readiness verification

The deployment process must verify that all services are healthy before
tests proceed. Each service exposes a health or readiness endpoint:

* Backend: `GET /health`
* Log tracker: `GET /version`
* Notification service: `GET /health`
* Frontend: HTTP 200 on the root URL

The `docker-compose.yml` should define `healthcheck` directives for each
service. The test stage waits for all health checks to pass before
execution.

---

## Linting

ruff is invoked as the first pipeline stage and can also be run locally.

```
ruff check .
```

The `lint.yml` GitHub Actions workflow runs on every push and reports
results back to the pull request.

Configuration lives in `pyproject.toml` under the `[tool.ruff]` section.

---

## Running tests

### All tests

```
pytest tests/
```

### By level

```
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

### E2E tests with Playwright

E2E tests require a running deployment. They can be executed inside the
Playwright Docker image or locally with Playwright installed:

```
pip install playwright pytest-playwright
playwright install
pytest tests/e2e/
```

In CI, the E2E tests run against the deployed containers using the
official Playwright Docker image (`mcr.microsoft.com/playwright/python`).

### Integration tests

Integration tests hit the backend API directly using HTTPX. They require
the backend and database to be running but do not require the frontend.

```
pytest tests/integration/
```

### Unit tests

Unit tests run in isolation with no external dependencies.

```
pytest tests/unit/
```

---

## Log tracker operations

### Submitting logs

```
POST http://localhost:8001/logs
Content-Type: application/json

["line one", "line two", "line three"]
```

Or with metadata (stored but not returned in v1):

```
POST http://localhost:8001/logs
Content-Type: application/json

[
  {"metadata": {"source": "ci", "stage": "build"}, "line": "build started"},
  {"metadata": {"source": "ci", "stage": "build"}, "line": "build complete"}
]
```

### Retrieving logs

```
GET http://localhost:8001/logs?start=2026-03-17T00:00:00Z&end=2026-03-17T23:59:59Z
```

Returns a JSON array of log line strings.

### Service info

```
GET http://localhost:8001/info
```

Returns JSON with: supported input formats, storage backend identifier,
max line size, installed image checksum, uptime, retention policy.

```
GET http://localhost:8001/version
```

Returns JSON with the semver version of the service.

---

## GitHub Actions workflows

### lint.yml

* **Trigger**: Every push to any branch
* **Steps**: Checkout, install ruff, run `ruff check .`
* **Output**: Annotations on the pull request

### ci.yml

* **Trigger**: Push to a non-draft pull request branch
* **Steps**:
    1. Checkout
    2. Build all images (`docker compose build`)
    3. Push images to local registry
    4. Deploy (`docker compose up -d`)
    5. Wait for health checks
    6. Run unit tests
    7. Run integration tests
    8. Run E2E tests (Playwright container)
    9. Upload test results and logs to log tracker
    10. Tear down (`docker compose down`)

---

## Known limitations

* **SQLite write serialization**: Both the application database and the
  log tracker serialize writes. Concurrent requests queue. This is
  acceptable for the toy setup. In a production system, the application
  would use PostgreSQL and the log tracker would buffer writes through a
  message queue (e.g. RabbitMQ, Redis Streams).

* **No log search**: The log tracker v1 supports time-range retrieval
  only. Regex or full-text search is not implemented. In a production
  setup, this would be handled by reverse indexing or delegated to the
  storage backend (e.g. Elasticsearch).

* **No metadata on read**: Structured log metadata is stored but not
  returned in v1. Future versions may expose it via a query parameter or
  a dedicated endpoint.

* **No authentication on internal services**: The log tracker and
  notification service do not require authentication. In a production
  setup, service-to-service authentication (e.g. mutual TLS, API keys)
  would be required.

* **Single-host only**: The entire stack runs on one machine. Horizontal
  scaling is not supported in this configuration.

---

## References

* [README.md](README.md) - Architecture, design rationale, test plan
* [Docker Compose docs](https://docs.docker.com/compose/)
* [FastAPI docs](https://fastapi.tiangolo.com/)
* [Playwright for Python](https://playwright.dev/python/)
* [ruff](https://docs.astral.sh/ruff/)
* [registry:2](https://hub.docker.com/_/registry)
