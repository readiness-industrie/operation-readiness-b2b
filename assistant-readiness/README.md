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


## V0.2 — cockpit opérationnel

Le dossier reste distinct de la vitrine. Le cockpit `public/dashboard.html` lit les dossiers persistés par `server.js` via `/api/dashboard` et permet de piloter réellement les points, responsables, échéances, preuves et états.

Vues disponibles :
- Vue d'ensemble et priorités du jour
- Dossiers
- Urgences
- Blocages
- Preuves à contrôler
- Relances préparées

Le référentiel métier local est dans `knowledge.js`. Il reprend le périmètre de l'offre Readiness Industry : jalons, catégories de prérequis, séquence A→Z et garde-fous.

Aucune API IA externe n'est nécessaire pour cette V0.2. Le moteur reste local et les données de dossier sont persistées côté serveur.

Le cockpit ne remplace pas le planning client et ne prend pas les décisions techniques, HSE, budgétaires ou d'arbitrage à la place d'Hervé.
