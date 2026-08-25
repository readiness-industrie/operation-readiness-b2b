# Sauvegarde et restauration

## Stratégie

1. PostgreSQL Render payant : point-in-time recovery géré par la plateforme.
2. Chaque nuit : sauvegarde applicative indépendante, chiffrée avant envoi dans le bucket privé.
3. Bucket : versioning, chiffrement serveur, accès IAM minimal, cycle de vie séparé des documents.

La sauvegarde applicative contient les tables `operations`, le manifeste SHA-256 et le contenu des documents. Elle est chiffrée avec `BACKUP_ENCRYPTION_KEY`, distincte de la clé applicative.

## Commandes

```bash
python manage.py backup_readiness --to-storage
python manage.py restore_readiness --storage-key backups/<fichier>.ri-backup --confirm-empty
```

La restauration refuse une base qui contient déjà une mission. La cible correcte est une base PostgreSQL neuve, migrée avec la même version du code, les mêmes `FIELD_ENCRYPTION_KEY` et `BACKUP_ENCRYPTION_KEY`.

## Test réel automatisé

```bash
./scripts/test_backup_restore.sh
```

Le script crée une base source temporaire, un compte/tenant/mission/document fictifs, chiffre la sauvegarde, migre une base cible vide, restaure, puis vérifie les quatre éléments et le contenu du PDF. Les fichiers temporaires sont supprimés à la fin.

## Exercice production

Chaque trimestre et avant un changement risqué :

1. créer une base temporaire isolée ;
2. restaurer la dernière sauvegarde ;
3. vérifier nombre de tenants/missions/documents, connexion d’un compte de test et empreintes ;
4. consigner date, opérateur, sauvegarde, résultat et durée ;
5. détruire la cible temporaire après validation.

Ne jamais tester une restauration par-dessus la production.
