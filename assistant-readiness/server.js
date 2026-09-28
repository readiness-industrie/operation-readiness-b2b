import http from "node:http";
import { readFile, writeFile, mkdir, unlink } from "node:fs/promises";
import { extname, join, dirname, basename, resolve, sep } from "node:path";
import { createHash, randomUUID, timingSafeEqual } from "node:crypto";
import { READINESS_OFFER } from "./knowledge.js";

const PORT = process.env.PORT || 3000;
const SECRET = (process.env.DASHBOARD_SECRET || "").trim();
const COOKIE_NAME = "readiness_auth";
const LOCKED_API = {error:"Assistant verrouillé : définissez DASHBOARD_SECRET pour l'ouvrir."};
const ROOT = new URL(".", import.meta.url).pathname;
// READINESS_STORE et READINESS_UPLOAD_DIR : sur Render, les pointer sous le même disque persistant (ex. /var/data).
const STORE = process.env.READINESS_STORE || join(ROOT, "data", "projects.json");
const UPLOAD_DIR = process.env.READINESS_UPLOAD_DIR || join(ROOT, "data", "uploads");
const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;

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
function secretConfigured(){ return SECRET.length>0; }
function safeEqual(given,expected){
  if(typeof given!=="string"||typeof expected!=="string") return false;
  const a=Buffer.from(given), b=Buffer.from(expected);
  if(a.length!==b.length) return false;
  return timingSafeEqual(a,b);
}
function authToken(){ return createHash("sha256").update("assistant-readiness.v0\0"+SECRET).digest("hex"); }
function parseCookies(req){
  const header=req.headers.cookie;
  if(typeof header!=="string"||!header) return {};
  const out={};
  header.split(";").forEach(function(part){
    const i=part.indexOf("=");
    if(i<0) return;
    const key=part.slice(0,i).trim();
    let value=part.slice(i+1).trim();
    try{ value=decodeURIComponent(value); }catch(e){}
    out[key]=value;
  });
  return out;
}
function authorized(req){
  if(!secretConfigured()) return false;
  const header=req.headers["x-dashboard-secret"];
  if(typeof header==="string"&&header.length>0&&safeEqual(header,SECRET)) return true;
  const token=parseCookies(req)[COOKIE_NAME];
  return typeof token==="string"&&safeEqual(token,authToken());
}
function cookieSecure(req){
  const proto=req.headers["x-forwarded-proto"];
  if(typeof proto==="string"&&proto.split(",")[0].trim()==="https") return true;
  return Boolean(req.socket&&req.socket.encrypted);
}
function safeNext(value){
  if(typeof value!=="string"||!value.startsWith("/")||value.startsWith("//")||value.includes("\\")||value.includes("\n")||value.includes("\r")) return "/";
  try{
    const parsed=new URL(value,"http://local");
    if(parsed.origin!=="http://local") return "/";
    if(parsed.pathname.startsWith("/api/")||parsed.pathname==="/login"||parsed.pathname==="/health") return "/";
    return parsed.pathname+parsed.search;
  }catch(e){ return "/"; }
}
function escHtml(s){ return String(s).replace(/[&<>"]/g,function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"}[c]; }); }
function gatePage(title,inner){
  return "<!doctype html><html lang=\"fr\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>"+escHtml(title)+"</title><style>body{margin:0;font-family:Inter,system-ui,sans-serif;background:#f4f6f9;color:#172033}main{max-width:440px;margin:10vh auto;background:#fff;border:1px solid #e0e5ec;border-radius:16px;padding:24px}h1{font-size:22px;margin:0 0 8px}p{color:#687386;line-height:1.45}label{display:block;font-weight:700;margin:14px 0 6px}input{width:100%;box-sizing:border-box;padding:11px;border:1px solid #d4dae3;border-radius:11px;font:inherit}button{margin-top:14px;width:100%;border:0;border-radius:12px;padding:12px;font:700 15px inherit;background:#172033;color:#fff;cursor:pointer}.err{color:#b42318;font-weight:700}</style></head><body><main>"+inner+"</main></body></html>";
}
function lockedPage(){ return gatePage("Assistant verrouillé","<h1>Assistant verrouillé</h1><p>Cet outil est interne. Il reste fermé tant que la variable <strong>DASHBOARD_SECRET</strong> n’est pas définie sur le serveur.</p>"); }
function loginPage(next,failed){
  const err=failed?"<p class=\"err\">Mot de passe incorrect.</p>":"";
  return gatePage("Accès interne","<h1>Accès interne</h1><p>Réservé à Readiness Industry. Saisissez le mot de passe du cockpit.</p>"+err+"<form method=\"post\" action=\"/login\"><input type=\"hidden\" name=\"next\" value=\""+escHtml(next)+"\"><label for=\"password\">Mot de passe</label><input id=\"password\" name=\"password\" type=\"password\" autocomplete=\"current-password\" required><button type=\"submit\">Entrer</button></form>");
}
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
function qualifyProspect(text,meta){
  const t=normalizeText(text), signals=[];
  if(/intégrateur|installation|mise en service|commissioning|SAT|FAT|ligne|robot|convoyage|rétrofit/i.test(t)) signals.push("Contexte industriel / installation détecté");
  if(/chef de projet|chargé d'affaires|project manager|coordinateur/i.test(t)) signals.push("Fonction de coordination projet détectée");
  if(/relance|suivi|retard|bloqué|prérequis|préparation|planning|délai|disponibilité/i.test(t)) signals.push("Besoin de coordination ou de suivi détecté");
  const missing=["Nature exacte du besoin","Jalon concerné et date","Nombre de points/intervenants","Périmètre que le prospect souhaite confier"];
  return {
    id:randomUUID(), type:"Prospect", client:meta.client||"Prospect non renseigné", projet:"",
    statut:"À traiter par Hervé", signaux:signals, faits:[t?"Contenu reçu du prospect.":"Aucun contenu reçu."],
    informations_manquantes:missing, qualification:signals.length?"À vérifier":"Insuffisant",
    prochaine_action:"Vérifier le besoin réel et le jalon concerné, puis décider si un échange ou une proposition Readiness est justifié.",
    reponse_proposee:"Bonjour, merci pour votre message. Pour vérifier rapidement si nous pouvons vous aider, pouvez-vous me préciser le jalon concerné, les points actuellement ouverts et ce qui doit être sécurisé avant ce jalon ?",
    validation_humaine_requise:true, created_at:new Date().toISOString(), updated_at:new Date().toISOString()
  };
}
function httpError(status, message){
  const err = new Error(message);
  err.status = status;
  return err;
}
async function readBuffer(req, limit){
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > limit) throw httpError(413, "Fichier trop volumineux (10 Mo maximum).");
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}
function parseMultipartFile(buf, contentType){
  const match = /boundary=(?:"([^"]+)"|([^;\s]+))/i.exec(contentType || "");
  if (!match) throw httpError(400, "Envoi de fichier invalide.");
  const boundary = match[1] || match[2];
  const sep = Buffer.from("--" + boundary);
  let cursor = buf.indexOf(sep);
  if (cursor < 0) throw httpError(400, "Envoi de fichier invalide.");
  let file = null;
  while (cursor >= 0 && cursor < buf.length) {
    let start = cursor + sep.length;
    if (buf[start] === 45 && buf[start + 1] === 45) break;
    if (buf[start] === 13 && buf[start + 1] === 10) start += 2;
    const next = buf.indexOf(sep, start);
    if (next < 0) break;
    let end = next;
    if (end >= 2 && buf[end - 2] === 13 && buf[end - 1] === 10) end -= 2;
    const part = buf.subarray(start, end);
    const splitAt = part.indexOf(Buffer.from("\r\n\r\n"));
    if (splitAt >= 0) {
      const headerText = part.subarray(0, splitAt).toString("utf8");
      const data = part.subarray(splitAt + 4);
      const disp = headerText.split(/\r\n/).find(function(line){ return /^content-disposition:/i.test(line); }) || "";
      const named = /name="([^"]*)"/.exec(disp);
      const namedFile = /filename="([^"]*)"/.exec(disp) || /filename\*=UTF-8''([^;\s]+)/i.exec(disp);
      if (namedFile && (!named || named[1] === "file" || named[1] === "preuve")) {
        let filename = namedFile[1];
        try { filename = decodeURIComponent(filename); } catch (e) {}
        file = {filename: filename, data: data};
      }
    }
    cursor = next;
  }
  if (!file || !file.data.length) throw httpError(400, "Aucun fichier reçu.");
  return file;
}
function sniffProof(buf, filename){
  const ext = extname(String(filename || "")).toLowerCase();
  const allowed = {".pdf":"application/pdf",".png":"image/png",".jpg":"image/jpeg",".jpeg":"image/jpeg",".webp":"image/webp",".gif":"image/gif"};
  const mime = allowed[ext];
  if (!mime) throw httpError(415, "Format non accepté. Déposez un PDF ou une image (PNG, JPEG, WEBP, GIF).");
  const ok = (mime === "application/pdf" && buf.subarray(0, 5).toString("utf8") === "%PDF-")
    || (mime === "image/png" && buf.length >= 8 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47)
    || (mime === "image/jpeg" && buf.length >= 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff)
    || (mime === "image/gif" && (buf.subarray(0, 6).toString("utf8") === "GIF87a" || buf.subarray(0, 6).toString("utf8") === "GIF89a"))
    || (mime === "image/webp" && buf.length >= 12 && buf.subarray(0, 4).toString("utf8") === "RIFF" && buf.subarray(8, 12).toString("utf8") === "WEBP");
  if (!ok) throw httpError(415, "Le fichier ne correspond pas à un PDF ou une image acceptée.");
  return {ext: ext, mime: mime};
}
function safeSegment(id){
  if (!/^[a-zA-Z0-9-]{8,80}$/.test(String(id || ""))) throw httpError(400, "Identifiant invalide.");
  return id;
}
function safeDownloadName(name){
  const base = basename(String(name || "preuve").replace(/\\/g, "/")).replace(/[\r\n"]/g, "").slice(0, 180);
  return base || "preuve";
}
function proofAbsolute(rel){
  const root = resolve(UPLOAD_DIR);
  const abs = resolve(root, String(rel || ""));
  if (abs !== root && !abs.startsWith(root + sep)) throw httpError(400, "Chemin de preuve invalide.");
  return abs;
}
function sendBinary(res, buf, mime, filename){
  const downloadName = safeDownloadName(filename);
  const ascii = downloadName.replace(/[^\x20-\x7E]/g, "_") || "preuve";
  res.writeHead(200, {
    "Content-Type": mime,
    "Content-Length": buf.length,
    "Content-Disposition": "inline; filename=\"" + ascii + "\"; filename*=UTF-8''" + encodeURIComponent(downloadName),
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff"
  });
  res.end(buf);
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
  if(u.pathname==="/health") return send(res,200,{ok:true,service:"assistant-readiness"});
  if(u.pathname==="/login"&&(req.method==="GET"||req.method==="POST")){
    if(!secretConfigured()){
      if(req.method==="GET") return send(res,200,lockedPage(),"text/html");
      return send(res,503,LOCKED_API);
    }
    if(req.method==="GET"){
      if(authorized(req)){ res.writeHead(302,{Location:"/","Cache-Control":"no-store"}); return res.end(); }
      return send(res,200,loginPage(safeNext(u.searchParams.get("next")||"/"),false),"text/html");
    }
    let raw="";
    for await(const chunk of req){ raw+=chunk; if(raw.length>4096) return send(res,413,{error:"Requête trop volumineuse."}); }
    const type=String(req.headers["content-type"]||"");
    let password="", next="/";
    if(type.includes("application/json")){
      try{
        const parsed=raw?JSON.parse(raw):{};
        password=typeof parsed.password==="string"?parsed.password:"";
        next=safeNext(typeof parsed.next==="string"?parsed.next:"/");
      }catch(e){ return send(res,400,{error:"Requête invalide."}); }
    }else{
      const params=new URLSearchParams(raw);
      password=params.get("password")||"";
      next=safeNext(params.get("next")||"/");
    }
    if(!safeEqual(password,SECRET)){
      if(type.includes("application/json")) return send(res,401,{error:"Clé cockpit requise."});
      return send(res,401,loginPage(next,true),"text/html");
    }
    const cookie=[COOKIE_NAME+"="+authToken(),"HttpOnly","SameSite=Lax","Path=/"];
    if(cookieSecure(req)) cookie.push("Secure");
    res.writeHead(303,{Location:next,"Set-Cookie":cookie.join("; "),"Cache-Control":"no-store"});
    return res.end();
  }
  if(u.pathname.startsWith("/api/")){
    if(!secretConfigured()) return send(res,503,LOCKED_API);
    if(!authorized(req)) return send(res,401,{error:"Clé cockpit requise."});
    if(req.method==="GET" && u.pathname==="/api/dashboard"){ const all=await load(); return send(res,200,{items:all.filter(function(x){return x.type!=="Prospect";}),prospects:all.filter(function(x){return x.type==="Prospect";}),persistent:true,secret_protected:Boolean(SECRET),knowledge:READINESS_OFFER}); }
    if(req.method==="POST" && u.pathname==="/api/prospect"){
      const b=await body(req), p=qualifyProspect(b.text,{client:b.client});
      const items=await load(); items.unshift(p); await save(items); return send(res,200,{prospect:p});
    }
    const cv=u.pathname.match(/^\/api\/prospect\/([^/]+)\/convert$/);
    if(req.method==="POST" && cv){
      const b=await body(req), items=await load(), i=items.findIndex(function(x){return x.id===cv[1] && x.type==="Prospect";});
      if(i<0) return send(res,404,{error:"Prospect introuvable."});
      if(b.confirmation!=="Hervé") return send(res,409,{error:"Conversion à confirmer par Hervé."});
      const p=items[i];
      if(p.statut==="Converti en projet") return send(res,409,{error:"Ce prospect est déjà converti en projet."});
      const d={id:randomUUID(),type:"Projet",client:p.client,projet:b.projet||"Projet à préciser",jalon:b.jalon||"Jalon non précisé",date_jalon:b.date_jalon||"",priorite:"Haute",etat:"À valider",progression:0,points:[{id:randomUUID(),categorie:"Qualification",statut:"À valider",priorite:"Haute",action:"Préciser le périmètre Readiness, le jalon et les points ouverts.",preuve_attendue:"périmètre et informations projet confirmés",responsable:"Hervé / client",echeance:"À préciser",motif:"Conversion du prospect en dossier projet."}],prochaine_action:"Cadrer le mandat et récupérer les informations projet nécessaires.",blocage:"Cadrage à réaliser",validation_humaine_requise:true,relances:[],preuves_a_controler:[],created_at:new Date().toISOString(),updated_at:new Date().toISOString()};
      p.statut="Converti en projet"; p.updated_at=new Date().toISOString(); items.unshift(d); await save(items); return send(res,200,{prospect:p,dossier:d});
    }
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
      if(b.validation_humaine_requise===false){ const open=items[i].points.filter(function(p){return p.statut!=="Clos";}); if(open.length) return send(res,409,{error:"Validation impossible : "+open.length+" point(s) ne sont pas Clos."}); }
      ["etat","priorite","prochaine_action","blocage"].forEach(function(k){if(b[k]!==undefined) items[i][k]=b[k];});
      if(b.validation_humaine_requise===false && b.confirmation==="Hervé") items[i].validation_humaine_requise=false;
      if(Array.isArray(items[i].points)) items[i].progression=Math.round(items[i].points.filter(function(p){return p.statut==="Clos";}).length/items[i].points.length*100);
      items[i].updated_at=new Date().toISOString(); await save(items); return send(res,200,{item:items[i]});
    }
    const proof=u.pathname.match(/^\/api\/dashboard\/([^/]+)\/points\/([^/]+)\/preuve$/);
    if((req.method==="POST"||req.method==="GET") && proof){
      let did, pid;
      try { did=safeSegment(proof[1]); pid=safeSegment(proof[2]); }
      catch(e){ return send(res,e.status||400,{error:e.message}); }
      const items=await load();
      const dossier=items.find(function(x){return x.id===did && x.type!=="Prospect";});
      if(!dossier) return send(res,404,{error:"Dossier introuvable."});
      const point=(dossier.points||[]).find(function(x){return x.id===pid;});
      if(!point) return send(res,404,{error:"Point introuvable."});
      if(req.method==="GET"){
        if(!point.preuve_fichier||!point.preuve_fichier.chemin) return send(res,404,{error:"Aucune preuve déposée."});
        try{
          const buf=await readFile(proofAbsolute(point.preuve_fichier.chemin));
          return sendBinary(res,buf,point.preuve_fichier.mime||"application/octet-stream",point.preuve_fichier.nom||"preuve");
        }catch(e){
          if(e.status) return send(res,e.status,{error:e.message});
          return send(res,404,{error:"Fichier de preuve introuvable."});
        }
      }
      if(Number(req.headers["content-length"]||0) > MAX_UPLOAD_BYTES + 65536){
        req.resume();
        return send(res,413,{error:"Fichier trop volumineux (10 Mo maximum)."});
      }
      try{
        const raw=await readBuffer(req, MAX_UPLOAD_BYTES + 65536);
        const file=parseMultipartFile(raw, req.headers["content-type"]);
        if(file.data.length>MAX_UPLOAD_BYTES) throw httpError(413,"Fichier trop volumineux (10 Mo maximum).");
        const kind=sniffProof(file.data, file.filename);
        const id=randomUUID();
        const rel=did+"/"+pid+"/"+id+kind.ext;
        const abs=proofAbsolute(rel);
        await mkdir(dirname(abs),{recursive:true});
        await writeFile(abs, file.data);
        const previous=point.preuve_fichier&&point.preuve_fichier.chemin;
        point.preuve_fichier={id:id,nom:safeDownloadName(file.filename),chemin:rel,mime:kind.mime,taille:file.data.length,depose_le:new Date().toISOString()};
        dossier.updated_at=new Date().toISOString();
        await save(items);
        if(previous && previous!==rel){ try{ await unlink(proofAbsolute(previous)); }catch(e){} }
        return send(res,200,{point:point,preuve_fichier:point.preuve_fichier});
      }catch(e){
        return send(res,e.status||500,{error:e.status?e.message:"Dépôt de la preuve impossible."});
      }
    }
    const pm=u.pathname.match(/^\/api\/dashboard\/([^/]+)\/points\/([^/]+)$/);
    if(req.method==="PATCH" && pm){
      const b=await body(req), items=await load(), i=items.findIndex(function(x){return x.id===pm[1];});
      if(i<0) return send(res,404,{error:"Dossier introuvable."});
      const p=items[i].points.find(function(x){return x.id===pm[2];});
      if(!p) return send(res,404,{error:"Point introuvable."});
      if(b.statut==="Clos" && (!b.preuve_recue || b.preuve_controle!=="Contrôlée")) return send(res,409,{error:"Un point ne peut être Clos qu’avec une preuve reçue et contrôlée."});
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
  if(file==="/index.html"||file==="/dashboard.html"){
    if(!secretConfigured()) return send(res,200,lockedPage(),"text/html");
    if(!authorized(req)) return send(res,200,loginPage(safeNext(u.pathname),false),"text/html");
  }
  try{
    const data=await readFile(join(ROOT,"public",file));
    const types={".html":"text/html",".js":"text/javascript",".css":"text/css",".json":"application/json"};
    return send(res,200,data.toString(),types[extname(file)]||"text/plain");
  }catch(e){ return send(res,404,"Not found","text/plain"); }
}
ensureStore().then(function(){http.createServer(function(req,res){handle(req,res).catch(function(e){send(res,500,{error:e.message});});}).listen(PORT,function(){console.log("Readiness assistant listening on "+PORT);});});
