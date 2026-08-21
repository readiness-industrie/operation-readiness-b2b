#!/bin/sh
set -eu

TEST_DIR="$(mktemp -d)"
trap 'rm -rf "$TEST_DIR"' EXIT

export DEBUG=true
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export FIELD_ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
export BACKUP_ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"

export SQLITE_PATH="$TEST_DIR/source.sqlite3"
export PRIVATE_MEDIA_ROOT="$TEST_DIR/source-media"
python manage.py migrate --noinput >/dev/null
python manage.py seed_restore_smoke >/dev/null
python manage.py backup_readiness --output "$TEST_DIR/backup.ri-backup" >/dev/null

export SQLITE_PATH="$TEST_DIR/restored.sqlite3"
export PRIVATE_MEDIA_ROOT="$TEST_DIR/restored-media"
python manage.py migrate --noinput >/dev/null
python manage.py restore_readiness --input "$TEST_DIR/backup.ri-backup" --confirm-empty >/dev/null
python manage.py verify_restore_smoke
