# Règles de vague : contrôles obligatoires avant de livrer

Ces contrôles sont faits par programme. Le résultat est collé dans `vagues/AAAA-MM-JJ/controle.md`. Aucun mail n'est envoyé par l'agent de vague.

## 1. Anti-doublon (obligatoire, pour chaque adresse et chaque entreprise)

Le code vit dans `readiness-industrie/Agents-readiness` (PR #17). Lecture seule.

```bash
git clone --depth 1 https://github.com/readiness-industrie/Agents-readiness.git /tmp/ar
cd /tmp/ar && npm ci --no-audit --no-fund
# Tout le fichier de la vague :
npm run doublon -- --fichier "$OLDPWD/vagues/AAAA-MM-JJ/mails.md"
# Ou un contact :
npm run doublon -- --email adresse@domaine.fr --company "Nom de l'entreprise"
```

- Code 0 : tout est libre. Code 1 : au moins un contact BLOQUÉ, il sort de la vague et va dans `ecartes.md` avec la ligne affichée (date du premier envoi ou du rebond).
- Code 2 : erreur (index illisible). La vague s'arrête et le dit. On ne remplace pas ce contrôle par une lecture à l'œil.
- Index lu : `ri-data/contacted-domains.json` (envois Gmail + rebonds). Un rebond bloque aussi les autres adresses de la même entreprise.

## 2. Texte du mail

```bash
cd /tmp/ar && npx tsx scripts/check-mails.ts "$OLDPWD/vagues/AAAA-MM-JJ/mails.md"
```

Règles (fichier unique `src/lib/ri/ops/regles.ts`) : moins de 150 mots, aucun « gratuit, essai, test, IA », aucun tiret, pas de « je, nous, Readiness Industry » en première moitié, lien readiness-industry.fr en bas puis « Hervé MENGUE, Readiness Industry ».

## 3. Cible

- Zone : Oise (60), Somme (80), Île-de-France. Jamais la Normandie.
- **Taille : plus de plafond.** Le plafond de 50 à 250 salariés a été levé par Hervé le 09/11/2026. Les grandes entreprises sont permises.
- Adresse générale : dernier recours seulement, après une recherche de nominatif notée. La personne ou le rôle visé est dans l'objet ET dans la première ligne.
