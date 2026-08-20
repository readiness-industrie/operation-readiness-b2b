# Mesure des futurs pilotes

Ce référentiel prépare la mesure des premières missions sans afficher publiquement de chiffres non prouvés.

## Événements à tracer

Chaque événement conserve au minimum : identifiant du projet, identifiant du prérequis, date et heure, auteur, type d'action, canal, résultat factuel, source ou preuve associée, prochaine action et date de prochaine action.

Types d'événements distincts :

- `prerequisite_opened` : prérequis inclus dans le périmètre ;
- `pursuit_action` : demande, appel, message ou relance effectuée ;
- `response_received` : réponse reçue, sans présumer qu'elle confirme le point ;
- `confirmation_obtained` : confirmation satisfaisant le critère défini par le client ;
- `evidence_retrieved` : preuve récupérée et reliée au prérequis ;
- `blocker_detected` : blocage identifié pour la première fois ;
- `blocker_escalated` : blocage remonté selon la règle convenue ;
- `prerequisite_closed` : point fermé selon le critère du client ;
- `client_intervention` : intervention du chef de projet explicitement sollicitée.

## Indicateurs calculables

| Indicateur | Calcul / source |
| --- | --- |
| Prérequis suivis | Nombre d'identifiants de prérequis distincts dans le périmètre |
| Relances / actions | Nombre d'événements `pursuit_action`, ventilé par canal et type |
| Confirmations obtenues | Nombre de prérequis avec `confirmation_obtained` |
| Preuves récupérées | Nombre d'événements `evidence_retrieved`, avec dédoublonnage par preuve |
| Délai moyen de réponse | Moyenne entre l'action sollicitant une réponse et le premier `response_received` associé |
| Blocages escaladés | Nombre de prérequis avec `blocker_escalated` |
| Anticipation du blocage | Écart entre `blocker_detected` et la date de mobilisation protégée |
| Temps chef de projet évité | Uniquement sur mesure déclarée ou chronométrée, avec méthode documentée ; jamais déduit automatiquement du nombre d'actions |

## Garde-fous d'intégrité

- Une action effectuée n'est pas une réponse obtenue.
- Une réponse obtenue n'est pas une confirmation.
- Une confirmation n'est comptée que si le critère client associé est satisfait.
- Un même message envoyé sur plusieurs canaux peut être ventilé, mais ne doit pas gonfler artificiellement un résultat.
- Toute estimation de temps évité conserve sa méthode et sa source.
- Les données T0 de début de mission et la date de mobilisation sont figées dans l'historique ; toute modification ultérieure est datée et motivée.
