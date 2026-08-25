# Limites, hypothèses et reports V1

## Décisions laissées configurables / à confirmer terrain

- Tarifs S/M/L et coefficients d’urgence : hypothèses de l’issue, modifiables dans `Paramètres`.
- Poids, seuils P0/P1/P2 et overrides : configurables, avec historique d’audit.
- Capacité : estimation manuelle + aide simple. Le logiciel ne promet pas une précision non mesurée.
- Cadence des relances : aucune fréquence universelle codée ; l’opérateur date la prochaine action selon P0/P1/P2/P3 et le délai réel.
- Rétention mission/document/audit : valeurs techniques par défaut, validation juridique obligatoire. L’outil de purge contrôlée n’est à exécuter qu’après cette validation.
- XL/multi-site : « sur devis », jamais calculé automatiquement.

## Volontairement reporté (P2 du brief)

- envoi/réception automatique d’e-mails ;
- intégration téléphonie, banque ou LC Pay Pro ;
- IA ou analyse de documents par un service externe ;
- recommandations apprises, analytics avancés ;
- calcul automatique fin de la capacité.

Ces reports réduisent les risques sécurité/RGPD et n’empêchent pas l’exécution manuelle d’une première mission.

## Limites avant première donnée réelle

- Le code est prêt à être déployé, mais aucune infrastructure de production ni compte Render/Scaleway n’est créé automatiquement.
- Le test RLS PostgreSQL doit passer dans la CI de la branche publiée et être rejoué après déploiement avec Alpha/Beta.
- La restauration production doit être exercée sur une base temporaire.
- Les clauses contractuelles, politique RGPD/rétention et DPA des hébergeurs doivent être validés par le responsable métier/juridique.
