from django.core.management.base import BaseCommand

from operations.db import rls_context
from operations.models import Prerequisite
from operations.services import apply_priority


class Command(BaseCommand):
    help = "Recalcule toutes les priorités à partir des paramètres courants."

    def handle(self, *args, **options):
        count = 0
        with rls_context(owner=True):
            for prerequisite in Prerequisite.objects.all().iterator():
                apply_priority(prerequisite)
                prerequisite.full_clean()
                prerequisite.save(update_fields=["priority_level", "priority_score", "priority_explanation", "priority_calculated_at", "updated_at"])
                count += 1
        self.stdout.write(self.style.SUCCESS(f"{count} priorité(s) recalculée(s)."))
