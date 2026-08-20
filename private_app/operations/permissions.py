from functools import wraps

from django.http import Http404, HttpResponseForbidden
from django.shortcuts import redirect

from .audit import audit_event
from .enums import UserRole
from .models import EvidenceDocument, Mission, MissionAccess, Prerequisite


def owner_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.role != UserRole.OWNER:
            audit_event(operation="OWNER_ACCESS_DENIED", result="DENIED", actor=request.user, tenant=request.user.tenant, request=request)
            return HttpResponseForbidden("Accès interdit.")
        return view(request, *args, **kwargs)

    return wrapped


def viewer_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.role != UserRole.CLIENT_VIEWER:
            return redirect("dashboard")
        return view(request, *args, **kwargs)

    return wrapped


def missions_for_user(user):
    if user.role == UserRole.OWNER:
        return Mission.objects.all()
    grant_ids = MissionAccess.objects.filter(user=user, tenant=user.tenant, is_active=True).values_list("mission_id", flat=True)
    return Mission.objects.filter(tenant=user.tenant, id__in=grant_ids)


def scoped_mission_or_404(request, mission_id):
    try:
        return missions_for_user(request.user).get(id=mission_id)
    except Mission.DoesNotExist:
        audit_event(
            operation="CROSS_TENANT_OR_UNAUTHORIZED_MISSION",
            result="DENIED",
            actor=request.user,
            tenant=getattr(request.user, "tenant", None),
            resource_type="Mission",
            resource_id=mission_id,
            request=request,
        )
        raise Http404("Ressource introuvable")


def scoped_prerequisite_or_404(request, prerequisite_id):
    missions = missions_for_user(request.user)
    try:
        return Prerequisite.objects.select_related("mission").get(id=prerequisite_id, mission__in=missions)
    except Prerequisite.DoesNotExist:
        audit_event(
            operation="CROSS_TENANT_OR_UNAUTHORIZED_PREREQUISITE",
            result="DENIED",
            actor=request.user,
            tenant=getattr(request.user, "tenant", None),
            resource_type="Prerequisite",
            resource_id=prerequisite_id,
            request=request,
        )
        raise Http404("Ressource introuvable")


def scoped_document_or_404(request, document_id):
    missions = missions_for_user(request.user)
    try:
        return EvidenceDocument.objects.select_related("mission").get(id=document_id, mission__in=missions)
    except EvidenceDocument.DoesNotExist:
        audit_event(
            operation="CROSS_TENANT_OR_UNAUTHORIZED_DOCUMENT",
            result="DENIED",
            actor=request.user,
            tenant=getattr(request.user, "tenant", None),
            resource_type="EvidenceDocument",
            resource_id=document_id,
            request=request,
        )
        raise Http404("Ressource introuvable")
