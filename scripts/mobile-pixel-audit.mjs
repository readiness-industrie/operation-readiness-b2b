import { chromium, devices } from "playwright";
import fs from "fs";
import path from "path";

const BASE =
  process.env.BASE_URL ||
  "https://readiness-industrie.github.io/operation-readiness-b2b";
const OUT = process.env.OUT_DIR || "/opt/cursor/artifacts/mobile-audit";
const PAGES = [
  "/",
  "/renfort-administratif.html",
  "/premier-echange.html",
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
function add(page, msg, extra = {}) {
  issues.push({ page, msg, ...extra });
}

function slug(p) {
  return p === "/" ? "home" : p.replace(/^\//, "").replace(/\.html$/, "");
}

async function scrollFull(page) {
  await page.evaluate(async () => {
    await new Promise((resolve) => {
      let y = 0;
      const step = () => {
        const max = document.documentElement.scrollHeight;
        y += Math.max(window.innerHeight * 0.85, 320);
        window.scrollTo(0, y);
        if (y >= max - 8) {
          window.scrollTo(0, 0);
          resolve();
          return;
        }
        requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  });
  await page.waitForTimeout(400);
}

async function auditPage(page, pagePath, phase) {
  const url = BASE + (pagePath === "/" ? "/" : pagePath);
  const name = slug(pagePath);

  await page.goto(url, { waitUntil: "networkidle", timeout: 90000 });

  // Cookie banner: accept to unblock bottom UI for rest of test
  const cc = page.locator(".ri-cc");
  if (await cc.isVisible().catch(() => false)) {
    await page.locator(".ri-cc .ri-ok").tap();
    await page.waitForTimeout(300);
  }

  const overflow = await page.evaluate(() => {
    const w = document.documentElement.scrollWidth;
    const vw = window.innerWidth;
    return { scrollWidth: w, innerWidth: vw, overflow: w > vw + 2 };
  });
  if (overflow.overflow) {
    add(pagePath, `Débordement horizontal scrollWidth=${overflow.scrollWidth} vs ${overflow.innerWidth}`);
  }

  const invisibleReveals = await page.evaluate(() => {
    const bad = [];
    document.querySelectorAll(".reveal").forEach((el) => {
      const st = getComputedStyle(el);
      const op = parseFloat(st.opacity);
      if (op < 0.95) {
        bad.push((el.textContent || "").trim().slice(0, 60));
      }
    });
    return bad;
  });
  if (invisibleReveals.length) {
    add(pagePath, `${invisibleReveals.length} bloc(s) .reveal encore invisibles avant scroll`, {
      samples: invisibleReveals.slice(0, 3),
    });
  }

  await scrollFull(page);

  const stillHidden = await page.evaluate(() => {
    let n = 0;
    document.querySelectorAll(".reveal").forEach((el) => {
      const op = parseFloat(getComputedStyle(el).opacity);
      if (op < 0.95) n++;
    });
    return n;
  });
  if (stillHidden) {
    add(pagePath, `${stillHidden} bloc(s) .reveal toujours invisibles après scroll complet`);
  }

  await page.screenshot({
    path: path.join(OUT, `${phase}-${name}-full.png`),
    fullPage: true,
  });

  const menuBtn = page
    .locator(".mobileMenu, .advMobileMenu, .nav-toggle")
    .first();
  if (await menuBtn.isVisible().catch(() => false)) {
    const box = await menuBtn.boundingBox();
    if (box) {
      const cx = box.x + box.width / 2;
      const cy = box.y + box.height / 2;
      const hit = await page.evaluate(
        ({ x, y }) => {
          const btn = document.querySelector(
            ".mobileMenu, .advMobileMenu, .nav-toggle"
          );
          const el = document.elementFromPoint(x, y);
          if (!btn || !el) return { ok: false, top: null };
          const ok = el === btn || btn.contains(el);
          return {
            ok,
            top: {
              tag: el.tagName,
              class: String(el.className || "").slice(0, 80),
            },
          };
        },
        { x: cx, y: cy }
      );

      if (!hit.ok) {
        add(pagePath, `Menu hamburger recouvert au tap (${JSON.stringify(hit.top)})`);
      }
    }

    await menuBtn.tap();
    await page.waitForTimeout(350);

    const open =
      (await page.locator(".mobileLinks.open, .advMobileLinks.open").count()) > 0 ||
      (await page.locator(".site-header.menu-open .main-nav").count()) > 0;

    if (!open) {
      add(pagePath, "Tap menu: panneau non ouvert");
    } else {
      await page.screenshot({
        path: path.join(OUT, `${phase}-${name}-menu-open.png`),
      });
      const firstLink = page
        .locator(".mobileLinks.open a, .advMobileLinks.open a, .site-header.menu-open .main-nav a")
        .first();
      if (await firstLink.count()) {
        const href = await firstLink.getAttribute("href");
        await firstLink.tap();
        await page.waitForTimeout(500);
        if (href?.startsWith("#")) {
          const id = href.slice(1);
          const vis = await page.locator(`#${id}`).isVisible().catch(() => false);
          if (!vis) add(pagePath, `Lien menu ancre ${href} non visible après tap`);
        }
      }
    }
  }
}

async function main() {
  const phase = process.env.PHASE || "live";
  fs.mkdirSync(OUT, { recursive: true });

  const pixel = devices["Pixel 7"];
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    ...pixel,
    hasTouch: true,
    isMobile: true,
  });
  const page = await context.newPage();

  for (const p of PAGES) {
    try {
      await auditPage(page, p, phase);
    } catch (e) {
      add(p, `Erreur audit: ${e.message}`);
    }
  }

  await browser.close();

  const outFile = path.join(OUT, `${phase}-issues.json`);
  fs.writeFileSync(outFile, JSON.stringify(issues, null, 2));
  console.log(JSON.stringify(issues, null, 2));
  process.exit(issues.length ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  process.exit(2);
});
