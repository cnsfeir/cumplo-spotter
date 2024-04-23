# Base container with Python 3.11 official image
FROM python:3.11-bullseye AS base

# Set up environment variables
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# Set up base work directory
WORKDIR /app

# =================================================================

# Build container with Poetry
FROM base AS builder

# Set Poetry version and environment variables
ENV POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

# Set up Pip environment variables
ENV PIP_NO_CACHE_DIR=off \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install OS package dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Install Keyrings support for Google Artifact Registry
RUN poetry self add keyrings.google-artifactregistry-auth

# Copy only the dependencies related files
COPY pyproject.toml poetry.lock ./
COPY cumplo_spotter ./cumplo_spotter

# Define the service account key as a build argument.
ARG CUMPLO_PYPI_BASE64_KEY

# Set the service account key location to a temporary file.
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account-credentials.json

# Save the service account key contents from the build argument to the temporary file.
RUN echo "$CUMPLO_PYPI_BASE64_KEY" | base64 -d> "$GOOGLE_APPLICATION_CREDENTIALS"

# Install base dependencies + REST API dependencies
RUN poetry install --without dev --with rest-api && rm -rf /tmp/poetry_cache

# Remove the service acccount key file.
RUN rm "$GOOGLE_APPLICATION_CREDENTIALS"

# =================================================================

# Final container with the app
FROM base AS final

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Activate the virtual environment
ENV PATH=/app/.venv/bin:$PATH

# Import the entrypoint script and make it executable
COPY entrypoint.sh /usr/bin/
RUN chmod +x /usr/bin/entrypoint.sh
ENTRYPOINT ["/usr/bin/entrypoint.sh"]

# Copy the rest of the code
COPY . ./

# Run the app
CMD exec uvicorn --workers 8 --host 0.0.0.0 --port 8080 cumplo_spotter.main:app
