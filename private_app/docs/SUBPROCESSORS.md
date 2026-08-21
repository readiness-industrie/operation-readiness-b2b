# Sous-traitants techniques proposés

Cette liste décrit l’architecture proposée, pas des contrats déjà souscrits.

| Service | Usage | Localisation choisie/connue | Données |
|---|---|---|---|
| Render | Hébergement web, cron, PostgreSQL, logs techniques | Francfort, Allemagne | Comptes, missions, historique, audit |
| Scaleway Object Storage | Stockage privé S3 compatible | Paris, France (`fr-par`) | Documents et sauvegardes chiffrées |
| GitHub | Dépôt public et CI sur données fictives | À confirmer contractuellement | Code uniquement, jamais données clients/secrets |

Avant production : valider DPA, mesures de sécurité, localisation/transferts, sous-traitants ultérieurs, durées de rétention et procédure d’incident avec un conseil RGPD/contractuel compétent.

ClamAV, Django, PostgreSQL et les bibliothèques Python sont exécutés dans l’infrastructure ; aucune pièce client n’est envoyée par le logiciel à un service IA.
