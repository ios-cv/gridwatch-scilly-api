.PHONY: nothing start-docker stop-docker clean-docker run-api run-tasks

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

nothing:
	@echo Please specify a make target.

start-docker: ## Starts docker containers of dependencies for local development and testing,
	@echo Starting docker containers of dependencies
	docker-compose run --rm start_dependencies

	@echo Ensuring necessary databases exist...
	@echo - gridwatch
	@docker run -it --link gridwatch-scilly-postgres:postgres --network gridwatch-scilly-api_gridwatch-scilly -ePGPASSWORD=mysecretpassword --rm postgres sh -c \
 'echo "SELECT '"'CREATE DATABASE gridwatch'"' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '"'gridwatch'"')\gexec" | psql -h "database" -p "5432" -U postgres'

	@echo Done

stop-docker: ## Stops docker containers of dependencies for local development and testing.
	@echo Stopping docker containers of dependencies
	docker-compose stop

clean-docker: ## Deletes the docker containers of dependencies for local development and testing.
	@echo Removing docker containers
	docker-compose down -v
	docker-compose rm -v

run-api: ## Runs the REST API web service.
	uvicorn --app-dir ${ROOT}src main:app --reload

run-tasks: ## Runs the background task runner.
	PYTHONPATH=${ROOT}src python -m src.tasks

test: ## Runs the test suite.
	pytest

fix-style: ## Fixes code style violations.
	black src

