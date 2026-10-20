/* Envoi des formulaires publics via Web3Forms (https://web3forms.com) */
(function () {
  "use strict";
  var API = "https://api.web3forms.com/submit";
  var ACCESS_KEY = "703aea08-dec2-44fc-ba45-a5bcb6f9a3b7";
  var FROM_NAME = "Site Readiness Industry";
  var FALLBACK_EMAIL = "hmreadinessindustry@gmail.com";
  var TIMEOUT_MS = 90000;

  window.riMailtoHref = function (subject, lines) {
    return (
      "mailto:" +
      FALLBACK_EMAIL +
      "?subject=" +
      encodeURIComponent(subject) +
      "&body=" +
      encodeURIComponent(lines.join("\n"))
    );
  };

  /**
   * @param {object} opts
   * @param {string} opts.subject
   * @param {string} opts.name
   * @param {string} opts.email
   * @param {string} opts.message
   * @param {object} [opts.fields] extra Web3Forms fields
   * @param {string} [opts.botcheck] honeypot value (non-empty = bot)
   * @param {HTMLElement} [opts.button]
   * @param {function} [opts.onWait]
   * @param {function} [opts.onSuccess]
   * @param {function} [opts.onError] receives mailtoHref
   * @param {function} opts.mailtoBody lines for fallback
   * @param {string} opts.mailtoSubject
   */
  window.riWeb3Submit = function (opts) {
    if (opts.botcheck) {
      if (opts.onError) opts.onError(opts.mailtoHref || riMailtoHref(opts.mailtoSubject, opts.mailtoBody()));
      return Promise.reject(new Error("botcheck"));
    }
    var payload = {
      access_key: ACCESS_KEY,
      subject: opts.subject,
      from_name: FROM_NAME,
      name: opts.name || "",
      email: opts.email || "",
      message: opts.message || "",
      botcheck: ""
    };
    if (opts.fields) {
      Object.keys(opts.fields).forEach(function (k) {
        payload[k] = opts.fields[k];
      });
    }
    var btn = opts.button;
    var prevText = btn && btn.textContent;
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Envoi en cours…";
    }
    if (opts.onWait) opts.onWait();
    var ctrl = new AbortController();
    var timer = setTimeout(function () {
      ctrl.abort();
    }, opts.timeout || TIMEOUT_MS);
    var mailto =
      opts.mailtoHref ||
      riMailtoHref(opts.mailtoSubject || opts.subject, opts.mailtoBody ? opts.mailtoBody() : [opts.message || ""]);
    return fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
      signal: ctrl.signal
    })
      .then(function (r) {
        return r.json().then(function (j) {
          return { status: r.status, j: j };
        });
      })
      .then(function (x) {
        if (!x.j || x.j.success !== true) {
          throw new Error((x.j && x.j.message) || "web3forms_failed");
        }
        if (btn) btn.textContent = "Demande envoyée ✓";
        if (opts.onSuccess) opts.onSuccess(x.j);
        return x.j;
      })
      .catch(function () {
        if (btn) {
          btn.disabled = false;
          btn.textContent = prevText || "Envoyer";
        }
        if (opts.onError) opts.onError(mailto);
        return Promise.reject(new Error("submit_failed"));
      })
      .finally(function () {
        clearTimeout(timer);
      });
  };
})();
