/* CTA point de situation 48 h sur les pages SEO (barre mobile + en-tête). */
(function () {
  if (document.body && document.body.dataset.noEssai !== undefined) return;
  var url = "index.html#contact";
  var css = document.createElement("style");
  css.textContent =
    ".ri-essai-btn{display:inline-flex;align-items:center;justify-content:center;background:#26756c;color:#fff!important;font-weight:800;font-size:.78rem;padding:10px 12px;border-radius:999px;text-decoration:none;line-height:1.15;box-shadow:0 6px 18px rgba(38,117,108,.25)}" +
    ".ri-essai-btn:hover{background:#1f5f58}" +
    ".ri-essai-hero{margin:14px 0 6px}" +
    ".ri-essai-bar{display:none}" +
    "@media(max-width:800px){.ri-essai-bar{display:block;position:fixed;left:0;right:0;bottom:0;z-index:9999;padding:10px 14px calc(10px + env(safe-area-inset-bottom));background:rgba(255,255,255,.96);border-top:1px solid #ddd;box-shadow:0 -6px 20px rgba(0,0,0,.08)}.ri-essai-bar .ri-essai-btn{display:flex;width:100%;font-size:.92rem;padding:14px;text-align:center}body{padding-bottom:76px}.ri-essai-head{display:none!important}}";
  document.head.appendChild(css);

  function btn(cls) {
    var a = document.createElement("a");
    a.href = url;
    a.className = "ri-essai-btn " + (cls || "");
    a.textContent = "Recevoir mon diagnostic 48 h";
    return a;
  }
  var header = document.querySelector("header");
  var nav = header && (header.querySelector("nav") || header.querySelector(".container") || header);
  if (nav) {
    nav.appendChild(btn("ri-essai-head"));
  }
  var h1 = document.querySelector("main h1, h1");
  if (h1 && !/essai-gratuit/.test(location.pathname)) {
    var wrap = document.createElement("div");
    wrap.className = "ri-essai-hero";
    wrap.appendChild(btn());
    var lead = h1.nextElementSibling && h1.nextElementSibling.tagName === "P" ? h1.nextElementSibling : h1;
    lead.insertAdjacentElement("afterend", wrap);
  }
  if (!/essai-gratuit/.test(location.pathname)) {
    var bar = document.createElement("div");
    bar.className = "ri-essai-bar";
    bar.appendChild(btn());
    document.body.appendChild(bar);
  }
})();
