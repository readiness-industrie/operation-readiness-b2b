# Readiness Industry — Landing page terrain

Landing page commerciale statique et démonstrateur simulé pour un service de poursuite active des prérequis avant une installation, un SAT ou une mise en service industrielle.

La page présente un **service humain opéré**, pas un logiciel SaaS à administrer. Le client cadre le mandat et garde les décisions ; le service poursuit les interlocuteurs autorisés, collecte les preuves, applique les contrôles documentaires convenus, trace les échanges et escalade les blocages. Toutes les données de la démonstration sont fictives.

## Structure

```text
.
├── index.html              # Structure et contenu éditorial de la landing page
├── styles.css              # Design, responsive, états et animations
├── simulation-data.js      # Données fictives de la simulation J-14 → J-0
├── app.js                  # Rendu, interactions, calculateur et formulaire local
├── robots.txt              # Consignes d'exploration et adresse du sitemap
├── sitemap.xml             # URL canonique à soumettre aux moteurs de recherche
├── mentions-legales.html   # Identification de l'éditeur, hébergeur et données personnelles
├── docs/
│   └── pilot-metrics.md    # Référentiel de mesure honnête des futurs pilotes
├── assets/
│   ├── favicon.svg
│   ├── og-readiness.svg
│   └── og-readiness.png
└── .nojekyll               # Empêche le traitement Jekyll sur GitHub Pages
```

## Lancement local

La page n'a aucune dépendance et ne nécessite pas de compilation.

Depuis ce dossier :

```bash
python3 -m http.server 8765
```

Puis ouvrir `http://127.0.0.1:8765/`.

Éviter l'ouverture directe en `file://` pour reproduire fidèlement le comportement de GitHub Pages.

## Déploiement GitHub Pages

1. Pousser les fichiers sur la branche `main` du dépôt.
2. Dans GitHub : **Settings → Pages**.
3. Dans **Build and deployment**, choisir **Deploy from a branch**.
4. Sélectionner la branche `main`, dossier `/ (root)`, puis enregistrer.

L'URL technique attendue pour ce dépôt est :

```text
https://readiness-industrie.github.io/operation-readiness-b2b/
```

La documentation GitHub Pages indique l'état de la première publication dans l'onglet **Actions** ou dans **Settings → Pages**.

## Modifier le contenu

- Textes, sections, titres et formulaire : `index.html`
- Ton visuel, couleurs, espacements et responsive : `styles.css`
- Meta title, meta description, canonical, partage social et données structurées : section `<head>` de `index.html`
- URL indexable et date de mise à jour : `sitemap.xml`
- Adresse du sitemap : `robots.txt`

L'ordre des sections suit le débrief du premier entretien terrain : service opéré, répartition des rôles, complexité J-30 → J-0, preuves et fermeture, simulation, coût, méthode, mandat, traçabilité, escalade, responsabilités, qualification, pilote et CTA final.

## Modifier la simulation

Les données sont séparées dans `simulation-data.js` :

- `days` : jours et libellés de la chronologie ;
- `statusMeta` : statuts visibles ;
- `prerequisites` : responsables, preuves, échéances, impacts et changements d'état ;
- `activities` : journal d'activité affiché dans la colonne de poursuite.

Pour chaque prérequis, `activeFrom` indique son premier jour visible. Les entrées de `changes` sont appliquées dans l'ordre chronologique jusqu'au jour sélectionné.

La V1 contient 12 prérequis initiaux et un treizième ajouté à J-6 pour illustrer l'ajout d'un nouveau point en cours d'opération.

## Calculateur

Le calculateur fonctionne uniquement dans le navigateur :

```text
(personnes × coût/jour × jours affectés)
+ location matériel
+ transport/hébergement
+ autres coûts
```

Aucune valeur n'est envoyée ou stockée.

## Formulaire de contact

Le formulaire valide les champs localement et ne stocke aucune donnée sur le site dans cette V1.

Le formulaire ouvre un e-mail prérempli vers l'adresse professionnelle configurée au début de `app.js` :

```js
const CONTACT_EMAIL = "hervemengue.pro@gmail.com";
```

Pour un vrai envoi serveur, choisir plus tard un service de formulaire adapté et ajouter une information de confidentialité correspondante.

## Informations légales à compléter

La page `mentions-legales.html` ne contient que les informations confirmées. Avant la prospection commerciale, ajouter les trois données obligatoires encore absentes du dépôt :

- adresse professionnelle de l'entrepreneur individuel ;
- numéro de téléphone professionnel ;
- numéro SIREN et, le cas échéant, la mention d'immatriculation correspondante.

Ne pas ajouter de mention de RC Pro tant que le contrat d'assurance n'a pas été vérifié.

## Mesure des pilotes

Le référentiel `docs/pilot-metrics.md` définit les événements et calculs nécessaires pour mesurer les premiers pilotes sans confondre action effectuée, réponse obtenue et prérequis confirmé.

## Domaine personnalisé

Avant une diffusion commerciale large :

1. acheter ou valider le domaine professionnel ;
2. ajouter le domaine dans **Settings → Pages → Custom domain** ;
3. appliquer les enregistrements DNS fournis par GitHub ;
4. activer **Enforce HTTPS** ;
5. remplacer les URL Open Graph par l'URL absolue du domaine définitif ;
6. ajouter le fichier `CNAME` créé ou demandé par GitHub.

Le dépôt reste l'infrastructure technique ; le domaine professionnel devient l'identité visible.

## Contrôles prévus

- HTML sémantique et navigation clavier ;
- contrastes lisibles ;
- responsive mobile et desktop ;
- respect de `prefers-reduced-motion` ;
- calculateur purement local ;
- aucune pièce jointe ni upload ;
- aucune donnée client, aucun témoignage, aucun prix et aucun ROI inventés.

## Démonstration de lecture (page autonome)

Page séparée, sans changer l'accueil : `demo-lecture.html`.

Guide pour modifier le dossier fictif **sans Cursor** : [`DEMO_LECTURE.md`](DEMO_LECTURE.md)

Les 12 prérequis se trouvent dans `demo-lecture-data.js`.

