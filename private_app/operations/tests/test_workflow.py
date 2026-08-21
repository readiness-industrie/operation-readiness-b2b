from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from operations.enums import (
    AcceptanceResult,
    ActionEventType,
    MissionState,
    PrerequisiteState,
)
from operations.models import ChangeRecord, MissionStateHistory
from operations.priorities import feasibility_recommendation
from operations.services import (
    TransitionError,
    build_work_queue,
    capture_t0,
    escalate_prerequisite,
    record_action,
    transition_mission,
    update_instance,
)

from .factories import mission, owner, prerequisite, tenant


class CriticalWorkflowTests(TestCase):
    def setUp(self):
        self.owner = owner()
        self.tenant = tenant("Alpha")

    def test_payment_and_onboarding_guard_activation(self):
        project = mission(self.tenant)
        item = prerequisite(project, self.owner)
        with self.assertRaises(TransitionError):
            transition_mission(mission=project, target_state=MissionState.ACTIVE, actor=self.owner, reason="Tentative directe")
        transition_mission(mission=project, target_state=MissionState.FEASIBILITY_VALIDATED, actor=self.owner, reason="Filtres validés")
        transition_mission(mission=project, target_state=MissionState.AWAITING_PAYMENT, actor=self.owner, reason="Devis accepté")
        transition_mission(mission=project, target_state=MissionState.ONBOARDING, actor=self.owner, reason="Déclenchement sans paiement pour test documenté")
        capture_t0(mission=project, actor=self.owner)
        transition_mission(mission=project, target_state=MissionState.READY_TO_PURSUE, actor=self.owner, reason="Onboarding complet")
        before_activation = timezone.now()
        transition_mission(mission=project, target_state=MissionState.ACTIVE, actor=self.owner, reason="Début réel")
        project.refresh_from_db()
        self.assertGreaterEqual(project.activated_at, before_activation)
        self.assertEqual(MissionStateHistory.objects.filter(mission=project).count(), 5)
        self.assertTrue(item.is_open)

    def test_unknown_acceptance_cannot_be_treated_as_validated(self):
        project = mission(self.tenant)
        project.acceptance_result = AcceptanceResult.UNKNOWN
        project.save()
        with self.assertRaises(TransitionError):
            transition_mission(
                mission=project,
                target_state=MissionState.FEASIBILITY_VALIDATED,
                actor=self.owner,
                reason="Tentative avec décision métier inconnue",
            )

    def test_normal_j10_fifteen_points_with_partial_answers(self):
        project = mission(self.tenant, state=MissionState.ACTIVE, due_days=10)
        items = [prerequisite(project, self.owner, f"PR-{index:02d}", due_hours=240) for index in range(1, 16)]
        for item in items[:5]:
            update_instance(
                instance=item,
                data={"state": PrerequisiteState.PARTIALLY_CONFIRMED, "confirmation_score": 2},
                actor=self.owner,
                reason="Réponse partielle du scénario normal",
                category="MINOR",
                recalculate=True,
            )
        snapshot = capture_t0(mission=project, actor=self.owner)
        queue = build_work_queue()
        self.assertEqual(snapshot["total"], 15)
        self.assertEqual(snapshot["partial"], 5)
        self.assertEqual(sum(len(items) for items in queue.values()) > 0, True)

    def test_late_payment_never_backdates_real_window(self):
        project = mission(self.tenant, due_days=3)
        project.created_at = timezone.now() - timedelta(days=10)
        project.state = MissionState.READY_TO_PURSUE
        project.save()
        activated = timezone.now()
        transition_mission(mission=project, target_state=MissionState.ACTIVE, actor=self.owner, reason="Paiement tardif confirmé")
        project.refresh_from_db()
        self.assertGreaterEqual(project.activated_at, activated)

    def test_vague_response_cannot_be_confirmation(self):
        project = mission(self.tenant)
        item = prerequisite(project, self.owner)
        with self.assertRaises(ValidationError):
            record_action(
                prerequisite=item,
                actor=self.owner,
                event_type=ActionEventType.RESPONSE,
                occurred_at=timezone.now(),
                channel="E-mail",
                factual_result="Normalement ce sera bon",
                next_action="",
                next_action_at=None,
                expected_event="",
                next_state=PrerequisiteState.CONFIRMED,
                closure_criterion_satisfied=True,
            )

    def test_technical_information_is_escalated_without_interpretation(self):
        project = mission(self.tenant, state=MissionState.ACTIVE)
        item = prerequisite(project, self.owner)
        escalation = escalate_prerequisite(
            prerequisite=item,
            actor=self.owner,
            data={
                "level": 3,
                "expected": "Confirmation factuelle selon critère client",
                "readiness_actions": "Demande et relance documentées",
                "obtained_or_missing": "Réponse reçue nécessitant une expertise technique",
                "time_remaining": "48 heures",
                "client_decision_reason": "Interprétation technique hors compétence Readiness",
            },
        )
        item.refresh_from_db()
        self.assertEqual(item.state, PrerequisiteState.ESCALATED)
        self.assertTrue(item.awaiting_client_decision)
        self.assertEqual(item.next_action, "")
        self.assertIn("hors compétence", escalation.client_decision_reason)

    def test_action_response_confirmation_are_separate_records(self):
        project = mission(self.tenant)
        item = prerequisite(project, self.owner)
        record_action(
            prerequisite=item,
            actor=self.owner,
            event_type=ActionEventType.ACTION,
            occurred_at=timezone.now(),
            channel="Téléphone",
            factual_result="Appel effectué, messagerie",
            next_action="Relancer par e-mail",
            next_action_at=timezone.now() + timedelta(hours=1),
            expected_event="Réponse écrite",
            next_state=PrerequisiteState.AWAITING_RESPONSE,
        )
        record_action(
            prerequisite=item,
            actor=self.owner,
            event_type=ActionEventType.RESPONSE,
            occurred_at=timezone.now(),
            channel="E-mail",
            factual_result="Réponse partielle reçue",
            next_action="Contrôler la pièce",
            next_action_at=timezone.now() + timedelta(hours=1),
            expected_event="Contrôle documentaire",
            next_state=PrerequisiteState.RESPONSE_TO_REVIEW,
        )
        record_action(
            prerequisite=item,
            actor=self.owner,
            event_type=ActionEventType.CONFIRMATION,
            occurred_at=timezone.now(),
            channel="Contrôle",
            factual_result="Critère client explicitement satisfait",
            next_action="",
            next_action_at=None,
            expected_event="",
            next_state=PrerequisiteState.CONFIRMED,
            closure_criterion_satisfied=True,
        )
        self.assertEqual(list(item.actions.values_list("event_type", flat=True).order_by("created_at")), ["ACTION", "RESPONSE", "CONFIRMATION"])

    def test_impossible_capacity_recommends_refusal_or_reduced_scope(self):
        project = mission(self.tenant, due_days=3)
        project.manual_load_estimate_hours = 40
        project.operator_available_hours = 8
        result, _ = feasibility_recommendation(project)
        self.assertEqual(result, "INSUFFICIENT_CAPACITY")
        project.reduced_scope_proposal = "Uniquement les cinq points critiques"
        result, _ = feasibility_recommendation(project)
        self.assertEqual(result, "CONDITIONAL")

    def test_new_prerequisite_and_date_change_keep_history_and_recalculate(self):
        project = mission(self.tenant, due_days=15)
        item = prerequisite(project, self.owner, due_hours=15 * 24, client_criticality=1)
        old_priority = item.priority_level
        update_instance(
            instance=item,
            data={"useful_deadline": timezone.now() + timedelta(days=5)},
            actor=self.owner,
            reason="Date client avancée de J+15 à J+5",
            category="MISSION_EVOLUTION",
            recalculate=True,
        )
        item.refresh_from_db()
        self.assertNotEqual(item.priority_level, old_priority)
        self.assertTrue(ChangeRecord.objects.filter(resource_id=item.id, before_data__has_key="useful_deadline").exists())

    def test_client_cancellation_is_preserved_not_deleted(self):
        project = mission(self.tenant)
        item = prerequisite(project, self.owner)
        update_instance(
            instance=item,
            data={
                "state": PrerequisiteState.CANCELLED_BY_CLIENT,
                "next_action": "",
                "next_action_at": None,
                "expected_event": "",
            },
            actor=self.owner,
            reason="Annulation explicite du client",
            category="MISSION_EVOLUTION",
            recalculate=True,
        )
        item.refresh_from_db()
        self.assertEqual(item.state, PrerequisiteState.CANCELLED_BY_CLIENT)
        with self.assertRaises(ValidationError):
            item.delete()

    def test_closure_requires_reason_and_generates_factual_report(self):
        project = mission(self.tenant, state=MissionState.ACTIVE)
        item = prerequisite(project, self.owner)
        with self.assertRaises(TransitionError):
            transition_mission(
                mission=project,
                target_state=MissionState.COMPLETED,
                actor=self.owner,
                reason="Tentative sans motif de clôture",
            )
        project.closure_reason = "Fin de la fenêtre opérationnelle convenue"
        project.save(update_fields=["closure_reason", "updated_at"])
        transition_mission(
            mission=project,
            target_state=MissionState.COMPLETED,
            actor=self.owner,
            reason="Clôture opérateur documentée",
        )
        project.refresh_from_db()
        self.assertEqual(project.closure_report["final_counts"]["open"], 1)
        self.assertEqual(project.closure_report["remaining"][0]["code"], item.code)
        self.assertEqual(project.closure_report["reason"], project.closure_reason)
