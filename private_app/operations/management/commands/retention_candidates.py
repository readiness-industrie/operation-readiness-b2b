from django.core.management.base import BaseCommand
from django.utils import timezone

from operations.db import rls_context
from operations.enums import MissionState
from operations.models import Mission


class Command(BaseCommand):
    help = "Liste sans modifier les missions arrivées à échéance de rétention."

    def handle(self, *args, **options):
        found = 0
        with rls_context(owner=True):
            missions = Mission.objects.filter(state__in=[MissionState.COMPLETED, MissionState.REFUSED], is_archived=False).select_related("tenant")
            now = timezone.now()
            for mission in missions:
                reference = mission.ended_at or mission.updated_at
                age_days = (now - reference).days
                if age_days >= mission.tenant.mission_retention_days:
                    found += 1
                    self.stdout.write(
                        f"{mission.id} | {mission.tenant.name} | {mission.code} | {age_days} jours | "
                        f"confirmation requise: DELETE-{mission.code}"
                    )
        self.stdout.write(self.style.SUCCESS(f"{found} candidate(s). Aucune donnée modifiée."))
