import math
from dataclasses import dataclass
from decimal import Decimal

from django.utils import timezone

from .enums import FeasibilityResult, PrerequisiteState, PriorityLevel


@dataclass(frozen=True)
class PriorityResult:
    level: str
    score: Decimal | None
    explanation: str
    time_score: int | None
    overridden: bool = False


def time_component(deadline, config, now=None):
    if deadline is None:
        return None
    now = now or timezone.now()
    remaining_seconds = (deadline - now).total_seconds()
    if remaining_seconds <= config.immediate_time_hours * 3600:
        return 3
    remaining_days = math.ceil(remaining_seconds / 86400)
    if remaining_days <= config.high_time_days:
        return 2
    if remaining_days <= config.medium_time_days:
        return 1
    return 0


def override_reason(prerequisite, config, now=None):
    now = now or timezone.now()
    if prerequisite.manual_p0_override:
        return prerequisite.override_reason or "Override P0 manuel documenté"
    if (
        config.override_overdue_missing
        and prerequisite.useful_deadline
        and prerequisite.useful_deadline < now
        and prerequisite.state != PrerequisiteState.CONFIRMED
    ):
        return "Échéance dépassée et confirmation manquante"
    if (
        prerequisite.client_declared_blocking
        and prerequisite.useful_deadline
        and (prerequisite.useful_deadline - now).total_seconds() <= config.override_blocking_within_hours * 3600
    ):
        return "Point déclaré bloquant par le client dans la fenêtre d’override"
    if config.override_critical_revelation and prerequisite.critical_blockage_revealed:
        return "Nouvelle information révélant un blocage critique"
    if config.override_immediate_escalation and prerequisite.immediate_escalation_triggered:
        return "Règle d’escalade immédiate déclenchée"
    return ""


def calculate_priority(prerequisite, config, now=None):
    now = now or timezone.now()
    reason = override_reason(prerequisite, config, now)
    if reason:
        return PriorityResult(PriorityLevel.P0, None, f"P0 direct — {reason}", None, True)

    components = {
        "criticité client": prerequisite.client_criticality,
        "temps": time_component(prerequisite.useful_deadline, config, now),
        "confirmation": prerequisite.confirmation_score,
        "dépendances": prerequisite.dependency_score,
        "inertie": prerequisite.inertia_score,
    }
    missing = [label for label, value in components.items() if value is None]
    if missing:
        return PriorityResult(
            PriorityLevel.UNKNOWN,
            None,
            "Priorité inconnue : information(s) manquante(s) — " + ", ".join(missing),
            components["temps"],
        )

    score = (
        Decimal(components["criticité client"]) * config.criticality_weight
        + Decimal(components["temps"]) * config.time_weight
        + Decimal(components["confirmation"]) * config.confirmation_weight
        + Decimal(components["dépendances"]) * config.dependencies_weight
        + Decimal(components["inertie"]) * config.inertia_weight
    )
    if score >= config.p0_min:
        level = PriorityLevel.P0
    elif score >= config.p1_min:
        level = PriorityLevel.P1
    elif score >= config.p2_min:
        level = PriorityLevel.P2
    else:
        level = PriorityLevel.P3
    explanation = (
        f"{level} — score {score} = criticité {components['criticité client']}×{config.criticality_weight} "
        f"+ temps {components['temps']}×{config.time_weight} + confirmation {components['confirmation']}×{config.confirmation_weight} "
        f"+ dépendances {components['dépendances']}×{config.dependencies_weight} + inertie {components['inertie']}×{config.inertia_weight}"
    )
    return PriorityResult(level, score, explanation, components["temps"])


def indicative_price(mission, config, now=None):
    if mission.approximate_open_count is None or mission.protected_at is None:
        return None, None, "Informations insuffisantes pour une indication"
    count = mission.approximate_open_count
    if count <= 5:
        base, size = config.price_s, "S"
    elif count <= 15:
        base, size = config.price_m, "M"
    elif count <= 30:
        base, size = config.price_l, "L"
    else:
        return None, "XL", "Sur devis — volume supérieur à 30 ou multi-sites"
    now = now or timezone.now()
    hours = (mission.protected_at - now).total_seconds() / 3600
    if hours <= 72:
        coefficient = config.urgency_72_hours
    elif hours <= 7 * 24:
        coefficient = config.urgency_7_days
    elif hours <= 15 * 24:
        coefficient = config.urgency_15_days
    else:
        coefficient = Decimal(1)
    return base * coefficient, size, f"Base {size} × coefficient indicatif {coefficient} — à confirmer manuellement"


def feasibility_recommendation(mission):
    if mission.manual_load_estimate_hours is None or mission.operator_available_hours is None:
        return None, "Estimation manuelle de charge et disponibilité requises"
    if mission.manual_load_estimate_hours > mission.operator_available_hours:
        if mission.reduced_scope_proposal:
            return FeasibilityResult.CONDITIONAL, "Charge supérieure à la disponibilité ; périmètre réduit documenté"
        return FeasibilityResult.INSUFFICIENT_CAPACITY, "Charge estimée supérieure à la disponibilité réelle"
    return FeasibilityResult.FEASIBLE, "Charge manuelle compatible avec la disponibilité renseignée — décision opérateur requise"
