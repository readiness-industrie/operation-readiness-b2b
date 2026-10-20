/* Mesure d'audience GA4 avec consentement (CNIL) – partagé par toutes les pages */
(function () {
  "use strict";
  var ID = "G-CXBR9QTFXS", KEY = "readiness_analytics_consent_v1";
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag("consent", "default", {
    analytics_storage: "denied",
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied"
  });
  if (window.__riConsent) return;
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function load() {
    if (window.__readinessAnalyticsLoaded) return;
    window.__readinessAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("consent", "update", { analytics_storage: "granted" });
    window.gtag("config", ID, { allow_google_signals: false, allow_ad_personalization_signals: false });
    var s = document.createElement("script");
    s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
    document.head.appendChild(s);
  }
  function clearCookies() {
    if (typeof window.gtag === "function") window.gtag("consent", "update", { analytics_storage: "denied" });
    document.cookie.split(";").forEach(function (c) {
      var n = c.split("=")[0].trim();
      if (n === "_ga" || n.indexOf("_ga_") === 0) {
        document.cookie = n + "=; Max-Age=0; path=/; SameSite=Lax";
        document.cookie = n + "=; Max-Age=0; path=/; domain=." + location.hostname + "; SameSite=Lax";
      }
    });
  }
  window.riTrack = function (name, params) {
    if (get() === "granted" && typeof window.gtag === "function") window.gtag("event", name, params || {});
  };
  var box;
  function build() {
    var css = document.createElement("style");
    css.textContent =
      ".ri-cc{position:fixed;z-index:2147483000;left:12px;right:12px;bottom:12px;max-width:560px;margin:0 auto;background:#fff;color:#10202b;border:1px solid #d9dee2;border-radius:16px;box-shadow:0 18px 50px rgba(16,32,43,.28);padding:18px 18px 16px;font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}" +
      ".ri-cc[hidden]{display:none}.ri-cc b{display:block;font-size:16px;margin-bottom:4px}.ri-cc p{margin:0 0 14px;color:#4a5a66}.ri-cc a{color:#0f5f57;font-weight:600}" +
      ".ri-cc-a{display:grid;grid-template-columns:1fr 1fr;gap:10px}.ri-cc button{min-height:46px;border-radius:10px;font:600 15px/1 inherit;font-family:inherit;cursor:pointer;border:2px solid #10202b;background:#fff;color:#10202b}.ri-cc button.ri-ok{background:#10202b;color:#fff}" +
      ".ri-cc button:focus-visible{outline:3px solid #2a9d8f;outline-offset:2px}.ri-cc-link{background:none;border:0;padding:0;color:inherit;text-decoration:underline;cursor:pointer;font:inherit}";
    document.head.appendChild(css);
    box = document.createElement("div");
    box.className = "ri-cc"; box.hidden = true;
    box.setAttribute("role", "dialog"); box.setAttribute("aria-label", "Mesure d'audience");
    box.innerHTML = '<b>Nous aidez-vous à améliorer ce site ?</b><p>Avec votre accord, nous mesurons la fréquentation de façon anonyme (Google Analytics). Pas de publicité, pas de revente. Vous pouvez changer d\'avis à tout moment via « Cookies » en bas de page. <a href="mentions-legales.html">En savoir plus</a></p>' +
      '<div class="ri-cc-a"><button type="button" class="ri-no">Refuser</button><button type="button" class="ri-ok">Accepter</button></div>';
    document.body.appendChild(box);
    box.querySelector(".ri-ok").addEventListener("click", function () { set("granted"); box.hidden = true; load(); });
    box.querySelector(".ri-no").addEventListener("click", function () { set("denied"); clearCookies(); box.hidden = true; });
    var open = function () { box.hidden = false; };
    Array.prototype.forEach.call(document.querySelectorAll("[data-manage-analytics]"), function (b) { b.addEventListener("click", open); });
    var foot = document.querySelector("footer");
    if (foot && !foot.querySelector("[data-manage-analytics]")) {
      var l = document.createElement("button"); l.type = "button"; l.className = "ri-cc-link"; l.textContent = "Cookies";
      l.setAttribute("data-manage-analytics", ""); l.addEventListener("click", open);
      var p = document.createElement("p"); p.style.margin = "8px 0 0"; p.appendChild(l); foot.appendChild(p);
    }
    window.__riConsent = { open: open };
    // Vidéo (page renfort) : un événement au premier lancement
    Array.prototype.forEach.call(document.querySelectorAll("video"), function (v) {
      v.addEventListener("play", function () {
        window.riTrack("video_start", { video_title: (v.currentSrc || "").split("/").pop(), page_path: location.pathname });
      }, { once: true });
    });
    document.addEventListener("click", function (ev) {
      var el = ev.target && ev.target.closest && ev.target.closest(".ri-cta-point-48h, [data-ri-track=\"demande_point_48h\"]");
      if (!el) return;
      window.riTrack("demande_point_48h", {
        page_path: location.pathname,
        link_url: el.getAttribute("href") || "",
        link_text: (el.textContent || "").trim().slice(0, 120)
      });
    });
    var c = get();
    if (c === "granted") load(); else if (c !== "denied") open();
  }
  window.__riConsent = { open: function () {} };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build); else build();
})();
