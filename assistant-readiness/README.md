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

Le service reste fermé tant que `DASHBOARD_SECRET` n'est pas défini.

En local :

```bash
DASHBOARD_SECRET='choisir-un-mot-de-passe-long' npm start
```

Puis ouvrir http://localhost:3000 et saisir ce mot de passe.

Pour un déploiement Render depuis ce dépôt, la commande de démarrage est :

```bash
node assistant-readiness/server.js
```

## Accès interne obligatoire

L'assistant n'est pas un site public. Il ne s'ouvre que pour les personnes qui ont le mot de passe.

- Sans `DASHBOARD_SECRET` (absente ou vide), toutes les routes `/api/*` répondent **503**. Personne ne peut lire, analyser, qualifier ou effacer un dossier. Les pages affichent seulement un écran verrouillé, pas l'outil.
- Avec `DASHBOARD_SECRET`, `index.html` et `dashboard.html` ne sont envoyées qu'après ce même secret. Un visiteur anonyme voit une demande de mot de passe.
- `/health` reste public et ne renvoie que `{"ok":true,"service":"assistant-readiness"}`.

Sur Render, après le déploiement de cette version :

1. Ouvrir le service de l'assistant.
2. Aller dans **Environment**.
3. Ajouter `DASHBOARD_SECRET` avec un mot de passe long, connu seulement des personnes qui opèrent le cockpit.
4. Enregistrer. Render redéploie.
5. Ouvrir l'URL du service : la page demande ce mot de passe. Tant que la variable est vide, l'outil reste fermé.

Le mot de passe se saisit dans le formulaire (un cookie HttpOnly de session est alors posé, jusqu'à la fermeture du navigateur). Pour un appel API, le même secret va dans l'en-tête `X-Dashboard-Secret`.

Ne pas écrire ce secret dans le dépôt. Une valeur vide veut dire **fermé**, pas ouvert. Les espaces en début ou en fin de valeur sont ignorés.

La page d'accueil répond en HTTP 200 avec l'écran verrouillé ou le formulaire seulement. Le contrôle de santé Render sur `/` peut donc réussir, sans renvoyer l'outil. La sonde dédiée est `/health`.

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

Aucune API IA externe n'est nécessaire pour cette V0.2. Le moteur reste local et les données de dossier sont persistées côté serveur. L'accès au cockpit exige `DASHBOARD_SECRET` : voir « Accès interne obligatoire ».

Le cockpit ne remplace pas le planning client et ne prend pas les décisions techniques, HSE, budgétaires ou d'arbitrage à la place d'Hervé.
