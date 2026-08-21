
import pyotp
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from operations.models import AuditLog
from operations.uploads import create_document

from .factories import mission, owner, prerequisite, tenant, tiny_pdf


class SecurityAndFileTests(TestCase):
    def setUp(self):
        self.owner = owner()
        self.tenant = tenant("Alpha")
        self.project = mission(self.tenant)
        self.item = prerequisite(self.project, self.owner)

    def test_upload_rejects_extension_content_mismatch(self):
        fake = SimpleUploadedFile("danger.pdf", b"MZ executable", content_type="application/pdf")
        with self.assertRaises(ValidationError):
            create_document(uploaded=fake, mission=self.project, prerequisite=self.item, actor=self.owner)

    @override_settings(REQUIRE_MALWARE_SCAN=True)
    def test_production_upload_stays_quarantined(self):
        document = create_document(uploaded=tiny_pdf(), mission=self.project, prerequisite=self.item, actor=self.owner)
        self.assertEqual(document.scan_state, "PENDING")
        self.assertFalse(document.is_client_shared)

    def test_password_then_mfa_login(self):
        secret = pyotp.random_base32()
        self.owner.set_mfa_secret(secret)
        self.owner.mfa_confirmed_at = __import__("django.utils.timezone", fromlist=["now"]).now()
        self.owner.save()
        client = Client()
        response = client.post(reverse("login"), {"identifier": self.owner.email, "password": "Very-Strong-Test-Password!"})
        self.assertRedirects(response, reverse("mfa_verify"), fetch_redirect_response=False)
        response = client.post(reverse("mfa_verify"), {"code": pyotp.TOTP(secret).now()})
        self.assertRedirects(response, reverse("dashboard"), fetch_redirect_response=False)
        self.assertTrue(AuditLog.objects.filter(operation="LOGIN", result="SUCCESS", actor=self.owner).exists())

    def test_first_login_mfa_setup_renders_qr_code(self):
        client = Client()
        response = client.post(
            reverse("login"),
            {"identifier": self.owner.email, "password": "Very-Strong-Test-Password!"},
        )
        self.assertRedirects(response, reverse("mfa_setup"), fetch_redirect_response=False)

        response = client.get(reverse("mfa_setup"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data:image/png;base64,")

    def test_owner_has_no_client_tenant(self):
        self.owner.tenant = self.tenant
        with self.assertRaises(ValidationError):
            self.owner.full_clean()

    def test_controlled_retention_removes_file_and_pseudonymizes(self):
        document = create_document(uploaded=tiny_pdf("retention-proof.pdf"), mission=self.project, prerequisite=self.item, actor=self.owner)
        stored_name = document.file.name
        storage = document.file.storage
        self.project.state = "COMPLETED"
        self.project.ended_at = __import__("django.utils.timezone", fromlist=["now"]).now() - __import__("datetime").timedelta(days=400)
        self.project.save()
        call_command(
            "execute_retention",
            mission=str(self.project.id),
            confirm=f"DELETE-{self.project.code}",
            reason="Échéance de rétention du test",
            verbosity=0,
        )
        self.project.refresh_from_db()
        document.refresh_from_db()
        self.item.primary_contact.refresh_from_db()
        self.assertTrue(self.project.is_archived)
        self.assertFalse(storage.exists(stored_name))
        self.assertEqual(document.file.name, "")
        self.assertEqual(document.scan_state, "REJECTED")
        self.assertTrue(self.item.primary_contact.full_name.startswith("[contact supprimé"))
