#!/bin/sh
set -eu
exec gunicorn readiness.wsgi:application \
  --bind "0.0.0.0:${PORT:-10000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --threads 2 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
