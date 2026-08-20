# Maintenance, mise à jour et rollback

## Avant chaque déploiement

1. `git diff` et absence de secrets/données réelles.
2. `python manage.py test operations.tests`.
3. test PostgreSQL/RLS en CI.
4. `./scripts/test_backup_restore.sh`.
5. `../scripts/test_public_regression.sh` depuis la racine.
6. `python manage.py check --deploy` avec les paramètres de production.
7. sauvegarde PostgreSQL + sauvegarde applicative chiffrée.

## Déploiement

- L’auto-déploiement est désactivé.
- Les migrations s’exécutent en `preDeployCommand`.
- Vérifier `/health/`, login, MFA, dashboard, upload/quarantaine, publication et portail Alpha.
- Ne jamais modifier simultanément le site GitHub Pages et l’application privée dans un correctif urgent.

## Rollback

1. si le schéma reste compatible, utiliser le rollback Render vers l’image précédente ;
2. si migration destructive/incorrecte, couper l’accès, préserver les logs, créer une base neuve depuis PITR/sauvegarde, pointer l’application après vérification ;
3. ne jamais éditer/supprimer manuellement les lignes d’historique pour « réparer ».

## Entretien récurrent

- hebdomadaire : uploads bloqués en quarantaine, erreurs cron, espace stockage, sauvegarde présente ;
- mensuel : dépendances et correctifs Django/Python/PostgreSQL/ClamAV ;
- trimestriel : restauration complète et revue des accès Viewers ;
- à chaque départ/changement de contact : désactiver le compte, révoquer les sessions et les accès mission.
