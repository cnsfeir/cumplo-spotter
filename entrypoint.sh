#!/bin/bash
set -e

# Activate virtual env
. /app/.venv/bin/activate

exec "$@"
