from contextlib import contextmanager

from django.db import connection, transaction


@contextmanager
def rls_context(*, tenant_id=None, owner=False):
    if connection.vendor != "postgresql":
        yield
        return
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT set_config('app.is_owner', %s, true)", ["true" if owner else "false"])
            cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [str(tenant_id or "")])
        yield
