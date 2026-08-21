from django.db import DatabaseError, connection, transaction
from django.test import TransactionTestCase

from operations.db import rls_context
from operations.models import Mission

from .factories import mission, tenant


class PostgresRowLevelSecurityTests(TransactionTestCase):
    databases = {"default"}

    def test_database_itself_hides_beta_from_alpha(self):
        if connection.vendor != "postgresql":
            self.skipTest("Test RLS exécuté uniquement sur PostgreSQL en CI/production-like.")
        with rls_context(owner=True):
            alpha = tenant("RLSAlpha")
            beta = tenant("RLSBeta")
            alpha_mission = mission(alpha, "RLS-A")
            beta_mission = mission(beta, "RLS-B")
        with rls_context(tenant_id=alpha.id):
            self.assertEqual(list(Mission.objects.values_list("code", flat=True)), [alpha_mission.code])
            self.assertFalse(Mission.objects.filter(pk=beta_mission.pk).exists())
            self.assertEqual(Mission.objects.filter(pk=beta_mission.pk).update(project_name="Accès croisé"), 0)
            with self.assertRaises(DatabaseError), transaction.atomic():
                mission(beta, "RLS-CROSS-WRITE")
        with rls_context(owner=True):
            self.assertEqual(Mission.objects.count(), 2)
            beta_mission.refresh_from_db()
            self.assertNotEqual(beta_mission.project_name, "Accès croisé")
