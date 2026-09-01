# Démonstration de lecture (page autonome)

Cette page sert à **tester une lecture d'état** auprès d'un prospect. Elle n'est pas le site commercial, ni le logiciel interne.

**URL publique (après mise en ligne) :**  
https://readiness-industrie.github.io/operation-readiness-b2b/demo-lecture.html

**URL locale :** dans ce dossier, lancer `python -m http.server 8765` puis ouvrir  
http://127.0.0.1:8765/demo-lecture.html

Les fichiers se modifient avec le Bloc-notes, VS Code, ou n'importe quel éditeur. Cursor n'est pas nécessaire.

## Fichiers

| Fichier | Rôle |
|---|---|
| `demo-lecture.html` | Page à ouvrir. Ne change presque jamais. |
| `demo-lecture-data.js` | **Les 12 prérequis et toutes les données fictives.** C'est le fichier à modifier pour changer le dossier. |
| `demo-lecture.js` | Logique d'affichage (compteurs, filtres, détails, « Votre attention »). |
| `demo-lecture.css` | Apparence. |

La page d'accueil (`index.html`) utilise d'autres fichiers (`simulation-data.js`, `app.js`, `styles.css`). Ne pas les mélanger.

## Modifier le dossier (demo-lecture-data.js)

Ouvrir `demo-lecture-data.js`.

1. **Titre du dossier** : champ `title` en haut du fichier.
2. **Jour affiché à l'ouverture** : `openingDay: -3` (J-3). Mettre `0` pour le jour de lancement, `-14` pour le début.
3. **Un prérequis** : chaque bloc dans `prerequisites` (PR-01 à PR-12).
   - `title` : nom du point
   - `changes` : l'historique. **Le dernier changement dont `day` est inférieur ou égal au jour affiché** détermine l'état visible.
4. **Dernière information** : champ `info` du changement.
5. **Ce qui manque** : champ `missing`.
6. **Prochaine action** : champ `nextAction`.
7. **Impact** : champ `impact` du prérequis.

Après modification : enregistrer le fichier, recharger la page (Ctrl+F5).

## Statuts possibles

Dans un `changes`, le champ `status` doit être l'un de ceux-ci :

| Valeur technique | Libellé affiché |
|---|---|
| `launch`, `progress`, `followup` | À obtenir |
| `received` | Reçu |
| `incomplete` | Incomplet |
| `contradictory` | Non conforme |
| `validate` | À valider |
| `blocked`, `decision` | Bloquant |
| `closed` | Fermé |

Pour fermer un point : `status: "closed"`, `missing` du type « Rien. Le critère de fermeture est satisfait. », `nextAction: "Aucune. Point fermé."`

## « Votre attention »

Un point apparaît dans **Votre attention** si son statut du jour est :

- `validate` (à valider)
- `blocked` (bloquant)
- `decision` (décision nécessaire)

Ce n'est pas une liste à part. Changer le `status` du dernier changement visible suffit.

Les compteurs (12 / 4 / 8 / 4) se calculent tout seuls. Pas besoin de les taper dans `demo-lecture.html`.

## Ce qu'il ne faut pas faire

- Mettre un vrai nom de client, un vrai site, ou un vrai document.
- Modifier `index.html` pour « coller » cette démo sur l'accueil.
- Modifier `private_app` depuis cette page : ce sont deux produits différents.

## Logiciel interne (console)

Cette page GitHub Pages **n'est pas** la console opérateur. La console tourne sur le PC, en local. Voir le fichier `LANCER_CONSOLE.bat` dans le dossier du clone opérationnel (pas ce dépôt vitrine).
