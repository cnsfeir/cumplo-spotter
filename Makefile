include .env
export

PYTHON_VERSION := $(shell python -c "print(open('.python-version').read().strip())")
INSTALLED_VERSION := $(shell python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

# Checks if the installed Python version matches the required version
.PHONY: check_python_version
check_python_version:
	@if [ "$(PYTHON_VERSION)" != "$(INSTALLED_VERSION)" ]; then \
		echo "ERROR: Installed Python version $(INSTALLED_VERSION) does not match the required version $(PYTHON_VERSION)"; \
		exit 1; \
	fi

# Creates a virtual environment and installs dependencies
.PHONY: setup_venv
setup_venv:
	@make check_python_version
	@rm -rf .venv
	@poetry install

# Activates the project configuration and logs in to gcloud
.PHONY: login
login:
	@gcloud config configurations activate $(PROJECT_ID)
	@gcloud auth application-default login

# Runs linters
.PHONY: lint
lint:
	@if [ ! -d ".venv" ]; then \
		echo "Virtual environment not found. Creating one..."; \
		make setup_venv; \
	fi

	@poetry run python -m black --check --line-length=120 .
	@poetry run python -m isort --check --settings-file pyproject.toml .
	@poetry run python -m bandit --config=pyproject.toml -r -q .
	@poetry run python -m flake8 --config=.flake8
	@poetry run python -m pylint --rcfile=pyproject.toml --recursive=y --ignore=.venv .
	@poetry run python -m mypy --config-file pyproject.toml .

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
.PHONY: update_common
update_common:
	@rm -rf .venv
	@poetry cache clear --no-interaction --all cumplo-pypi
	@poetry update
