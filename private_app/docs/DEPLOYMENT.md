# Déploiement — accès téléphone et PC

## Où sera le logiciel ?

La V1 est une application web privée hébergée séparément du site commercial :

- site public : l’adresse GitHub Pages actuelle reste inchangée ;
- logiciel privé : une nouvelle adresse HTTPS, initialement du type `https://readiness-industry-private.onrender.com` ;
- adresse professionnelle facultative ensuite : `https://app.votre-domaine.fr`.

Depuis un PC, ouvrir l’adresse dans Chrome, Edge, Firefox ou Safari. Depuis un téléphone Android/iPhone, ouvrir exactement la même adresse ; l’écran s’adapte automatiquement. Il est possible d’utiliser « Ajouter à l’écran d’accueil » pour obtenir une icône, sans publier une application dans les stores.

## Infrastructure proposée

- Render, région Francfort : application Django + PostgreSQL.
- Scaleway Object Storage, région Paris (`fr-par`) : bucket privé versionné pour documents et sauvegardes.
- TLS/HTTPS obligatoire.

Ne pas utiliser les offres gratuites en production réelle : elles ne fournissent pas le niveau de disponibilité et de restauration exigé. Choisir une base PostgreSQL payante avec PITR avant la première donnée client.

## Préparation des secrets

Générer hors du dépôt trois secrets différents :

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Ils correspondent à `SECRET_KEY`, `FIELD_ENCRYPTION_KEY`, `BACKUP_ENCRYPTION_KEY`. Ne jamais les coller dans GitHub, un issue, un e-mail ou une capture d’écran. Les stocker dans le coffre de secrets Render et dans un gestionnaire de mots de passe personnel.

## Déploiement contrôlé

1. Faire passer tous les tests locaux et la CI GitHub.
2. Créer un bucket Scaleway privé en région Paris, activer versioning, chiffrement serveur et politique de cycle de vie.
3. Dans Render, créer un Blueprint depuis `render.yaml`.
4. Choisir des offres payantes adaptées pour le web, PostgreSQL et les deux cron jobs.
5. Renseigner les mêmes secrets dans chaque service concerné. Renseigner les clés de stockage avec des droits limités au bucket et aux préfixes nécessaires.
6. Vérifier que la base et le web sont tous les deux à Francfort et communiquent via l’URL PostgreSQL interne.
7. Exécuter `python manage.py bootstrap_owner --username <nom> --email <email>` dans le shell Render.
8. Ouvrir l’URL, définir le MFA, enregistrer les codes de secours hors ligne.
9. Créer Alpha/Beta fictifs avec `ALLOW_DEMO_SEED=true python manage.py seed_isolation_demo`, exécuter les tentatives croisées documentées dans `SECURITY.md`, puis retirer `ALLOW_DEMO_SEED`.
10. Tester une sauvegarde, restaurer dans une base temporaire neuve, vérifier les comptes/mission/document, puis détruire proprement l’environnement temporaire.
11. Seulement après, créer le premier vrai client.

Le Blueprint désactive l’auto-déploiement : une mise à jour de `main` ne part pas automatiquement en production sans contrôle.

## Domaine personnalisé

Quand un domaine est disponible :

1. ajouter `app.votre-domaine.fr` au service Render ;
2. ajouter le DNS demandé par Render ;
3. définir `ALLOWED_HOSTS=app.votre-domaine.fr` ;
4. définir `CSRF_TRUSTED_ORIGINS=https://app.votre-domaine.fr` ;
5. vérifier HTTPS, MFA, login/logout et en-têtes avec `python manage.py check --deploy`.
