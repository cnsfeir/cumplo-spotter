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

# Set pip environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_NO_CACHE_DIR=off

# Prefer system python for UV
ENV UV_PYTHON_PREFERENCE=only-system

# Install OS package dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install Keyrings support for Google Artifact Registry
RUN uv pip install keyrings.google-artifactregistry-auth --system
RUN uv pip install cumplo-common --keyring-provider subprocess --extra-index-url https://oauth2accesstoken@us-central1-python.pkg.dev/cumplo-scraper/cumplo-pypi/simple --system

# Copy only the dependencies related files
# COPY pyproject.toml uv.lock ./
COPY pyproject.toml ./
COPY cumplo_spotter ./cumplo_spotter

# Add the Google Cloud credentials
COPY cumplo_pypi_credentials.json /tmp/cumplo_pypi_credentials.json
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/cumplo_pypi_credentials.json

# Install all dependencies
RUN uv pip sync pyproject.toml --system
