#!/bin/sh
set -eu
python manage.py backup_readiness --to-storage
