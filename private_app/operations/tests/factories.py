from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from operations.enums import (
    AcceptanceResult,
    FeasibilityResult,
    MissionState,
    PrerequisiteState,
    TriState,
    UserRole,
)
from operations.models import Contact, Mission, MissionAccess, Organization, User
from operations.services import create_prerequisite


def owner(username="owner"):
    return User.objects.create_user(username=username, email=f"{username}@example.invalid", password="Very-Strong-Test-Password!", role=UserRole.OWNER)


def tenant(label):
    return Organization.objects.create(name=f"Client {label}", slug=label.lower())


def viewer(organization, label):
    return User.objects.create_user(
        username=f"viewer-{label.lower()}",
        email=f"viewer-{label.lower()}@example.invalid",
        password="Very-Strong-Test-Password!",
        role=UserRole.CLIENT_VIEWER,
        tenant=organization,
    )


def mission(organization, label="M-001", state=MissionState.QUALIFICATION, due_days=10):
    return Mission.objects.create(
        tenant=organization,
        code=label,
        project_name=f"Projet {label}",
        protected_at=timezone.now() + timedelta(days=due_days),
        approximate_open_count=5,
        acceptance_know=TriState.YES,
        acceptance_scope=TriState.YES,
        acceptance_authority=TriState.YES,
        acceptance_responsibility=TriState.YES,
        acceptance_result=AcceptanceResult.ACCEPTABLE,
        feasibility_result=FeasibilityResult.FEASIBLE,
        financial_trigger_required=False,
        financial_exception_reason="Test sans flux financier",
        state=state,
    )


def contact(organization, project, label="Contact"):
    return Contact.objects.create(
        tenant=organization,
        mission=project,
        full_name=label,
        email=f"{label.lower().replace(' ', '-')}@example.invalid",
        authorized_for_contact=TriState.YES,
    )


def prerequisite(project, actor, label="PR-001", due_hours=240, **overrides):
    person = overrides.pop("primary_contact", None) or contact(project.tenant, project, f"Contact {label}")
    data = {
        "code": label,
        "title": f"Point {label}",
        "client_closure_criterion": "Confirmation écrite selon la règle client",
        "useful_deadline": timezone.now() + timedelta(hours=due_hours),
        "client_criticality": 2,
        "primary_contact": person,
        "contact_authorization_confirmed": TriState.YES,
        "initial_state": "Ouvert",
        "taken_over_at": timezone.now(),
        "state": PrerequisiteState.ACTION_PLANNED,
        "confirmation_score": 3,
        "dependency_score": 1,
        "inertia_score": 1,
        "next_action": "Relancer le contact",
        "next_action_at": timezone.now() + timedelta(hours=1),
        "expected_event": "Réponse écrite",
    }
    data.update(overrides)
    return create_prerequisite(mission=project, actor=actor, data=data, reason="Création test")


def grant(user, project):
    return MissionAccess.objects.create(tenant=project.tenant, user=user, mission=project)


def login_client(client, user):
    client.force_login(user)
    session = client.session
    session["session_version"] = user.session_version
    session.save()


def tiny_pdf(name="proof.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF", content_type="application/pdf")
