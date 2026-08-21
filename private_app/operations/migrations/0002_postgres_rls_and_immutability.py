from django.db import migrations

TENANT_TABLES = [
    "operations_mission",
    "operations_missionstatehistory",
    "operations_extensionrequest",
    "operations_contact",
    "operations_changerecord",
    "operations_prerequisite",
    "operations_evidencedocument",
    "operations_escalationrecord",
    "operations_actionrecord",
    "operations_publicationsnapshot",
    "operations_securityincident",
    "operations_missionaccess",
]

IMMUTABLE_TABLES = [
    "operations_missionstatehistory",
    "operations_changerecord",
    "operations_escalationrecord",
    "operations_actionrecord",
    "operations_auditlog",
]


def enable_security(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for table in TENANT_TABLES:
            cursor.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY')
            cursor.execute(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY')
            cursor.execute(
                f'''CREATE POLICY tenant_isolation ON "{table}"
                USING (
                    current_setting('app.is_owner', true) = 'true'
                    OR tenant_id::text = current_setting('app.tenant_id', true)
                )
                WITH CHECK (
                    current_setting('app.is_owner', true) = 'true'
                    OR tenant_id::text = current_setting('app.tenant_id', true)
                )'''
            )
        cursor.execute(
            """CREATE OR REPLACE FUNCTION readiness_reject_history_mutation()
            RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'Readiness history rows are immutable';
            END;
            $$ LANGUAGE plpgsql"""
        )
        for table in IMMUTABLE_TABLES:
            cursor.execute(
                f'''CREATE TRIGGER reject_history_mutation
                BEFORE UPDATE OR DELETE ON "{table}"
                FOR EACH ROW EXECUTE FUNCTION readiness_reject_history_mutation()'''
            )


def disable_security(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        for table in IMMUTABLE_TABLES:
            cursor.execute(f'DROP TRIGGER IF EXISTS reject_history_mutation ON "{table}"')
        cursor.execute("DROP FUNCTION IF EXISTS readiness_reject_history_mutation()")
        for table in TENANT_TABLES:
            cursor.execute(f'DROP POLICY IF EXISTS tenant_isolation ON "{table}"')
            cursor.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY')


class Migration(migrations.Migration):
    dependencies = [("operations", "0001_initial")]
    operations = [migrations.RunPython(enable_security, disable_security)]
