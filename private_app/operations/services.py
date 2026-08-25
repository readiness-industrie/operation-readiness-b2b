from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from .audit import audit_event
from .enums import (
    AcceptanceResult,
    ActionEventType,
    ChangeCategory,
    FeasibilityResult,
    MissionState,
    PrerequisiteState,
    PriorityLevel,
    TriState,
)
from .models import (
    ActionRecord,
    BusinessConfig,
    ChangeRecord,
    EscalationRecord,
    EvidenceDocument,
    Mission,
    MissionStateHistory,
    Prerequisite,
    PublicationSnapshot,
    serialize_model,
)
from .priorities import calculate_priority, indicative_price


class TransitionError(ValidationError):
    pass


ALLOWED_TRANSITIONS = {
    MissionState.QUALIFICATION: {MissionState.MISSING_INFORMATION, MissionState.FEASIBILITY_VALIDATED, MissionState.REFUSED},
    MissionState.MISSING_INFORMATION: {MissionState.QUALIFICATION, MissionState.FEASIBILITY_VALIDATED, MissionState.REFUSED},
    MissionState.FEASIBILITY_VALIDATED: {MissionState.AWAITING_PAYMENT, MissionState.REFUSED},
    MissionState.AWAITING_PAYMENT: {MissionState.ONBOARDING, MissionState.REFUSED},
    MissionState.ONBOARDING: {MissionState.READY_TO_PURSUE, MissionState.REFUSED},
    MissionState.READY_TO_PURSUE: {MissionState.ACTIVE, MissionState.REFUSED},
    MissionState.ACTIVE: {MissionState.AWAITING_CLIENT_DECISION, MissionState.COMPLETED},
    MissionState.AWAITING_CLIENT_DECISION: {MissionState.ACTIVE, MissionState.COMPLETED},
    MissionState.COMPLETED: set(),
    MissionState.REFUSED: set(),
}


def _record_change(instance, before, actor, reason, category=ChangeCategory.MINOR):
    ChangeRecord.objects.create(
        tenant=instance.tenant,
        mission=instance if isinstance(instance, Mission) else instance.mission,
        resource_type=type(instance).__name__,
        resource_id=instance.id,
        category=category,
        before_data=before,
        after_data=serialize_model(instance),
        reason=reason,
        author=actor,
    )


@transaction.atomic
def create_mission(*, tenant, actor, data, reason="Qualification initiale"):
    mission = Mission(tenant=tenant, **data)
    config = BusinessConfig.get_solo()
    amount, _, _ = indicative_price(mission, config)
    mission.indicative_amount = amount
    mission.full_clean()
    mission.save()
    MissionStateHistory.objects.create(
        tenant=tenant,
        mission=mission,
        from_state="",
        to_state=MissionState.QUALIFICATION,
        reason=reason,
        author=actor,
    )
    audit_event(operation="MISSION_CREATE", result="SUCCESS", actor=actor, tenant=tenant, resource_type="Mission", resource_id=mission.id)
    return mission


@transaction.atomic
def update_instance(*, instance, data, actor, reason, category=ChangeCategory.MINOR, recalculate=False):
    if not reason.strip():
        raise ValidationError("Le motif du changement est obligatoire.")
    before = serialize_model(instance)
    for field, value in data.items():
        setattr(instance, field, value)
    if isinstance(instance, Mission):
        amount, _, _ = indicative_price(instance, BusinessConfig.get_solo())
        instance.indicative_amount = amount
    if isinstance(instance, Prerequisite) and recalculate:
        apply_priority(instance)
    instance.full_clean()
    instance.save()
    _record_change(instance, before, actor, reason, category)
    audit_event(
        operation=f"{type(instance).__name__.upper()}_UPDATE",
        result="SUCCESS",
        actor=actor,
        tenant=instance.tenant,
        resource_type=type(instance).__name__,
        resource_id=instance.id,
        details={"reason": reason, "category": category},
    )
    return instance


def apply_priority(prerequisite, now=None):
    result = calculate_priority(prerequisite, BusinessConfig.get_solo(), now=now)
    prerequisite.priority_level = result.level
    prerequisite.priority_score = result.score
    prerequisite.priority_explanation = result.explanation
    prerequisite.priority_calculated_at = timezone.now()
    return result


def _validate_transition_guard(mission, target_state):
    accepted = {AcceptanceResult.ACCEPTABLE, AcceptanceResult.ACCEPTABLE_URGENT}
    feasible = {FeasibilityResult.FEASIBLE, FeasibilityResult.CONDITIONAL}
    if target_state == MissionState.FEASIBILITY_VALIDATED:
        if mission.acceptance_result not in accepted:
            raise TransitionError("Le filtre d'acceptation n'est pas validé.")
        if mission.feasibility_result not in feasible:
            raise TransitionError("La faisabilité doit être validée ou conditionnelle.")
    if target_state == MissionState.ONBOARDING and not mission.payment_satisfied:
        raise TransitionError("Le déclenchement financier convenu n'est pas confirmé.")
    if target_state == MissionState.READY_TO_PURSUE:
        if not mission.payment_satisfied:
            raise TransitionError("Le paiement requis n'est pas confirmé.")
        if not mission.t0_captured_at:
            raise TransitionError("L'état initial T0 doit être enregistré.")
        prerequisites = list(mission.prerequisites.all())
        if not prerequisites:
            raise TransitionError("Au moins un prérequis est requis.")
        invalid = []
        for prerequisite in prerequisites:
            if not prerequisite.client_closure_criterion:
                invalid.append(prerequisite.code)
            if prerequisite.contact_authorization_confirmed != TriState.YES:
                invalid.append(prerequisite.code)
            try:
                prerequisite.full_clean()
            except ValidationError:
                invalid.append(prerequisite.code)
        if invalid:
            raise TransitionError("Onboarding incomplet pour : " + ", ".join(sorted(set(invalid))))
    if target_state == MissionState.ACTIVE:
        if mission.state not in {MissionState.READY_TO_PURSUE, MissionState.AWAITING_CLIENT_DECISION}:
            raise TransitionError("La mission doit être READY TO PURSUE ou reprendre après décision client.")
        if not mission.payment_satisfied:
            raise TransitionError("Le paiement requis n'est pas confirmé.")
    if target_state == MissionState.COMPLETED and not mission.closure_reason:
        raise TransitionError("Le motif de clôture est obligatoire.")


@transaction.atomic
def transition_mission(*, mission, target_state, actor, reason):
    if target_state not in ALLOWED_TRANSITIONS.get(mission.state, set()):
        raise TransitionError(f"Transition interdite : {mission.state} → {target_state}.")
    if not reason.strip():
        raise TransitionError("Le motif de changement d'état est obligatoire.")
    _validate_transition_guard(mission, target_state)
    before = mission.state
    mission.state = target_state
    if target_state == MissionState.ACTIVE and not mission.activated_at:
        mission.activated_at = timezone.now()
    if target_state == MissionState.COMPLETED:
        mission.ended_at = timezone.now()
        mission.closure_report = build_closure_report(mission)
    mission.save(update_fields=["state", "activated_at", "ended_at", "closure_report", "updated_at"])
    MissionStateHistory.objects.create(
        tenant=mission.tenant,
        mission=mission,
        from_state=before,
        to_state=target_state,
        reason=reason,
        author=actor,
    )
    audit_event(
        operation="MISSION_STATE_CHANGE",
        result="SUCCESS",
        actor=actor,
        tenant=mission.tenant,
        resource_type="Mission",
        resource_id=mission.id,
        details={"from": before, "to": target_state, "reason": reason},
    )
    return mission


@transaction.atomic
def capture_t0(*, mission, actor):
    if mission.t0_captured_at:
        raise ValidationError("Le T0 existe déjà et ne peut pas être écrasé.")
    prerequisites = list(mission.prerequisites.all())
    snapshot = {
        "captured_at": timezone.now().isoformat(),
        "total": len(prerequisites),
        "open": sum(1 for item in prerequisites if item.is_open),
        "critical_client": sum(1 for item in prerequisites if item.client_criticality == 3),
        "partial": sum(1 for item in prerequisites if item.state == PrerequisiteState.PARTIALLY_CONFIRMED),
        "missing_priority_information": sum(1 for item in prerequisites if item.priority_level == PriorityLevel.UNKNOWN),
        "states": {state: sum(1 for item in prerequisites if item.state == state) for state, _ in PrerequisiteState.choices},
    }
    mission.t0_snapshot = snapshot
    mission.t0_captured_at = timezone.now()
    mission.save(update_fields=["t0_snapshot", "t0_captured_at", "updated_at"])
    audit_event(operation="MISSION_T0_CAPTURE", result="SUCCESS", actor=actor, tenant=mission.tenant, resource_type="Mission", resource_id=mission.id)
    return snapshot


@transaction.atomic
def create_prerequisite(*, mission, actor, data, reason="Ajout du prérequis"):
    prerequisite = Prerequisite(tenant=mission.tenant, mission=mission, **data)
    apply_priority(prerequisite)
    prerequisite.full_clean()
    prerequisite.save()
    ChangeRecord.objects.create(
        tenant=mission.tenant,
        mission=mission,
        resource_type="Prerequisite",
        resource_id=prerequisite.id,
        category=ChangeCategory.MISSION_EVOLUTION,
        before_data={},
        after_data=serialize_model(prerequisite),
        reason=reason,
        author=actor,
    )
    audit_event(operation="PREREQUISITE_CREATE", result="SUCCESS", actor=actor, tenant=mission.tenant, resource_type="Prerequisite", resource_id=prerequisite.id)
    return prerequisite


@transaction.atomic
def record_action(
    *,
    prerequisite,
    actor,
    event_type,
    occurred_at,
    channel,
    factual_result,
    next_action,
    next_action_at,
    expected_event,
    next_state,
    closure_criterion_satisfied=False,
):
    if event_type == ActionEventType.RESPONSE and next_state == PrerequisiteState.CONFIRMED:
        raise ValidationError("Une réponse obtenue ne peut pas clôturer directement le point : enregistrez une confirmation distincte.")
    if event_type == ActionEventType.CONFIRMATION and not closure_criterion_satisfied:
        raise ValidationError("Une confirmation exige que le critère de clôture client soit explicitement satisfait.")
    before = serialize_model(prerequisite)
    action = ActionRecord(
        tenant=prerequisite.tenant,
        mission=prerequisite.mission,
        prerequisite=prerequisite,
        event_type=event_type,
        occurred_at=occurred_at,
        channel=channel,
        factual_result=factual_result,
        next_action=next_action,
        next_action_at=next_action_at,
        expected_event=expected_event,
        author=actor,
    )
    action.full_clean()
    action.save()
    prerequisite.last_action_at = occurred_at
    prerequisite.last_action_summary = factual_result
    if event_type == ActionEventType.RESPONSE:
        prerequisite.last_response_at = occurred_at
        prerequisite.last_response_summary = factual_result
        prerequisite.new_information_at = occurred_at
    prerequisite.next_action = next_action
    prerequisite.next_action_at = next_action_at
    prerequisite.expected_event = expected_event
    prerequisite.state = next_state
    prerequisite.closure_criterion_satisfied = closure_criterion_satisfied
    if next_state != PrerequisiteState.ESCALATED:
        prerequisite.awaiting_client_decision = False
        prerequisite.client_decision_expected = ""
    apply_priority(prerequisite)
    prerequisite.full_clean()
    prerequisite.save()
    _record_change(prerequisite, before, actor, f"Journal rapide — {ActionEventType(event_type).label}")
    audit_event(operation="ACTION_RECORD", result="SUCCESS", actor=actor, tenant=prerequisite.tenant, resource_type="Prerequisite", resource_id=prerequisite.id, details={"event_type": event_type})
    return action


@transaction.atomic
def escalate_prerequisite(*, prerequisite, actor, data):
    before = serialize_model(prerequisite)
    escalation = EscalationRecord(
        tenant=prerequisite.tenant,
        mission=prerequisite.mission,
        prerequisite=prerequisite,
        author=actor,
        **data,
    )
    escalation.full_clean()
    escalation.save()
    prerequisite.escalation_level = data["level"]
    prerequisite.immediate_escalation_triggered = True
    if int(data["level"]) == 3:
        prerequisite.state = PrerequisiteState.ESCALATED
        prerequisite.awaiting_client_decision = True
        prerequisite.client_decision_expected = data["client_decision_reason"]
        prerequisite.next_action = ""
        prerequisite.next_action_at = None
        prerequisite.expected_event = ""
    apply_priority(prerequisite)
    prerequisite.full_clean()
    prerequisite.save()
    _record_change(prerequisite, before, actor, "Escalade documentée", ChangeCategory.MISSION_EVOLUTION)
    audit_event(operation="PREREQUISITE_ESCALATE", result="SUCCESS", actor=actor, tenant=prerequisite.tenant, resource_type="Prerequisite", resource_id=prerequisite.id, details={"level": data["level"]})
    return escalation


def build_work_queue(now=None):
    now = now or timezone.now()
    open_items = list(
        Prerequisite.objects.exclude(state__in=Prerequisite.CLOSED_STATES)
        .select_related("mission", "tenant")
        .filter(mission__state__in=[MissionState.ACTIVE, MissionState.AWAITING_CLIENT_DECISION, MissionState.READY_TO_PURSUE])
    )
    tie_key = lambda p: (p.useful_deadline or timezone.datetime.max.replace(tzinfo=timezone.get_current_timezone()), -(p.client_criticality or 0), -(p.dependency_score or 0), -(p.inertia_score or 0))
    return {
        "new_information": sorted([p for p in open_items if p.new_information_at and (not p.last_reviewed_at or p.new_information_at > p.last_reviewed_at)], key=tie_key),
        "p0": sorted([p for p in open_items if p.priority_level == PriorityLevel.P0], key=tie_key),
        "client_decisions": sorted([p for p in open_items if p.awaiting_client_decision], key=tie_key),
        "p1": sorted([p for p in open_items if p.priority_level == PriorityLevel.P1], key=tie_key),
        "followups_due": sorted([p for p in open_items if p.next_action_at and p.next_action_at <= now], key=tie_key),
        "responses_to_review": sorted([p for p in open_items if p.state == PrerequisiteState.RESPONSE_TO_REVIEW], key=tie_key),
        "missing_information": sorted([p for p in open_items if p.priority_level == PriorityLevel.UNKNOWN or p.state == PrerequisiteState.TO_QUALIFY], key=tie_key),
        "p2": sorted([p for p in open_items if p.priority_level == PriorityLevel.P2], key=tie_key),
        "p3": sorted([p for p in open_items if p.priority_level == PriorityLevel.P3], key=tie_key),
    }


def _report_counts(prerequisites):
    return {
        "total": len(prerequisites),
        "confirmed": sum(1 for p in prerequisites if p.state == PrerequisiteState.CONFIRMED),
        "open": sum(1 for p in prerequisites if p.is_open),
        "cancelled_client": sum(1 for p in prerequisites if p.state == PrerequisiteState.CANCELLED_BY_CLIENT),
        "closed_unresolved": sum(1 for p in prerequisites if p.state == PrerequisiteState.CLOSED_UNRESOLVED),
        "p0": sum(1 for p in prerequisites if p.priority_level == PriorityLevel.P0),
        "p1": sum(1 for p in prerequisites if p.priority_level == PriorityLevel.P1),
    }


@transaction.atomic
def publish_client_snapshot(*, mission, actor, summary_note=""):
    prerequisites = list(mission.prerequisites.filter(client_published=True).order_by("code"))
    all_items = list(mission.prerequisites.all())
    documents = list(EvidenceDocument.objects.filter(mission=mission, is_client_shared=True, scan_state="SAFE"))
    version = (mission.publications.aggregate(value=Max("version"))["value"] or 0) + 1
    payload = {
        "mission": {"code": mission.code, "project_name": mission.project_name, "site_name": mission.site_name},
        "t0": mission.t0_snapshot,
        "counts": _report_counts(all_items),
        "summary_note": summary_note,
        "prerequisites": [
            {
                "id": str(p.id),
                "code": p.code,
                "title": p.title,
                "state": p.get_state_display(),
                "client_criticality": p.get_client_criticality_display() if p.client_criticality is not None else "Inconnue",
                "useful_deadline": p.useful_deadline.isoformat() if p.useful_deadline else None,
                "client_summary": p.client_summary,
                "next_step": p.client_decision_expected if p.awaiting_client_decision else p.next_action,
            }
            for p in prerequisites
        ],
        "actions_count": mission.actions.count(),
        "escalations_count": mission.escalations.count(),
        "last_updated_at": timezone.now().isoformat(),
    }
    publication = PublicationSnapshot.objects.create(
        tenant=mission.tenant,
        mission=mission,
        version=version,
        payload=payload,
        shared_document_ids=[str(document.id) for document in documents],
        published_by=actor,
    )
    audit_event(operation="CLIENT_PUBLICATION_CREATE", result="SUCCESS", actor=actor, tenant=mission.tenant, resource_type="PublicationSnapshot", resource_id=publication.id, details={"version": version})
    return publication


@transaction.atomic
def revoke_publication(*, publication, actor, reason):
    if publication.revoked_at:
        raise ValidationError("Cette publication est déjà révoquée.")
    if not reason.strip():
        raise ValidationError("Le motif de révocation est obligatoire.")
    publication.revoked_at = timezone.now()
    publication.revoked_by = actor
    publication.revoke_reason = reason
    publication.save(update_fields=["revoked_at", "revoked_by", "revoke_reason", "updated_at"])
    audit_event(operation="CLIENT_PUBLICATION_REVOKE", result="SUCCESS", actor=actor, tenant=publication.tenant, resource_type="PublicationSnapshot", resource_id=publication.id, details={"reason": reason})


def build_closure_report(mission):
    prerequisites = list(mission.prerequisites.all().order_by("code"))
    return {
        "t0": mission.t0_snapshot,
        "final_counts": _report_counts(prerequisites),
        "actions_realized": mission.actions.count(),
        "proofs_recovered": mission.documents.filter(scan_state="SAFE").count(),
        "escalations": mission.escalations.count(),
        "remaining": [
            {
                "code": p.code,
                "title": p.title,
                "state": p.get_state_display(),
                "last_known": p.last_response_summary or p.last_action_summary or p.initial_state,
            }
            for p in prerequisites
            if p.is_open or p.state == PrerequisiteState.CLOSED_UNRESOLVED
        ],
        "ended_at": timezone.now().isoformat(),
        "reason": mission.closure_reason,
    }
