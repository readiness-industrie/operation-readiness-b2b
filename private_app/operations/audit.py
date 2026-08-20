import hashlib

from .models import AuditLog


def _digest(value):
    return hashlib.sha256((value or "").encode()).hexdigest() if value else ""


def audit_event(
    *,
    operation,
    result,
    actor=None,
    tenant=None,
    resource_type="",
    resource_id="",
    request=None,
    details=None,
):
    if request is not None:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
        remote = forwarded or request.META.get("REMOTE_ADDR", "")
        user_agent = request.META.get("HTTP_USER_AGENT", "")
    else:
        remote = user_agent = ""
    return AuditLog.objects.create(
        tenant=tenant,
        actor=actor if getattr(actor, "is_authenticated", False) else None,
        actor_label=(getattr(actor, "username", "") or getattr(actor, "email", "")) if actor else "",
        operation=operation,
        resource_type=resource_type,
        resource_id=str(resource_id or ""),
        result=result,
        ip_hash=_digest(remote),
        user_agent_hash=_digest(user_agent),
        details=details or {},
    )
