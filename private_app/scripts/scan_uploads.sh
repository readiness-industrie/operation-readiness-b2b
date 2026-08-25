#!/bin/sh
set -eu
mkdir -p /tmp/readiness-clamav
freshclam --stdout --datadir=/tmp/readiness-clamav || true
export CLAMAV_DATABASE_DIR=/tmp/readiness-clamav
python manage.py scan_uploads
