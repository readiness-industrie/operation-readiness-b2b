import base64
import hashlib
import io
import json
import secrets
import time
from datetime import timedelta

import pyotp
import qrcode
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.http import (
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseNotAllowed,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .audit import audit_event
from .enums import DocumentScanState, MissionState, UserRole
from .forms import (
    AcceptanceForm,
    ActionForm,
    BusinessConfigForm,
    ClientViewerCreateForm,
    ClosureForm,
    ContactForm,
    DocumentUploadForm,
    EscalationForm,
    ExtensionRequestForm,
    FeasibilityForm,
    FinancialForm,
    IncidentForm,
    LoginForm,
    MFACodeForm,
    MissionAccessForm,
    MissionCreateForm,
    MissionQualificationForm,
    OrganizationForm,
    PrerequisiteForm,
    PublishForm,
    RevokePublicationForm,
    StateTransitionForm,
)
from .models import (
    BusinessConfig,
    EvidenceDocument,
    LoginAttempt,
    Mission,
    Organization,
    PublicationSnapshot,
    SecurityIncident,
    User,
    serialize_model,
)
from .permissions import (
    missions_for_user,
    owner_required,
    scoped_document_or_404,
    scoped_mission_or_404,
    scoped_prerequisite_or_404,
    viewer_required,
)
from .priorities import feasibility_recommendation, indicative_price
from .services import (
    ALLOWED_TRANSITIONS,
    TransitionError,
    build_work_queue,
    capture_t0,
    create_mission,
    create_prerequisite,
    escalate_prerequisite,
    publish_client_snapshot,
    record_action,
    revoke_publication,
    transition_mission,
    update_instance,
)
from .uploads import create_document, mark_document_shared


def _hash(value):
    return hashlib.sha256((value or "").encode()).hexdigest()


def _add_form_validation_error(form, error):
    """Renvoyer une validation métier dans le formulaire au lieu d'une erreur 500."""
    if hasattr(error, "message_dict"):
        for field, field_messages in error.message_dict.items():
            target = field if field in form.fields else None
            for message in field_messages:
                form.add_error(target, message)
        return
    form.add_error(None, error)


def _client_ip(request):
    return request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR", "")


def _preauth_user(request):
    user_id = request.session.get("preauth_user_id")
    started = request.session.get("preauth_started", 0)
    if not user_id or time.time() - started > 300:
        request.session.pop("preauth_user_id", None)
        return None
    return User.objects.filter(id=user_id, is_active=True).first()


def _complete_login(request, user):
    login(request, user)
    request.session.cycle_key()
    request.session["session_version"] = user.session_version
    request.session.pop("preauth_user_id", None)
    request.session.pop("preauth_started", None)
    request.session.pop("mfa_setup_secret", None)
    request.session.pop("mfa_failures", None)
    audit_event(operation="LOGIN", result="SUCCESS", actor=user, tenant=user.tenant, request=request)
    return redirect("portal_home" if user.role == UserRole.CLIENT_VIEWER else "dashboard")


def _recovery_codes():
    return [f"{secrets.token_hex(3).upper()}-{secrets.token_hex(3).upper()}" for _ in range(8)]


def login_view(request):
    if request.user.is_authenticated:
        return redirect("portal_home" if request.user.role == UserRole.CLIENT_VIEWER else "dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        identifier = form.cleaned_data["identifier"].strip()
        identifier_hash = _hash(identifier.lower())
        ip_hash = _hash(_client_ip(request))
        since = timezone.now() - timedelta(minutes=15)
        LoginAttempt.objects.filter(created_at__lt=timezone.now() - timedelta(days=30)).delete()
        failures = LoginAttempt.objects.filter(
            created_at__gte=since,
            succeeded=False,
        ).filter(identifier_hash=identifier_hash).count()
        ip_failures = LoginAttempt.objects.filter(created_at__gte=since, succeeded=False, ip_hash=ip_hash).count()
        if failures >= 5 or ip_failures >= 20:
            audit_event(operation="LOGIN_RATE_LIMIT", result="DENIED", request=request, details={"identifier_hash": identifier_hash})
            form.add_error(None, "Trop de tentatives. Réessayez dans 15 minutes.")
        else:
            user_record = User.objects.filter(email__iexact=identifier).first() or User.objects.filter(username__iexact=identifier).first()
            user = authenticate(request, username=user_record.username if user_record else identifier, password=form.cleaned_data["password"])
            LoginAttempt.objects.create(identifier_hash=identifier_hash, ip_hash=ip_hash, succeeded=bool(user))
            if user:
                request.session["preauth_user_id"] = str(user.id)
                request.session["preauth_started"] = time.time()
                return redirect("mfa_verify" if user.mfa_is_configured else "mfa_setup")
            audit_event(operation="LOGIN_PASSWORD", result="DENIED", request=request, details={"identifier_hash": identifier_hash})
            form.add_error(None, "Identifiants invalides.")
    return render(request, "operations/login.html", {"form": form})


def mfa_setup(request):
    user = _preauth_user(request)
    if not user:
        return redirect("login")
    if user.mfa_is_configured:
        return redirect("mfa_verify")
    secret = request.session.get("mfa_setup_secret") or pyotp.random_base32()
    request.session["mfa_setup_secret"] = secret
    uri = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="Readiness Industry")
    image = qrcode.make(uri)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    qr_data = base64.b64encode(buffer.getvalue()).decode()
    form = MFACodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if pyotp.TOTP(secret).verify(form.cleaned_data["code"].replace(" ", ""), valid_window=1):
            recovery_codes = _recovery_codes()
            user.set_mfa_secret(secret)
            user.set_recovery_codes(recovery_codes)
            user.mfa_confirmed_at = timezone.now()
            user.save(update_fields=["mfa_secret_encrypted", "mfa_recovery_hashes", "mfa_confirmed_at"])
            audit_event(operation="MFA_SETUP", result="SUCCESS", actor=user, tenant=user.tenant, request=request)
            request.session["new_recovery_codes"] = recovery_codes
            return redirect("mfa_recovery_codes")
        form.add_error("code", "Code invalide.")
    return render(request, "operations/mfa_setup.html", {"form": form, "secret": secret, "qr_data": qr_data})


def mfa_recovery_codes(request):
    user = _preauth_user(request)
    codes = request.session.get("new_recovery_codes")
    if not user or not codes:
        return redirect("login")
    if request.method == "POST":
        request.session.pop("new_recovery_codes", None)
        return _complete_login(request, user)
    return render(request, "operations/mfa_recovery_codes.html", {"codes": codes})


def mfa_verify(request):
    user = _preauth_user(request)
    if not user:
        return redirect("login")
    if not user.mfa_is_configured:
        return redirect("mfa_setup")
    form = MFACodeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        failures = int(request.session.get("mfa_failures", 0))
        if failures >= 5:
            request.session.flush()
            return redirect("login")
        code = form.cleaned_data["code"].replace(" ", "").upper()
        valid = pyotp.TOTP(user.get_mfa_secret()).verify(code, valid_window=1)
        if not valid and "-" in code:
            valid = user.consume_recovery_code(code)
        if valid:
            return _complete_login(request, user)
        request.session["mfa_failures"] = failures + 1
        audit_event(operation="MFA_VERIFY", result="DENIED", actor=user, tenant=user.tenant, request=request)
        form.add_error("code", "Code invalide.")
    return render(request, "operations/mfa_verify.html", {"form": form})


@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        audit_event(operation="LOGOUT", result="SUCCESS", actor=request.user, tenant=request.user.tenant, request=request)
    logout(request)
    return redirect("login")


@owner_required
def dashboard(request):
    queue = build_work_queue()
    missions = Mission.objects.select_related("tenant").exclude(state__in=[MissionState.COMPLETED, MissionState.REFUSED]).order_by("protected_at")
    return render(request, "operations/dashboard.html", {"queue": queue, "missions": missions})


@owner_required
def mission_list(request):
    missions = Mission.objects.select_related("tenant").all()
    return render(request, "operations/mission_list.html", {"missions": missions})


@owner_required
def mission_create(request):
    form = MissionCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        fields = form._meta.fields
        tenant = form.cleaned_data.pop("tenant")
        data = {field: form.cleaned_data[field] for field in fields if field != "tenant"}
        mission = create_mission(tenant=tenant, actor=request.user, data=data)
        messages.success(request, "Mission créée en qualification.")
        return redirect("mission_detail", mission_id=mission.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Nouvelle qualification", "submit_label": "Créer la mission"})


@owner_required
def mission_detail(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    config = BusinessConfig.get_solo()
    price, size, price_note = indicative_price(mission, config)
    feasibility, feasibility_note = feasibility_recommendation(mission)
    latest_publication = mission.publications.filter(revoked_at__isnull=True).first()
    context = {
        "mission": mission,
        "prerequisites": mission.prerequisites.select_related("primary_contact").all(),
        "contacts": mission.contacts.all(),
        "documents": mission.documents.all(),
        "state_history": mission.state_history.select_related("author").all(),
        "changes": mission.changes.select_related("author")[:30],
        "extensions": mission.extensions.all(),
        "price": price,
        "size": size,
        "price_note": price_note,
        "feasibility_recommendation": feasibility,
        "feasibility_note": feasibility_note,
        "latest_publication": latest_publication,
        "allowed_transitions": ALLOWED_TRANSITIONS.get(mission.state, set()),
    }
    audit_event(operation="MISSION_ACCESS", result="SUCCESS", actor=request.user, tenant=mission.tenant, resource_type="Mission", resource_id=mission.id, request=request)
    return render(request, "operations/mission_detail.html", context)


def _model_form_update(request, mission, form_class, title):
    form = form_class(request.POST or None, instance=mission)
    if request.method == "POST" and form.is_valid():
        data = {field: form.cleaned_data[field] for field in form._meta.fields}
        try:
            update_instance(
                instance=mission,
                data=data,
                actor=request.user,
                reason=form.cleaned_data["change_reason"],
                category=form.cleaned_data["change_category"],
            )
        except ValidationError as error:
            _add_form_validation_error(form, error)
        else:
            messages.success(request, "Mission mise à jour et changement historisé.")
            return redirect("mission_detail", mission_id=mission.id)
    return render(request, "operations/form_page.html", {"form": form, "title": title, "mission": mission, "submit_label": "Enregistrer"})


@owner_required
def mission_qualification(request, mission_id):
    return _model_form_update(request, scoped_mission_or_404(request, mission_id), MissionQualificationForm, "Qualification rapide")


@owner_required
def mission_acceptance(request, mission_id):
    return _model_form_update(request, scoped_mission_or_404(request, mission_id), AcceptanceForm, "Filtre d’acceptation")


@owner_required
def mission_feasibility(request, mission_id):
    return _model_form_update(request, scoped_mission_or_404(request, mission_id), FeasibilityForm, "Faisabilité et capacité")


@owner_required
def mission_financial(request, mission_id):
    return _model_form_update(request, scoped_mission_or_404(request, mission_id), FinancialForm, "Déclenchement financier")


@owner_required
def mission_transition(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    choices = [(state, MissionState(state).label) for state in ALLOWED_TRANSITIONS.get(mission.state, set())]
    form = StateTransitionForm(request.POST or None)
    form.fields["target_state"].choices = choices
    if request.method == "POST" and form.is_valid():
        try:
            transition_mission(mission=mission, target_state=form.cleaned_data["target_state"], actor=request.user, reason=form.cleaned_data["reason"])
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "État de mission mis à jour.")
            return redirect("mission_detail", mission_id=mission.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Changer l’état de mission", "mission": mission, "submit_label": "Appliquer"})


@owner_required
def mission_close(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    form = ClosureForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        update_instance(instance=mission, data={"closure_reason": form.cleaned_data["closure_reason"]}, actor=request.user, reason=form.cleaned_data["transition_reason"])
        try:
            transition_mission(mission=mission, target_state=MissionState.COMPLETED, actor=request.user, reason=form.cleaned_data["transition_reason"])
        except TransitionError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Mission clôturée ; rapport final figé.")
            return redirect("mission_detail", mission_id=mission.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Clôturer la mission", "mission": mission, "submit_label": "Clôturer"})


@owner_required
@require_POST
def mission_capture_t0(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    try:
        capture_t0(mission=mission, actor=request.user)
        messages.success(request, "T0 enregistré et figé.")
    except ValidationError as error:
        messages.error(request, "; ".join(error.messages))
    return redirect("mission_detail", mission_id=mission.id)


@owner_required
def contact_create(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        contact = form.save(commit=False)
        contact.tenant = mission.tenant
        contact.mission = mission
        contact.full_clean()
        contact.save()
        audit_event(operation="CONTACT_CREATE", result="SUCCESS", actor=request.user, tenant=mission.tenant, resource_type="Contact", resource_id=contact.id)
        messages.success(request, "Contact ajouté.")
        return redirect("mission_detail", mission_id=mission.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Ajouter un contact autorisé", "mission": mission, "submit_label": "Ajouter"})


@owner_required
def prerequisite_create(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    form = PrerequisiteForm(request.POST or None, mission=mission)
    if request.method == "POST" and form.is_valid():
        data = {field: form.cleaned_data[field] for field in form._meta.fields}
        try:
            prerequisite = create_prerequisite(
                mission=mission,
                actor=request.user,
                data=data,
                reason=form.cleaned_data["change_reason"],
            )
        except ValidationError as error:
            _add_form_validation_error(form, error)
        else:
            messages.success(request, "Prérequis créé, scoré sans inventer les données manquantes et historisé.")
            return redirect("prerequisite_detail", prerequisite_id=prerequisite.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Nouveau prérequis", "mission": mission, "submit_label": "Créer"})


@owner_required
def prerequisite_detail(request, prerequisite_id):
    prerequisite = scoped_prerequisite_or_404(request, prerequisite_id)
    return render(
        request,
        "operations/prerequisite_detail.html",
        {
            "prerequisite": prerequisite,
            "actions": prerequisite.actions.select_related("author").all(),
            "escalations": prerequisite.escalations.select_related("author").all(),
            "documents": prerequisite.documents.all(),
            "changes": prerequisite.mission.changes.filter(resource_id=prerequisite.id).select_related("author"),
        },
    )


@owner_required
def prerequisite_update(request, prerequisite_id):
    prerequisite = scoped_prerequisite_or_404(request, prerequisite_id)
    form = PrerequisiteForm(request.POST or None, instance=prerequisite, mission=prerequisite.mission)
    if request.method == "POST" and form.is_valid():
        data = {field: form.cleaned_data[field] for field in form._meta.fields}
        update_instance(
            instance=prerequisite,
            data=data,
            actor=request.user,
            reason=form.cleaned_data["change_reason"],
            category=form.cleaned_data["change_category"],
            recalculate=True,
        )
        messages.success(request, "Prérequis mis à jour, priorité recalculée et historique conservé.")
        return redirect("prerequisite_detail", prerequisite_id=prerequisite.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Modifier le prérequis", "mission": prerequisite.mission, "submit_label": "Enregistrer"})


@owner_required
def prerequisite_action(request, prerequisite_id):
    prerequisite = scoped_prerequisite_or_404(request, prerequisite_id)
    initial = {"next_state": prerequisite.state, "next_action": prerequisite.next_action, "next_action_at": prerequisite.next_action_at, "expected_event": prerequisite.expected_event}
    form = ActionForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        try:
            record_action(prerequisite=prerequisite, actor=request.user, **form.cleaned_data)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Journal mis à jour. Action, réponse et confirmation restent distinctes.")
            return redirect("prerequisite_detail", prerequisite_id=prerequisite.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Journal rapide (<2 minutes)", "mission": prerequisite.mission, "submit_label": "Enregistrer"})


@owner_required
def prerequisite_escalate(request, prerequisite_id):
    prerequisite = scoped_prerequisite_or_404(request, prerequisite_id)
    form = EscalationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            escalate_prerequisite(prerequisite=prerequisite, actor=request.user, data=form.cleaned_data)
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Escalade structurée et historisée.")
            return redirect("prerequisite_detail", prerequisite_id=prerequisite.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Escalader le prérequis", "mission": prerequisite.mission, "submit_label": "Escalader"})


@owner_required
def document_upload(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    form = DocumentUploadForm(request.POST or None, request.FILES or None, mission=mission)
    if request.method == "POST" and form.is_valid():
        try:
            document = create_document(uploaded=form.cleaned_data["file"], mission=mission, prerequisite=form.cleaned_data["prerequisite"], actor=request.user)
        except ValidationError as error:
            form.add_error("file", error)
        else:
            audit_event(operation="DOCUMENT_UPLOAD", result="SUCCESS", actor=request.user, tenant=mission.tenant, resource_type="EvidenceDocument", resource_id=document.id, details={"sha256": document.sha256, "scan": document.scan_state})
            messages.success(request, "Document stocké en privé" + (" et placé en quarantaine." if document.scan_state == DocumentScanState.PENDING else "."))
            return redirect("mission_detail", mission_id=mission.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Ajouter un document privé", "mission": mission, "submit_label": "Téléverser"})


@owner_required
@require_POST
def document_toggle_share(request, document_id):
    document = scoped_document_or_404(request, document_id)
    try:
        mark_document_shared(document, not document.is_client_shared)
    except ValidationError as error:
        messages.error(request, "; ".join(error.messages))
    else:
        audit_event(operation="DOCUMENT_SHARE" if document.is_client_shared else "DOCUMENT_UNSHARE", result="SUCCESS", actor=request.user, tenant=document.tenant, resource_type="EvidenceDocument", resource_id=document.id)
        messages.success(request, "Partage client mis à jour. Une nouvelle publication est nécessaire pour rendre le changement visible.")
    return redirect("mission_detail", mission_id=document.mission_id)


@require_GET
def document_download(request, document_id):
    if not request.user.is_authenticated:
        raise Http404("Ressource introuvable")
    document = scoped_document_or_404(request, document_id)
    if document.scan_state != DocumentScanState.SAFE or not document.file:
        raise Http404("Ressource introuvable")
    if request.user.role == UserRole.CLIENT_VIEWER:
        publications = document.mission.publications.filter(revoked_at__isnull=True).order_by("-version")
        publication = publications.first()
        if not publication or str(document.id) not in publication.shared_document_ids:
            audit_event(operation="UNPUBLISHED_DOCUMENT_ACCESS", result="DENIED", actor=request.user, tenant=request.user.tenant, resource_type="EvidenceDocument", resource_id=document.id, request=request)
            raise Http404("Ressource introuvable")
    audit_event(operation="DOCUMENT_DOWNLOAD", result="SUCCESS", actor=request.user, tenant=document.tenant, resource_type="EvidenceDocument", resource_id=document.id, request=request)
    return FileResponse(document.file.open("rb"), as_attachment=True, filename=document.original_name, content_type="application/octet-stream")


@owner_required
def mission_publish(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    form = PublishForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        publication = publish_client_snapshot(mission=mission, actor=request.user, summary_note=form.cleaned_data["summary_note"])
        messages.success(request, f"Projection client v{publication.version} publiée. Les données internes restent exclues.")
        return redirect("mission_detail", mission_id=mission.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Publier une projection client contrôlée", "mission": mission, "submit_label": "Publier"})


@owner_required
def publication_revoke(request, publication_id):
    publication = get_object_or_404(PublicationSnapshot, id=publication_id)
    form = RevokePublicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        revoke_publication(publication=publication, actor=request.user, reason=form.cleaned_data["reason"])
        messages.success(request, "Publication révoquée ; l’ancien lien ne donne plus accès.")
        return redirect("mission_detail", mission_id=publication.mission_id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Révoquer la publication", "mission": publication.mission, "submit_label": "Révoquer"})


@viewer_required
def portal_home(request):
    missions = missions_for_user(request.user).select_related("tenant")
    rows = []
    for mission in missions:
        publication = mission.publications.filter(revoked_at__isnull=True).first()
        if publication:
            rows.append((mission, publication))
    return render(request, "operations/portal_home.html", {"rows": rows})


@require_GET
def portal_publication(request, publication_id):
    if not request.user.is_authenticated:
        return redirect("login")
    try:
        publication = PublicationSnapshot.objects.get(
            id=publication_id,
            revoked_at__isnull=True,
            mission__in=missions_for_user(request.user),
        )
    except PublicationSnapshot.DoesNotExist:
        audit_event(
            operation="CROSS_TENANT_OR_REVOKED_PUBLICATION",
            result="DENIED",
            actor=request.user,
            tenant=getattr(request.user, "tenant", None),
            resource_type="PublicationSnapshot",
            resource_id=publication_id,
            request=request,
        )
        raise Http404("Ressource introuvable")
    audit_event(operation="CLIENT_PUBLICATION_ACCESS", result="SUCCESS", actor=request.user, tenant=request.user.tenant, resource_type="PublicationSnapshot", resource_id=publication.id, request=request)
    documents = EvidenceDocument.objects.filter(id__in=publication.shared_document_ids, tenant=request.user.tenant, scan_state=DocumentScanState.SAFE)
    return render(request, "operations/portal_detail.html", {"publication": publication, "payload": publication.payload, "documents": documents})


@viewer_required
@require_GET
def portal_api_summary(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    publication = mission.publications.filter(revoked_at__isnull=True).first()
    if not publication:
        raise Http404("Ressource introuvable")
    return JsonResponse(publication.payload)


@owner_required
def organization_list(request):
    return render(request, "operations/organization_list.html", {"organizations": Organization.objects.all()})


@owner_required
def organization_create(request):
    form = OrganizationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        organization = form.save()
        audit_event(operation="ORGANIZATION_CREATE", result="SUCCESS", actor=request.user, tenant=organization, resource_type="Organization", resource_id=organization.id)
        return redirect("organization_list")
    return render(request, "operations/form_page.html", {"form": form, "title": "Créer un espace client isolé", "submit_label": "Créer"})


@owner_required
def viewer_create(request):
    form = ClientViewerCreateForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        audit_event(operation="CLIENT_VIEWER_CREATE", result="SUCCESS", actor=request.user, tenant=user.tenant, resource_type="User", resource_id=user.id)
        messages.success(request, "Viewer créé. Il configurera son MFA à la première connexion.")
        return redirect("organization_list")
    return render(request, "operations/form_page.html", {"form": form, "title": "Créer un Client Viewer nominatif", "submit_label": "Créer"})


@owner_required
def mission_access_create(request, tenant_id):
    tenant = get_object_or_404(Organization, id=tenant_id)
    form = MissionAccessForm(request.POST or None, tenant=tenant)
    if request.method == "POST" and form.is_valid():
        access = form.save(commit=False)
        access.tenant = tenant
        access.full_clean()
        access.save()
        audit_event(operation="MISSION_ACCESS_GRANT", result="SUCCESS", actor=request.user, tenant=tenant, resource_type="MissionAccess", resource_id=access.id)
        return redirect("organization_list")
    return render(request, "operations/form_page.html", {"form": form, "title": f"Accès lecture seule — {tenant.name}", "submit_label": "Accorder"})


@owner_required
def extension_create(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    form = ExtensionRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        extension = form.save(commit=False)
        extension.tenant = mission.tenant
        extension.mission = mission
        extension.author = request.user
        extension.full_clean()
        extension.save()
        audit_event(operation="EXTENSION_CREATE", result="SUCCESS", actor=request.user, tenant=mission.tenant, resource_type="ExtensionRequest", resource_id=extension.id)
        messages.success(request, "Extension/avenant créé sans interrompre le périmètre initial.")
        return redirect("mission_detail", mission_id=mission.id)
    return render(request, "operations/form_page.html", {"form": form, "title": "Qualifier une évolution / extension", "mission": mission, "submit_label": "Créer"})


@owner_required
def config_view(request):
    config = BusinessConfig.get_solo()
    form = BusinessConfigForm(request.POST or None, instance=config)
    if request.method == "POST" and form.is_valid():
        before = serialize_model(config)
        config = form.save(commit=False)
        config.full_clean()
        config.save()
        audit_event(operation="BUSINESS_CONFIG_UPDATE", result="SUCCESS", actor=request.user, resource_type="BusinessConfig", resource_id=config.id, details={"reason": form.cleaned_data["change_reason"], "before": before, "after": serialize_model(config)})
        messages.success(request, "Paramètres métier mis à jour sans modification de code.")
        return redirect("config")
    return render(request, "operations/form_page.html", {"form": form, "title": "Paramètres métier configurables", "submit_label": "Enregistrer"})


@owner_required
def incident_list(request):
    return render(request, "operations/incident_list.html", {"incidents": SecurityIncident.objects.select_related("tenant").all()})


@owner_required
def incident_create(request):
    form = IncidentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        incident = form.save(commit=False)
        incident.created_by = request.user
        incident.save()
        audit_event(operation="INCIDENT_CREATE", result="SUCCESS", actor=request.user, tenant=incident.tenant, resource_type="SecurityIncident", resource_id=incident.id)
        return redirect("incident_list")
    return render(request, "operations/form_page.html", {"form": form, "title": "Journaliser un incident", "submit_label": "Enregistrer"})


@owner_required
@require_POST
def revoke_other_sessions(request):
    request.user.session_version += 1
    request.user.save(update_fields=["session_version"])
    request.session["session_version"] = request.user.session_version
    audit_event(operation="SESSIONS_REVOKE", result="SUCCESS", actor=request.user, request=request)
    messages.success(request, "Toutes les autres sessions ont été révoquées.")
    return redirect("dashboard")


@owner_required
@require_GET
def mission_export(request, mission_id):
    mission = scoped_mission_or_404(request, mission_id)
    payload = {
        "exported_at": timezone.now().isoformat(),
        "mission": serialize_model(mission),
        "contacts": [serialize_model(item) for item in mission.contacts.all()],
        "prerequisites": [serialize_model(item) for item in mission.prerequisites.all()],
        "actions": [serialize_model(item) for item in mission.actions.all()],
        "escalations": [serialize_model(item) for item in mission.escalations.all()],
        "changes": [serialize_model(item) for item in mission.changes.all()],
        "documents": [serialize_model(item) for item in mission.documents.all()],
        "state_history": [serialize_model(item) for item in mission.state_history.all()],
    }
    audit_event(operation="MISSION_EXPORT", result="SUCCESS", actor=request.user, tenant=mission.tenant, resource_type="Mission", resource_id=mission.id, request=request)
    response = HttpResponse(json.dumps(payload, ensure_ascii=False, indent=2, default=str), content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="readiness-{mission.code}-export.json"'
    return response


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


def method_not_allowed(request, *args, **kwargs):
    return HttpResponseNotAllowed(["GET"])
