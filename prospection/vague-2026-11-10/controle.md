# Contrôle du 10 novembre 2026

Relecture séparée du dossier, après la rédaction. Aucun envoi.

## Verdicts

| Société | Statut | Motif |
|---|---|---|
| Delpharm Brétigny | à compléter | Zone 91, industrie pharmaceutique, taille 180 dans l'offre, offre HelloWork 84515651 encore en ligne, publiée le 16/10/2026, arrêt technique été 2027 encore devant nous. Adresse nominative non trouvée. Domaine delpharm.com à contrôler dans Gmail avant toute suite. |
| TotalEnergies Grandpuits | à compléter | Zone 77. Dernière source indépendante du chantier bioraffinerie : 19/07/2026, ouverture annoncée fin 2026. Pas d'article de novembre qui dise que le démarrage a eu lieu, ni qu'il est encore devant nous. Taille 250, déclaration de 2025, pas un effectif de novembre. Guillaume Alliot nommé, adresse non publiée. Domaine totalenergies.com. |
| SGD Pharma Sucy-en-Brie | bloqué | Les URL travaux neufs répondent 410. Le rôle n'est plus au tableau des postes ouverts. Le four cité est celui de 2021. Pas d'adresse nominative. |
| Eurolysine Amiens | bloqué | Pas de mise en service d'équipement datée et encore devant nous. contact@ est une boîte générale. |
| Evoluderm | bloqué | Effectif 39 à une cinquantaine, cible faible. Jour J annoncé en 2029, sans ligne datée proche. contact@ refusé. c.janin@ n'est pas relié à un nom. |
| Tiamat | bloqué | Déjà dans contacted-domains.json le 07/09/2026. Usine reportée sine die le 16/09/2026. 35 personnes. |
| Cabinets, intérim, SSI, BTP, transport | bloqué | Client masqué ou métier hors usine qui prépare un jour J. |
| Dossiers du 9 novembre 14 h | non rouverts | Le motif restant n'est pas la taille. |

Prêt à décider : 0.
Mails : 0.

## Ce que le contrôle a rattrapé

1. Les moteurs montraient encore les offres HelloWork SGD 82399538 et 82379343. Un appel direct répond 410 Gone. Elles ne sont pas comptées comme offres ouvertes. Correctif appliqué dans les fiches.
2. L'ancienne URL HelloWork Delpharm 81102072 répond aussi 410. Une autre URL, 84515651, répond 200 et contient encore Brétigny, 180 personnes, l'arrêt technique de l'été 2027, et la date du 16/10/2026. Seule cette URL est citée comme offre vivante.
3. La page employeur job.delpharm.com répond, mais le corps lisible ce soir était une coquille sans référence. La date « 9 novembre » lue sur cette coquille n'est pas reprise comme une republication. La date retenue est celle de la page HelloWork encore lisible.
4. L'offre France Travail 214DDJN n'a pas été rouverte : le relais a renvoyé un défi d'accès. L'actualisation du 23/10/2026 reste une donnée d'index, pas une relecture de ce soir.
5. Des outils de prospection publient le format prénom.nom pour Eurolysine et SGD, et masquent des adresses derrière un compte. Aucune de ces adresses n'est recopiée. Seule une adresse écrite à côté d'un nom, sur une page publique, aurait compté.
6. L'unité de recyclage chimique de Grandpuits a démarré en mars 2026. Le dossier ne la présente pas comme un jour J encore devant nous. Seule la bioraffinerie, encore en construction au 19 juillet, est gardée, avec la réserve de fraîcheur.
7. L'article sur Goodyear du 31 mai 2026 (transformation jusqu'en 2028) ne suffit pas à rouvrir le dossier du 9 novembre : l'adresse nominative manque toujours.
8. c.janin@evoluderm.com est le courriel d'une fiche société, pas celui d'une personne nommée sur la même ligne. Non utilisé.
9. Les mots interdits des mails n'ont pas de support ce soir, puisqu'il n'y a pas de mail. Les offres sources contiennent « coordination » et « visio » dans leur propre texte de recrutement. Ces mots ne sont pas repris dans un message.
10. L'arrêté WeylChem de juillet 2026 n'a pas été lu. Il n'est pas transformé en projet.

## Anti-doublon local

Fichiers utilisés : contacted-domains.json (30/10/2026), exclusions.json, exclus-connus.md, vague du 9 novembre matin, vague du 9 novembre 14 h. Gmail n'a pas été consulté. Les domaines à vérifier avant tout envoi futur : delpharm.com, totalenergies.com, sgd-pharma.com, sgdgroup.com, eurolysine.com, evoluderm.com. tiamat-energy.com est déjà dans le fichier des domaines contactés.

## Action hebdomadaire

Le fichier `.github/workflows/vivier-hebdo.yml` existe sur la branche de la PR 50, pas encore sur main. Il ajoute des libellés publics, il n'envoie rien. Il n'est pas reconstruit dans cette vague. Il reste à fusionner avec la PR 50.
