from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from operations.audit import audit_event
from operations.db import rls_context
from operations.enums import DocumentScanState, MissionState
from operations.models import Mission


class Command(BaseCommand):
    help = "Exécute une suppression contrôlée arrivée à rétention, avec confirmation exacte."

    def add_arguments(self, parser):
        parser.add_argument("--mission", required=True)
        parser.add_argument("--confirm", required=True)
        parser.add_argument("--reason", required=True)

    def handle(self, *args, **options):
        with rls_context(owner=True), transaction.atomic():
            try:
                mission = Mission.objects.select_for_update().select_related("tenant").get(id=options["mission"])
            except Mission.DoesNotExist as error:
                raise CommandError("Mission introuvable.") from error
            if options["confirm"] != f"DELETE-{mission.code}":
                raise CommandError("Confirmation incorrecte.")
            if mission.state not in {MissionState.COMPLETED, MissionState.REFUSED}:
                raise CommandError("Seule une mission terminée ou refusée peut être traitée.")
            reference = mission.ended_at or mission.updated_at
            age_days = (timezone.now() - reference).days
            if age_days < mission.tenant.mission_retention_days:
                raise CommandError("La durée de rétention configurée n'est pas atteinte.")
            for publication in mission.publications.filter(revoked_at__isnull=True):
                publication.revoked_at = timezone.now()
                publication.revoke_reason = options["reason"]
                publication.save(update_fields=["revoked_at", "revoke_reason", "updated_at"])
            mission.viewer_accesses.update(is_active=False)
            for document in mission.documents.all():
                if document.file and document.file.name and document.file.storage.exists(document.file.name):
                    document.file.storage.delete(document.file.name)
                document.file = ""
                document.original_name = "[supprimé selon politique de rétention]"
                document.is_client_shared = False
                document.shared_at = None
                document.scan_state = DocumentScanState.REJECTED
                document.scan_details = "Contenu supprimé selon politique de rétention"
                document.retention_deleted_at = timezone.now()
                document.retention_reason = options["reason"]
                document.save(
                    update_fields=[
                        "file",
                        "original_name",
                        "is_client_shared",
                        "shared_at",
                        "scan_state",
                        "scan_details",
                        "retention_deleted_at",
                        "retention_reason",
                        "updated_at",
                    ]
                )
            for contact in mission.contacts.all():
                contact.full_name = f"[contact supprimé {str(contact.id)[:8]}]"
                contact.organization_name = ""
                contact.job_title = ""
                contact.email = ""
                contact.phone = ""
                contact.authorization_source = ""
                contact.internal_note = ""
                contact.save()
            mission.is_archived = True
            mission.save(update_fields=["is_archived", "updated_at"])
            audit_event(
                operation="RETENTION_EXECUTE",
                result="SUCCESS",
                tenant=mission.tenant,
                resource_type="Mission",
                resource_id=mission.id,
                details={"reason": options["reason"], "age_days": age_days},
            )
        self.stdout.write(self.style.SUCCESS("Rétention exécutée : accès révoqués, documents supprimés, contacts pseudonymisés, audit conservé."))
