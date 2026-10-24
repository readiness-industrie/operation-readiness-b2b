(function () {
  var MQ = "(max-width: 800px)";

  function isMobile() {
    return window.matchMedia(MQ).matches;
  }

  function bindMenu(btn, panel, header) {
    if (!btn || !panel) return null;
    var hdr =
      header ||
      btn.closest("header") ||
      btn.closest(".site-header");
    function setOpen(open) {
      panel.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
      if (hdr) hdr.classList.toggle("menu-open", open);
    }
    function toggle() {
      setOpen(!panel.classList.contains("open"));
    }
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      toggle();
    });
    panel.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        setOpen(false);
      });
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setOpen(false);
    });
    return { setOpen: setOpen, toggle: toggle };
  }

  function wireBrandToggle(header, nav) {
    if (!nav) return;
    var brand = header.querySelector(".identity:not(.identity-footer), .logo");
    if (!brand || brand.dataset.riNavToggleBound) return;
    brand.dataset.riNavToggleBound = "1";
    brand.setAttribute("data-ri-nav-toggle", "");
    brand.addEventListener("click", function (e) {
      if (!isMobile()) return;
      e.preventDefault();
      nav.toggle();
    });
  }

  function initHeader(header) {
    if (!header || header.dataset.riNavInit) return;
    header.dataset.riNavInit = "1";
    var btn =
      header.querySelector(".mobileMenu") ||
      header.querySelector(".advMobileMenu");
    var panel =
      header.querySelector(".mobileLinks") ||
      header.querySelector(".advMobileLinks");
    var nav = bindMenu(btn, panel, header);
    wireBrandToggle(header, nav);
  }

  function injectSiteNav() {
    var body = document.body;
    if (!body || !body.hasAttribute("data-ri-site-nav")) return;
    if (document.querySelector(".ri-injected-header")) return;

    var header = document.createElement("header");
    header.className = "site-header ri-injected-header";
    header.setAttribute("data-header", "");
    header.innerHTML =
      '<div class="container header-inner">' +
      '<a class="identity" href="index.html" aria-label="Readiness Industry">' +
      '<span class="identity-mark" aria-hidden="true"><span></span><span></span><span></span></span>' +
      "<span><strong>Readiness Industry</strong><small>PME industrielles</small></span></a>" +
      '<nav class="advDesktopNav" aria-label="Navigation principale">' +
      '<a href="index.html">Accueil</a>' +
      '<a href="renfort-administratif.html">Renfort ADV</a>' +
      '<a href="index.html#contact">Recevoir mon point de situation (48 h)</a>' +
      "</nav>" +
      '<button class="advMobileMenu" type="button" aria-expanded="false" aria-label="Ouvrir le menu">' +
      '<span class="menu-bars" aria-hidden="true"><span></span><span></span><span></span></span>' +
      "</button>" +
      '<div class="advMobileLinks">' +
      '<a href="index.html">Accueil</a>' +
      '<a href="renfort-administratif.html">Renfort ADV (commandes, livraisons, factures)</a>' +
      '<a href="index.html#contact">Recevoir mon point de situation (48 h)</a>' +
      '<a href="mentions-legales.html">Mentions légales</a>' +
      "</div></div>";

    var skip = document.querySelector(".skip-link");
    if (skip && skip.parentNode) {
      skip.parentNode.insertBefore(header, skip.nextSibling);
    } else {
      body.insertBefore(header, body.firstChild);
    }
    initHeader(header);
  }

  document.querySelectorAll("header, .site-header").forEach(initHeader);

  var navToggle = document.querySelector(".nav-toggle");
  var mainNav = document.querySelector(".site-header .main-nav");
  if (navToggle && mainNav) {
    bindMenu(navToggle, mainNav, navToggle.closest(".site-header"));
  }

  injectSiteNav();
})();
