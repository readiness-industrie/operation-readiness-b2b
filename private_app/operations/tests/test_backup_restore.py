import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet
from django.test import SimpleTestCase


class BackupRestoreWindowsTests(SimpleTestCase):
    def test_backup_restore_recovers_fictional_document(self):
        app = Path(__file__).resolve().parents[2]
        python = sys.executable
        secret = secrets.token_urlsafe(48)
        field_key = Fernet.generate_key().decode()
        backup_key = Fernet.generate_key().decode()

        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            source = base / "source"
            restored = base / "restored"
            source.mkdir()
            restored.mkdir()
            archive = base / "backup.ri-backup"

            def run(extra, *args):
                env = os.environ.copy()
                env.update(
                    {
                        "DEBUG": "true",
                        "SECRET_KEY": secret,
                        "FIELD_ENCRYPTION_KEY": field_key,
                        "BACKUP_ENCRYPTION_KEY": backup_key,
                    }
                )
                env.update(extra)
                completed = subprocess.run(
                    [python, "manage.py", *args],
                    cwd=app,
                    env=env,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
                return completed.stdout

            source_env = {"SQLITE_PATH": str(source / "db.sqlite3"), "PRIVATE_MEDIA_ROOT": str(source / "media")}
            restored_env = {"SQLITE_PATH": str(restored / "db.sqlite3"), "PRIVATE_MEDIA_ROOT": str(restored / "media")}
            run(source_env, "migrate", "--noinput")
            run(source_env, "seed_restore_smoke")
            run(source_env, "backup_readiness", "--output", str(archive))
            run(restored_env, "migrate", "--noinput")
            run(restored_env, "restore_readiness", "--input", str(archive), "--confirm-empty")
            output = run(restored_env, "verify_restore_smoke")
            self.assertIn("compte, client, mission et document intacts", output)
