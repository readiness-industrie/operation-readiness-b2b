# Sécurité, autorisation et isolation

## Contrôles présents

- MFA TOTP obligatoire après mot de passe, codes de secours à usage unique.
- Mots de passe Argon2, validation minimale 14 caractères.
- Limitation des tentatives mot de passe et MFA.
- Sessions HttpOnly, SameSite Strict, Secure en production, révocation par version de session.
- TLS forcé, HSTS, CSP, anti-frame, no-sniff, CSRF, validation d’entrée.
- Rôles Owner / Client Viewer. Aucun admin générique exposé.
- Autorisation côté serveur sur missions, prérequis, API, publications et documents.
- PostgreSQL RLS forcé ; aucun choix de tenant fourni par le navigateur.
- Publications client figées et explicitement versionnées.
- Documents privés, extension/type réel/taille/empreinte contrôlés, quarantaine antivirus.
- Audit append-only logique ; triggers PostgreSQL interdisant UPDATE/DELETE sur les historiques critiques.
- Aucun secret, dump ou fichier réel dans GitHub.

## Campagne Alpha/Beta obligatoire avant portail réel

Créer exclusivement les données fictives :

```bash
ALLOW_DEMO_SEED=true python manage.py seed_isolation_demo
```

Avec le compte Alpha, vérifier que chacune des tentatives suivantes échoue avec 404/403/405 neutre et crée, lorsque pertinent, un audit `DENIED` :

1. coller l’URL de publication Beta ;
2. remplacer l’UUID mission Alpha par Beta dans l’API ;
3. ouvrir l’URL d’un document Beta ;
4. ouvrir une publication Alpha révoquée ;
5. ouvrir une URL après déconnexion ;
6. ajouter/modifier `?tenant=<uuid-beta>` ;
7. envoyer un POST vers l’API de synthèse ou le portail.

Les tests automatisés correspondants sont dans `operations/tests/test_isolation.py`. `test_postgres_rls.py` vérifie en plus que la base elle-même cache Beta sous contexte Alpha avec un rôle non-superuser.

Une seule réussite d’accès croisé interdit l’activation du portail et doit ouvrir un incident critique.

## Uploads

Formats V1 : PDF, PNG, JPEG, DOCX, XLSX, TXT UTF-8, CSV UTF-8. Limite par défaut : 15 Mo, configurable. Les exécutables, SVG, archives génériques et incohérences extension/contenu sont rejetés.

En production `REQUIRE_MALWARE_SCAN=true`. Le cron exécute ClamAV toutes les 15 minutes. Un fichier `PENDING` ne peut être partagé ou téléchargé par un Viewer.

## Incident

1. révoquer les sessions / désactiver les comptes concernés ;
2. identifier tenant, missions, documents et publications ;
3. préserver/exporter les logs ;
4. ouvrir un `SecurityIncident` ;
5. restaurer dans une base neuve si nécessaire ;
6. produire les éléments contractuels/RGPD avec le conseil juridique compétent.

Les durées de conservation livrées sont des valeurs techniques modifiables, pas un avis juridique. Elles doivent être validées avant production réelle.

Après validation de la politique, `python manage.py retention_candidates` donne un aperçu sans écriture. `execute_retention --mission <uuid> --confirm DELETE-<code> --reason <motif>` ne fonctionne qu’après l’échéance configurée et sur une mission terminée/refusée ; il révoque les accès, supprime physiquement les fichiers, pseudonymise les contacts, archive la mission et conserve un audit minimal.
