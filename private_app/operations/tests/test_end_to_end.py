from datetime import timedelta
from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from operations.models import Mission, Organization, Prerequisite, PublicationSnapshot

from .factories import login_client, owner


class FirstRealMissionEndToEndTests(TestCase):
    def setUp(self):
        self.owner = owner("herve-e2e")
        self.client = Client()
        login_client(self.client, self.owner)

    def assert_redirect(self, response):
        self.assertEqual(response.status_code, 302, response.content.decode(errors="ignore"))

    @staticmethod
    def local_datetime(value):
        return timezone.localtime(value).strftime("%Y-%m-%dT%H:%M")

    def transition(self, mission, target_state, reason):
        response = self.client.post(
            reverse("mission_transition", args=[mission.id]),
            {"target_state": target_state, "reason": reason},
        )
        self.assert_redirect(response)
        mission.refresh_from_db()
        self.assertEqual(mission.state, target_state)

    def test_new_client_j10_runs_from_qualification_to_closure(self):
        response = self.client.post(
            reverse("organization_create"),
            {
                "name": "Client Démonstration",
                "slug": "client-demonstration",
                "is_active": "on",
                "mission_retention_days": 365,
                "document_retention_days": 365,
                "audit_retention_days": 730,
                "privacy_notes": "Données fictives de test",
            },
        )
        self.assert_redirect(response)
        organization = Organization.objects.get(slug="client-demonstration")
        protected_at = timezone.now() + timedelta(days=10)

        response = self.client.post(
            reverse("mission_create"),
            {
                "tenant": organization.id,
                "code": "DEMO-001",
                "project_name": "Installation ligne fictive",
                "site_name": "Site test",
                "protected_at": self.local_datetime(protected_at),
                "approximate_open_count": 1,
                "approximate_critical_count": 1,
                "interlocutor_count": 1,
                "previous_steps": "Premier appel réalisé",
                "coordinates_available": "YES",
                "closure_criteria_available": "YES",
                "contact_authorizations_available": "YES",
                "client_expectation": "Poursuivre et documenter sans décision technique",
            },
        )
        self.assert_redirect(response)
        mission = Mission.objects.get(tenant=organization, code="DEMO-001")

        reason = {"change_reason": "Validation du dossier fictif", "change_category": "MISSION_EVOLUTION"}
        response = self.client.post(
            reverse("mission_acceptance", args=[mission.id]),
            {
                "acceptance_know": "YES",
                "acceptance_scope": "YES",
                "acceptance_authority": "YES",
                "acceptance_responsibility": "YES",
                "acceptance_result": "ACCEPTABLE",
                "acceptance_note": "Périmètre conforme",
                **reason,
            },
        )
        self.assert_redirect(response)
        mission.refresh_from_db()
        self.assertEqual(mission.indicative_amount, Decimal("1875.00"))

        response = self.client.post(
            reverse("mission_feasibility", args=[mission.id]),
            {
                "operational_window_hours": 240,
                "expected_active_prerequisites": 1,
                "expected_p0_p1": 1,
                "expected_actions": 4,
                "committed_load_hours": 0,
                "operator_available_hours": 20,
                "manual_load_estimate_hours": 2,
                "reduced_scope_proposal": "",
                "feasibility_result": "FEASIBLE",
                "feasibility_note": "Charge compatible",
                **reason,
            },
        )
        self.assert_redirect(response)
        self.transition(mission, "FEASIBILITY_VALIDATED", "Contrôles validés")
        self.transition(mission, "AWAITING_PAYMENT", "Offre acceptée")

        response = self.client.post(
            reverse("mission_financial", args=[mission.id]),
            {
                "commercial_status": "Accepté",
                "mission_type": "S",
                "agreed_amount": 1500,
                "payment_expected_amount": 750,
                "payment_received_amount": 750,
                "payment_received_at": self.local_datetime(timezone.now()),
                "financial_trigger_required": "on",
                "financial_exception_reason": "",
                **reason,
            },
        )
        self.assert_redirect(response)
        self.transition(mission, "ONBOARDING", "Paiement reçu")

        response = self.client.post(
            reverse("contact_create", args=[mission.id]),
            {
                "full_name": "Contact Fictif",
                "organization_name": "Client Démonstration",
                "job_title": "Chef de projet",
                "email": "contact@example.invalid",
                "phone": "0102030405",
                "authorized_for_contact": "YES",
                "authorization_source": "Mandat client fictif",
                "internal_note": "",
            },
        )
        self.assert_redirect(response)
        contact = mission.contacts.get()

        response = self.client.post(
            reverse("prerequisite_create", args=[mission.id]),
            {
                "code": "PR-001",
                "title": "Alimentation électrique disponible",
                "client_closure_criterion": "Confirmation écrite et photo selon le client",
                "useful_deadline": self.local_datetime(protected_at),
                "client_criticality": 3,
                "client_declared_blocking": "on",
                "primary_contact": contact.id,
                "secondary_contact": "",
                "escalation_contact": contact.id,
                "contact_authorization_confirmed": "YES",
                "initial_state": "Ouvert, confirmation absente",
                "initial_previous_actions": "Premier mail envoyé par le client",
                "taken_over_at": self.local_datetime(timezone.now()),
                "state": "ACTION_PLANNED",
                "confirmation_score": 3,
                "dependency_score": 2,
                "inertia_score": 1,
                "next_action": "Appeler le contact autorisé",
                "next_action_at": self.local_datetime(timezone.now() + timedelta(hours=2)),
                "expected_event": "Confirmation écrite",
                "client_decision_expected": "",
                "escalation_rule": "Niveau 3 si retard annoncé",
                "override_reason": "",
                "client_published": "on",
                "client_summary": "Confirmation encore attendue",
                "change_reason": "Onboarding initial",
                "change_category": "MISSION_EVOLUTION",
            },
        )
        self.assert_redirect(response)
        prerequisite = Prerequisite.objects.get(mission=mission, code="PR-001")
        self.assertEqual(prerequisite.primary_contact, contact)

        self.assert_redirect(self.client.post(reverse("mission_capture_t0", args=[mission.id])))
        self.transition(mission, "READY_TO_PURSUE", "Onboarding complet")
        self.transition(mission, "ACTIVE", "Démarrage réel après paiement")

        response = self.client.post(
            reverse("prerequisite_action", args=[prerequisite.id]),
            {
                "event_type": "RESPONSE",
                "occurred_at": self.local_datetime(timezone.now()),
                "channel": "Téléphone",
                "factual_result": "Normalement ce sera bon",
                "next_state": "RESPONSE_TO_REVIEW",
                "next_action": "Demander la preuve définie",
                "next_action_at": self.local_datetime(timezone.now() + timedelta(hours=3)),
                "expected_event": "Photo et confirmation écrite",
            },
        )
        self.assert_redirect(response)
        prerequisite.refresh_from_db()
        self.assertNotEqual(prerequisite.state, "CONFIRMED")

        response = self.client.post(
            reverse("prerequisite_action", args=[prerequisite.id]),
            {
                "event_type": "CONFIRMATION",
                "occurred_at": self.local_datetime(timezone.now()),
                "channel": "E-mail",
                "factual_result": "Critère client reçu et satisfait",
                "next_state": "CONFIRMED",
                "closure_criterion_satisfied": "on",
                "next_action": "",
                "next_action_at": "",
                "expected_event": "",
            },
        )
        self.assert_redirect(response)

        self.assert_redirect(
            self.client.post(
                reverse("mission_publish", args=[mission.id]),
                {"summary_note": "Point confirmé selon critère client"},
            )
        )
        self.assert_redirect(
            self.client.post(
                reverse("mission_close", args=[mission.id]),
                {
                    "closure_reason": "Tous les prérequis convenus sont clôturés",
                    "transition_reason": "Fin de mission documentée",
                },
            )
        )

        mission.refresh_from_db()
        prerequisite.refresh_from_db()
        self.assertEqual(mission.state, "COMPLETED")
        self.assertTrue(mission.payment_satisfied)
        self.assertIsNotNone(mission.t0_captured_at)
        self.assertIsNotNone(mission.activated_at)
        self.assertIsNotNone(mission.ended_at)
        self.assertTrue(mission.closure_report)
        self.assertEqual(prerequisite.state, "CONFIRMED")
        self.assertEqual(prerequisite.actions.count(), 2)
        self.assertEqual(PublicationSnapshot.objects.filter(mission=mission).count(), 1)
