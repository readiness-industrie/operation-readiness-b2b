from django.contrib.auth import logout
from django.db import connection, transaction


class TenantDatabaseContextMiddleware:
    """Applique un contexte RLS local à la transaction de chaque requête."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if connection.vendor != "postgresql":
            return self.get_response(request)
        with transaction.atomic():
            user = getattr(request, "user", None)
            is_owner = bool(user and user.is_authenticated and user.role == "OWNER")
            tenant_id = str(user.tenant_id) if user and user.is_authenticated and user.tenant_id else ""
            with connection.cursor() as cursor:
                cursor.execute("SELECT set_config('app.is_owner', %s, true)", ["true" if is_owner else "false"])
                cursor.execute("SELECT set_config('app.tenant_id', %s, true)", [tenant_id])
            return self.get_response(request)


class SessionVersionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated and request.session.get("session_version") != user.session_version:
            logout(request)
        return self.get_response(request)


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; "
            "frame-ancestors 'none'; connect-src 'self'"
        )
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
        response.headers["Cache-Control"] = "no-store"
        return response
