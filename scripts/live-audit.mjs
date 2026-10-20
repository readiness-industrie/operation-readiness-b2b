import { chromium, devices } from "playwright";

const BASE =
  process.env.BASE_URL ||
  "https://readiness-industrie.github.io/operation-readiness-b2b";
const PAGES = [
  "/",
  "/renfort-administratif.html",
  "/essai-gratuit.html",
  "/mentions-legales.html",
  "/prerequis-mise-en-service-industrielle.html",
  "/preparation-sat-industriel.html",
  "/checklist-preparation-installation-industrielle.html",
  "/prerequis-avant-installation-machine-industrielle.html",
  "/preparation-site-avant-installation-industrielle.html",
  "/coordination-fournisseurs-avant-installation.html",
  "/suivi-prerequis-avant-mise-en-service.html",
  "/points-bloquants-avant-installation-machine.html",
  "/checklist-avant-intervention-industrielle.html",
  "/demo-lecture.html",
];

const issues = [];

function add(severity, page, msg) {
  issues.push({ severity, page, msg });
}

async function auditPage(page, path, label) {
  const url = BASE + (path === "/" ? "/" : path);
  const consoleErrors = [];
  const failed = [];

  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => consoleErrors.push(String(err)));
  page.on("response", (res) => {
    const u = res.url();
    if (res.status() >= 400 && u.includes("operation-readiness-b2b")) {
      failed.push(`${res.status()} ${u}`);
    }
  });

  await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });

  const bodyText = await page.locator("body").innerText();
  if (/â€|Ã©|Ã |â€™/.test(bodyText)) {
    add("encoding", path, "Mojibake détecté dans le texte visible");
  }
  if (/[\u2014\u2013]/.test(bodyText)) {
    add("tirets", path, "Tiret cadratin ou demi-cadratin visible dans le texte");
  }

  const links = await page.locator("a[href]").evaluateAll((els, base) => {
    return els.map((a) => ({ href: a.getAttribute("href"), text: (a.textContent || "").trim().slice(0, 60) }));
  }, BASE);

  for (const { href } of links) {
    if (!href || href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) continue;
    if (href.startsWith("http") && !href.includes("readiness-industrie.github.io") && !href.includes("calendly.com")) continue;
    let target = href;
    if (href.startsWith("#")) {
      const id = href.slice(1);
      const count = await page.locator(`[id="${id.replace(/"/g, "")}"]`).count();
      if (count === 0) add("anchor", path, `Ancre manquante: ${href}`);
      continue;
    }
    if (href.startsWith("./#")) {
      const id = href.slice(2);
      if (path !== "/" && href.includes("#")) {
        /* cross-page anchor checked separately */
      }
    }
    if (href.startsWith("/") || href.includes("operation-readiness-b2b") || !href.startsWith("http")) {
      try {
        const full = href.startsWith("http") ? href : new URL(href, url).href;
        if (!full.includes("readiness-industrie.github.io")) continue;
        const r = await page.request.get(full);
        if (r.status() >= 400) add("link", path, `Lien ${r.status()}: ${href}`);
      } catch (e) {
        add("link", path, `Lien invalide: ${href} (${e.message})`);
      }
    }
  }

  for (const err of consoleErrors) {
    if (/favicon|analytics|third.party/i.test(err)) continue;
    add("console", path, `[${label}] ${err}`);
  }
  for (const f of failed) add("404", path, f);
}

async function testCookies(page) {
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  await page.evaluate(() => localStorage.removeItem("readiness_analytics_consent_v1"));
  await page.reload({ waitUntil: "networkidle" });
  const banner = page.locator(".ri-cc");
  if (!(await banner.isVisible())) add("cookies", "/", "Bandeau cookies non visible au premier chargement");
  await page.locator(".ri-no").click();
  if (await banner.isVisible()) add("cookies", "/", "Refus cookies: bandeau reste visible");
  await page.evaluate(() => localStorage.removeItem("readiness_analytics_consent_v1"));
  await page.reload({ waitUntil: "networkidle" });
  await page.locator(".ri-ok").click();
  if (await banner.isVisible()) add("cookies", "/", "Acceptation cookies: bandeau reste visible");
  await page.goto(BASE + "/mentions-legales.html", { waitUntil: "networkidle" });
  await page.locator('[data-manage-analytics]').first().click();
  if (!(await banner.isVisible())) add("cookies", "/mentions-legales.html", "Gérer mes cookies: bandeau ne s'ouvre pas");
}

async function testFormsNoSubmit(page) {
  await page.route("https://api.web3forms.com/submit", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ success: true }) })
  );

  await page.goto(BASE + "/#contact", { waitUntil: "networkidle" });
  const cf = page.locator("#contact-form");
  if (!(await cf.count())) add("form", "/", "Formulaire #contact-form absent");
  else {
    await cf.locator('[name="nom"]').fill("Test");
    await cf.locator('[name="societe"]').fill("Test SA");
    await cf.locator('[name="email"]').fill("test@example.com");
    await cf.locator('[name="message"]').fill("Test sans envoi");
    await cf.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);
    if (await page.locator("#form-success").isHidden()) add("form", "/", "Soumission contact simulée: pas de succès affiché");
  }

  await page.goto(BASE + "/renfort-administratif.html#contact-adv", { waitUntil: "networkidle" });
  const af = page.locator("#adv-form");
  if (!(await af.count())) add("form", "/renfort-administratif.html", "Formulaire ADV absent");
  else {
    await af.locator('[name="nom"]').fill("Test");
    await af.locator('[name="entreprise"]').fill("Test SA");
    await af.locator('[name="email"]').fill("test@example.com");
    await af.locator('[name="contexte"]').fill("Test");
    await af.locator('button[type="submit"]').click();
    await page.waitForTimeout(500);
  }

  await page.goto(BASE + "/essai-gratuit.html", { waitUntil: "networkidle" });
  await page.locator("#name").fill("Test");
  await page.locator("#company").fill("Test SA");
  await page.locator("#email").fill("test@example.com");
  await page.locator("#consent").check();
  await page.locator("#send").click();
  await page.waitForTimeout(500);
}

async function testAnchorHeaderOverlap(page) {
  const iphone = devices["iPhone 13"];
  await page.setViewportSize(iphone.viewport);
  await page.goto(BASE + "/renfort-administratif.html", { waitUntil: "networkidle" });
  await page.locator(".advMobileMenu").click();
  await page.locator('.advMobileLinks a[href="#tarifs"]').click();
  await page.waitForTimeout(600);
  const overlap = await page.evaluate(() => {
    const hdr = document.querySelector(".site-header");
    const h2 = document.querySelector("#tarifs h2");
    if (!hdr || !h2) return true;
    const hb = hdr.getBoundingClientRect().bottom;
    const t = h2.getBoundingClientRect().top;
    return t < hb + 4;
  });
  if (overlap) {
    add("layout", "/renfort-administratif.html#tarifs", "Titre Tarifs masqué sous l'en-tête fixe (ancre mobile)");
  }
  await page.goto(BASE + "/#tarifs", { waitUntil: "networkidle" });
  await page.waitForTimeout(400);
  const homeOverlap = await page.evaluate(() => {
    const hdr = document.querySelector("header");
    const sec = document.getElementById("tarifs");
    const h = sec && (sec.querySelector("h2") || sec.querySelector("h3"));
    if (!hdr || !h) return false;
    return h.getBoundingClientRect().top < hdr.getBoundingClientRect().bottom + 4;
  });
  if (homeOverlap) {
    add("layout", "/#tarifs", "Titre tarifs accueil masqué sous l'en-tête (ancre mobile)");
  }
}

async function testMobileMenu(page) {
  const iphone = devices["iPhone 13"];
  await page.setViewportSize(iphone.viewport);
  await page.goto(BASE + "/", { waitUntil: "networkidle" });
  const menu = page.locator(".mobileMenu");
  if (await menu.isVisible()) {
    await menu.click();
    if (!(await page.locator(".mobileLinks.open").count())) add("menu", "/", "Menu mobile accueil ne s'ouvre pas");
  }
  await page.goto(BASE + "/renfort-administratif.html", { waitUntil: "networkidle" });
  const am = page.locator(".advMobileMenu");
  if (await am.isVisible()) {
    await am.click();
    if (!(await page.locator(".advMobileLinks.open").count())) add("menu", "/renfort-administratif.html", "Menu mobile ADV ne s'ouvre pas");
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  for (const p of PAGES) await auditPage(page, p, "desktop");

  await testCookies(page);
  await testFormsNoSubmit(page);
  await testMobileMenu(page);
  await testAnchorHeaderOverlap(page);

  const mobileCtx = await browser.newContext({ ...devices["iPhone 13"] });
  const mp = await mobileCtx.newPage();
  for (const p of ["/", "/renfort-administratif.html", "/essai-gratuit.html"]) {
    await auditPage(mp, p, "mobile");
  }

  await browser.close();

  const uniq = new Map();
  for (const i of issues) uniq.set(`${i.severity}|${i.page}|${i.msg}`, i);
  console.log(JSON.stringify([...uniq.values()], null, 2));
  process.exit(uniq.size ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
