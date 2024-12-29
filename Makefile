include .env
export

PYTHON_VERSION := $(shell python -c "print(open('.python-version').read().strip())")
INSTALLED_VERSION := $(shell python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

# Activates the project configuration and logs in to gcloud
.PHONY: login
login:
	@gcloud config configurations activate $(PROJECT_ID)
	@gcloud auth application-default login

# Runs linters
.PHONY: lint
lint:
	@ruff check --fix
	@ruff format
	@mypy --config-file pyproject.toml .

# Builds the Docker image
.PHONY: build
build:
	@docker compose build cumplo-spotter --build-arg CUMPLO_PYPI_BASE64_KEY=`base64 -i cumplo_pypi_credentials.json`

# Starts the Docker container
.PHONY: start
start:
	@docker compose up -d cumplo-spotter

# Stops the Docker container
.PHONY: down
down:
	@docker compose down

# Updates the common library
.PHONY: update-common
update-common:
	@rm -rf .venv
	@poetry cache clear --no-interaction --all cumplo-pypi
	@poetry update
