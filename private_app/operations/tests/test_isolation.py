from django.test import Client, TestCase
from django.urls import reverse

from operations.enums import DocumentScanState
from operations.services import publish_client_snapshot, revoke_publication
from operations.uploads import create_document, mark_document_shared

from .factories import (
    grant,
    login_client,
    mission,
    owner,
    prerequisite,
    tenant,
    tiny_pdf,
    viewer,
)


class AlphaBetaIsolationTests(TestCase):
    def setUp(self):
        self.owner = owner()
        self.alpha = tenant("Alpha")
        self.beta = tenant("Beta")
        self.alpha_viewer = viewer(self.alpha, "Alpha")
        self.beta_viewer = viewer(self.beta, "Beta")
        self.alpha_mission = mission(self.alpha, "ALPHA-001")
        self.beta_mission = mission(self.beta, "BETA-001")
        grant(self.alpha_viewer, self.alpha_mission)
        grant(self.beta_viewer, self.beta_mission)
        self.alpha_item = prerequisite(self.alpha_mission, self.owner, "A-PR")
        self.beta_item = prerequisite(self.beta_mission, self.owner, "B-PR")
        self.alpha_item.client_published = True
        self.alpha_item.client_summary = "Résumé Alpha"
        self.alpha_item.save()
        self.beta_item.client_published = True
        self.beta_item.client_summary = "Résumé Beta confidentiel"
        self.beta_item.save()
        self.alpha_publication = publish_client_snapshot(mission=self.alpha_mission, actor=self.owner)
        self.beta_publication = publish_client_snapshot(mission=self.beta_mission, actor=self.owner)
        self.client = Client()
        login_client(self.client, self.alpha_viewer)

    def test_cross_publication_url_is_neutral_404(self):
        response = self.client.get(reverse("portal_publication", args=[self.beta_publication.id]))
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, "Beta confidentiel", status_code=404)

    def test_guessed_cross_mission_api_id_is_404(self):
        response = self.client.get(reverse("portal_api_summary", args=[self.beta_mission.id]))
        self.assertEqual(response.status_code, 404)

    def test_browser_tenant_parameter_is_ignored(self):
        response = self.client.get(reverse("portal_api_summary", args=[self.alpha_mission.id]), {"tenant": str(self.beta.id)})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ALPHA-001")
        self.assertNotContains(response, "BETA-001")

    def test_viewer_cannot_post_to_read_only_api(self):
        response = self.client.post(reverse("portal_api_summary", args=[self.alpha_mission.id]), {"state": "CONFIRMED"})
        self.assertEqual(response.status_code, 405)

    def test_access_after_logout_fails(self):
        self.client.post(reverse("logout"))
        response = self.client.get(reverse("portal_publication", args=[self.alpha_publication.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_revoked_old_link_fails(self):
        revoke_publication(publication=self.alpha_publication, actor=self.owner, reason="Version obsolète")
        response = self.client.get(reverse("portal_publication", args=[self.alpha_publication.id]))
        self.assertEqual(response.status_code, 404)

    def test_cross_document_access_fails(self):
        document = create_document(uploaded=tiny_pdf("beta-proof.pdf"), mission=self.beta_mission, prerequisite=self.beta_item, actor=self.owner)
        mark_document_shared(document, True)
        self.beta_publication = publish_client_snapshot(mission=self.beta_mission, actor=self.owner)
        response = self.client.get(reverse("document_download", args=[document.id]))
        self.assertEqual(response.status_code, 404)

    def test_unpublished_alpha_document_is_still_hidden(self):
        document = create_document(uploaded=tiny_pdf("alpha-proof.pdf"), mission=self.alpha_mission, prerequisite=self.alpha_item, actor=self.owner)
        self.assertEqual(document.scan_state, DocumentScanState.SAFE)
        response = self.client.get(reverse("document_download", args=[document.id]))
        self.assertEqual(response.status_code, 404)

    def test_cross_attempt_is_audited(self):
        from operations.models import AuditLog

        self.client.get(reverse("portal_api_summary", args=[self.beta_mission.id]))
        self.assertTrue(AuditLog.objects.filter(operation="CROSS_TENANT_OR_UNAUTHORIZED_MISSION", result="DENIED").exists())
