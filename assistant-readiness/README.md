# Assistant Readiness Industry

Socle opérationnel distinct du site vitrine.

## Réellement présent dans V0.1

- réception d'un contenu de prospect ou projet ;
- qualification locale par règles métier Readiness ;
- détection des catégories de prérequis déjà présentes dans le site ;
- création d'un dossier structuré ;
- points avec action, responsable à identifier, échéance à préciser et preuve attendue ;
- cockpit serveur ;
- persistance des dossiers dans data/projects.json ;
- changements d'état ;
- blocage de la clôture tant que la validation humaine est requise ;
- aucun appel à une API IA externe.

## Architecture

public/index.html → server.js → moteur métier local → stockage serveur.

Le moteur ne prétend pas comprendre un document qu'il n'a pas reçu. Il ne fabrique ni date, ni responsable, ni preuve, ni validation.

## Lancement

npm start

Puis ouvrir http://localhost:3000.

Pour un déploiement Render depuis ce dépôt :
node assistant-readiness/server.js

Variable recommandée :
DASHBOARD_SECRET

Cette version construit d'abord le flux réellement utilisable et persistant. La lecture native PDF/Word, Gmail, les relances automatiques et une IA externe restent volontairement hors de cette V0.1.
