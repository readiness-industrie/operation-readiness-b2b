import os
import shutil
import subprocess
import tempfile

from django.core.management.base import BaseCommand, CommandError

from operations.audit import audit_event
from operations.db import rls_context
from operations.enums import DocumentScanState
from operations.models import EvidenceDocument


class Command(BaseCommand):
    help = "Analyse les uploads en quarantaine avec clamdscan."

    def handle(self, *args, **options):
        scanner = shutil.which("clamdscan") or shutil.which("clamscan")
        if not scanner:
            raise CommandError("clamdscan introuvable : aucun document n'a été sorti de quarantaine.")
        with rls_context(owner=True):
            documents = list(EvidenceDocument.objects.filter(scan_state=DocumentScanState.PENDING))
            for document in documents:
                with tempfile.NamedTemporaryFile() as target:
                    with document.file.open("rb") as source:
                        shutil.copyfileobj(source, target)
                    target.flush()
                    command = [scanner, "--no-summary"]
                    database_dir = os.getenv("CLAMAV_DATABASE_DIR")
                    if database_dir and scanner.endswith("clamscan"):
                        command.append(f"--database={database_dir}")
                    command.append(target.name)
                    result = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
                if result.returncode == 0:
                    document.scan_state = DocumentScanState.SAFE
                    document.scan_details = "ClamAV : aucun contenu malveillant détecté"
                elif result.returncode == 1:
                    document.scan_state = DocumentScanState.REJECTED
                    document.scan_details = "ClamAV : contenu malveillant détecté"
                else:
                    document.scan_details = "ClamAV : erreur d'analyse, fichier maintenu en quarantaine"
                document.save(update_fields=["scan_state", "scan_details", "updated_at"])
                audit_event(operation="DOCUMENT_SCAN", result=document.scan_state, tenant=document.tenant, resource_type="EvidenceDocument", resource_id=document.id)
        self.stdout.write(self.style.SUCCESS(f"{len(documents)} document(s) traité(s)."))
