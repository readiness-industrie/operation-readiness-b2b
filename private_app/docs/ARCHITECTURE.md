# Architecture V1

## Séparation non négociable

| Composant | Emplacement | Données |
|---|---|---|
| Site public | Racine du dépôt, GitHub Pages | Contenu marketing fictif/public uniquement |
| Application privée | `private_app/`, service web Render distinct | Logique applicative, aucun secret dans GitHub |
| Base | PostgreSQL privé, région Francfort | Missions, utilisateurs, historique, audit |
| Documents | Bucket S3 compatible privé, région Paris | Pièces et preuves, clés aléatoires tenant/mission/document |
| Sauvegardes | Même stockage privé sous préfixe dédié, chiffrées avant envoi | Export complet chiffré + documents |

L’URL publique ne change pas. L’application privée reçoit une autre adresse, par exemple `https://readiness-industry-private.onrender.com`, puis éventuellement `https://app.votre-domaine.fr`.

## Choix techniques

- Django 5.2 LTS, rendu serveur : peu de JavaScript, CSRF/session/auth inclus, maintenance simple pour un opérateur seul.
- PostgreSQL : transactions, contraintes, historique et Row Level Security.
- UUID non séquentiels : aucune URL client fondée sur un identifiant incrémental devinable.
- Interface responsive : une seule application web sur téléphone et PC.
- Stockage S3 privé : aucune URL publique permanente ; le serveur autorise chaque téléchargement.
- MFA TOTP obligatoire pour l’Owner et les Viewers.
- Aucun service IA, aucun envoi automatique de données à une IA.

## Défense en profondeur multi-client

1. Le Viewer est rattaché à un seul `Organization`.
2. Un `MissionAccess` nominatif autorise explicitement chaque dossier.
3. Toutes les vues utilisent un queryset limité par l’utilisateur connecté.
4. PostgreSQL applique en plus une policy RLS `deny-by-default` avec `FORCE ROW LEVEL SECURITY`.
5. Les fichiers portent un préfixe `tenant/mission/document` et ne sont servis qu’après le même contrôle.
6. Le portail lit une `PublicationSnapshot` figée, jamais les tables internes en direct.
7. Une tentative non autorisée reçoit un 404 neutre et produit un audit `DENIED`.

## Modèle métier principal

- `Mission` : qualification, acceptation, faisabilité/capacité, finance, T0, état, clôture.
- `Prerequisite` : critère client, criticité client nullable, priorité Readiness, prochaine action ou décision attendue.
- `ActionRecord` : action, réponse ou confirmation — événements distincts et immuables.
- `EscalationRecord` : les cinq éléments obligatoires du protocole.
- `ChangeRecord` : avant/après, auteur, date, motif, catégorie commerciale.
- `MissionStateHistory` : chaque transition d’état.
- `PublicationSnapshot` : projection client contrôlée et versionnée.
- `EvidenceDocument` : fichier privé, empreinte SHA-256, quarantaine, partage explicite.
- `AuditLog` / `SecurityIncident` : événements de sécurité et procédure d’incident.
- `BusinessConfig` : poids, seuils, overrides, tarifs, urgence, capacité et taille upload modifiables sans changer le code.

## Interprétation temporelle documentée

Le brief définit `≤48 h`, `3–5 jours`, `6–10 jours`, `>10 jours`. Pour couvrir sans trou la période entre 48 h et 72 h, le moteur conserve le seuil exact `≤48 h`, puis arrondit le reste au jour supérieur : 49 h devient 3 jours et reçoit donc la composante `3–5 jours`. Les seuils restent configurables.
