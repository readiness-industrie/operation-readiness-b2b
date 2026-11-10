/* Formulaire simple (accueil et /contact) : envoi Web3Forms, sujet « Site RI ». */
(function () {
  "use strict";
  var SUBJECT = "Site RI - Contact";

  function show(el, on) {
    if (!el) return;
    el.hidden = !on;
  }

  function bind(form) {
    if (!form || form.dataset.riBound) return;
    form.dataset.riBound = "1";
    var wait = form.querySelector("[data-form-wait]");
    var err = form.querySelector("[data-form-err]");
    var ok = form.querySelector("[data-form-ok]");
    var btn = form.querySelector('button[type="submit"]');

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (err) err.innerHTML = "";
      show(err, false);
      show(ok, false);

      var nom = (form.nom.value || "").trim();
      var societe = (form.societe.value || "").trim();
      var email = (form.email.value || "").trim();
      var message = (form.message.value || "").trim();
      var consent = !!(form.consentement && form.consentement.checked);

      if (!nom || !societe || !email || !message || !consent) {
        if (err) {
          err.textContent =
            "Merci de remplir le nom, la société, l'e-mail, le message, et d'accepter l'usage de ces informations pour vous répondre.";
          show(err, true);
        }
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        if (err) {
          err.textContent = "L'adresse e-mail ne semble pas valide.";
          show(err, true);
        }
        return;
      }
      if (typeof window.riWeb3Submit !== "function") {
        if (err) {
          err.innerHTML =
            'L\'envoi est indisponible. Écrivez à <a href="mailto:hmreadinessindustry@gmail.com">hmreadinessindustry@gmail.com</a>.';
          show(err, true);
        }
        return;
      }

      var lines = [
        "Nom : " + nom,
        "Société : " + societe,
        "E-mail : " + email,
        "Consentement RGPD : oui",
        "",
        message
      ];

      window.riWeb3Submit({
        subject: SUBJECT,
        name: nom,
        email: email,
        message: lines.join("\n"),
        fields: { societe: societe, consentement_rgpd: "oui" },
        botcheck: ((form.botcheck && form.botcheck.value) || "").trim(),
        button: btn,
        formName: form.getAttribute("data-form-name") || "",
        leadMethod: form.getAttribute("data-lead-method") || "",
        mailtoSubject: SUBJECT + " - " + societe,
        mailtoBody: function () {
          return lines;
        },
        onWait: function () {
          show(wait, true);
        },
        onSuccess: function () {
          form.reset();
          show(wait, false);
          show(ok, true);
        },
        onError: function (mailto) {
          show(wait, false);
          if (err) {
            err.innerHTML =
              'L\'envoi n\'a pas abouti. Écrivez à <a href="mailto:hmreadinessindustry@gmail.com">hmreadinessindustry@gmail.com</a> ou <a href="' +
              mailto +
              '">envoyez un e-mail prérempli</a>.';
            show(err, true);
          }
        }
      });
    });
  }

  function init() {
    document.querySelectorAll("form[data-ri-contact]").forEach(bind);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
