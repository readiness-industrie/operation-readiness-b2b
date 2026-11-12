# Règles de vague : contrôles obligatoires avant de livrer

Ces contrôles sont faits par programme, sur le box, par le Copilote. Le résultat est collé dans `vagues/AAAA-MM-JJ/controle.md`. Aucun mail n'est envoyé par l'agent de vague.

## 1. Anti-doublon (obligatoire, pour chaque adresse et chaque entreprise)

L'agent de vague ne clone pas `Agents-readiness` et ne lance aucun contrôle anti-doublon. Il ne s'arrête pas faute de pouvoir le faire.

Il renvoie la liste des candidats, une ligne par candidat : entreprise, adresse, domaine. Sans verdict anti-doublon : ni « libre », ni « absent des contactés », ni « bloqué ».

Le contrôle est fait ensuite sur le box par le Copilote : outil anti-doublon (`npm run doublon`), recherche Gmail `in:sent` et `rg` dans les rapports d'envoi. Seule sa sortie compte. Un candidat bloqué sort de la vague.

## 2. Texte du mail

Le contrôle du texte est fait sur le box par le Copilote. L'agent de vague ne le lance pas.

Règles (fichier unique `src/lib/ri/ops/regles.ts`) : moins de 150 mots, aucun « gratuit, essai, test, IA », aucun tiret, pas de « je, nous, Readiness Industry » en première moitié, lien readiness-industry.fr en bas puis « Hervé MENGUE, Readiness Industry ».

## 3. Cible

- Zone : Oise (60), Somme (80), Île-de-France. Jamais la Normandie.
- **Taille : plus de plafond.** Le plafond de 50 à 250 salariés a été levé par Hervé le 09/11/2026. Les grandes entreprises sont permises.
- Adresse générale : dernier recours seulement, après une recherche de nominatif notée. La personne ou le rôle visé est dans l'objet ET dans la première ligne.
