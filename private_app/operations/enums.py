from django.db import models


class UserRole(models.TextChoices):
    OWNER = "OWNER", "Owner / opérateur"
    CLIENT_VIEWER = "CLIENT_VIEWER", "Client — lecture seule"


class TriState(models.TextChoices):
    UNKNOWN = "UNKNOWN", "Inconnu"
    YES = "YES", "Oui"
    NO = "NO", "Non"


class AcceptanceResult(models.TextChoices):
    UNKNOWN = "UNKNOWN", "Non décidé"
    ACCEPTABLE = "ACCEPTABLE", "Acceptable"
    ACCEPTABLE_URGENT = "ACCEPTABLE_URGENT", "Acceptable en urgence"
    TO_COMPLETE = "TO_COMPLETE", "À compléter avant acceptation"
    OUT_OF_SCOPE = "OUT_OF_SCOPE", "Hors périmètre"


class FeasibilityResult(models.TextChoices):
    UNKNOWN = "UNKNOWN", "Non décidé"
    FEASIBLE = "FEASIBLE", "Faisable"
    CONDITIONAL = "CONDITIONAL", "Faisable sous conditions / périmètre à réduire"
    INSUFFICIENT_CAPACITY = "INSUFFICIENT_CAPACITY", "Capacité insuffisante"
    UNREALISTIC = "UNREALISTIC", "Attente irréaliste / impossible à promettre"


class MissionState(models.TextChoices):
    QUALIFICATION = "QUALIFICATION", "Qualification"
    MISSING_INFORMATION = "MISSING_INFORMATION", "Informations manquantes"
    FEASIBILITY_VALIDATED = "FEASIBILITY_VALIDATED", "Faisabilité validée"
    AWAITING_PAYMENT = "AWAITING_PAYMENT", "En attente paiement"
    ONBOARDING = "ONBOARDING", "Onboarding"
    READY_TO_PURSUE = "READY_TO_PURSUE", "Ready to pursue"
    ACTIVE = "ACTIVE", "Active"
    AWAITING_CLIENT_DECISION = "AWAITING_CLIENT_DECISION", "En attente décision client"
    COMPLETED = "COMPLETED", "Terminée"
    REFUSED = "REFUSED", "Refusée"


class PrerequisiteState(models.TextChoices):
    TO_QUALIFY = "TO_QUALIFY", "À qualifier"
    READY_TO_PURSUE = "READY_TO_PURSUE", "Ready to pursue"
    ACTION_PLANNED = "ACTION_PLANNED", "Action planifiée"
    AWAITING_RESPONSE = "AWAITING_RESPONSE", "En attente de réponse"
    TO_FOLLOW_UP = "TO_FOLLOW_UP", "À relancer"
    RESPONSE_TO_REVIEW = "RESPONSE_TO_REVIEW", "Réponse à contrôler"
    PARTIALLY_CONFIRMED = "PARTIALLY_CONFIRMED", "Partiellement confirmé"
    CONFIRMED = "CONFIRMED", "Confirmé selon critère client"
    ESCALATED = "ESCALATED", "Escaladé / décision client attendue"
    CANCELLED_BY_CLIENT = "CANCELLED_BY_CLIENT", "Annulé par le client"
    CLOSED_UNRESOLVED = "CLOSED_UNRESOLVED", "Clôturé non résolu"


class PriorityLevel(models.TextChoices):
    UNKNOWN = "UNKNOWN", "À déterminer"
    P0 = "P0", "P0 — agir maintenant"
    P1 = "P1", "P1 — aujourd’hui"
    P2 = "P2", "P2 — planifié rapidement"
    P3 = "P3", "P3 — surveillance"


class ActionEventType(models.TextChoices):
    ACTION = "ACTION", "Action effectuée"
    RESPONSE = "RESPONSE", "Réponse obtenue"
    CONFIRMATION = "CONFIRMATION", "Prérequis confirmé"
    NOTE = "NOTE", "Information factuelle"


class EscalationLevel(models.IntegerChoices):
    NORMAL = 0, "Niveau 0 — suivi normal"
    PRIMARY = 1, "Niveau 1 — interlocuteur principal"
    SECOND_CHANNEL = 2, "Niveau 2 — second canal / contact"
    CLIENT_DECISION = 3, "Niveau 3 — décision client"


class Visibility(models.TextChoices):
    INTERNAL = "INTERNAL", "Interne Readiness"
    CLIENT = "CLIENT", "Publié client"


class DocumentScanState(models.TextChoices):
    PENDING = "PENDING", "En quarantaine"
    SAFE = "SAFE", "Validé"
    REJECTED = "REJECTED", "Rejeté"


class ChangeCategory(models.TextChoices):
    MINOR = "MINOR", "Modification interne mineure"
    MISSION_EVOLUTION = "MISSION_EVOLUTION", "Évolution de mission"
    MATERIAL_EXTENSION = "MATERIAL_EXTENSION", "Extension matérielle / avenant"
