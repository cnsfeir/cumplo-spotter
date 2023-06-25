# Base container with Python 3.11 official image
FROM python:3.11-slim AS base

# Set up environment variables
ENV LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# Set up base work directory
WORKDIR /app

# Build container with Poetry
FROM base AS builder

# Set Poetry version
ENV POETRY_VERSION=1.3.2

# Set up Pip environment variables
ENV PIP_NO_CACHE_DIR=off \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install OS package dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock ./

# Export dependencies from Poetry and install them with pip
RUN poetry export --format requirements.txt --output requirements.txt

# Final container with the app
FROM base AS final

# Copy requirements from builder
COPY --from=builder /app/requirements.txt /app/requirements.txt

# Create Python virtual environment
RUN python -m venv /venv

# So we can use the executables from the virtual environment
ENV PATH="/venv/bin:$PATH"

# Export dependencies from Poetry and install them with pip
RUN /venv/bin/pip install -r requirements.txt && rm requirements.txt

# Copy the rest of the code
COPY . ./

# Run the app
CMD exec uvicorn --host 0.0.0.0 --port 8080 main:app