import hashlib
import json
import uuid
from pathlib import Path

from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from .enums import (
    AcceptanceResult,
    ActionEventType,
    ChangeCategory,
    DocumentScanState,
    EscalationLevel,
    FeasibilityResult,
    MissionState,
    PrerequisiteState,
    PriorityLevel,
    TriState,
    UserRole,
    Visibility,
)


def utcnow():
    return timezone.now()


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(default=utcnow, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ImmutableModel(models.Model):
    """Protection applicative ; PostgreSQL ajoute aussi des triggers d'immutabilité."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk and type(self).objects.filter(pk=self.pk).exists():
            raise ValidationError("Cet enregistrement historique est immuable.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("La suppression d'un enregistrement historique est interdite.")


class Organization(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=80, unique=True)
    is_active = models.BooleanField(default=True)
    mission_retention_days = models.PositiveIntegerField(default=365)
    audit_retention_days = models.PositiveIntegerField(default=730)
    document_retention_days = models.PositiveIntegerField(default=365)
    privacy_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=24, choices=UserRole.choices, default=UserRole.CLIENT_VIEWER)
    tenant = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.PROTECT, related_name="users")
    mfa_secret_encrypted = models.TextField(blank=True)
    mfa_recovery_hashes = models.JSONField(default=list, blank=True)
    mfa_confirmed_at = models.DateTimeField(null=True, blank=True)
    session_version = models.PositiveIntegerField(default=1)

    REQUIRED_FIELDS = ["email"]

    def clean(self):
        super().clean()
        if self.role == UserRole.OWNER and self.tenant_id:
            raise ValidationError({"tenant": "Le compte Owner n'appartient pas à un client."})
        if self.role == UserRole.CLIENT_VIEWER and not self.tenant_id:
            raise ValidationError({"tenant": "Un Client Viewer doit être rattaché à un client."})

    @property
    def mfa_is_configured(self):
        return bool(self.mfa_secret_encrypted and self.mfa_confirmed_at)

    def set_mfa_secret(self, raw_secret):
        self.mfa_secret_encrypted = Fernet(settings.FIELD_ENCRYPTION_KEY.encode()).encrypt(raw_secret.encode()).decode()

    def get_mfa_secret(self):
        if not self.mfa_secret_encrypted:
            return ""
        return Fernet(settings.FIELD_ENCRYPTION_KEY.encode()).decrypt(self.mfa_secret_encrypted.encode()).decode()

    def set_recovery_codes(self, codes):
        self.mfa_recovery_hashes = [hashlib.sha256(code.encode()).hexdigest() for code in codes]

    def consume_recovery_code(self, code):
        digest = hashlib.sha256(code.strip().upper().encode()).hexdigest()
        if digest not in self.mfa_recovery_hashes:
            return False
        hashes = list(self.mfa_recovery_hashes)
        hashes.remove(digest)
        self.mfa_recovery_hashes = hashes
        self.save(update_fields=["mfa_recovery_hashes"])
        return True


class BusinessConfig(TimestampedModel):
    name = models.CharField(max_length=80, default="Configuration V1", unique=True)
    criticality_weight = models.DecimalField(max_digits=4, decimal_places=2, default=2)
    time_weight = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    confirmation_weight = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    dependencies_weight = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    inertia_weight = models.DecimalField(max_digits=4, decimal_places=2, default=1)
    immediate_time_hours = models.PositiveIntegerField(default=48)
    high_time_days = models.PositiveIntegerField(default=5)
    medium_time_days = models.PositiveIntegerField(default=10)
    p0_min = models.DecimalField(max_digits=5, decimal_places=2, default=13)
    p1_min = models.DecimalField(max_digits=5, decimal_places=2, default=9)
    p2_min = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    override_overdue_missing = models.BooleanField(default=True)
    override_blocking_within_hours = models.PositiveIntegerField(default=48)
    override_critical_revelation = models.BooleanField(default=True)
    override_immediate_escalation = models.BooleanField(default=True)
    price_s = models.DecimalField(max_digits=10, decimal_places=2, default=1500)
    price_m = models.DecimalField(max_digits=10, decimal_places=2, default=2500)
    price_l = models.DecimalField(max_digits=10, decimal_places=2, default=4000)
    urgency_15_days = models.DecimalField(max_digits=4, decimal_places=2, default=1.25)
    urgency_7_days = models.DecimalField(max_digits=4, decimal_places=2, default=1.50)
    urgency_72_hours = models.DecimalField(max_digits=4, decimal_places=2, default=2.00)
    weekly_operator_capacity_hours = models.DecimalField(max_digits=6, decimal_places=2, default=30)
    estimated_minutes_per_action = models.PositiveIntegerField(default=12)
    max_parallel_p0 = models.PositiveIntegerField(default=6)
    max_upload_bytes = models.PositiveIntegerField(default=15 * 1024 * 1024)
    retention_policy_note = models.TextField(blank=True)

    @classmethod
    def get_solo(cls):
        instance, _ = cls.objects.get_or_create(name="Configuration V1")
        return instance

    def clean(self):
        if not (self.p0_min > self.p1_min > self.p2_min >= 0):
            raise ValidationError("Les seuils doivent respecter P0 > P1 > P2 >= 0.")
        if not (self.immediate_time_hours <= self.high_time_days * 24 <= self.medium_time_days * 24):
            raise ValidationError("Les seuils temporels sont incohérents.")


class Mission(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="missions")
    code = models.CharField(max_length=40)
    project_name = models.CharField(max_length=180)
    site_name = models.CharField(max_length=180, blank=True)
    protected_at = models.DateTimeField(null=True, blank=True, verbose_name="Date/heure à protéger")

    approximate_open_count = models.PositiveIntegerField(null=True, blank=True)
    approximate_critical_count = models.PositiveIntegerField(null=True, blank=True)
    interlocutor_count = models.PositiveIntegerField(null=True, blank=True)
    previous_steps = models.TextField(blank=True)
    coordinates_available = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    closure_criteria_available = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    contact_authorizations_available = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    client_expectation = models.TextField(blank=True)

    acceptance_know = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    acceptance_scope = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    acceptance_authority = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    acceptance_responsibility = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    acceptance_result = models.CharField(max_length=28, choices=AcceptanceResult.choices, default=AcceptanceResult.UNKNOWN)
    acceptance_note = models.TextField(blank=True)

    operational_window_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    expected_active_prerequisites = models.PositiveIntegerField(null=True, blank=True)
    expected_p0_p1 = models.PositiveIntegerField(null=True, blank=True)
    expected_actions = models.PositiveIntegerField(null=True, blank=True)
    committed_load_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    operator_available_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    manual_load_estimate_hours = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    reduced_scope_proposal = models.TextField(blank=True)
    feasibility_result = models.CharField(max_length=32, choices=FeasibilityResult.choices, default=FeasibilityResult.UNKNOWN)
    feasibility_note = models.TextField(blank=True)

    commercial_status = models.CharField(max_length=80, blank=True)
    mission_type = models.CharField(max_length=80, blank=True)
    indicative_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    agreed_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_expected_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_received_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_received_at = models.DateTimeField(null=True, blank=True)
    financial_trigger_required = models.BooleanField(default=True)
    financial_exception_reason = models.TextField(blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    state = models.CharField(max_length=36, choices=MissionState.choices, default=MissionState.QUALIFICATION)
    t0_snapshot = models.JSONField(null=True, blank=True)
    t0_captured_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    closure_reason = models.TextField(blank=True)
    closure_report = models.JSONField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["tenant", "code"], name="unique_mission_code_per_tenant")]

    def __str__(self):
        return f"{self.code} — {self.project_name}"

    @property
    def payment_satisfied(self):
        if not self.financial_trigger_required:
            return bool(self.financial_exception_reason)
        if self.payment_expected_amount is None or self.payment_received_at is None or self.payment_received_amount is None:
            return False
        return self.payment_received_amount >= self.payment_expected_amount

    def delete(self, *args, **kwargs):
        raise ValidationError("Une mission ne peut pas être supprimée ; utilisez l'archivage contrôlé.")


class Contact(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="contacts")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="contacts")
    full_name = models.CharField(max_length=180)
    organization_name = models.CharField(max_length=180, blank=True)
    job_title = models.CharField(max_length=180, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    authorized_for_contact = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    authorization_source = models.CharField(max_length=180, blank=True)
    internal_note = models.TextField(blank=True)

    class Meta:
        ordering = ["full_name"]

    def clean(self):
        if self.mission_id and self.tenant_id != self.mission.tenant_id:
            raise ValidationError("Le contact et la mission doivent appartenir au même client.")

    def __str__(self):
        return self.full_name


class MissionAccess(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="mission_accesses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mission_accesses")
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name="viewer_accesses")
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "mission"], name="unique_viewer_mission_access")]

    def clean(self):
        if self.user_id and (self.user.role != UserRole.CLIENT_VIEWER or self.user.tenant_id != self.tenant_id):
            raise ValidationError("Le Viewer doit appartenir au même client.")
        if self.mission_id and self.mission.tenant_id != self.tenant_id:
            raise ValidationError("La mission doit appartenir au même client.")


CRITICALITY_CHOICES = [
    (0, "0 — secondaire"),
    (1, "1 — important"),
    (2, "2 — très important"),
    (3, "3 — susceptible de bloquer/perturber selon le client"),
]
CONFIRMATION_SCORE_CHOICES = [
    (0, "0 — critère/preuve reçu"),
    (1, "1 — positif, confirmation finale manquante"),
    (2, "2 — vague/partiel/ancien"),
    (3, "3 — aucune réponse/retard/engagement non tenu"),
]
DEPENDENCY_CHOICES = [(0, "0 — indépendant"), (1, "1 — une action dépend"), (2, "2 — plusieurs actions dépendent")]
INERTIA_CHOICES = [(0, "0 — simple/rapide"), (1, "1 — plusieurs personnes/services"), (2, "2 — retard/processus long/contact difficile")]


class Prerequisite(TimestampedModel):
    CLOSED_STATES = {
        PrerequisiteState.CONFIRMED,
        PrerequisiteState.CANCELLED_BY_CLIENT,
        PrerequisiteState.CLOSED_UNRESOLVED,
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="prerequisites")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="prerequisites")
    code = models.CharField(max_length=40)
    title = models.CharField(max_length=220)
    client_closure_criterion = models.TextField()
    useful_deadline = models.DateTimeField(null=True, blank=True)
    client_criticality = models.PositiveSmallIntegerField(choices=CRITICALITY_CHOICES, null=True, blank=True)
    client_declared_blocking = models.BooleanField(default=False)
    primary_contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.PROTECT, related_name="primary_prerequisites")
    secondary_contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.PROTECT, related_name="secondary_prerequisites")
    escalation_contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.PROTECT, related_name="escalation_prerequisites")
    contact_authorization_confirmed = models.CharField(max_length=12, choices=TriState.choices, default=TriState.UNKNOWN)
    initial_state = models.TextField()
    initial_previous_actions = models.TextField(blank=True)
    taken_over_at = models.DateTimeField(null=True, blank=True)

    state = models.CharField(max_length=36, choices=PrerequisiteState.choices, default=PrerequisiteState.TO_QUALIFY)
    closure_criterion_satisfied = models.BooleanField(default=False)
    confirmation_score = models.PositiveSmallIntegerField(choices=CONFIRMATION_SCORE_CHOICES, null=True, blank=True)
    dependency_score = models.PositiveSmallIntegerField(choices=DEPENDENCY_CHOICES, null=True, blank=True)
    inertia_score = models.PositiveSmallIntegerField(choices=INERTIA_CHOICES, null=True, blank=True)
    priority_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    priority_level = models.CharField(max_length=12, choices=PriorityLevel.choices, default=PriorityLevel.UNKNOWN)
    priority_explanation = models.TextField(blank=True)
    priority_calculated_at = models.DateTimeField(null=True, blank=True)
    manual_p0_override = models.BooleanField(default=False)
    override_reason = models.TextField(blank=True)
    critical_blockage_revealed = models.BooleanField(default=False)
    immediate_escalation_triggered = models.BooleanField(default=False)

    next_action = models.CharField(max_length=240, blank=True)
    next_action_at = models.DateTimeField(null=True, blank=True)
    expected_event = models.CharField(max_length=240, blank=True)
    last_action_at = models.DateTimeField(null=True, blank=True)
    last_action_summary = models.TextField(blank=True)
    last_response_at = models.DateTimeField(null=True, blank=True)
    last_response_summary = models.TextField(blank=True)
    awaiting_client_decision = models.BooleanField(default=False)
    client_decision_expected = models.TextField(blank=True)
    escalation_rule = models.TextField(blank=True)
    escalation_level = models.PositiveSmallIntegerField(choices=EscalationLevel.choices, default=EscalationLevel.NORMAL)
    last_reviewed_at = models.DateTimeField(null=True, blank=True)
    new_information_at = models.DateTimeField(null=True, blank=True)

    client_published = models.BooleanField(default=False)
    client_summary = models.TextField(blank=True)

    class Meta:
        ordering = ["priority_level", "useful_deadline", "code"]
        constraints = [models.UniqueConstraint(fields=["mission", "code"], name="unique_prerequisite_code_per_mission")]

    def __str__(self):
        return f"{self.code} — {self.title}"

    @property
    def is_open(self):
        return self.state not in self.CLOSED_STATES

    def clean(self):
        errors = {}
        if self.mission_id and self.tenant_id != self.mission.tenant_id:
            errors["tenant"] = "Le prérequis et la mission doivent appartenir au même client."
        for field in ("primary_contact", "secondary_contact", "escalation_contact"):
            contact = getattr(self, field, None)
            if contact and (contact.tenant_id != self.tenant_id or contact.mission_id != self.mission_id):
                errors[field] = "Ce contact n'appartient pas à cette mission."
        if self.state == PrerequisiteState.CONFIRMED and not self.closure_criterion_satisfied:
            errors["closure_criterion_satisfied"] = "Aucune confirmation sans critère client satisfait."
        if self.is_open:
            has_next_action = bool(self.next_action and self.next_action_at and self.expected_event)
            has_client_decision = bool(self.awaiting_client_decision and self.client_decision_expected)
            if not (has_next_action or has_client_decision):
                errors["next_action"] = "Un point ouvert exige une action datée ou une décision client explicitement attendue."
        if self.state == PrerequisiteState.ESCALATED and not self.awaiting_client_decision:
            errors["awaiting_client_decision"] = "Une escalade de niveau client doit attendre une décision explicite."
        if self.manual_p0_override and not self.override_reason:
            errors["override_reason"] = "Un override P0 exige un motif factuel."
        if errors:
            raise ValidationError(errors)

    def delete(self, *args, **kwargs):
        raise ValidationError("Un prérequis ne peut pas être supprimé ; annulez-le en conservant l'historique.")


class MissionStateHistory(ImmutableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="mission_state_history")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="state_history")
    from_state = models.CharField(max_length=36, choices=MissionState.choices, blank=True)
    to_state = models.CharField(max_length=36, choices=MissionState.choices)
    reason = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="mission_transitions")
    created_at = models.DateTimeField(default=utcnow, editable=False)

    class Meta:
        ordering = ["-created_at"]


class ActionRecord(ImmutableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="actions")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="actions")
    prerequisite = models.ForeignKey(Prerequisite, on_delete=models.PROTECT, related_name="actions")
    event_type = models.CharField(max_length=20, choices=ActionEventType.choices)
    occurred_at = models.DateTimeField(default=utcnow)
    channel = models.CharField(max_length=80, blank=True)
    factual_result = models.TextField()
    next_action = models.CharField(max_length=240, blank=True)
    next_action_at = models.DateTimeField(null=True, blank=True)
    expected_event = models.CharField(max_length=240, blank=True)
    visibility = models.CharField(max_length=16, choices=Visibility.choices, default=Visibility.INTERNAL)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="actions_created")
    created_at = models.DateTimeField(default=utcnow, editable=False)

    class Meta:
        ordering = ["-occurred_at", "-created_at"]

    def clean(self):
        if self.prerequisite_id and (
            self.tenant_id != self.prerequisite.tenant_id or self.mission_id != self.prerequisite.mission_id
        ):
            raise ValidationError("Action, client, mission et prérequis doivent correspondre.")


class EscalationRecord(ImmutableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="escalations")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="escalations")
    prerequisite = models.ForeignKey(Prerequisite, on_delete=models.PROTECT, related_name="escalations")
    level = models.PositiveSmallIntegerField(choices=EscalationLevel.choices)
    expected = models.TextField()
    readiness_actions = models.TextField()
    obtained_or_missing = models.TextField()
    time_remaining = models.CharField(max_length=180)
    client_decision_reason = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="escalations_created")
    created_at = models.DateTimeField(default=utcnow, editable=False)

    class Meta:
        ordering = ["-created_at"]


class ChangeRecord(ImmutableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="changes")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="changes")
    resource_type = models.CharField(max_length=60)
    resource_id = models.UUIDField()
    category = models.CharField(max_length=32, choices=ChangeCategory.choices, default=ChangeCategory.MINOR)
    before_data = models.JSONField(default=dict)
    after_data = models.JSONField(default=dict)
    reason = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="changes_created")
    created_at = models.DateTimeField(default=utcnow, editable=False)

    class Meta:
        ordering = ["-created_at"]


class ExtensionRequest(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="extensions")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="extensions")
    description = models.TextField()
    category = models.CharField(max_length=32, choices=ChangeCategory.choices, default=ChangeCategory.MATERIAL_EXTENSION)
    commercial_status = models.CharField(max_length=80, default="À qualifier")
    agreed_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="extensions_created")


def document_upload_path(instance, filename):
    suffix = Path(filename).suffix.lower()[:10]
    return f"tenants/{instance.tenant_id}/missions/{instance.mission_id}/documents/{instance.id}{suffix}"


class EvidenceDocument(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="documents")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="documents")
    prerequisite = models.ForeignKey(Prerequisite, null=True, blank=True, on_delete=models.PROTECT, related_name="documents")
    file = models.FileField(upload_to=document_upload_path, max_length=500, blank=True)
    original_name = models.CharField(max_length=255)
    detected_type = models.CharField(max_length=100)
    size_bytes = models.PositiveBigIntegerField()
    sha256 = models.CharField(max_length=64)
    scan_state = models.CharField(max_length=16, choices=DocumentScanState.choices, default=DocumentScanState.PENDING)
    scan_details = models.CharField(max_length=255, blank=True)
    is_client_shared = models.BooleanField(default=False)
    shared_at = models.DateTimeField(null=True, blank=True)
    retention_deleted_at = models.DateTimeField(null=True, blank=True)
    retention_reason = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="documents_uploaded")

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.mission_id and self.mission.tenant_id != self.tenant_id:
            raise ValidationError("Le document doit appartenir au même client que la mission.")
        if self.prerequisite_id and (
            self.prerequisite.tenant_id != self.tenant_id or self.prerequisite.mission_id != self.mission_id
        ):
            raise ValidationError("Le document doit appartenir au même dossier que le prérequis.")
        if self.is_client_shared and self.scan_state != DocumentScanState.SAFE:
            raise ValidationError("Un document non validé ne peut pas être partagé.")

    def delete(self, *args, **kwargs):
        raise ValidationError("Un document de mission ne peut pas être supprimé silencieusement.")


class PublicationSnapshot(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, on_delete=models.PROTECT, related_name="publications")
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name="publications")
    version = models.PositiveIntegerField()
    payload = models.JSONField()
    shared_document_ids = models.JSONField(default=list)
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="publications_created")
    published_at = models.DateTimeField(default=utcnow)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="publications_revoked")
    revoke_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-version"]
        constraints = [models.UniqueConstraint(fields=["mission", "version"], name="unique_publication_version")]

    @property
    def is_active(self):
        return self.revoked_at is None


class AuditLog(ImmutableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.PROTECT, related_name="audit_logs")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs")
    actor_label = models.CharField(max_length=180, blank=True)
    operation = models.CharField(max_length=80)
    resource_type = models.CharField(max_length=60, blank=True)
    resource_id = models.CharField(max_length=80, blank=True)
    result = models.CharField(max_length=40)
    ip_hash = models.CharField(max_length=64, blank=True)
    user_agent_hash = models.CharField(max_length=64, blank=True)
    details = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=utcnow, editable=False)

    class Meta:
        ordering = ["-created_at"]


class SecurityIncident(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.PROTECT, related_name="incidents")
    title = models.CharField(max_length=220)
    detected_at = models.DateTimeField(default=utcnow)
    status = models.CharField(max_length=60, default="OUVERT")
    accounts_projects_data = models.TextField(blank=True)
    access_revocation = models.TextField(blank=True)
    logs_preserved = models.BooleanField(default=False)
    recovery_actions = models.TextField(blank=True)
    notification_information = models.TextField(blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="incidents_created")


class LoginAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    identifier_hash = models.CharField(max_length=64, db_index=True)
    ip_hash = models.CharField(max_length=64, db_index=True)
    succeeded = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=utcnow, db_index=True)

    class Meta:
        ordering = ["-created_at"]


def serialize_model(instance):
    data = {}
    for field in instance._meta.concrete_fields:
        if field.name in {"mfa_secret_encrypted", "password"}:
            continue
        value = field.value_from_object(instance)
        if isinstance(value, (uuid.UUID, timezone.datetime)):
            value = str(value)
        try:
            json.dumps(value)
        except TypeError:
            value = str(value)
        data[field.name] = value
    return data
