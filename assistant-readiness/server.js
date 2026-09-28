import http from "node:http";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { extname, join, dirname } from "node:path";
import { randomUUID } from "node:crypto";

const PORT = process.env.PORT || 3000;
const SECRET = process.env.DASHBOARD_SECRET || "";
const ROOT = new URL(".", import.meta.url).pathname;
const STORE = process.env.READINESS_STORE || join(ROOT, "data", "projects.json");
const UPLOAD_DIR = process.env.READINESS_UPLOAD_DIR || join(ROOT, "data", "uploads");

const CATEGORIES = [
  ["Accès / site", /accès|badge|zone|site|circulation|coactivité|accueil/i],
  ["Travaux préparatoires", /travaux|génie civil|réservation|support|protection|réserve/i],
  ["Électricité / utilités", /électricité|alimentation|air comprimé|eau|gaz|utilité|réseau/i],
  ["Interfaces", /interface|convoyeur|machine amont|machine aval|raccordement|automatisme/i],
  ["Documents / autorisations", /plan|document|autorisation|HSE|PV|FAT|SAT|certificat|dossier/i],
  ["Fournisseurs / intervenants", /fournisseur|sous-traitant|intervenant|prestataire|entreprise tierce/i],
  ["Logistique", /livraison|transport|manutention|levage|déchargement|stockage|matériel/i],
  ["Disponibilité / décision", /interlocuteur|disponible|validation|décision|arbitrage|responsable/i]
];

async function ensureStore(){
  await mkdir(dirname(STORE), {recursive:true});
  await mkdir(UPLOAD_DIR, {recursive:true});
  try { await readFile(STORE,"utf8"); } catch { await writeFile(STORE,"[]","utf8"); }
}
async function load(){ await ensureStore(); return JSON.parse(await readFile(STORE,"utf8")); }
async function save(items){ await ensureStore(); await writeFile(STORE,JSON.stringify(items,null,2),"utf8"); }
function send(res,status,data,type){ type=type||"application/json"; res.writeHead(status,{"Content-Type":type+"; charset=utf-8","Cache-Control":"no-store"}); res.end(type==="application/json"?JSON.stringify(data):data); }
function authorized(req){ return !SECRET || req.headers["x-dashboard-secret"]===SECRET; }
async function body(req){ let raw=""; for await(const chunk of req) raw+=chunk; return raw?JSON.parse(raw):{}; }
function sourceSummary(text){ const t=normalizeText(text); return {characters:t.length, lines:t?t.split(/\\n/).length:0, words:t?t.split(/\\s+/).length:0}; }
function prepareFollowups(points){ return points.map(function(p){ return {categorie:p.categorie, destinataire:p.responsable, objet:"Point à confirmer : "+p.categorie, demande:p.action, preuve_attendue:p.preuve_attendue, statut:"Brouillon à valider avec Hervé"}; }); }
function normalizeText(x){ return String(x||"").replace(/\r/g,"").trim(); }
function classify(text){ return CATEGORIES.filter(function(x){return x[1].test(text);}).map(function(x){return x[0];}); }
function findMilestone(text){ const m=text.match(/(?:SAT|mise en service|installation|intervention|réception|jalon)[^\n.!?]{0,100}/i); return m?m[0].trim():"Jalon non précisé"; }
function extractDate(text){ const m=text.match(/\b(?:[0-3]?\d)[\/-](?:0?[1-9]|1[0-2])[\/-](?:20\d{2})\b/); return m?m[0]:""; }

function analyze(text,meta){
  meta=meta||{}; const t=normalizeText(text); const categories=classify(t); const points=[];
  const templates=[
    ["Accès / site","Confirmer l'accès du personnel, des véhicules et de la zone d'intervention.","confirmation récente ou preuve d'accès"],
    ["Travaux préparatoires","Confirmer les travaux nécessaires et leur état réel avant l'intervention.","confirmation datée, photo ou document adapté"],
    ["Électricité / utilités","Confirmer la disponibilité effective des énergies et utilités nécessaires.","confirmation récente et caractéristique utile"],
    ["Interfaces","Contrôler les interfaces avec les équipements existants et les responsables associés.","validation/document d'interface ou confirmation responsable"],
    ["Documents / autorisations","Vérifier les documents, versions et autorisations nécessaires.","document ou validation identifiable"],
    ["Fournisseurs / intervenants","Relancer les intervenants concernés et obtenir leur échéance.","réponse datée avec responsable et échéance"],
    ["Logistique","Confirmer livraison, manutention, levage et moyens nécessaires.","confirmation logistique"],
    ["Disponibilité / décision","Identifier l'interlocuteur disponible et toute décision nécessaire.","nom/rôle, disponibilité ou validation"]
  ];
  templates.forEach(function(x){
    if(categories.includes(x[0])) points.push({
      id:randomUUID(), categorie:x[0], statut:"À vérifier", priorite:"Haute",
      action:x[1], preuve_attendue:x[2], responsable:"À identifier", echeance:"À préciser",
      motif:"Le texte mentionne ce sujet, mais ne fournit pas assez d'éléments pour le déclarer sécurisé."
    });
  });
  if(!points.length) points.push({
    id:randomUUID(), categorie:"Qualification", statut:"À valider", priorite:"Haute",
    action:"Identifier le jalon, les prérequis ouverts et les responsables à poursuivre.",
    preuve_attendue:"liste des points avec responsable, échéance et preuve attendue",
    responsable:"Hervé / client", echeance:"À préciser",
    motif:"Le contenu fourni ne permet pas encore de normaliser un périmètre Readiness."
  });
  return {
    client:meta.client||"Client non renseigné", projet:meta.projet||"Projet non renseigné",
    jalon:findMilestone(t), date_jalon:extractDate(t), resume:t.slice(0,700),
    faits:[t?"Demande ou contenu reçu.":"Aucun contenu reçu.",categories.length?"Catégories détectées : "+categories.join(", ")+".":"Aucune catégorie Readiness certaine détectée."],
    inconnus:["Responsable de chaque point","Échéance de chaque action","Preuve attendue pour fermer chaque point","Décisions ou arbitrages restant au client"],
    points:points,
    prochaine_action:"Compléter les responsables, échéances et preuves des points ouverts, puis lancer les premières relances autorisées.",
    escalade:points.length+" point(s) nécessitent une vérification avant de considérer le jalon sécurisé.",
    validation_humaine_requise:true, confiance:categories.length?"À vérifier":"Insuffisant"
  };
}
function normalizePoint(p){
  return Object.assign({
    id:randomUUID(), statut:"À vérifier", priorite:"Haute",
    action:"Action à définir", preuve_attendue:"Preuve à définir",
    responsable:"À identifier", echeance:"À préciser",
    motif:""
  }, p);
}
function dossierFromAnalysis(a){
  return {
    id:randomUUID(), client:a.client, projet:a.projet, jalon:a.jalon, date_jalon:a.date_jalon,
    priorite:"Haute", etat:"À valider", progression:0, points:a.points.map(normalizePoint),
    prochaine_action:a.prochaine_action, blocage:"Vérifications à effectuer", relances:a.relances||[], preuves_a_controler:a.points.map(function(p){return {point_id:p.id,preuve_attendue:p.preuve_attendue,statut:"À contrôler"};}),
    validation_humaine_requise:true, created_at:new Date().toISOString(), updated_at:new Date().toISOString()
  };
}
async function handle(req,res){
  const u=new URL(req.url,"http://localhost");
  if(u.pathname==="/health") return send(res,200,{ok:true,service:"assistant-readiness",external_ai:false});
  if(u.pathname.startsWith("/api/")){
    if(!authorized(req)) return send(res,401,{error:"Clé cockpit requise."});
    if(req.method==="GET" && u.pathname==="/api/dashboard") return send(res,200,{items:await load(),persistent:true,secret_protected:Boolean(SECRET)});
    if(req.method==="POST" && u.pathname==="/api/analyze"){
      const b=await body(req); const a=analyze(b.text,{client:b.client,projet:b.projet}); a.source=sourceSummary(b.text); a.relances=prepareFollowups(a.points); const dossier=dossierFromAnalysis(a); dossier.relances=a.relances;
      const items=await load(); items.unshift(dossier); await save(items); return send(res,200,{analysis:a,dossier:dossier});
    }
    const m=u.pathname.match(/^\/api\/dashboard\/([^/]+)$/);
    if(req.method==="PATCH" && m){
      const b=await body(req), items=await load(), i=items.findIndex(function(x){return x.id===m[1];});
      if(i<0) return send(res,404,{error:"Dossier introuvable."});
      if(b.etat==="Terminé" && items[i].validation_humaine_requise) return send(res,409,{error:"Ce dossier reste À valider tant que la validation humaine est requise."});
      if(b.validation_humaine_requise===false && b.confirmation!=="Hervé") return send(res,409,{error:"La validation humaine doit être confirmée par Hervé."});
      ["etat","priorite","prochaine_action","blocage"].forEach(function(k){if(b[k]!==undefined) items[i][k]=b[k];});
      if(b.validation_humaine_requise===false && b.confirmation==="Hervé") items[i].validation_humaine_requise=false;
      if(Array.isArray(items[i].points)) items[i].progression=Math.round(items[i].points.filter(function(p){return p.statut==="Clos";}).length/items[i].points.length*100);
      items[i].updated_at=new Date().toISOString(); await save(items); return send(res,200,{item:items[i]});
    }
    const pm=u.pathname.match(/^\/api\/dashboard\/([^/]+)\/points\/([^/]+)$/);
    if(req.method==="PATCH" && pm){
      const b=await body(req), items=await load(), i=items.findIndex(function(x){return x.id===pm[1];});
      if(i<0) return send(res,404,{error:"Dossier introuvable."});
      const p=items[i].points.find(function(x){return x.id===pm[2];});
      if(!p) return send(res,404,{error:"Point introuvable."});
      ["statut","priorite","action","preuve_attendue","responsable","echeance","motif","preuve_recue","preuve_date","preuve_controle","preuve_commentaire"].forEach(function(k){if(b[k]!==undefined)p[k]=b[k];});
      items[i].progression=Math.round(items[i].points.filter(function(x){return x.statut==="Clos";}).length/items[i].points.length*100);
      const blocked=items[i].points.filter(function(x){return x.statut==="Bloqué";});
      items[i].blocage=blocked.length?blocked.map(function(x){return x.categorie+": "+x.motif;}).join(" | "):"";
      items[i].updated_at=new Date().toISOString(); await save(items); return send(res,200,{item:items[i],point:p});
    }
    if(req.method==="GET" && pm){
      const items=await load(), d=items.find(function(x){return x.id===pm[1];});
      if(!d) return send(res,404,{error:"Dossier introuvable."});
      const p=d.points.find(function(x){return x.id===pm[2];});
      return p?send(res,200,{point:p}):send(res,404,{error:"Point introuvable."});
    }
    if(req.method==="DELETE" && u.pathname==="/api/dashboard"){
      if(u.searchParams.get("confirm")!=="oui") return send(res,400,{error:"Confirmation requise."});
      await save([]); return send(res,200,{items:[]});
    }
    return send(res,404,{error:"Route inconnue."});
  }
  let file=u.pathname==="/"?"/index.html":u.pathname;
  if(file.includes("..")) return send(res,400,{error:"Chemin invalide."});
  try{
    const data=await readFile(join(ROOT,"public",file));
    const types={".html":"text/html",".js":"text/javascript",".css":"text/css",".json":"application/json"};
    return send(res,200,data.toString(),types[extname(file)]||"text/plain");
  }catch(e){ return send(res,404,"Not found","text/plain"); }
}
ensureStore().then(function(){http.createServer(function(req,res){handle(req,res).catch(function(e){send(res,500,{error:e.message});});}).listen(PORT,function(){console.log("Readiness assistant listening on "+PORT);});});
