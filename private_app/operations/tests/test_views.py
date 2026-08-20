from django.test import Client, TestCase
from django.urls import reverse

from operations.services import publish_client_snapshot

from .factories import login_client, mission, owner, prerequisite, tenant


class OperatorInterfaceSmokeTests(TestCase):
    def setUp(self):
        self.owner = owner()
        self.tenant = tenant("Alpha")
        self.mission = mission(self.tenant)
        self.item = prerequisite(self.mission, self.owner)
        self.client = Client()
        login_client(self.client, self.owner)

    def test_critical_operator_pages_render(self):
        urls = [
            reverse("dashboard"),
            reverse("mission_list"),
            reverse("mission_detail", args=[self.mission.id]),
            reverse("mission_qualification", args=[self.mission.id]),
            reverse("mission_acceptance", args=[self.mission.id]),
            reverse("mission_feasibility", args=[self.mission.id]),
            reverse("mission_financial", args=[self.mission.id]),
            reverse("prerequisite_detail", args=[self.item.id]),
            reverse("prerequisite_action", args=[self.item.id]),
            reverse("prerequisite_escalate", args=[self.item.id]),
            reverse("config"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_owner_can_preview_controlled_publication(self):
        self.item.client_published = True
        self.item.client_summary = "Résumé publié"
        self.item.save()
        publication = publish_client_snapshot(mission=self.mission, actor=self.owner)
        response = self.client.get(reverse("portal_publication", args=[publication.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Résumé publié")
        self.assertNotContains(response, self.item.priority_explanation)
