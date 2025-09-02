#!/bin/bash

# RUN_PORT=${PORT:-8000}
# RUN_HOST=${HOST:-0.0.0.0}

# gunicorn -k uvicorn.workers.UvicornWorker -b $RUN_HOST:$RUN_PORT core.main:app --reload

set -e

RUN_PORT=${PORT:-8000}
RUN_HOST=${HOST:-0.0.0.0}

# Match development (case-insensitive)
case "$ENV" in
  development|Development|DEVELOPMENT)
    echo "[entrypoint] Development mode: running uvicorn with debugpy wait-for-client"
    # Ensure debugpy installed; waits until debugger attaches on 5678
    exec python -Xfroxen_modules=off -m debugpy  --wait-for-client --listen 0.0.0.0:5678 -m uvicorn core.main:app \
        --host "$RUN_HOST" --port "$RUN_PORT" --reload
    ;;
  *)
    echo "[entrypoint] Production mode: gunicorn"
    exec gunicorn -k uvicorn.workers.UvicornWorker -b "$RUN_HOST:$RUN_PORT" core.main:app --reload
    ;;
esac