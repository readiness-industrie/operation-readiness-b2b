import hashlib
import io
import json
import tempfile
import zipfile
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from operations.db import rls_context
from operations.models import Mission


class Command(BaseCommand):
    help = "Restaure une sauvegarde dans une base migrée et vide. Refuse tout écrasement."

    def add_arguments(self, parser):
        parser.add_argument("--input")
        parser.add_argument("--storage-key")
        parser.add_argument("--confirm-empty", action="store_true")

    def handle(self, *args, **options):
        if not options["confirm_empty"]:
            raise CommandError("Ajoutez --confirm-empty après avoir vérifié que la base cible est neuve et vide.")
        with rls_context(owner=True):
            if Mission.objects.exists():
                raise CommandError("Restauration refusée : la base contient déjà une mission.")
        if bool(options["input"]) == bool(options["storage_key"]):
            raise CommandError("Indiquez exactement un --input local ou un --storage-key privé.")
        if options["storage_key"]:
            with default_storage.open(options["storage_key"], "rb") as source:
                encrypted = source.read()
        else:
            encrypted = Path(options["input"]).read_bytes()
        try:
            raw_archive = Fernet(settings.BACKUP_ENCRYPTION_KEY.encode()).decrypt(encrypted)
        except InvalidToken as error:
            raise CommandError("Clé de sauvegarde incorrecte ou sauvegarde altérée.") from error
        with zipfile.ZipFile(io.BytesIO(raw_archive)) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            with tempfile.NamedTemporaryFile(suffix=".json") as fixture:
                fixture.write(archive.read("data.json"))
                fixture.flush()
                with rls_context(owner=True):
                    call_command("loaddata", fixture.name)
            for document_id, metadata in manifest["files"].items():
                content = archive.read(f"documents/{document_id}")
                if hashlib.sha256(content).hexdigest() != metadata["sha256"]:
                    raise CommandError(f"Intégrité incorrecte pour le document {document_id}.")
                storage_name = metadata["storage_name"]
                if default_storage.exists(storage_name):
                    raise CommandError(f"Le fichier cible existe déjà : {storage_name}")
                default_storage.save(storage_name, ContentFile(content))
        self.stdout.write(self.style.SUCCESS("Restauration terminée et intégrité des documents vérifiée."))
