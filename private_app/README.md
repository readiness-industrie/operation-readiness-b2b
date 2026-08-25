# Readiness Industry — application opérationnelle privée V1

Application serveur destinée à exécuter une première mission réelle conformément à l’issue GitHub #3. Le code est public, mais les données, secrets, documents et sauvegardes sont exclusivement stockés hors GitHub dans des services privés.

## Démarrage local

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.lock
python manage.py migrate
python manage.py bootstrap_owner --username herve --email votre-adresse@example.fr
python manage.py runserver
```

Ouvrir `http://127.0.0.1:8000/`. Le premier accès impose la configuration MFA et affiche huit codes de secours une seule fois.

## Vérifications

```bash
python manage.py test operations.tests
./scripts/test_backup_restore.sh
cd .. && ./scripts/test_public_regression.sh
```

Le test PostgreSQL/RLS est exécuté dans GitHub Actions avec un rôle non-superuser. Le portail client ne doit pas être activé en production tant que ce test et les scénarios Alpha/Beta ne sont pas verts.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Déploiement téléphone et PC](docs/DEPLOYMENT.md)
- [Guide opérateur](docs/OPERATOR_GUIDE.md)
- [Sécurité et isolation](docs/SECURITY.md)
- [Sauvegarde et restauration](docs/BACKUP_RESTORE.md)
- [Maintenance, mise à jour et rollback](docs/MAINTENANCE.md)
- [Sous-traitants techniques](docs/SUBPROCESSORS.md)
- [Limites et reports V1](docs/LIMITS.md)
