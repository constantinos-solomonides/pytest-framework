# pytest-framework

An end-to-end testing framework built with AI assistance. The framework
deploys, tests, and reports on containerized applications running on a
single host. A mock twitter clone serves as the system under test (SUT)
during framework development.

## Architecture

The project has three distinct layers, each with a clear boundary:

```
pytest-framework/
|-- framework/         The testing infrastructure (framework)
|-- sut/               The application(s) being tested (swappable)
|-- tests/             The test suite that exercises the SUT
```

The **framework** provides CI/CD pipelines, a log tracker API, a
notification service stub, and a local artifact registry. It is
application-agnostic; any containerized application placed under `sut/`
can be tested by it.

The **SUT** (system under test) is a mock twitter clone. It exists solely
to validate the framework. It can be replaced with any application that
exposes health endpoints and runs in Docker containers.

The **tests** directory contains the pytest-based test suite. Tests are
organized by level (e2e, integration, unit) and run against the SUT
through the framework.

## Selected stack

### Framework

| Component | Selected | Rationale |
|---|---|---|
| VCS | GitHub | Cloud-hosted, zero self-hosting overhead |
| CI/CD Runner | GitHub Actions | Native to GitHub, zero additional infra |
| Linter | ruff | Fastest, single binary, replaces multiple tools |
| Notification Service | Custom REST API | Stub; full control over schema |
| Build System | Docker | Required for deployment, reproducible builds |
| Artifact Tracker | Local Docker Registry | Official image (registry:2), self-contained |
| Log Tracker | Custom REST API | Custom container, SQLite backend |
| Deployment Target | Docker Compose | Standard, simple YAML |
| Test Runner | pytest | Lightest, pip-installable, largest ecosystem |

### SUT (mock twitter clone)

| Component | Selected | Rationale |
|---|---|---|
| Frontend | React/TypeScript | Component-based, rich testing ecosystem |
| Backend API | FastAPI/Python | Async support, automatic OpenAPI docs |
| Database | SQLite | Zero-config, file-based, single-host |
| Authentication | JWT | Stateless, no extra infrastructure |
| Orchestration | Docker Compose | Single-command startup |

### Test tooling

| Level | Selected | Rationale |
|---|---|---|
| E2E | Playwright | Official Docker image, modern |
| Integration | pytest + HTTPX | Async-capable, direct API testing |
| Unit | pytest | Fast, granular, extensive plugins |

## Project structure

```
pytest-framework/
|-- README.md
|-- IMPLEMENTATION.md
|-- Makefile                              Build/deploy/test commands
|-- docker-compose.yml                    Top-level: includes both sub-composes
|-- .env                                  Generated, gitignored
|-- .gitignore
|-- scripts/
|   |-- generate_env.sh                   Bootstrap script for .env
|-- framework/
|   |-- docker-compose.framework.yml      Framework services
|   |-- log-tracker/
|   |   |-- Dockerfile
|   |   |-- requirements.txt
|   |   |-- app/
|   |       |-- main.py                   Log tracker API
|   |-- notification-service/
|   |   |-- Dockerfile
|   |   |-- requirements.txt
|   |   |-- app/
|   |       |-- main.py                   Notification stub
|   |-- workflows/                        GitHub Actions definitions
|-- sut/
|   |-- twitter-clone/
|       |-- docker-compose.sut.yml        SUT services
|       |-- backend/
|       |   |-- Dockerfile
|       |   |-- requirements.txt
|       |   |-- app/
|       |       |-- main.py               FastAPI entry point
|       |-- frontend/
|           |-- Dockerfile
|           |-- package.json
|           |-- src/
|               |-- index.html            Placeholder
|-- tests/
|   |-- conftest.py                       Shared fixtures
|   |-- requirements.txt                  Test dependencies
|   |-- e2e/                              Playwright tests
|   |-- integration/                      API-level tests (HTTPX)
|   |-- unit/                             Isolated logic tests
|-- data/
    |-- app.db                            SUT database (gitignored)
    |-- logs.db                           Log tracker database (gitignored)
```

## Quick start

```
# 1. Bootstrap (generates .env, creates data directory)
make bootstrap

# 2. Build all container images
make build

# 3. Start all services
make up

# 4. Run tests
make test

# 5. Tear down
make down
```

Run `make help` for the full list of commands.

## Log Tracker API

Custom REST API for centralized log storage. Designed to be swappable:
replace the container with any implementation exposing the same contract.

| Endpoint | Method | Description |
|---|---|---|
| `/logs` | POST | Accept JSON log data |
| `/logs` | GET | Retrieve log lines by time range |
| `/info` | GET | Service capabilities, limits, uptime |
| `/version` | GET | Semver version as JSON |

**Input**: JSON list of strings, or list of objects with `metadata` and
`line` keys. Metadata is stored but not returned in v1.

**Retrieval**: Time range only in v1. Uses log timestamp if parseable,
insertion time otherwise. Returns log line text only.

**Limits**: 16KB per line. Total storage cap with FIFO eviction.

**Future**: Regex search (reverse indexing), metadata on read, advanced
filters. See IMPLEMENTATION.md for full spec.

## SUT: mock twitter clone

The application validates the framework. Its capabilities for v0.1.0:

* Users can view posts without logging in
* Users must log in to post
* Posts may be up to 256 ASCII characters
* Posts must contain at least one non-whitespace character
* Duplicate posts by the same user are rejected within 10 seconds;
  identical content from different users is always accepted

## Design reference

See [IMPLEMENTATION.md](IMPLEMENTATION.md) for prerequisites, container
inventory, configuration, CI/CD workflows, test plan, and known
limitations.
