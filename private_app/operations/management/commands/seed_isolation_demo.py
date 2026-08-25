import os
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from operations.db import rls_context
from operations.enums import (
    AcceptanceResult,
    FeasibilityResult,
    MissionState,
    PrerequisiteState,
    TriState,
    UserRole,
)
from operations.models import Contact, Mission, MissionAccess, Organization, User
from operations.services import capture_t0, create_prerequisite, publish_client_snapshot


class Command(BaseCommand):
    help = "Crée exclusivement les clients fictifs Alpha/Beta pour les tests d'isolation."

    def handle(self, *args, **options):
        if not settings.DEBUG and os.getenv("ALLOW_DEMO_SEED") != "true":
            raise CommandError("Commande bloquée en production sans ALLOW_DEMO_SEED=true.")
        password = os.getenv("DEMO_VIEWER_PASSWORD", "Demo-Readiness-2026!")
        with rls_context(owner=True):
            owner = User.objects.filter(role=UserRole.OWNER).first()
            if not owner:
                raise CommandError("Créez d'abord le compte Owner.")
            for label in ("alpha", "beta"):
                tenant, _ = Organization.objects.get_or_create(slug=f"client-{label}", defaults={"name": f"CLIENT {label.upper()} — FICTIF"})
                viewer, created = User.objects.get_or_create(
                    username=f"viewer-{label}",
                    defaults={"email": f"viewer-{label}@example.invalid", "role": UserRole.CLIENT_VIEWER, "tenant": tenant},
                )
                if created:
                    viewer.set_password(password)
                    viewer.save()
                mission, created = Mission.objects.get_or_create(
                    tenant=tenant,
                    code=f"{label.upper()}-001",
                    defaults={
                        "project_name": f"Mission fictive {label.title()}",
                        "protected_at": timezone.now() + timedelta(days=10),
                        "approximate_open_count": 1,
                        "acceptance_know": TriState.YES,
                        "acceptance_scope": TriState.YES,
                        "acceptance_authority": TriState.YES,
                        "acceptance_responsibility": TriState.YES,
                        "acceptance_result": AcceptanceResult.ACCEPTABLE,
                        "feasibility_result": FeasibilityResult.FEASIBLE,
                        "financial_trigger_required": False,
                        "financial_exception_reason": "Jeu de données fictif non commercial",
                        "state": MissionState.READY_TO_PURSUE,
                    },
                )
                contact, _ = Contact.objects.get_or_create(
                    tenant=tenant,
                    mission=mission,
                    full_name=f"Contact {label.title()} fictif",
                    defaults={"email": f"contact-{label}@example.invalid", "authorized_for_contact": TriState.YES},
                )
                if created:
                    create_prerequisite(
                        mission=mission,
                        actor=owner,
                        data={
                            "code": "PR-001",
                            "title": f"Prérequis confidentiel {label.title()}",
                            "client_closure_criterion": "Confirmation écrite définie par le client fictif",
                            "useful_deadline": mission.protected_at,
                            "client_criticality": 2,
                            "primary_contact": contact,
                            "contact_authorization_confirmed": TriState.YES,
                            "initial_state": "Ouvert au T0",
                            "taken_over_at": timezone.now(),
                            "state": PrerequisiteState.ACTION_PLANNED,
                            "confirmation_score": 3,
                            "dependency_score": 1,
                            "inertia_score": 1,
                            "next_action": "Contacter le responsable fictif",
                            "next_action_at": timezone.now() + timedelta(hours=2),
                            "expected_event": "Réponse écrite",
                            "client_published": True,
                            "client_summary": "Point fictif encore ouvert",
                        },
                    )
                    capture_t0(mission=mission, actor=owner)
                    publish_client_snapshot(mission=mission, actor=owner, summary_note=f"Données fictives {label.title()}")
                MissionAccess.objects.get_or_create(tenant=tenant, user=viewer, mission=mission)
        self.stdout.write(self.style.SUCCESS("Clients fictifs Alpha/Beta créés. Ne jamais utiliser ces données comme données réelles."))
