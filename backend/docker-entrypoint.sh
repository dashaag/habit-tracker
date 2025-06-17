#!/bin/sh

set -e

echo "Applying database migrations..."
alembic upgrade head
echo "Migrations applied."

# If no command is provided, default to running uvicorn.
if [ -z "$1" ]; then
    set -- uvicorn app.main:app --host 0.0.0.0 --port 5001
fi

exec "$@"
