from datetime import timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from operations.enums import ActionEventType, MissionState, PrerequisiteState, PriorityLevel
from operations.services import build_work_queue, record_action
from operations.tests.factories import login_client, mission, owner, prerequisite, tenant, tiny_pdf
from operations.uploads import create_document


class DailyQueueExceptionTests(TestCase):
    def setUp(self):
        self.owner = owner("queue-owner")
        self.http = Client()
        login_client(self.http, self.owner)
        self.tenant = tenant("Queue")
        self.project = mission(self.tenant, "QUEUE-001", state=MissionState.ACTIVE, due_days=12)

    def test_planned_p2_p3_are_counted_but_not_listed_on_dashboard(self):
        planned = prerequisite(
            self.project,
            self.owner,
            "PR-FUTUR",
            due_hours=24 * 12,
            client_criticality=0,
            confirmation_score=0,
            dependency_score=0,
            inertia_score=0,
        )
        planned.next_action_at = timezone.now() + timedelta(days=5)
        planned.save(update_fields=["next_action_at"])
        planned.refresh_from_db()
        self.assertIn(planned.priority_level, {PriorityLevel.P2, PriorityLevel.P3})

        queue = build_work_queue()
        self.assertGreaterEqual(len(queue["p2"]) + len(queue["p3"]), 1)
        response = self.http.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertNotIn("P2 planifiés", body)
        self.assertNotIn("P3 sous surveillance", body)
        self.assertIn("Actions futures", body)
        self.assertNotIn("PR-FUTUR", body)
        self.assertContains(response, "QUEUE-001")
        self.assertContains(self.http.get(reverse("mission_detail", args=[self.project.id])), "PR-FUTUR")

    def test_uploaded_proof_enters_queue_then_leaves_after_review(self):
        item = prerequisite(self.project, self.owner, "PR-PREUVE", due_hours=72)
        create_document(uploaded=tiny_pdf("preuve-client.pdf"), mission=self.project, prerequisite=item, actor=self.owner)
        item.refresh_from_db()
        queue = build_work_queue()
        self.assertIn(item, queue["new_information"])
        self.assertIn(item, queue["responses_to_review"])
        self.assertContains(self.http.get(reverse("dashboard")), "PR-PREUVE")

        record_action(
            prerequisite=item,
            actor=self.owner,
            event_type=ActionEventType.ACTION,
            occurred_at=timezone.now(),
            channel="Contrôle",
            factual_result="Preuve contrôlée, incomplète",
            next_action="Relancer la photo manquante",
            next_action_at=timezone.now() + timedelta(days=1),
            expected_event="Photo complémentaire",
            next_state=PrerequisiteState.AWAITING_RESPONSE,
        )
        item.refresh_from_db()
        queue = build_work_queue()
        self.assertNotIn(item, queue["new_information"])
        self.assertNotIn(item, queue["responses_to_review"])


class OperatorDayLoadTests(TestCase):
    def test_today_queue_hides_planned_items_among_100_prerequisites(self):
        from operations.services import escalate_prerequisite

        user = owner("load-owner")
        http = Client()
        login_client(http, user)
        clients = [tenant(f"Load{i}") for i in range(1, 6)]
        missions = [
            mission(clients[i % 5], f"LOAD-{i+1:02d}", state=MissionState.ACTIVE, due_days=8)
            for i in range(10)
        ]
        planned_codes = []
        due_codes = []
        now = timezone.now()
        for index in range(100):
            project = missions[index % 10]
            if index % 10 == 0:
                item = prerequisite(project, user, f"L-{index:03d}", due_hours=-2, client_criticality=3)
                due_codes.append(item.code)
            elif index % 10 == 1:
                item = prerequisite(project, user, f"L-{index:03d}", due_hours=8)
                item.next_action_at = now - timedelta(minutes=5)
                item.save(update_fields=["next_action_at"])
                due_codes.append(item.code)
            elif index % 10 == 2:
                item = prerequisite(project, user, f"L-{index:03d}", due_hours=48)
                create_document(uploaded=tiny_pdf(f"l-{index}.pdf"), mission=project, prerequisite=item, actor=user)
                due_codes.append(item.code)
            elif index % 10 == 3:
                item = prerequisite(project, user, f"L-{index:03d}", due_hours=72)
                escalate_prerequisite(
                    prerequisite=item,
                    actor=user,
                    data={
                        "level": 3,
                        "expected": "Décision",
                        "readiness_actions": "Dossier transmis",
                        "obtained_or_missing": "Preuve incomplète",
                        "time_remaining": "24 h",
                        "client_decision_reason": "Le client doit trancher",
                    },
                )
                due_codes.append(item.code)
            else:
                item = prerequisite(
                    project,
                    user,
                    f"L-{index:03d}",
                    due_hours=24 * 12,
                    client_criticality=0,
                    confirmation_score=0,
                    dependency_score=0,
                    inertia_score=0,
                )
                item.next_action_at = now + timedelta(days=6)
                item.save(update_fields=["next_action_at"])
                planned_codes.append((item.code, project))

        body = http.get(reverse("dashboard")).content.decode()
        self.assertIn("Ce qu’il faut faire maintenant", body)
        self.assertTrue(any(code in body for code in due_codes))
        self.assertFalse(any(code in body for code, _mission in planned_codes))
        self.assertNotIn("P2 planifiés", body)
        planned_code, planned_mission = planned_codes[0]
        self.assertContains(http.get(reverse("mission_detail", args=[planned_mission.id])), planned_code)
