import hashlib
import io
import json
import zipfile
from pathlib import Path

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from operations.db import rls_context
from operations.models import EvidenceDocument


class Command(BaseCommand):
    help = "Crée une sauvegarde applicative chiffrée (données + documents)."

    def add_arguments(self, parser):
        parser.add_argument("--output", help="Chemin du fichier .ri-backup")
        parser.add_argument("--to-storage", action="store_true", help="Copie aussi la sauvegarde chiffrée dans le stockage privé configuré")

    def handle(self, *args, **options):
        settings.BACKUP_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
        output = Path(options["output"] or settings.BACKUP_DIR / f"readiness-{timezone.now():%Y%m%d-%H%M%S}.ri-backup")
        output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        data_buffer = io.StringIO()
        with rls_context(owner=True):
            call_command("dumpdata", "operations", indent=2, stdout=data_buffer)
            documents = list(EvidenceDocument.objects.all())
            archive_buffer = io.BytesIO()
            with zipfile.ZipFile(archive_buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("data.json", data_buffer.getvalue())
                manifest = {"created_at": timezone.now().isoformat(), "document_count": len(documents), "format": 1, "files": {}}
                for document in documents:
                    archive_name = f"documents/{document.id}"
                    with document.file.open("rb") as source:
                        raw = source.read()
                    archive.writestr(archive_name, raw)
                    manifest["files"][str(document.id)] = {"storage_name": document.file.name, "sha256": hashlib.sha256(raw).hexdigest()}
                archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        encrypted = Fernet(settings.BACKUP_ENCRYPTION_KEY.encode()).encrypt(archive_buffer.getvalue())
        output.write_bytes(encrypted)
        output.chmod(0o600)
        digest = hashlib.sha256(encrypted).hexdigest()
        output.with_suffix(output.suffix + ".sha256").write_text(f"{digest}  {output.name}\n")
        if options["to_storage"]:
            storage_key = f"backups/{output.name}"
            if default_storage.exists(storage_key):
                raise RuntimeError(f"La clé de sauvegarde existe déjà : {storage_key}")
            default_storage.save(storage_key, ContentFile(encrypted))
            self.stdout.write(self.style.SUCCESS(f"Stockage privé : {storage_key}"))
        self.stdout.write(self.style.SUCCESS(str(output)))
