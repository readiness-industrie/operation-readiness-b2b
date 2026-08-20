from django.core.management.base import BaseCommand, CommandError

from operations.db import rls_context
from operations.models import EvidenceDocument, Mission, Organization, User


class Command(BaseCommand):
    help = "Vérifie le jeu restauré, y compris le contenu du document."

    def handle(self, *args, **options):
        with rls_context(owner=True):
            if User.objects.filter(username="restore-smoke-owner").count() != 1:
                raise CommandError("Compte Owner non restauré.")
            if Organization.objects.filter(slug="restore-smoke").count() != 1:
                raise CommandError("Client fictif non restauré.")
            if Mission.objects.filter(code="RESTORE-001").count() != 1:
                raise CommandError("Mission fictive non restaurée.")
            document = EvidenceDocument.objects.get(original_name="restore-proof.pdf")
            with document.file.open("rb") as source:
                if b"restore-smoke" not in source.read():
                    raise CommandError("Contenu du document restauré incorrect.")
        self.stdout.write(self.style.SUCCESS("Restauration vérifiée : compte, client, mission et document intacts."))
