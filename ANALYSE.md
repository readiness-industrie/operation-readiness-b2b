# Analyse de Readiness Industry

8 novembre 2026. Pour toi, Hervé. Rien n'est modifié sur le site. Rien n'est à fusionner. Le prix, partout, est à fixer par toi.

Le dépôt lu est `main` au commit `8bbc683` (8 novembre 2026, 19 h 17, « Remplacer les appels à réserver un échange par un seul lien e-mail »). Une première lecture avait été faite sur `25040e3`. Le commit du soir change le contact public : je le dis quand la phrase n'est plus la même.

## 0. Ce qui a été ouvert

Le nombre de lignes est le nombre de retours à la ligne, comme `wc -l`. Un fichier d'une seule ligne sans retour compte 0.

### Dépôt du site, commit `8bbc683`

Pages, textes et scripts ouverts :

| Fichier | Lignes | Lecture |
|---|---:|---|
| `index.html` | 499 | entière, puis relue sur le contact et les tarifs après `8bbc683` |
| `pret-au-jour-j.html` | 291 | entière, contact relu |
| `renfort-administratif.html` | 474 | entière, contact relu |
| `premier-echange.html` | 35 | entière sur `8bbc683` (elle faisait 111 lignes avant) |
| `conditions.html` | 138 | entière, articles prix et contact relus |
| `confidentialite.html` | 65 | entière |
| `mentions-legales.html` | 158 | entière, paragraphe contact relu |
| `checklist-preparation-installation-industrielle.html` | 144 | entière sur `25040e3` ; le bouton a été repris dans `8bbc683` |
| `preparation-sat-industriel.html` | 105 | idem |
| `prerequis-mise-en-service-industrielle.html` | 58 | idem, phrase de zone et bouton relus |
| `prerequis-avant-installation-machine-industrielle.html` | 45 | idem |
| `checklist-avant-intervention-industrielle.html` | 3 | page minifiée lue ; bouton mis à jour dans `8bbc683` |
| `coordination-fournisseurs-avant-installation.html` | 3 | idem |
| `points-bloquants-avant-installation-machine.html` | 3 | idem |
| `preparation-site-avant-installation-industrielle.html` | 3 | idem |
| `suivi-prerequis-avant-mise-en-service.html` | 3 | idem |
| `essai-gratuit.html` | 16 | entière sur `8bbc683` |
| `demo-lecture.html` | 135 | entière |
| `llms.txt` | 51 | entière |
| `llms-full.txt` | 94 | entière |
| `robots.txt` | 167 | entière |
| `sitemap.xml` | 21 | entier |
| JSON-LD | dans `index.html`, `pret-au-jour-j.html`, `renfort-administratif.html` et les pages article | lu avec ces pages |
| `mentions` et conditions : pas de bloc JSON-LD | — | vérifié |
| `README.md` | 148 | lu |
| `DEMO_LECTURE.md` | 76 | lu |
| `docs/pilot-metrics.md` | 41 | lu |
| `analytics.js` | 106 | lu |
| `web3forms.js` | 123 | lu |
| `essai.js` | 2 | lu (il ne fait plus rien) |
| `mobile-nav.js` | 110 | parcouru |
| `app.js` | 607 | lu pour les textes et les montants |
| `demo-lecture.js` | 679 | idem |
| `demo-lecture-data.js` | 14 | lu |
| `assistant-readiness/` (README 93, knowledge 44, server 404, deux pages, package 8) | lu | |
| `scripts/live-audit.mjs` | 308 | rôle lu |
| `scripts/mobile-pixel-audit.mjs` | 208 | rôle lu |
| `.well-known/security.txt` | 3 | lu |
| `CNAME` | 0 | `www.readiness-industry.fr` |
| `googlebeb818d1ef24c80f.html` | 0 | fichier de vérification, une ligne |
| `.node-version` | 1 | `24.22.1` |
| `.nojekyll` | 1 | vide |

Pas lu comme un texte :

| Fichier | Taille | Pourquoi |
|---|---:|---|
| `styles.css` | 4 211 lignes | feuille de style ; cherchée sur les mots commerciaux, pas relue phrase par phrase |
| `demo-lecture.css` | 4 105 lignes | idem |
| `simulation-method.css` | 0 ligne utile | fichier vide de texte |
| `simulation-data.js` | 341 lignes | début lu (scénario fictif, libellés de statut) ; pas chaque ligne de prérequis |
| `assets/video/renfort-adv.mp4` | 6 296 150 octets | vidéo, pas visionnée |
| photos jpg et png du site | de 5 943 à 232 755 octets | images, pas décrites |
| `assets/favicon.svg`, `assets/og-readiness.svg` | 6 et 33 lignes | dessins |

### Archive `dossier-analyse.tar.gz`

127 fichiers. Décompressée dans un dossier de travail, hors du site.

Textes lus en entier (lignes) : fiches agents (cyber 21, finance 60, commercial 106, communication 87, juridique 123, administratif 179, suivi 63, bilan 61, structure 50, carnet assistant 11, Jules 345, fiches du 29 octobre 240, Gallagher industrie 306, plan Diether 17), six fichiers `.source.txt` d'avatars (4 chacun), agents de réalisation (pilotage 75, ADV 75), bases (pilotage 197, ADV 174), vérification 16, fréquences 6, `enrichir.py` 89, `freq.py` 80, modèles (csv d'une ligne ou tableaux courts, relances 14 et 15, compte rendu 19), offres JSON 610, Elias (synthèse 398, notes 6, séance 2 155, offre 178, présentation 182, crédibilité 75), confidentialité (42, 64, 22), prospection (modèle 254, carnet 66, checklist 78, méthode août 249), bases de référence (Gallagher 124, entreprise 144, ADV 264, industrie 274), structure (plan 324, diagnostic 236, analyse complète 115, analyse supérieure 54, deux tests de chaîne 262 chacun), améliorations déjà là (règles 198, fiche 31, questions 13, recette 23, trois inventaires 94, 91 et 111, deux registres d'une ligne, README 14), packs admin et contrats (73, 94, 74, 111, 63, 57, 41, 87, 170, 114, 26), `regles-maitres.txt` 163, `manifest.json` 109.

Le dossier `realisation/sources-v3` est vide.

Copies HTML de `structure/audit-2026-11-08` : comparées octet par octet au dépôt **avant** `8bbc683`. Elles étaient identiques à `25040e3`. Elles ne sont plus le site de ce soir. Les `.lu.txt` (de 43 à 502 lignes) sont des extraits de ces anciennes pages. Je ne les ai pas relus ligne à ligne après avoir lu les HTML.

Pas lu comme un texte :

| Fichier | Taille | Lecture |
|---|---:|---|
| `Fiches_agents_Readiness_Industry.docx` | 42 972 octets | texte extrait et lu ; le `.md` de 240 lignes dit la même chose |
| six avatars `.jpg` | 51 126 à 108 012 octets | pas décrits ; les `.source.txt` donnent la page Unsplash |

### Pages web ouvertes pour les méthodes

Ouvertes et utilisées plus bas :

- https://copyblogger.com/problem-agitate-solve/ (Demian Farnworth, 2 juin 2014) : problème, agiter, solution
- https://www.huthwaiteinternational.com/spin-methodology : quatre questions SPIN, Neil Rackham
- https://www.momtestbook.com/ : parler de ce qui s'est passé, pas d'une question biaisée
- https://www.atlassian.com/agile/project-management/raid-log : risques, hypothèses, problèmes, décisions ou dépendances
- https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4 : article 28
- https://www.cnil.fr/fr/sous-traitance-exemple-de-clauses : exemple du 4 octobre 2017

J'ai retiré les méthodes dont je n'ai pas ouvert la page : pourcentages Gong, livre *Shift!*, *Influence* de Cialdini, cours Unbounce, et l'idée que le registre RAID voudrait seulement dire « actions et décisions ». Atlassian dit que le D est « décisions ou dépendances ». Le registre que je te laisse prend les dépendances, et une colonne à part pour ta décision, parce que le chef de projet décide.

La page EUR-Lex du règlement n'a pas répondu (délai dépassé). Je m'appuie sur la reproduction de l'article 28 par la CNIL, page ouverte.

## 1. Ce qui n'est pas conforme

### Le site de ce soir est mieux aligné qu'il ne l'était à 18 h

Avant `8bbc683`, l'accueil disait : « Parlons de votre prochain jalon : premier échange de 30 minutes ». Les conditions disaient : « Le premier échange de 30 minutes est sans engagement et sans frais. » Il y avait un lien Calendly. Cela contredisait « 15 minutes au plus » et « pas d'appel imposé ».

Le commit du soir retire Calendly, les formulaires visibles et les « 30 minutes ». La phrase actuelle, `index.html` ligne 487 et `premier-echange.html` ligne 30 : « Un court échange de 15 minutes, si vous le souhaitez. » Le bouton, ligne 488 de l'accueil : « Décrivez-nous votre projet en deux lignes », vers `hmreadinessindustry@gmail.com`, objet « Mon projet ». Les conditions, ligne 89, ne disent plus « sans frais ».

Ça, c'est conforme. Le reste ne l'est pas encore.

### Le nom de fichier dit encore « gratuit »

`essai-gratuit.html` existe. `robots.txt` ligne 8 : `Disallow: /essai-gratuit.html`. La page redirige vers `premier-echange.html` et n'affiche plus le mot. Le nom, lui, est encore public si quelqu'un tape l'adresse. Ça contredit « rien de gratuit ».

### Le chiffre de 2 000 à 3 600 € n'a pas de source sur la page

`index.html` lignes 390-391 :

« une mise en service reportée parce que le site n'est pas prêt peut coûter environ 2 000 à 3 600 € HT de refacturation fournisseur (deux techniciens immobilisés deux jours, puis un nouveau déplacement) […] Estimation basse, à partir de tarifs journaliers publiés par des fournisseurs et des barèmes URSSAF 2026 »

Aucun lien. Ton calcul du 7 novembre, dans `seance2-travail.md`, est une autre hypothèse (environ 1 200 à 3 100 € pour une journée et une nuit, effectifs non établis). La page URSSAF de ce dossier était en erreur 500. Je ne reprends pas ces montants comme un fait.

### Deux packs de contrats, et l'un parle d'outils au client

`contrats-01`, article 12 : « y compris des agents ou outils d'intelligence artificielle ». `contrats-02` ligne 20 : « Assistance par outils d'IA ». `contrats-03` et `contrats-04` le redisent. Interdit dans un document client.

Le même pack, `contrats-01` ligne 19 : « Le diagnostic offert proposé dans le cadre du Renfort ADV est gratuit ». `contrats-02` a une ligne « Diagnostic offert », « 0 € ». `admin-pack-04` commence par « Devis gratuit ». Interdit.

Paiement, les deux côtés :

- Pack contrats : « un acompte de 30 % est facturé à la commande » (`contrats-01`).
- Pack admin, journal : acompte retiré, une seule échéance. Le site, `conditions.html` lignes 81-84 : « 30 jours après la date d'exécution » et « Aucun escompte ».

Responsabilité, les deux côtés : le pack admin parle d'une « obligation de moyens renforcée » et d'une faute présumée si le livrable manque. Le pack contrats et le site disent une obligation de moyens, faute à prouver côté contrats, « aucun résultat n'est garanti » sur le site (ligne 75).

### Les règles de mail ne sont pas les règles du site

Règles maîtres, catégorie C : « Après installation ou mise en service, qui porte chez vous la fermeture des points restant ouverts jusqu'à la réception ». L'offre publique s'arrête avant le jour J. `index.html` ligne 477 : « Est-ce du pilotage de projet ? » Réponse : « Non. Le chef de projet reste décisionnaire. »

La base du 29 octobre, `Fiches_agents_Readiness_Industry.md` ligne 14 : « Premier échange de 30 minutes […] sans frais. Rien de gratuit ni de remise en public. » Les deux phrases sont dans la même ligne.

`offre-readiness-industry-v1.md` : check-list « gratuite », diagnostic « déduit si vous commandez », « échange gratuit de 30 minutes », pack « 10 à 15 % de moins ». `presentation-offre.md` : « Diagnostic ADV offert », « prix réduit », « remise de parrainage ». À ne plus utiliser.

`presentation-offre.md` ligne 12 dit au client : « Des agents IA […] m'aident à aller plus vite. » Le plan Diether du 4 novembre laisse ouvert : « citer l'innovation (IA). Contradiction avec la règle ».

### « Démarrer à l'heure » promet trop

`seance2-travail.md`, versions 2 et 3 et mélange Elias : « démarrer à l'heure », « démarrer leurs installations à la date prévue ». La synthèse propose : « Le jour J, tout est prêt. » Le site, conditions ligne 75, dit le contraire : aucun résultat n'est garanti. `preparation-sat-industriel.html` le dit aussi pour le SAT.

Le mot « 8 ans » est interdit dans les mails. Les textes d'octobre l'écrivent. Le site et la séance 2 disent « 9 ans ». Tu n'as pas tranché dans un seul endroit.

### La page ADV dit encore « pour démarrer »

`renfort-administratif.html` ligne 370 : « Le type de dossiers et la situation suffisent pour démarrer. » Ce n'est pas « je débute ». Ça peut se lire ainsi. À changer quand tu voudras toucher au site.

La même page charge encore `web3forms.js` (ligne 434) et un script qui cherche un formulaire `adv-form` qui n'est plus dans la page. Les mentions, ligne 91 : « Le site ne transmet pas de formulaire. » Le script mort ne contredit pas cette phrase tant que le formulaire est absent. Il ne devrait plus être là.

Le pied de page garde le téléphone (`index.html` ligne 493, page ADV ligne 390). Ce n'est pas un appel imposé. C'est un deuxième chemin, alors que le commit du soir voulait un seul lien e-mail.

### Étude d'offres d'emploi n'est pas une liste de prospects

`verification-v3.md` : étude nationale, « jamais de prospection en Normandie ». Dans le JSON ajouté, La Chapelle-Longueville (Eure) et La Hague (Manche) sont en Normandie. Le fichier ne le dit pas. Ce sont des offres lues, pas des cibles. Ne les contacte pas.

P29 est classé en zone prioritaire alors que l'annonce dit « HDF/IDF/Normandie ». Même règle : on n'y va pas.

### Gmail n'a pas été rouvert ici

Le diagnostic du 8 novembre dit 14 messages entrants, des suites chez Consultys, Menissez et AXE-S-ONE, et « aucun contrat signé ». Je n'ai pas rouvert Gmail. Je ne confirme pas ces fils. Tu les revérifies avant d'écrire.

## 2. Ce qui est fragile, et comment le renforcer

**Un seul prix pour la première mission.** La grille publique existe (550, 900, 1 800, 2 500, et l'ADV à part). Les textes d'octobre en ont d'autres (1 200 à 4 500, 900 à 3 200, relais mensuel). Renfort : tu coches un seul montant de la grille du site, sur la fiche `ameliorations/fiche-premiere-mission.md`. Tu l'écris sur le devis. Tu ne négocies pas.

**Le oui de demain n'a pas de papier unique.** Deux packs se contredisent. Renfort : tu pars du devis et de la lettre de ce dossier, tu choisis la phrase de paiement du site (30 jours, pas d'escompte) sauf avis contraire après relecture, et tu ne sors pas l'autre pack.

**Le coût affiché n'est pas sourcé.** Renfort : tu retires la fourchette de l'accueil, ou tu la remplaces par un calcul dont tu peux montrer les liens. En attendant, tu ne la cites pas dans un mail.

**Les mails d'août ont eu des réponses, et ils sont interdits ensuite.** « Je mène actuellement une étude très ciblée » est dans `prospection-methode-aout.md` et dans les mails Menissez et Clextral cités comme ayant répondu. `modele-offre-emploi.md` et la checklist l'interdisent. Renfort : tu gardes le fait qui te concerne (leur annonce, leur projet), tu ne dis plus « étude ». Tu ne réécris pas un mail qui a déjà été envoyé.

**Trop de prénoms pour les mêmes tâches.** Camille, Marc, Léa, Noémie, Olivier, Chloé, Jules contrôleur, puis Jules commercial, Inès, Emma, Hugo, Théo, Léo, Clara, Iris. Les crons sont notés désactivés le 3 novembre. Renfort : une personne prépare le mail, tu l'envoies. Tu ne relances pas l'usine à agents avant le premier client payé.

**Pas de compteur.** Le carnet dit « 1 531 domaines » puis « 4 cibles valides » puis « 7 ». Le diagnostic dit 1 947 messages, pas 1 947 entreprises. Renfort : une ligne par entreprise, dans un tableur que tu as déjà. Colonnes : société, ville, rôle, adresse vérifiée, date d'envoi, réponse, suite. Tu ne remplis que ce que Gmail montre.

**La preuve « 9 ans » et les habilitations.** Tu les as dites le 8 novembre (H0V, B1V, B2V, BR, BC, CACES R486 B à renouveler, transpalette et chariot). Elles ne sont pas dans le dépôt sous forme de copie. Renfort : tu les gardes pour toi. Tu ne les mets sur le site que le jour où la copie est dans le dossier, et tu dis « obtenu » pour le CACES, comme tu l'as noté, pas « à jour » s'il ne l'est pas.

**RC Pro.** Les modèles disent de ne pas écrire « assuré ». Elias demande l'attestation. Renfort : tu ne l'affirmes pas. Tu décides si tu souscris. Ce n'est pas un outil de prospection : c'est une assurance. Je ne te dis pas de payer.

**Confidentialité publique, solide, et trous.** La page confidentialité est claire : accord avant les documents, trois façons d'envoyer, suppression en fin de mission, zone Oise / Somme (Amiens) / Île-de-France. Les mentions ne disent plus que le courrier arrive dans Gmail, alors que l'adresse est une adresse Gmail. Renfort : une phrase, quand tu voudras, « le message est reçu sur la messagerie Google de Readiness Industry ». Pas dans cette branche.

**Pages SEO.** Elles expliquent le métier et renvoient vers toi. Plusieurs ne redisent pas la zone. Le mot « coordination » est dans une adresse (`coordination-fournisseurs-avant-installation.html`) alors que tes mails l'interdisent. Renfort : tu ne changes pas l'adresse (les liens casseraient). Tu réserves l'interdit aux mails et à LinkedIn, sauf si tu décides l'inverse.

## 3. Utile, à renforcer, à laisser de côté

| Élément | Classe | Pourquoi |
|---|---|---|
| Page d'accueil, Prêt au Jour J, conditions, confidentialité, mentions | Utile | L'offre, la zone, le décideur et les prix y sont. Le contact du soir est le bon. |
| `llms.txt` et `llms-full.txt` | Utile | Ils répètent les mêmes mots que le site. |
| Grille 550 / 900 / 1 800 / 2 500 et ADV 250 / 500 / 900 | Utile | Déjà publique. Tu choisis dedans. |
| Page ADV | À renforcer | Utile si un client la demande. Pas dans le premier mail. Retirer le script de formulaire mort et la phrase « pour démarrer ». |
| Pages articles (checklists, SAT, prérequis) | Utile | Elles décrivent le problème sans vendre deux offres. |
| `essai-gratuit.html` | À abandonner | Le nom contredit la règle. Redirection seulement. À retirer quand tu accepteras une modification du site, avec une redirection gardée le temps que d'anciens liens meurent. Pas dans cette branche. |
| `robots.txt` | À renforcer | Il répète vingt fois les mêmes trois interdits. Un bloc suffit. Il cite encore la page « essai gratuit ». |
| Démo de lecture, `app.js`, assistant local | À laisser de côté pour l'instant | Preuve de méthode, pas un produit. L'assistant perd les dossiers si le disque n'est pas durable. Tu ne le montres pas à un client. Tu ne prends pas d'abonnement pour lui. |
| Vidéo ADV | Utile plus tard | Pas visionnée ici. Tu ne t'en sers pas dans le premier mail. |
| Agent « Prêt au Jour J » et ses quatre modèles | Utile | Le rôle est bon : préparer, alerter, ne pas décider. Les modèles sont des en-têtes vides : tu les remplis sur une vraie mission. |
| Agent ADV et ses modèles | À laisser de côté tant qu'on ne te le demande pas | Même qualité de squelette. L'offre reste seconde. |
| Bases d'offres (57 et 60) et le JSON | Utile comme étude | Elles montrent des tâches qui reviennent (planning, fournisseurs, commandes, factures). Elles ne prouvent pas qu'une entreprise va t'acheter. Tu ne prospectes pas la liste nationale. |
| `verification-v3.md` et `frequences-v3.txt` | Utile | Ils disent eux-mêmes la limite. |
| Modèle de mail du 3 novembre et checklist | À renforcer | Bonne ossature (leur fait, pas une candidature, décisions chez eux, lien à la fin). Enlever le mot « test » qui traîne dans la checklist. |
| Méthode d'août | À abandonner pour les prochains envois | Ouverture « étude ciblée », interdite ensuite. Tu gardes le fichier comme archive, tu ne t'en sers plus. |
| Carnet d'erreurs prospection et carnet de Jules | Utile | Ils empêchent de refaire les mêmes mails. |
| Règles maîtres Gmail | Utile, à discuter | Obligatoires pour l'envoi. Elles couvrent l'après-installation, le site non. Tu tranches. Tu ne les supprimes pas. |
| Fiches du 29 octobre (Camille, Marc, Léa, quatre contrôles) | À abandonner comme mode d'emploi | Remplacées dans les faits le 3 novembre, et les contrôles n'ont pas été construits. Tu gardes le fichier. Tu ne relances pas ces prénoms. |
| Jules commercial, Inès | À renforcer plus tard | Utiles le jour où tu envoies peu de mails propres et deux textes LinkedIn. Pas une équipe à faire tourner cette semaine. |
| Emma, Hugo, Théo, Léo, Clara, Iris, Diether | À laisser de côté | Ils préparent la maison. Ils ne rapportent pas le premier oui. Le plan Diether cite l'IA : tu ne l'appliques pas. |
| Avatars | À abandonner pour le site | Photos de banque d'images. Tu ne les publies pas. Toi seul es sur le site. |
| Gallagher / Medvi | À laisser de côté | Utile comme rappel « tu livres le travail, tu ne vends pas un outil ». Le rapprochement B2C n'est pas une méthode pour tes mails. |
| Elias, synthèse et séance 2 | Utile | La cible, les trois cas, l'interdit de toucher au site avant la séance 3. Tu ne copies pas les phrases « à l'heure » ni « tout est prêt ». |
| Offre et présentation d'octobre | À abandonner comme texte client | Gratuit, remise, IA, 8 ans, deux grilles. |
| Kit confidentialité | Utile | À faire signer avant les documents. Le modèle se fait relire. Tu retires toute phrase sur un outil d'aide si elle part chez le client. |
| Deux packs admin / contrats | À renforcer en un seul | Tu n'en envoies aucun tel quel. Le devis et la lettre de `ameliorations/` servent de base, après ta relecture. |
| Tests de chaîne du 8 novembre | Utile comme exercice | Zéro envoi. Aucun des dix dossiers n'est autorisé. Tu ne les envoies pas depuis ce fichier. |
| Analyses du 8 novembre déjà dans l'archive | Archive | `analyse-complete` s'arrête à l'inventaire. Celle-ci la remplace pour la décision. Tu ne publies pas l'archive. |
| `sources-v3` vide | À abandonner | Rien dedans. |

## 4. Les fichiers de règles

| Fichier | Rôle | Doublon | Contradiction |
|---|---|---|---|
| `regles-maitres.txt` (163 lignes, copie du brouillon Gmail) | Ce qu'il faut relire avant un envoi | Recopié en annexe de `regles-unifiees-PROJET.md` lignes 36 à 198 | Catégorie C jusqu'à la réception. Le site s'arrête avant le jour J (`index.html` ligne 477 : « Est-ce du pilotage de projet ? Non. »). |
| `regles-unifiees-PROJET.md` | Projet du 8 novembre, non appliqué | Contient la copie intégrale du maître | Il ne tranche pas. Il liste les arbitrages. C'est sain. Il ne doit pas devenir une deuxième loi. |
| `fiche-commercial.md` et `jules-base-connaissances.md` | Mail, relance, mots interdits | Reprennent la checklist | Jules y est le commercial. Le 29 octobre, Jules contrôle Léa (`Fiches_agents` lignes 108-110). « 15 min max, jamais poussé » (base Jules) contre « 30 minutes sans frais » (fiche du 29 octobre, ligne 14). |
| `checklist-qc.md` | Contrôle avant envoi | Résumé du modèle de mail | Ligne qui demande encore une « CTA légère : test / mission », alors que le carnet interdit « test ». |
| `carnet-erreurs.md` (prospection) | Erreurs à ne pas refaire | — | Dit le vivier « quasi épuisé » sans joindre la liste. |
| `prospection-methode-aout.md` | Ancienne structure de mail | Même but que le modèle du 3 novembre | « Étude très ciblée » contre l'interdit du 3 novembre. |
| `Fiches_agents_Readiness_Industry.md` | Équipe du 29 octobre | Mêmes métiers que les fiches du 3 novembre | 30 minutes sans frais, et « rien de gratuit », même paragraphe. |
| `structure-entreprise.md` | Tableau « validé » du 5 novembre | Reprend les fiches | Des fiches encore marquées « brouillon » le 3 novembre y sont « validées » le 5. |
| `confidentialite/modele-accord` et `contrats-04` et `admin-pack-03` | Trois accords | Même sujet | Les contrats nomment des outils d'aide. Le modèle de novembre l'interdit aussi, donc le mot arrive chez le client. Le pack admin laisse une case « [outil d'aide à la rédaction] ». |
| `contrats-01` et `admin-pack-01` | Deux CGV | Même titre | Acompte contre pas d'acompte. Moyen contre moyen renforcé. Tribunal de Beauvais « à confirmer » contre clause retirée dans le journal admin. |
| `conditions.html` | CGV publiques | Troisième texte | 30 jours, pas d'escompte, obligation de moyens, 15 minutes si le client veut. C'est le texte que le client peut déjà lire. |
| `plan-structure-2026-11-08.md` | Décisions proposées, non faites | Reprend les règles | Refuse de changer seul le 10/10/10, et propose en même temps de viser la qualité plutôt que 30 envois. |
| `agents/fiche-juridique.md` | Veille | — | « Dire quand une personne parle à une IA » et, plus bas, ne pas dire « IA » aux clients. |

Organisation simple, à discuter, pas à appliquer ce soir : trois fichiers dans un dossier `regles/`, décrits dans `ameliorations/regles-regroupees-PROJET.md`. Le brouillon Gmail reste la référence d'envoi tant que tu n'as pas écrit le contraire. On n'efface rien.

## 5. Améliorations, avec une méthode dont j'ai ouvert la page

**Mail.** Problème du prospect, conséquence concrète, puis toi. Page ouverte : https://copyblogger.com/problem-agitate-solve/ La page agite fort, jusqu'à la peur. Toi, tu restes sur un fait (leur annonce, leur jalon, un point non confirmé). Pas d'adjectif. Toi et le lien, à la fin seulement. Un seul lien. Pas de demande de créneau.

**Réponse.** Quatre questions : situation, problème, implication, besoin formulé par eux. Page ouverte : https://www.huthwaiteinternational.com/spin-methodology Les huit questions sont dans `ameliorations/questions-spin.md`.

**Ne pas te faire mentir.** Le site du Mom Test demande des faits passés, pas « cela vous intéresserait-il ». Page ouverte : https://www.momtestbook.com/ D'où la question « la dernière fois, qu'est-ce qui manquait le matin ».

**Livrable de mission.** Un registre des risques, hypothèses, problèmes déjà là, et dépendances. Page ouverte : https://www.atlassian.com/agile/project-management/raid-log Le D y est « décision ou dépendance ». Je prends la dépendance, et une colonne séparée pour la décision du chef de projet, pour ne pas décider à sa place. Fichier : `ameliorations/registre-raid.csv`. Tu le tiens dans un tableur, pas dans un outil payant.

**Contrat de données.** Article 28, texte CNIL : https://www.cnil.fr/fr/reglement-europeen-protection-donnees/chapitre4 Exemple de clauses, qui ne suffit pas seul : https://www.cnil.fr/fr/sous-traitance-exemple-de-clauses La lettre reprend : instructions écrites, confidentialité, pas de sous-traitant sans accord, aide sur les droits, alerte si violation, suppression ou renvoi, information pour un contrôle. Aucun outil n'est nommé.

## 6. Ce qui est construit

Dans `ameliorations/` de cette branche, et nulle part sur le site :

- `fiche-premiere-mission.md`
- `devis-type.md`
- `lettre-de-mission.md` (clause article 28)
- `registre-raid.csv` (trois situations de ton récit du 8 novembre, marquées comme exemples)
- `questions-spin.md`
- `regles-regroupees-PROJET.md`
- `cas-terrain.md`

Le prix est à fixer par toi. Aucun de ces fichiers n'est un envoi.

## 7. Quoi faire, dans l'ordre

1. Tu fixes le prix de la première mission en cochant un montant déjà sur le site. Tu l'écris sur la fiche. Tu ne crées pas un quatrième prix.
2. Tu lis le devis et la lettre. Tu choisis la phrase de paiement du site, sauf si la relecture te dit autre chose. Tu laisses vide la case « messagerie » tant que tu n'as pas décidé si Gmail peut recevoir les données de mission.
3. Tu fais relire ces deux pages (la CCI de l'Oise est déjà citée dans tes packs). Tu ne signes pas avant.
4. Tu ouvres Gmail. Tu regardes seulement les fils où un humain a répondu. Tu ne réponds pas depuis ce document. S'il faut écrire, le message parle de leur jalon, et de toi à la fin. Quinze minutes seulement s'ils le demandent.
5. Les prochains mails neufs : Oise, Somme côté Amiens, Île-de-France. Une offre, Prêt au Jour J. Leur fait en premier. Pas de gratuit, pas de remise, pas d'outil, pas de « je débute », pas de Normandie, pas de quota de 30. Tu valides chaque envoi. La carte de visite v2 des règles maîtres reste obligatoire si ces règles l'exigent encore : si tu ne l'as pas, tu n'envoies pas.
6. Tu ne prends aucun outil payant.
7. Tu laisses les agents, l'assistant et la démo éteints jusqu'au premier paiement.
8. Le site : tu n'y touches pas dans cette branche. Quand tu voudras, après la séance avec Elias si tu tiens son interdit : retirer le nom `essai-gratuit`, retirer ou sourcer les 2 000 à 3 600 €, retirer le script mort de la page ADV, et décider si le téléphone reste au pied de page. Les trois cas ne vont en ligne que sur ton oui.
9. Le 19 novembre, tu gardes la phrase déjà sur le site. Tu ne retiens pas « démarrer à l'heure » ni « le jour J, tout est prêt ».
10. Cette branche reste un brouillon. On ne la fusionne pas.

Rien n'a été envoyé. Rien n'a été publié. Le site en production n'est pas modifié par ces fichiers.
