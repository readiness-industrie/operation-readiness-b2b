// Référentiel métier Readiness Industry V1
// Ce fichier est la source métier locale de l'assistant. Il ne remplace pas les décisions humaines.

export const READINESS_OFFER = {
  name: "Readiness Industry",
  promise: "Poursuivre à distance les points ouverts qui conditionnent un jalon industriel, jusqu'à confirmation, preuve, clôture ou arbitrage client.",
  role: "service humain opéré, assisté par un moteur local",
  clientKeeps: ["décisions techniques","arbitrages","HSE","budget","mobilisation des équipes","validation finale"],
  operation: [
    "Cadrer le jalon, sa date et le périmètre",
    "Identifier les points ouverts et leurs dépendances",
    "Identifier responsable, échéance et preuve attendue",
    "Poursuivre les interlocuteurs autorisés",
    "Enregistrer les réponses sans les confondre avec une confirmation",
    "Collecter et contrôler les preuves disponibles",
    "Faire ressortir les blocages et leur impact",
    "Escalader ce qui nécessite une décision",
    "Revérifier les points critiques à l'approche du jalon",
    "Clôturer uniquement selon le critère défini avec le client"
  ],
  categories: [
    {name:"Accès / site",examples:["accès","badge","zone","site","circulation","coactivité","accueil"],proof:"confirmation récente ou preuve d'accès"},
    {name:"Travaux préparatoires",examples:["travaux","génie civil","réservation","support","protection","réserve"],proof:"confirmation datée, photo ou document adapté"},
    {name:"Électricité / utilités",examples:["électricité","alimentation","air comprimé","eau","gaz","utilité","réseau"],proof:"confirmation récente et caractéristique utile"},
    {name:"Interfaces",examples:["interface","convoyeur","machine amont","machine aval","raccordement","automatisme"],proof:"validation ou document d'interface"},
    {name:"Documents / autorisations",examples:["plan","document","autorisation","HSE","PV","FAT","SAT","certificat","dossier"],proof:"document ou validation identifiable"},
    {name:"Fournisseurs / intervenants",examples:["fournisseur","sous-traitant","intervenant","prestataire","entreprise tierce"],proof:"réponse datée avec responsable et échéance"},
    {name:"Logistique",examples:["livraison","transport","manutention","levage","déchargement","stockage","matériel","outillage"],proof:"confirmation logistique"},
    {name:"Disponibilité / décision",examples:["interlocuteur","disponible","validation","décision","arbitrage","responsable"],proof:"nom/rôle, disponibilité ou validation"}
  ],
  milestones:["SAT","FAT","mise en service","installation","réception","intervention"],
  followupCadence:["J-30","J-15","J-7","J-2"],
  states:["À vérifier","À faire","En cours","À valider","Bloqué","Clos"],
  rules:[
    "Une action effectuée n'est pas une réponse obtenue.",
    "Une réponse obtenue n'est pas une confirmation.",
    "Une confirmation n'est comptée que si le critère convenu est satisfait.",
    "Un point critique ne devient pas Clos sans preuve reçue et contrôlée lorsque cette preuve est requise.",
    "Une information absente reste absente.",
    "Aucune date, responsable, preuve ou validation ne doit être inventé.",
    "Les décisions techniques, HSE, budgétaires et arbitrages restent humains.",
    "Le cockpit ne remplace pas le planning du chef de projet."
  ]
};
