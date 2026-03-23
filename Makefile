# pytest-framework Makefile
# Simplifies bootstrap, build, deploy, test, and teardown operations.
#
# Usage:
#   make bootstrap    Generate .env and prepare data directory
#   make build        Build all container images
#   make up           Start all services (framework + SUT)
#   make down         Stop and remove all containers
#   make restart      Rebuild and restart everything
#   make test         Run all tests (unit, integration, e2e)
#   make test-unit    Run unit tests only
#   make test-int     Run integration tests only
#   make test-e2e     Run e2e tests only
#   make lint         Run ruff linter
#   make status       Show container status and health
#   make logs         Tail logs from all containers
#   make clean        Stop containers and remove data files
#   make help         Show this help

.PHONY: bootstrap build up down restart test test-unit test-int test-e2e \
        lint status logs clean help

COMPOSE := docker compose
COMPOSE_FILE := docker-compose.yml
PYTEST := python -m pytest

# -- Bootstrap -----------------------------------------------------------

bootstrap: .env data
	@echo "Bootstrap complete."

.env:
	@bash scripts/generate_env.sh --force

data:
	@mkdir -p data

# -- Build ---------------------------------------------------------------

build:
	$(COMPOSE) -f $(COMPOSE_FILE) build

# -- Deploy --------------------------------------------------------------

up: bootstrap
	$(COMPOSE) -f $(COMPOSE_FILE) up -d
	@echo "Waiting for health checks..."
	@sleep 5
	@$(COMPOSE) -f $(COMPOSE_FILE) ps

down:
	$(COMPOSE) -f $(COMPOSE_FILE) down

restart: down build up

# -- Test ----------------------------------------------------------------

test:
	$(PYTEST) tests/ -v

test-unit:
	$(PYTEST) tests/unit/ -v

test-int:
	$(PYTEST) tests/integration/ -v

test-e2e:
	$(PYTEST) tests/e2e/ -v

# -- Lint ----------------------------------------------------------------

lint:
	ruff check .

# -- Observability -------------------------------------------------------

status:
	$(COMPOSE) -f $(COMPOSE_FILE) ps

logs:
	$(COMPOSE) -f $(COMPOSE_FILE) logs -f --tail=50

# -- Cleanup -------------------------------------------------------------

clean: down
	rm -f data/*.db
	@echo "Containers stopped, database files removed."

# -- Help ----------------------------------------------------------------

help:
	@head -n 18 Makefile | grep '^#' | sed 's/^# *//'
