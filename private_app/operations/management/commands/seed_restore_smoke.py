from datetime import timedelta

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from operations.db import rls_context
from operations.enums import (
    AcceptanceResult,
    FeasibilityResult,
    MissionState,
    UserRole,
)
from operations.models import Mission, Organization, User
from operations.uploads import create_document


class Command(BaseCommand):
    help = "Crée un jeu strictement fictif destiné au test sauvegarde/restauration."

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("Commande de test interdite hors DEBUG.")
        with rls_context(owner=True):
            owner = User.objects.create_user(
                username="restore-smoke-owner",
                email="restore-smoke@example.invalid",
                password="Restore-Smoke-Test-Password!",
                role=UserRole.OWNER,
            )
            tenant = Organization.objects.create(name="Restore Smoke Fictif", slug="restore-smoke")
            mission = Mission.objects.create(
                tenant=tenant,
                code="RESTORE-001",
                project_name="Test restauration fictif",
                protected_at=timezone.now() + timedelta(days=10),
                acceptance_result=AcceptanceResult.ACCEPTABLE,
                feasibility_result=FeasibilityResult.FEASIBLE,
                financial_trigger_required=False,
                financial_exception_reason="Test",
                state=MissionState.QUALIFICATION,
            )
            create_document(
                uploaded=SimpleUploadedFile("restore-proof.pdf", b"%PDF-1.4\nrestore-smoke\n%%EOF", content_type="application/pdf"),
                mission=mission,
                prerequisite=None,
                actor=owner,
            )
        self.stdout.write(self.style.SUCCESS("Jeu de restauration créé."))
