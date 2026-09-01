/*
 * Données entièrement fictives pour la démonstration.
 * Le rendu et la logique d'interface se trouvent dans app.js.
 */
window.SIMULATION_DATA = {
  title: "Démarrage simulé d'une prestation opérationnelle",
  disclaimer: "Scénario fictif. Aucune référence à un client réel.",
  openingDay: -3,
  days: [
    { day: -14, label: "Cadrage du démarrage" },
    { day: -13, label: "Périmètre et planning" },
    { day: -12, label: "Périmètre fermé" },
    { day: -11, label: "Ressources et accès" },
    { day: -10, label: "Planning confirmé" },
    { day: -9, label: "Documentation demandée" },
    { day: -8, label: "Premiers éléments reçus" },
    { day: -7, label: "Transfert de connaissances" },
    { day: -6, label: "Données incomplètes" },
    { day: -5, label: "Accès encore ouverts" },
    { day: -4, label: "Dépendance externe" },
    { day: -3, label: "État actuel du dossier" },
    { day: -2, label: "Décisions encore ouvertes" },
    { day: -1, label: "Une décision obtenue" },
    { day: 0, label: "Jour de lancement" }
  ],
  statusMeta: {
    launch: { label: "À obtenir", className: "status-launch" },
    progress: { label: "À obtenir", className: "status-progress" },
    followup: { label: "À obtenir", className: "status-followup" },
    received: { label: "Reçu", className: "status-received" },
    incomplete: { label: "Incomplet", className: "status-incomplete" },
    contradictory: { label: "Non conforme", className: "status-contradictory" },
    validate: { label: "À valider", className: "status-validate" },
    blocked: { label: "Bloquant", className: "status-blocked" },
    decision: { label: "Bloquant", className: "status-decision" },
    closed: { label: "Fermé", className: "status-closed" }
  },
  prerequisites: [
    {
      id: "PR-01",
      title: "Périmètre de la prestation validé",
      responsible: "Chef de projet donneur d'ordre",
      company: "Équipe projet simulée",
      primary: "Chef de projet",
      backup: "Directeur de projet",
      channel: "Compte rendu écrit",
      due: "J-12",
      proof: "Périmètre signé ou confirmé par écrit",
      criticality: "Haute",
      escalation: "Directeur de projet si le périmètre n'est pas confirmé avant J-12",
      impact: "Le démarrage ne peut pas être cadré sans périmètre commun.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "progress",
          info: "Le cadrage liste les activités incluses et exclues. La confirmation écrite n'est pas encore reçue.",
          source: "Réunion de cadrage simulée",
          action: "Périmètre proposé",
          missing: "Confirmation écrite du périmètre",
          nextAction: "Obtenir la confirmation écrite",
          nextDate: "J-13"
        },
        {
          day: -12,
          status: "closed",
          info: "Le périmètre a été confirmé par écrit. Activités incluses et exclues sont alignées.",
          source: "Compte rendu validé simulé",
          action: "Critère de fermeture satisfait",
          missing: "Rien. Le critère de fermeture est satisfait.",
          nextAction: "Aucune. Point fermé.",
          nextDate: "Sans objet"
        }
      ]
    },
    {
      id: "PR-02",
      title: "Planning de démarrage confirmé",
      responsible: "Chef de projet donneur d'ordre",
      company: "Équipe projet simulée",
      primary: "Chef de projet",
      backup: "Planificateur",
      channel: "E-mail",
      due: "J-10",
      proof: "Date de démarrage et jalons confirmés par les deux parties",
      criticality: "Haute",
      escalation: "Directeur de projet si les dates divergent encore à J-10",
      impact: "Ressources et accès ne peuvent pas être verrouillés sans date commune.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "launch",
          info: "Une fenêtre de démarrage est évoquée, sans date commune confirmée.",
          source: "Cadrage initial simulé",
          action: "Point créé",
          missing: "Date de démarrage et jalons confirmés",
          nextAction: "Demander la confirmation des dates",
          nextDate: "J-12"
        },
        {
          day: -13,
          status: "contradictory",
          info: "Le site indique un lundi. Le prestataire indique le mercredi suivant.",
          source: "Deux e-mails simulés",
          action: "Écart de dates tracé",
          missing: "Une date commune de démarrage",
          nextAction: "Faire confirmer un calendrier unique",
          nextDate: "J-11"
        },
        {
          day: -10,
          status: "closed",
          info: "Les deux parties ont confirmé la même date de démarrage et les jalons associés.",
          source: "Fil d'e-mail commun simulé",
          action: "Critère de fermeture satisfait",
          missing: "Rien. Le critère de fermeture est satisfait.",
          nextAction: "Aucune. Point fermé.",
          nextDate: "Sans objet"
        }
      ]
    },
    {
      id: "PR-03",
      title: "Ressources nécessaires disponibles",
      responsible: "Responsable d'équipe prestataire",
      company: "Prestataire simulé",
      primary: "Responsable d'équipe",
      backup: "Responsable de site prestataire",
      channel: "E-mail",
      due: "J-4",
      proof: "Noms et disponibilités des personnes prévues sur la période de démarrage",
      criticality: "Haute",
      escalation: "Chef de projet si un poste prévu n'est pas couvert à J-4",
      impact: "Le démarrage peut commencer en sous-effectif.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "launch",
          info: "Les profils nécessaires sont listés. Les noms ne sont pas encore confirmés.",
          source: "Cadrage initial simulé",
          action: "Liste des profils enregistrée",
          missing: "Noms et disponibilités des personnes prévues",
          nextAction: "Demander la composition de l'équipe",
          nextDate: "J-11"
        },
        {
          day: -11,
          status: "progress",
          info: "Quatre personnes sont nommées. Le référent de relais n'est pas encore confirmé.",
          source: "Responsable d'équipe simulé",
          action: "Composition partielle reçue",
          missing: "Confirmation du référent de relais",
          nextAction: "Obtenir le nom du relais",
          nextDate: "J-6"
        },
        {
          day: -5,
          status: "followup",
          info: "Le référent prévu est absent la première semaine. Un relais a été demandé, sans réponse.",
          source: "Journal de suivi simulé",
          action: "Relance envoyée",
          missing: "Nom et disponibilité du relais pour la première semaine",
          nextAction: "Relancer le responsable d'équipe",
          nextDate: "J-4"
        },
        {
          day: -3,
          status: "followup",
          info: "Toujours pas de relais nommé pour la première semaine. L'équipe nominative est sinon complète.",
          source: "Journal de suivi simulé",
          action: "Point encore ouvert",
          missing: "Nom et disponibilité du relais pour la première semaine",
          nextAction: "Obtenir le nom du relais avant le lancement",
          nextDate: "J-1"
        },
        {
          day: 0,
          status: "followup",
          info: "Le relais n'est toujours pas nommé. Le lancement peut se faire, avec une couverture fragile la première semaine.",
          source: "Journal de suivi simulé",
          action: "Risque de couverture maintenu visible",
          missing: "Nom et disponibilité du relais pour la première semaine",
          nextAction: "Trancher si le lancement se fait sans relais nommé",
          nextDate: "J-0"
        }
      ]
    },
    {
      id: "PR-04",
      title: "Accès aux outils et environnements ouverts",
      responsible: "Référent accès / SI",
      company: "Site simulé",
      primary: "Référent accès",
      backup: "Responsable SI adjoint",
      channel: "E-mail",
      due: "J-2",
      proof: "Confirmation nominative des accès ouverts (messagerie, dossiers, environnements prévus)",
      criticality: "Haute",
      escalation: "Chef de projet si des accès nominatifs manquent à J-2",
      impact: "Les personnes présentes ne pourront pas travailler le jour du lancement.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "launch",
          info: "La liste des accès nécessaires est définie. Aucune ouverture nominative n'est encore confirmée.",
          source: "Cadrage initial simulé",
          action: "Liste des accès enregistrée",
          missing: "Ouverture nominative des accès prévus",
          nextAction: "Envoyer la liste nominative au référent accès",
          nextDate: "J-11"
        },
        {
          day: -11,
          status: "progress",
          info: "La liste nominative a été transmise au référent accès.",
          source: "E-mail simulé",
          action: "Demande envoyée",
          missing: "Confirmation d'ouverture des accès",
          nextAction: "Obtenir la confirmation nominative",
          nextDate: "J-6"
        },
        {
          day: -5,
          status: "incomplete",
          info: "Les accès messagerie sont ouverts. Les accès à l'environnement de production ne le sont pas pour deux personnes.",
          source: "Référent accès simulé",
          action: "Réponse partielle reçue",
          missing: "Accès environnement de production pour deux personnes",
          nextAction: "Demander le complément nominatif",
          nextDate: "J-3"
        },
        {
          day: -3,
          status: "incomplete",
          info: "Deux personnes n'ont toujours pas l'accès à l'environnement de production. Les autres accès listés sont ouverts.",
          source: "Référent accès simulé",
          action: "Complément encore attendu",
          missing: "Accès environnement de production pour deux personnes",
          nextAction: "Obtenir les deux accès manquants",
          nextDate: "J-2"
        },
        {
          day: -1,
          status: "received",
          info: "Les deux accès manquants sont annoncés ouverts. Le contrôle nominatif n'est pas encore fait.",
          source: "Référent accès simulé",
          action: "Complément reçu",
          missing: "Contrôle nominatif des deux accès ouverts",
          nextAction: "Vérifier les deux noms dans la confirmation",
          nextDate: "J-0"
        },
        {
          day: 0,
          status: "closed",
          info: "Les deux noms manquants figurent dans la confirmation d'accès. Le critère est satisfait.",
          source: "Journal de contrôle simulé",
          action: "Critère de fermeture satisfait",
          missing: "Rien. Le critère de fermeture est satisfait.",
          nextAction: "Aucune. Point fermé.",
          nextDate: "Sans objet"
        }
      ]
    },
    {
      id: "PR-05",
      title: "Documentation nécessaire reçue",
      responsible: "Référent documentation",
      company: "Site simulé",
      primary: "Référent documentation",
      backup: "Chef de projet",
      channel: "E-mail",
      due: "J-8",
      proof: "Jeu de documents listé au cadrage, réceptionné",
      criticality: "Haute",
      escalation: "Chef de projet si le jeu n'est pas arrivé à J-8",
      impact: "Le contrôle documentaire et le transfert de connaissances ne peuvent pas avancer.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "progress",
          info: "La liste des documents attendus a été transmise.",
          source: "Cadrage initial simulé",
          action: "Demande envoyée",
          missing: "Réception du jeu de documents listé",
          nextAction: "Recevoir le jeu documentaire",
          nextDate: "J-9"
        },
        {
          day: -8,
          status: "received",
          info: "Le jeu de documents est arrivé. Il n'est pas encore contrôlé. Le contrôle est suivi dans le point suivant.",
          source: "Référent documentation simulé",
          action: "Réception tracée",
          missing: "Contrôle du jeu reçu (point documentation contrôlée)",
          nextAction: "Lancer le contrôle documentaire",
          nextDate: "J-6"
        },
        {
          day: -6,
          status: "closed",
          info: "La réception est confirmée. Le contrôle de conformité est porté par le prérequis documentation contrôlée.",
          source: "Journal de suivi simulé",
          action: "Critère de réception satisfait",
          missing: "Rien. Le critère de fermeture est satisfait.",
          nextAction: "Aucune. Point fermé.",
          nextDate: "Sans objet"
        }
      ]
    },
    {
      id: "PR-06",
      title: "Documentation contrôlée",
      responsible: "Référent métier désigné",
      company: "Équipe projet simulée",
      primary: "Référent métier",
      backup: "Chef de projet",
      channel: "E-mail",
      due: "J-3",
      proof: "Contrôle de présence, version et complétude, puis validation métier si prévue",
      criticality: "Haute",
      escalation: "Chef de projet si la validation métier n'est pas faite à J-3",
      impact: "Des consignes obsolètes ou incomplètes peuvent être utilisées au lancement.",
      activeFrom: -8,
      changes: [
        {
          day: -8,
          status: "progress",
          info: "Le jeu est reçu. Le contrôle de présence, version et complétude n'a pas commencé.",
          source: "Journal de suivi simulé",
          action: "Contrôle planifié",
          missing: "Contrôle documentaire du jeu reçu",
          nextAction: "Contrôler présence, version et complétude",
          nextDate: "J-6"
        },
        {
          day: -6,
          status: "incomplete",
          info: "Une procédure listée au cadrage est absente du jeu reçu.",
          source: "Contrôle documentaire simulé",
          action: "Pièce manquante identifiée",
          missing: "Procédure de consignation absente du jeu",
          nextAction: "Demander la procédure manquante",
          nextDate: "J-4"
        },
        {
          day: -4,
          status: "received",
          info: "La procédure manquante est arrivée. Le contrôle de forme est terminé. La validation métier reste à faire.",
          source: "Référent documentation simulé",
          action: "Complément réceptionné",
          missing: "Validation métier du jeu contrôlé",
          nextAction: "Demander la validation au référent métier",
          nextDate: "J-3"
        },
        {
          day: -3,
          status: "validate",
          info: "Présence, versions et dates ont été contrôlées. La validation métier n'est pas faite. Sans cette validation, le point ne peut pas être fermé.",
          source: "Contrôle documentaire simulé",
          action: "Contrôle de forme terminé",
          missing: "Validation métier du référent désigné",
          nextAction: "Obtenir la validation métier",
          nextDate: "J-1",
          attention: true
        },
        {
          day: -1,
          status: "closed",
          info: "Le référent métier a validé le jeu contrôlé. Le critère de fermeture est satisfait.",
          source: "Validation métier simulée",
          action: "Critère de fermeture satisfait",
          missing: "Rien. Le critère de fermeture est satisfait.",
          nextAction: "Aucune. Point fermé.",
          nextDate: "Sans objet"
        }
      ]
    },
    {
      id: "PR-07",
      title: "Données nécessaires au démarrage disponibles",
      responsible: "Référent données",
      company: "Site simulé",
      primary: "Référent données",
      backup: "Responsable SI adjoint",
      channel: "E-mail",
      due: "J-3",
      proof: "Jeu de données prévu au cadrage, complet selon la liste",
      criticality: "Haute",
      escalation: "Chef de projet si le jeu reste incomplet à J-3",
      impact: "Les équipes peuvent démarrer sans le référentiel prévu.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "launch",
          info: "La liste des données attendues est définie. Aucun extrait n'est encore reçu.",
          source: "Cadrage initial simulé",
          action: "Liste enregistrée",
          missing: "Jeu de données listé au cadrage",
          nextAction: "Demander l'extrait prévu",
          nextDate: "J-8"
        },
        {
          day: -8,
          status: "progress",
          info: "La demande d'extrait a été envoyée.",
          source: "E-mail simulé",
          action: "Demande envoyée",
          missing: "Réception de l'extrait complet",
          nextAction: "Recevoir l'extrait",
          nextDate: "J-6"
        },
        {
          day: -6,
          status: "incomplete",
          info: "Un extrait est arrivé. La table des codes de consignation prévue au cadrage n'y figure pas.",
          source: "Référent données simulé",
          action: "Réception partielle tracée",
          missing: "Table des codes de consignation",
          nextAction: "Demander le complément de données",
          nextDate: "J-4"
        },
        {
          day: -3,
          status: "incomplete",
          info: "La table des codes de consignation n'est toujours pas dans l'extrait. Le reste du jeu est utilisable.",
          source: "Journal de suivi simulé",
          action: "Complément encore ouvert",
          missing: "Table des codes de consignation",
          nextAction: "Obtenir la table manquante",
          nextDate: "J-1"
        },
        {
          day: 0,
          status: "incomplete",
          info: "La table manquante n'est pas reçue. Le lancement peut se faire avec un jeu partiel, au prix d'un travail à la main.",
          source: "Journal de suivi simulé",
          action: "Écart maintenu visible",
          missing: "Table des codes de consignation",
          nextAction: "Décider si le lancement se fait avec un jeu partiel",
          nextDate: "J-0"
        }
      ]
    },
    {
      id: "PR-08",
      title: "Préparation et transfert de connaissances réalisé",
      responsible: "Référent métier sortant",
      company: "Site simulé",
      primary: "Référent métier sortant",
      backup: "Chef de projet",
      channel: "Session + compte rendu",
      due: "J-5",
      proof: "Session tenue et compte rendu partagé aux personnes prévues",
      criticality: "Haute",
      escalation: "Chef de projet si la session n'a pas eu lieu à J-5",
      impact: "L'équipe de démarrage arrive sans les consignes orales prévues.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "launch",
          info: "Une session de transfert est prévue. La date n'est pas encore confirmée.",
          source: "Cadrage initial simulé",
          action: "Point créé",
          missing: "Date de session et liste des participants",
          nextAction: "Confirmer la session de transfert",
          nextDate: "J-10"
        },
        {
          day: -10,
          status: "progress",
          info: "La session est calée. Le compte rendu n'existe pas encore.",
          source: "Agenda simulé",
          action: "Date confirmée",
          missing: "Session tenue et compte rendu partagé",
          nextAction: "Tenir la session prévue",
          nextDate: "J-7"
        },
        {
          day: -7,
          status: "received",
          info: "La session a eu lieu. Le compte rendu n'est pas encore partagé.",
          source: "Référent métier sortant simulé",
          action: "Session tenue",
          missing: "Compte rendu partagé aux participants",
          nextAction: "Recevoir et diffuser le compte rendu",
          nextDate: "J-5"
        },
        {
          day: -5,
          status: "closed",
          info: "Le compte rendu a été partagé aux personnes prévues. Le critère de fermeture est satisfait.",
          source: "Journal de suivi simulé",
          action: "Critère de fermeture satisfait",
          missing: "Rien. Le critère de fermeture est satisfait.",
          nextAction: "Aucune. Point fermé.",
          nextDate: "Sans objet"
        }
      ]
    },
    {
      id: "PR-09",
      title: "Actions ouvertes issues des précédents échanges",
      responsible: "Chef de projet donneur d'ordre",
      company: "Équipe projet simulée",
      primary: "Chef de projet",
      backup: "Coordinateur projet",
      channel: "Compte rendu",
      due: "J-2",
      proof: "Toutes les actions listées au dernier compte rendu sont closes ou reportées avec un responsable",
      criticality: "Modérée",
      escalation: "Directeur de projet si plus de deux actions restent sans responsable à J-2",
      impact: "Des sujets déjà vus reviennent le jour du lancement.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "progress",
          info: "Cinq actions étaient ouvertes à l'issue du cadrage.",
          source: "Compte rendu de cadrage simulé",
          action: "Actions enregistrées",
          missing: "Clôture ou report nommé des cinq actions",
          nextAction: "Suivre chaque action jusqu'à clôture ou report",
          nextDate: "J-8"
        },
        {
          day: -8,
          status: "progress",
          info: "Trois actions sont closes. Deux restent ouvertes : modèle de ticket et règle d'escalade interne.",
          source: "Journal de suivi simulé",
          action: "Avancement tracé",
          missing: "Modèle de ticket et règle d'escalade interne",
          nextAction: "Relancer les deux responsables concernés",
          nextDate: "J-4"
        },
        {
          day: -3,
          status: "progress",
          info: "Le modèle de ticket est clos. La règle d'escalade interne n'a toujours pas de version écrite.",
          source: "Journal de suivi simulé",
          action: "Une action encore ouverte",
          missing: "Règle d'escalade interne écrite",
          nextAction: "Obtenir la règle d'escalade écrite",
          nextDate: "J-1"
        },
        {
          day: -1,
          status: "closed",
          info: "La règle d'escalade interne a été écrite et partagée. Plus aucune action du dernier compte rendu n'est ouverte.",
          source: "Chef de projet simulé",
          action: "Critère de fermeture satisfait",
          missing: "Rien. Le critère de fermeture est satisfait.",
          nextAction: "Aucune. Point fermé.",
          nextDate: "Sans objet"
        }
      ]
    },
    {
      id: "PR-10",
      title: "Dépendances externes confirmées",
      responsible: "Coordinateur prestataire externe",
      company: "Prestataire externe simulé",
      primary: "Coordinateur externe",
      backup: "Responsable d'agence",
      channel: "Téléphone + e-mail",
      due: "J-4",
      proof: "Créneau et moyen confirmés par le prestataire externe",
      criticality: "Critique",
      escalation: "Chef de projet dès qu'un décalage est annoncé",
      impact: "Le lancement peut glisser d'une journée, avec équipe déjà mobilisée.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "progress",
          info: "Une intervention externe est prévue sur le créneau de lancement. La confirmation ferme n'est pas reçue.",
          source: "Cadrage initial simulé",
          action: "Dépendance enregistrée",
          missing: "Confirmation ferme du créneau externe",
          nextAction: "Demander la confirmation du prestataire externe",
          nextDate: "J-7"
        },
        {
          day: -7,
          status: "followup",
          info: "Aucune confirmation ferme. Le coordinateur externe dit « normalement c'est bon ».",
          source: "Appel simulé",
          action: "Relance effectuée",
          missing: "Confirmation écrite du créneau",
          nextAction: "Obtenir une confirmation écrite",
          nextDate: "J-4"
        },
        {
          day: -4,
          status: "decision",
          info: "Le prestataire externe annonce qu'il ne peut pas tenir le créneau du matin. Il propose l'après-midi. Cela décale le reste du lancement.",
          source: "Coordinateur externe simulé",
          action: "Écart et impact signalés",
          missing: "Décision : garder le matin, accepter l'après-midi, ou reporter",
          nextAction: "Trancher le créneau de l'intervention externe",
          nextDate: "J-3",
          attention: true
        },
        {
          day: -3,
          status: "decision",
          info: "Toujours pas de décision sur le créneau. L'équipe interne est déjà calée sur le matin.",
          source: "Journal de suivi simulé",
          action: "Blocage maintenu visible",
          missing: "Décision : garder le matin, accepter l'après-midi, ou reporter",
          nextAction: "Trancher le créneau de l'intervention externe",
          nextDate: "J-1",
          attention: true
        },
        {
          day: -1,
          status: "progress",
          info: "Le chef de projet a tranché : l'après-midi est accepté. Une confirmation écrite du prestataire est encore attendue.",
          source: "Décision chef de projet simulée",
          action: "Instruction reçue",
          missing: "Confirmation écrite du créneau après-midi",
          nextAction: "Recevoir la confirmation écrite de l'après-midi",
          nextDate: "J-0"
        },
        {
          day: 0,
          status: "received",
          info: "La confirmation écrite de l'après-midi est arrivée. Le contrôle du créneau reste à faire avant de fermer.",
          source: "Prestataire externe simulé",
          action: "Confirmation reçue",
          missing: "Contrôle du créneau écrit contre l'instruction",
          nextAction: "Contrôler que le créneau écrit est bien l'après-midi",
          nextDate: "J-0"
        }
      ]
    },
    {
      id: "PR-11",
      title: "Blocages ou risques nécessitant une décision",
      responsible: "Chef de projet donneur d'ordre",
      company: "Équipe projet simulée",
      primary: "Chef de projet",
      backup: "Directeur de projet",
      channel: "Point de décision",
      due: "J-2",
      proof: "Décision écrite sur chaque blocage ouvert",
      criticality: "Critique",
      escalation: "Directeur de projet si le blocage n'est pas tranché à J-2",
      impact: "Le lancement part avec un risque connu non tranché.",
      activeFrom: -4,
      isAdded: true,
      changes: [
        {
          day: -4,
          status: "decision",
          info: "L'accès temporaire à la zone de production le matin du lancement n'est pas accordé par l'exploitation. Sans cet accès, une partie du démarrage se fait hors zone.",
          source: "Exploitation simulée",
          action: "Blocage documenté",
          missing: "Décision : obtenir l'accès matin, décaler, ou démarrer hors zone",
          nextAction: "Trancher l'accès zone de production le matin du lancement",
          nextDate: "J-2",
          attention: true
        },
        {
          day: -3,
          status: "decision",
          info: "L'exploitation maintient son refus du matin. Aucune décision projet n'est encore écrite.",
          source: "Journal de suivi simulé",
          action: "Blocage toujours ouvert",
          missing: "Décision écrite sur l'accès zone de production",
          nextAction: "Trancher l'accès zone de production le matin du lancement",
          nextDate: "J-1",
          attention: true
        },
        {
          day: 0,
          status: "decision",
          info: "Toujours pas de décision écrite. Le lancement arrive avec ce blocage ouvert.",
          source: "Journal de suivi simulé",
          action: "Exception encore ouverte",
          missing: "Décision écrite sur l'accès zone de production",
          nextAction: "Trancher avant de lancer, ou lancer en assumant le risque",
          nextDate: "J-0",
          attention: true
        }
      ]
    },
    {
      id: "PR-12",
      title: "Readiness finale avant lancement",
      responsible: "Chef de projet donneur d'ordre",
      company: "Équipe projet simulée",
      primary: "Chef de projet",
      backup: "Directeur de projet",
      channel: "Revue de dossier",
      due: "J-0",
      proof: "Les points bloquants sont fermés ou explicitement assumés par écrit",
      criticality: "Critique",
      escalation: "Directeur de projet si un bloquant reste sans décision au matin du lancement",
      impact: "On lance sans savoir ce qui est réellement prêt.",
      activeFrom: -14,
      changes: [
        {
          day: -14,
          status: "launch",
          info: "La readiness finale ne peut pas être fermée tant que les autres points ne sont pas lisibles.",
          source: "Cadrage initial simulé",
          action: "Point créé, volontairement non fermé",
          missing: "Vue claire des points encore ouverts, manquants et bloquants",
          nextAction: "Laisser les autres points avancer",
          nextDate: "J-3"
        },
        {
          day: -3,
          status: "blocked",
          info: "Le dossier n'est pas prêt à lancer : une validation métier manque, une dépendance externe n'est pas tranchée, un accès zone n'est pas tranché.",
          source: "Revue de dossier simulée",
          action: "Readiness refusée à ce stade",
          missing: "Validation métier, décision créneau externe, décision accès zone",
          nextAction: "Traiter d'abord les points listés dans Votre attention",
          nextDate: "J-1",
          attention: true
        },
        {
          day: -1,
          status: "blocked",
          info: "La validation métier est faite. Le créneau externe a une instruction. L'accès zone de production n'est toujours pas tranché. La readiness finale reste bloquée.",
          source: "Revue de dossier simulée",
          action: "Un bloquant reste ouvert",
          missing: "Décision écrite sur l'accès zone de production",
          nextAction: "Trancher l'accès zone, ou assumer le lancement par écrit",
          nextDate: "J-0",
          attention: true
        },
        {
          day: 0,
          status: "blocked",
          info: "Le lancement est calendairement arrivé. La readiness finale n'est pas fermée : le blocage d'accès zone n'a pas de décision écrite.",
          source: "Revue de dossier simulée",
          action: "Écart rendu visible le jour J",
          missing: "Décision écrite sur l'accès zone de production",
          nextAction: "Décider maintenant : lancer en assumant le risque, ou décaler",
          nextDate: "J-0",
          attention: true
        }
      ]
    }
  ],
  activities: [
    { day: -14, title: "12 points structurés", detail: "Responsables, preuves, échéances et prochaines actions enregistrés." },
    { day: -13, title: "Dates de démarrage divergentes", detail: "Le site et le prestataire n'indiquent pas le même jour." },
    { day: -12, title: "Périmètre fermé", detail: "La confirmation écrite aligne le périmètre inclus et exclu." },
    { day: -11, title: "Équipe partielle", detail: "Quatre noms reçus. Le relais de la première semaine n'est pas nommé." },
    { day: -10, title: "Planning fermé", detail: "Une date commune de démarrage est confirmée." },
    { day: -8, title: "Documentation reçue", detail: "Le jeu est arrivé. Le contrôle n'est pas encore fait." },
    { day: -7, title: "Session de transfert tenue", detail: "Le compte rendu n'est pas encore partagé." },
    { day: -6, title: "Données incomplètes", detail: "La table des codes de consignation manque dans l'extrait." },
    { day: -6, title: "Procédure absente", detail: "Une procédure listée au cadrage n'est pas dans le jeu documentaire." },
    { day: -5, title: "Transfert fermé", detail: "Le compte rendu a été partagé aux personnes prévues." },
    { day: -5, title: "Accès partiels", detail: "Deux personnes n'ont pas l'environnement de production." },
    { day: -4, title: "Créneau externe impossible le matin", detail: "Le prestataire propose l'après-midi. Une décision est nécessaire.", attention: true },
    { day: -4, title: "Accès zone refusé le matin", detail: "L'exploitation refuse l'accès production. Une décision est nécessaire.", attention: true },
    { day: -3, title: "État actuel du dossier", detail: "Quatre points demandent une action maintenant. Le reste se lit sans tout parcourir." },
    { day: -2, title: "Décisions encore ouvertes", detail: "Créneau externe et accès zone n'ont pas d'instruction écrite." },
    { day: -1, title: "Validation métier obtenue", detail: "La documentation contrôlée peut être fermée." },
    { day: -1, title: "Créneau après-midi tranché", detail: "Il reste la confirmation écrite du prestataire externe." },
    { day: 0, title: "Jour de lancement", detail: "La readiness finale n'est pas fermée : l'accès zone n'a pas de décision écrite." }
  ]
};
