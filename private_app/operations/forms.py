from django import forms
from django.utils import timezone

from .enums import (
    ActionEventType,
    ChangeCategory,
    MissionState,
    PrerequisiteState,
    UserRole,
)
from .models import (
    BusinessConfig,
    Contact,
    ExtensionRequest,
    Mission,
    MissionAccess,
    Organization,
    Prerequisite,
    SecurityIncident,
    User,
)


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%dT%H:%M")
        super().__init__(*args, **kwargs)


class ReasonForm(forms.Form):
    change_reason = forms.CharField(label="Motif du changement", widget=forms.Textarea(attrs={"rows": 2}))
    change_category = forms.ChoiceField(label="Catégorie", choices=ChangeCategory.choices, initial=ChangeCategory.MINOR)


class LoginForm(forms.Form):
    identifier = forms.CharField(label="Identifiant ou e-mail", max_length=254)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class MFACodeForm(forms.Form):
    code = forms.CharField(label="Code d’authentification ou code de secours", max_length=32, strip=True)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ["name", "slug", "is_active", "mission_retention_days", "document_retention_days", "audit_retention_days", "privacy_notes"]
        widgets = {"privacy_notes": forms.Textarea(attrs={"rows": 3})}


class MissionCreateForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = [
            "tenant",
            "code",
            "project_name",
            "site_name",
            "protected_at",
            "approximate_open_count",
            "approximate_critical_count",
            "interlocutor_count",
            "previous_steps",
            "coordinates_available",
            "closure_criteria_available",
            "contact_authorizations_available",
            "client_expectation",
        ]
        widgets = {
            "protected_at": DateTimeLocalInput(),
            "previous_steps": forms.Textarea(attrs={"rows": 3}),
            "client_expectation": forms.Textarea(attrs={"rows": 3}),
        }


class MissionQualificationForm(ReasonForm, forms.ModelForm):
    class Meta:
        model = Mission
        fields = [
            "protected_at",
            "approximate_open_count",
            "approximate_critical_count",
            "interlocutor_count",
            "previous_steps",
            "coordinates_available",
            "closure_criteria_available",
            "contact_authorizations_available",
            "client_expectation",
        ]
        widgets = {
            "protected_at": DateTimeLocalInput(),
            "previous_steps": forms.Textarea(attrs={"rows": 3}),
            "client_expectation": forms.Textarea(attrs={"rows": 3}),
        }


class AcceptanceForm(ReasonForm, forms.ModelForm):
    class Meta:
        model = Mission
        fields = [
            "acceptance_know",
            "acceptance_scope",
            "acceptance_authority",
            "acceptance_responsibility",
            "acceptance_result",
            "acceptance_note",
        ]
        widgets = {"acceptance_note": forms.Textarea(attrs={"rows": 3})}

    def clean(self):
        cleaned = super().clean()
        accepted = {"ACCEPTABLE", "ACCEPTABLE_URGENT"}
        if cleaned.get("acceptance_result") in accepted:
            controls = [cleaned.get(name) for name in ("acceptance_know", "acceptance_scope", "acceptance_authority", "acceptance_responsibility")]
            if any(value != "YES" for value in controls):
                raise forms.ValidationError("Les quatre contrôles doivent être Oui avant une acceptation.")
        return cleaned


class FeasibilityForm(ReasonForm, forms.ModelForm):
    class Meta:
        model = Mission
        fields = [
            "operational_window_hours",
            "expected_active_prerequisites",
            "expected_p0_p1",
            "expected_actions",
            "committed_load_hours",
            "operator_available_hours",
            "manual_load_estimate_hours",
            "reduced_scope_proposal",
            "feasibility_result",
            "feasibility_note",
        ]
        widgets = {
            "reduced_scope_proposal": forms.Textarea(attrs={"rows": 3}),
            "feasibility_note": forms.Textarea(attrs={"rows": 3}),
        }


class FinancialForm(ReasonForm, forms.ModelForm):
    class Meta:
        model = Mission
        fields = [
            "commercial_status",
            "mission_type",
            "agreed_amount",
            "payment_expected_amount",
            "payment_received_amount",
            "payment_received_at",
            "financial_trigger_required",
            "financial_exception_reason",
        ]
        widgets = {
            "payment_received_at": DateTimeLocalInput(),
            "financial_exception_reason": forms.Textarea(attrs={"rows": 2}),
        }


class StateTransitionForm(forms.Form):
    target_state = forms.ChoiceField(label="Nouvel état", choices=MissionState.choices)
    reason = forms.CharField(label="Motif", widget=forms.Textarea(attrs={"rows": 2}))


class ClosureForm(forms.Form):
    closure_reason = forms.CharField(label="Motif de clôture", widget=forms.Textarea(attrs={"rows": 3}))
    transition_reason = forms.CharField(label="Motif du changement d’état", widget=forms.Textarea(attrs={"rows": 2}))


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["full_name", "organization_name", "job_title", "email", "phone", "authorized_for_contact", "authorization_source", "internal_note"]
        widgets = {"internal_note": forms.Textarea(attrs={"rows": 2})}


class PrerequisiteForm(ReasonForm, forms.ModelForm):
    class Meta:
        model = Prerequisite
        fields = [
            "code",
            "title",
            "client_closure_criterion",
            "useful_deadline",
            "client_criticality",
            "client_declared_blocking",
            "primary_contact",
            "secondary_contact",
            "escalation_contact",
            "contact_authorization_confirmed",
            "initial_state",
            "initial_previous_actions",
            "taken_over_at",
            "state",
            "closure_criterion_satisfied",
            "confirmation_score",
            "dependency_score",
            "inertia_score",
            "next_action",
            "next_action_at",
            "expected_event",
            "awaiting_client_decision",
            "client_decision_expected",
            "escalation_rule",
            "manual_p0_override",
            "override_reason",
            "critical_blockage_revealed",
            "immediate_escalation_triggered",
            "client_published",
            "client_summary",
        ]
        widgets = {
            "useful_deadline": DateTimeLocalInput(),
            "taken_over_at": DateTimeLocalInput(),
            "next_action_at": DateTimeLocalInput(),
            "client_closure_criterion": forms.Textarea(attrs={"rows": 3}),
            "initial_state": forms.Textarea(attrs={"rows": 3}),
            "initial_previous_actions": forms.Textarea(attrs={"rows": 2}),
            "client_decision_expected": forms.Textarea(attrs={"rows": 2}),
            "escalation_rule": forms.Textarea(attrs={"rows": 2}),
            "override_reason": forms.Textarea(attrs={"rows": 2}),
            "client_summary": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, mission=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.mission = mission or getattr(self.instance, "mission", None)
        contacts = Contact.objects.none()
        if self.mission and self.mission.pk:
            contacts = self.mission.contacts.all()
        for name in ("primary_contact", "secondary_contact", "escalation_contact"):
            self.fields[name].queryset = contacts
        if not self.instance.pk:
            self.fields["taken_over_at"].initial = timezone.now()


class ActionForm(forms.Form):
    event_type = forms.ChoiceField(label="Nature de l’événement", choices=ActionEventType.choices)
    occurred_at = forms.DateTimeField(label="Date/heure", widget=DateTimeLocalInput(), initial=timezone.now)
    channel = forms.CharField(label="Canal / action", max_length=80, required=False)
    factual_result = forms.CharField(label="Résultat factuel", widget=forms.Textarea(attrs={"rows": 3}))
    next_state = forms.ChoiceField(label="État après mise à jour", choices=PrerequisiteState.choices)
    closure_criterion_satisfied = forms.BooleanField(label="Critère de clôture client explicitement satisfait", required=False)
    next_action = forms.CharField(label="Prochaine action", max_length=240, required=False)
    next_action_at = forms.DateTimeField(label="Date/heure prochaine action", widget=DateTimeLocalInput(), required=False)
    expected_event = forms.CharField(label="Événement attendu", max_length=240, required=False)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("next_state") not in {
            PrerequisiteState.CONFIRMED,
            PrerequisiteState.CANCELLED_BY_CLIENT,
            PrerequisiteState.CLOSED_UNRESOLVED,
            PrerequisiteState.ESCALATED,
        } and not all(cleaned.get(field) for field in ("next_action", "next_action_at", "expected_event")):
            raise forms.ValidationError("Un point ouvert exige une prochaine action datée et un événement attendu.")
        return cleaned


class EscalationForm(forms.Form):
    level = forms.TypedChoiceField(label="Niveau", choices=[(1, "Niveau 1"), (2, "Niveau 2"), (3, "Niveau 3 — décision client")], coerce=int)
    expected = forms.CharField(label="Ce qui était attendu", widget=forms.Textarea(attrs={"rows": 2}))
    readiness_actions = forms.CharField(label="Ce que Readiness a fait", widget=forms.Textarea(attrs={"rows": 2}))
    obtained_or_missing = forms.CharField(label="Ce qui a été obtenu ou non", widget=forms.Textarea(attrs={"rows": 2}))
    time_remaining = forms.CharField(label="Temps restant", max_length=180)
    client_decision_reason = forms.CharField(label="Pourquoi une intervention/décision client est requise", widget=forms.Textarea(attrs={"rows": 2}))


class DocumentUploadForm(forms.Form):
    file = forms.FileField(label="Document / preuve")
    prerequisite = forms.ModelChoiceField(label="Prérequis associé", queryset=Prerequisite.objects.none(), required=False)

    def __init__(self, *args, mission=None, **kwargs):
        super().__init__(*args, **kwargs)
        if mission:
            self.fields["prerequisite"].queryset = mission.prerequisites.all()


class PublishForm(forms.Form):
    summary_note = forms.CharField(label="Message de synthèse client", widget=forms.Textarea(attrs={"rows": 3}), required=False)


class RevokePublicationForm(forms.Form):
    reason = forms.CharField(label="Motif de révocation", widget=forms.Textarea(attrs={"rows": 2}))


class ExtensionRequestForm(forms.ModelForm):
    class Meta:
        model = ExtensionRequest
        fields = ["description", "category", "commercial_status", "agreed_amount", "validated_at"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3}), "validated_at": DateTimeLocalInput()}


class BusinessConfigForm(ReasonForm, forms.ModelForm):
    class Meta:
        model = BusinessConfig
        exclude = ["name", "created_at", "updated_at"]
        widgets = {"retention_policy_note": forms.Textarea(attrs={"rows": 3})}


class IncidentForm(forms.ModelForm):
    class Meta:
        model = SecurityIncident
        fields = [
            "tenant",
            "title",
            "detected_at",
            "status",
            "accounts_projects_data",
            "access_revocation",
            "logs_preserved",
            "recovery_actions",
            "notification_information",
            "closed_at",
        ]
        widgets = {
            "detected_at": DateTimeLocalInput(),
            "closed_at": DateTimeLocalInput(),
            "accounts_projects_data": forms.Textarea(attrs={"rows": 3}),
            "access_revocation": forms.Textarea(attrs={"rows": 3}),
            "recovery_actions": forms.Textarea(attrs={"rows": 3}),
            "notification_information": forms.Textarea(attrs={"rows": 3}),
        }


class ClientViewerCreateForm(forms.ModelForm):
    password = forms.CharField(label="Mot de passe temporaire", widget=forms.PasswordInput, min_length=14)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "tenant", "is_active"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = UserRole.CLIENT_VIEWER
        user.set_password(self.cleaned_data["password"])
        user.full_clean()
        if commit:
            user.save()
        return user


class MissionAccessForm(forms.ModelForm):
    class Meta:
        model = MissionAccess
        fields = ["user", "mission", "is_active"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            self.fields["user"].queryset = User.objects.filter(tenant=tenant, role=UserRole.CLIENT_VIEWER)
            self.fields["mission"].queryset = Mission.objects.filter(tenant=tenant)
