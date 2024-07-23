FROM mcr.microsoft.com/vscode/devcontainers/python:3.12-bookworm

# Set up Python environment variables
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# Set up base work directory dynamically
ARG WORKSPACE_FOLDER
WORKDIR /workspaces/${WORKSPACE_FOLDER}

# Set Poetry and pip environment variables
ARG POETRY_VERSION
ENV POETRY_VERSION=${POETRY_VERSION} \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_NO_CACHE_DIR=off

# Install OS package dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Install Keyrings support for Google Artifact Registry
RUN poetry self add keyrings.google-artifactregistry-auth

# Copy only the dependencies related files
COPY pyproject.toml poetry.lock ./
COPY cumplo_spotter ./cumplo_spotter

# Add the Google Cloud credentials
COPY cumplo_pypi_credentials.json /tmp/cumplo_pypi_credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/cumplo_pypi_credentials.json

# Install all dependencies
RUN poetry install
