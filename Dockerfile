# Base container with Python 3.12 official image
FROM python:3.12-slim-bookworm AS base

# Set up Python environment variables
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# Set up base work directory
WORKDIR /app

# =================================================================

# Build container with UV
FROM base AS builder

# Set pip environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_NO_CACHE_DIR=off

# Install OS package dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Install Keyrings support for Google Artifact Registry
RUN uv pip install keyrings.google-artifactregistry-auth

# Copy only the dependencies related files
COPY pyproject.toml uv.lock ./
COPY cumplo_spotter ./cumplo_spotter

# Define the service account key as a build argument.
ARG CUMPLO_PYPI_BASE64_KEY

# Set the service account key location to a temporary file.
ENV GOOGLE_APPLICATION_CREDENTIALS=/tmp/service_account_credentials.json

# Save the service account key contents from the build argument to the temporary file.
RUN echo "$CUMPLO_PYPI_BASE64_KEY" | base64 -d> "$GOOGLE_APPLICATION_CREDENTIALS"

# Install dependencies and the project globally
RUN uv pip sync && \
    rm -rf /root/.cache/uv && \
    rm -rf /tmp/uv_cache && \
    rm -rf "$GOOGLE_APPLICATION_CREDENTIALS"

# =================================================================

# Final container with the app
FROM base AS final

# Copy global site-packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the rest of the code
COPY . ./

# Run the app
CMD exec uvicorn --workers 8 --host 0.0.0.0 --port 8080 cumplo_spotter.main:app
