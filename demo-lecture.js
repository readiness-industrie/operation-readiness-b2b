(function () {
  "use strict";

  const data = window.SIMULATION_DATA;
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const euroFormatter = new Intl.NumberFormat("fr-FR", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0
  });

  const CONTACT_EMAIL = "hervemengue.pro@gmail.com";
  const ANALYTICS_MEASUREMENT_ID = "G-CXBR9QTFXS";
  const ANALYTICS_CONSENT_KEY = "readiness_analytics_consent_v1";

  function qs(selector, root = document) {
    return root.querySelector(selector);
  }

  function qsa(selector, root = document) {
    return Array.from(root.querySelectorAll(selector));
  }


  function readAnalyticsConsent() {
    try {
      return window.localStorage.getItem(ANALYTICS_CONSENT_KEY);
    } catch (_error) {
      return null;
    }
  }

  function saveAnalyticsConsent(value) {
    try {
      window.localStorage.setItem(ANALYTICS_CONSENT_KEY, value);
    } catch (_error) {
      // Le choix reste valable pour la page courante si le stockage est indisponible.
    }
  }

  function loadAnalytics() {
    if (!ANALYTICS_MEASUREMENT_ID || window.__readinessAnalyticsLoaded) return;

    window.__readinessAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = window.gtag || function () {
      window.dataLayer.push(arguments);
    };

    window.gtag("js", new Date());
    window.gtag("config", ANALYTICS_MEASUREMENT_ID, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });

    const script = document.createElement("script");
    script.async = true;
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(ANALYTICS_MEASUREMENT_ID);
    script.dataset.readinessAnalytics = "true";
    document.head.appendChild(script);
  }

  function disableAnalytics() {
    if (typeof window.gtag === "function") {
      window.gtag("consent", "update", { analytics_storage: "denied" });
    }

    document.cookie.split(";").forEach((item) => {
      const name = item.split("=")[0].trim();
      if (name === "_ga" || name.startsWith("_ga_")) {
        document.cookie = name + "=; Max-Age=0; path=/; SameSite=Lax";
      }
    });
  }

  function initAnalyticsConsent() {
    const banner = qs("[data-analytics-consent]");
    if (!banner) return;

    const openBanner = () => {
      banner.hidden = false;
    };
    const closeBanner = () => {
      banner.hidden = true;
    };

    qsa("[data-manage-analytics]").forEach((button) => button.addEventListener("click", openBanner));

    qs("[data-analytics-accept]", banner).addEventListener("click", () => {
      saveAnalyticsConsent("granted");
      closeBanner();
      loadAnalytics();
    });

    qs("[data-analytics-refuse]", banner).addEventListener("click", () => {
      saveAnalyticsConsent("denied");
      disableAnalytics();
      closeBanner();
    });

    const consent = readAnalyticsConsent();
    if (consent === "granted") loadAnalytics();
    else if (consent !== "denied") openBanner();
  }

  function dayCode(day) {
    return day === 0 ? "J-0" : `J${day}`;
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function initHeader() {
    const header = qs("[data-header]");
    const toggle = qs(".nav-toggle");
    const nav = qs("#main-nav");
    if (!header || !toggle || !nav) return;

    const updateHeader = () => header.classList.toggle("scrolled", window.scrollY > 20);
    updateHeader();
    window.addEventListener("scroll", updateHeader, { passive: true });

    toggle.addEventListener("click", () => {
      const isOpen = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isOpen));
      header.classList.toggle("menu-open", !isOpen);
    });

    nav.addEventListener("click", (event) => {
      if (event.target.closest("a")) {
        toggle.setAttribute("aria-expanded", "false");
        header.classList.remove("menu-open");
      }
    });
  }

  function initReveal() {
    const elements = qsa(".reveal");
    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      elements.forEach((element) => element.classList.add("visible"));
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -45px" }
    );

    elements.forEach((element) => observer.observe(element));
  }

  function initSimulation() {
    if (!data) return;

    const timeline = qs("#simulation-timeline");
    const list = qs("#prerequisite-list");
    const activityFeed = qs("#activity-feed");
    const dayLabel = qs("#current-day-label");
    const metricTotal = qs("#metric-total");
    const metricClosed = qs("#metric-closed");
    const metricActions = qs("#metric-actions");
    const metricAttention = qs("#metric-attention");
    const attentionSummary = metricAttention ? metricAttention.closest(".attention-summary") : null;
    const attentionBox = qs("#attention-box");
    const attentionCopy = qs("#attention-copy");
    const attentionList = qs("#attention-list");
    const filter = qs("#status-filter");
    const prevButton = qs("#sim-prev");
    const nextButton = qs("#sim-next");
    const playButton = qs("#sim-play");
    const playLabel = playButton ? qs("[data-play-label]", playButton) : null;
    const dialog = qs("#prerequisite-dialog");
    const dialogId = qs("#dialog-id");
    const dialogTitle = qs("#dialog-title");
    const dialogBody = qs("#dialog-body");

    if (!list || !filter || !dialog || !dialogBody || !metricTotal || !metricClosed || !metricActions || !metricAttention) return;

    let currentIndex = 0;
    let playTimer = null;
    let currentFilter = "all";

    const openingDay = Number.isInteger(data.openingDay) ? data.openingDay : data.days[0].day;
    const openingIndex = data.days.findIndex((item) => item.day === openingDay);
    currentIndex = openingIndex >= 0 ? openingIndex : 0;

    const eventDays = new Set((data.activities || []).map((activity) => activity.day));

    if (timeline) {
      data.days.forEach((item, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `timeline-day${eventDays.has(item.day) ? " has-event" : ""}`;
        button.dataset.index = String(index);
        button.setAttribute("aria-label", `${dayCode(item.day)} : ${item.label}`);
        button.innerHTML = `<i aria-hidden="true"></i><span>${dayCode(item.day)}</span>`;
        button.addEventListener("click", () => {
          stopPlayback();
          currentIndex = index;
          render();
        });
        timeline.appendChild(button);
      });
    }

    function snapshotFor(prerequisite, day) {
      const visibleChanges = prerequisite.changes.filter((change) => change.day <= day);
      return visibleChanges.length ? visibleChanges[visibleChanges.length - 1] : null;
    }

    function activePrerequisites(day) {
      return data.prerequisites
        .filter((prerequisite) => prerequisite.activeFrom <= day)
        .map((prerequisite) => ({ prerequisite, snapshot: snapshotFor(prerequisite, day) }))
        .filter((item) => item.snapshot);
    }

    function needsDecision(snapshot) {
      return ["validate", "blocked", "decision"].includes(snapshot.status);
    }

    function isClosed(snapshot) {
      return snapshot.status === "closed";
    }

    function isAttentionItem(item) {
      return needsDecision(item.snapshot);
    }

    function missingLabel(snapshot) {
      if (snapshot.missing) return snapshot.missing;
      return isClosed(snapshot) ? "Rien. Le critère de fermeture est satisfait." : "Information encore à préciser";
    }

    function matchesFilter(item) {
      const status = item.snapshot.status;
      if (currentFilter === "closed") return status === "closed";
      if (currentFilter === "open") return status !== "closed";
      if (currentFilter === "obtain") return ["launch", "progress", "followup"].includes(status);
      if (currentFilter === "received") return status === "received";
      if (currentFilter === "nonconform") return ["incomplete", "contradictory"].includes(status);
      if (currentFilter === "attention") return isAttentionItem(item);
      return true;
    }

    function renderPrerequisiteRow(item, day) {
      const { prerequisite, snapshot } = item;
      const status = data.statusMeta[snapshot.status];
      const isNew = prerequisite.isAdded && prerequisite.activeFrom === day;
      const missing = missingLabel(snapshot);
      const subtitle = isClosed(snapshot)
        ? `${prerequisite.company}. Échéance ${prerequisite.due}`
        : `Manque : ${missing}`;
      const row = document.createElement("article");
      row.className = `prerequisite-row${isNew ? " is-new" : ""}`;
      row.innerHTML = `
        <span class="prerequisite-id">${escapeHtml(prerequisite.id)}</span>
        <div class="prerequisite-name">
          <strong title="${escapeHtml(prerequisite.title)}">${escapeHtml(prerequisite.title)}</strong>
          <small>${escapeHtml(subtitle)}</small>
        </div>
        <div class="prerequisite-action">
          <small>Prochaine action</small>
          <strong title="${escapeHtml(snapshot.nextAction)}">${escapeHtml(snapshot.nextAction)}</strong>
        </div>
        <button class="prerequisite-detail" type="button" aria-label="Voir le détail de ${escapeHtml(prerequisite.title)}">→</button>
      `;

      const statusPill = document.createElement("span");
      statusPill.className = `status-pill ${status.className}`;
      statusPill.textContent = status.label;
      qs(".prerequisite-name", row).appendChild(statusPill);
      qs(".prerequisite-detail", row).addEventListener("click", () => openDetail(prerequisite, snapshot, day));
      return row;
    }

    function renderActivities(day) {
      if (!activityFeed) return;

      const visible = data.activities
        .filter((activity) => activity.day <= day)
        .slice(-7)
        .reverse();

      activityFeed.innerHTML = "";
      if (!visible.length) {
        const empty = document.createElement("li");
        empty.className = "activity-empty";
        empty.textContent = "Les informations du dossier apparaîtront ici.";
        activityFeed.appendChild(empty);
        return;
      }

      visible.forEach((activity) => {
        const li = document.createElement("li");
        li.innerHTML = `
          <time>${dayCode(activity.day)}</time>
          <div><strong>${escapeHtml(activity.title)}</strong><span>${escapeHtml(activity.detail)}</span></div>
        `;
        activityFeed.appendChild(li);
      });
    }

    function openDetail(prerequisite, snapshot, day) {
      const status = data.statusMeta[snapshot.status];
      const history = prerequisite.changes.filter((change) => change.day <= day).slice().reverse();
      dialogId.textContent = `${prerequisite.id} · ${dayCode(day)}`;
      dialogTitle.textContent = prerequisite.title;
      const closed = isClosed(snapshot);
      const decision = needsDecision(snapshot);
      dialogBody.innerHTML = `
        <div class="dialog-status-row">
          <span class="status-pill ${status.className}">${escapeHtml(status.label)}</span>
          <small>Échéance ${escapeHtml(prerequisite.due)}. Criticité ${escapeHtml(prerequisite.criticality)}</small>
        </div>
        <dl class="dialog-grid">
          <div><dt>Dernière information</dt><dd>${escapeHtml(snapshot.info)}</dd></div>
          <div><dt>Ce qui manque</dt><dd>${escapeHtml(missingLabel(snapshot))}</dd></div>
          <div><dt>Prochaine action</dt><dd>${escapeHtml(snapshot.nextAction)}. ${escapeHtml(snapshot.nextDate)}</dd></div>
          <div><dt>Décision nécessaire</dt><dd>${decision ? "Oui" : "Non"}</dd></div>
          <div><dt>Point réellement fermé</dt><dd>${closed ? "Oui. Le critère de fermeture est satisfait." : "Non"}</dd></div>
          <div><dt>Impact éventuel</dt><dd>${escapeHtml(prerequisite.impact)}</dd></div>
          <div><dt>Responsable</dt><dd>${escapeHtml(prerequisite.responsible)}<br>${escapeHtml(prerequisite.company)}</dd></div>
          <div><dt>Contacts</dt><dd>${escapeHtml(prerequisite.primary)}<br>Relais : ${escapeHtml(prerequisite.backup)}</dd></div>
          <div><dt>Preuve attendue</dt><dd>${escapeHtml(prerequisite.proof)}</dd></div>
          <div><dt>Canal</dt><dd>${escapeHtml(prerequisite.channel)}</dd></div>
          <div><dt>Source</dt><dd>${escapeHtml(snapshot.source)}</dd></div>
          <div><dt>Si ça reste bloqué</dt><dd>${escapeHtml(prerequisite.escalation)}</dd></div>
        </dl>
        <h3 class="dialog-history-title">Historique jusqu'à ${dayCode(day)}</h3>
        <ol class="dialog-history">
          ${history
            .map(
              (change) => `
                <li>
                  <time>${dayCode(change.day)}</time>
                  <div><strong>${escapeHtml(change.action)}</strong><span>${escapeHtml(change.info)}</span></div>
                </li>`
            )
            .join("")}
        </ol>
      `;

      document.body.classList.add("dialog-open");
      if (typeof dialog.showModal === "function") dialog.showModal();
      else dialog.setAttribute("open", "");
    }

    function closeDetail() {
      document.body.classList.remove("dialog-open");
      if (typeof dialog.close === "function") dialog.close();
      else dialog.removeAttribute("open");
    }

    function render() {
      const currentDay = data.days[currentIndex];
      const activeItems = activePrerequisites(currentDay.day);
      const filteredItems = activeItems.filter(matchesFilter);
      const closedItems = activeItems.filter((item) => isClosed(item.snapshot));
      const openItems = activeItems.filter((item) => !isClosed(item.snapshot));
      const attentionItems = activeItems.filter(isAttentionItem);

      if (dayLabel) dayLabel.textContent = `${dayCode(currentDay.day)} : ${currentDay.label}`;
      metricTotal.textContent = String(activeItems.length);
      metricClosed.textContent = String(closedItems.length);
      metricActions.textContent = String(openItems.length);
      metricAttention.textContent = attentionItems.length
        ? `${attentionItems.length} action${attentionItems.length > 1 ? "s" : ""}`
        : "0 action";
      if (attentionSummary) attentionSummary.classList.toggle("has-attention", attentionItems.length > 0);
      if (attentionBox) attentionBox.classList.toggle("has-attention", attentionItems.length > 0);
      if (attentionCopy) {
        attentionCopy.textContent = attentionItems.length
          ? `${attentionItems.length} point${attentionItems.length > 1 ? "s" : ""} demand${attentionItems.length > 1 ? "ent" : "e"} une action maintenant. Le reste du dossier n'a pas besoin d'être relu ligne à ligne.`
          : "Aucune validation ni décision nécessaire à ce stade. Rien à traiter en priorité.";
      }

      if (attentionList) {
        attentionList.innerHTML = "";
        attentionList.hidden = attentionItems.length === 0;
        attentionItems.forEach((item) => {
          const li = document.createElement("li");
          const button = document.createElement("button");
          button.type = "button";
          const status = data.statusMeta[item.snapshot.status];
          button.innerHTML = `
            <span class="attention-item-title">${escapeHtml(item.prerequisite.title)}</span>
            <span class="attention-item-meta">${escapeHtml(status.label)}. ${escapeHtml(item.snapshot.nextAction)}</span>
          `;
          button.addEventListener("click", () => openDetail(item.prerequisite, item.snapshot, currentDay.day));
          li.appendChild(button);
          attentionList.appendChild(li);
        });
      }

      list.innerHTML = "";
      if (!filteredItems.length) {
        const empty = document.createElement("div");
        empty.className = "empty-state";
        empty.textContent = "Aucun point ne correspond à ce filtre pour cette journée.";
        list.appendChild(empty);
      } else {
        filteredItems.forEach((item) => list.appendChild(renderPrerequisiteRow(item, currentDay.day)));
      }

      renderActivities(currentDay.day);
      if (timeline) {
        qsa(".timeline-day", timeline).forEach((button, index) => {
          const active = index === currentIndex;
          button.classList.toggle("active", active);
          button.setAttribute("aria-current", active ? "step" : "false");
        });
        qs(".timeline-day.active", timeline)?.scrollIntoView({ inline: "center", block: "nearest", behavior: prefersReducedMotion ? "auto" : "smooth" });
      }
      if (prevButton) prevButton.disabled = currentIndex === 0;
      if (nextButton) nextButton.disabled = currentIndex === data.days.length - 1;
    }

    function stopPlayback() {
      if (playTimer) window.clearInterval(playTimer);
      playTimer = null;
      if (playButton) playButton.setAttribute("aria-pressed", "false");
      if (playLabel) playLabel.textContent = currentIndex === data.days.length - 1 ? "Revoir depuis le début" : "Voir l'évolution";
    }

    function startPlayback() {
      if (!playButton) return;
      if (playTimer) {
        stopPlayback();
        return;
      }
      if (currentIndex === data.days.length - 1) currentIndex = 0;
      playButton.setAttribute("aria-pressed", "true");
      if (playLabel) playLabel.textContent = "Mettre en pause";
      render();
      playTimer = window.setInterval(() => {
        if (currentIndex >= data.days.length - 1) {
          stopPlayback();
          return;
        }
        currentIndex += 1;
        render();
      }, prefersReducedMotion ? 1600 : 1050);
    }

    if (prevButton) {
      prevButton.addEventListener("click", () => {
        stopPlayback();
        currentIndex = Math.max(0, currentIndex - 1);
        render();
      });
    }

    if (nextButton) {
      nextButton.addEventListener("click", () => {
        stopPlayback();
        currentIndex = Math.min(data.days.length - 1, currentIndex + 1);
        render();
      });
    }

    if (playButton) playButton.addEventListener("click", startPlayback);
    filter.addEventListener("change", () => {
      currentFilter = filter.value;
      render();
    });
    qs("[data-dialog-close]", dialog).addEventListener("click", closeDetail);
    dialog.addEventListener("click", (event) => {
      const bounds = dialog.getBoundingClientRect();
      const outside =
        event.clientX < bounds.left ||
        event.clientX > bounds.right ||
        event.clientY < bounds.top ||
        event.clientY > bounds.bottom;
      if (outside) closeDetail();
    });
    dialog.addEventListener("close", () => document.body.classList.remove("dialog-open"));

    render();
  }

  function initCalculator() {
    const form = qs("#exposure-calculator");
    const result = qs("#exposure-result");
    if (!form || !result) return;

    const getValue = (name) => {
      const value = Number.parseFloat(form.elements[name].value);
      return Number.isFinite(value) && value > 0 ? value : 0;
    };

    const calculate = () => {
      const peopleCost = getValue("people") * getValue("dailyCost") * getValue("days");
      const total = peopleCost + getValue("equipment") + getValue("travel") + getValue("other");
      result.textContent = euroFormatter.format(total);
    };

    form.addEventListener("input", calculate);
    calculate();
  }

  function initHistory() {
    const button = qs("#toggle-history");
    const history = qs(".history-list");
    if (!button || !history) return;

    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!expanded));
      button.textContent = expanded ? "Afficher un historique complet" : "Réduire l'historique";
      history.dataset.collapsed = String(expanded);
    });
  }

  function initWorkflow() {
    const demo = qs(".workflow-demo");
    const controls = qsa("[data-workflow-step]", demo);
    const playButton = qs("#workflow-play");
    const caption = qs("#workflow-caption");
    if (!demo || !playButton || !caption) return;

    const captions = {
      before: "Avant : demandes, appels, documents et relances arrivent directement vers le chef de projet.",
      transition: "La couche de poursuite reprend les flux définis dans le mandat du client.",
      after: "Avec le service : seules l'information importante et la décision nécessaire remontent au chef de projet."
    };
    let timers = [];

    const clearTimers = () => {
      timers.forEach((timer) => window.clearTimeout(timer));
      timers = [];
    };

    const setState = (state) => {
      demo.dataset.workflowState = state;
      caption.textContent = captions[state];
      controls.forEach((button) => {
        const active = button.dataset.workflowStep === state;
        button.classList.toggle("active", active);
        button.setAttribute("aria-pressed", String(active));
      });
    };

    controls.forEach((button) => {
      button.addEventListener("click", () => {
        clearTimers();
        setState(button.dataset.workflowStep);
      });
    });

    playButton.addEventListener("click", () => {
      clearTimers();
      setState("before");
      if (prefersReducedMotion) {
        setState("after");
        return;
      }
      timers.push(window.setTimeout(() => setState("transition"), 900));
      timers.push(window.setTimeout(() => setState("after"), 2100));
    });
  }

  function initContactForm() {
    const form = qs("#contact-form");
    const status = qs("#form-status");
    if (!form || !status) return;

    const requiredFields = qsa("[required]", form);
    requiredFields.forEach((field) => {
      field.addEventListener("input", () => field.removeAttribute("aria-invalid"));
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      status.className = "form-status";
      status.textContent = "";

      const invalid = requiredFields.filter((field) => !field.checkValidity());
      if (invalid.length) {
        invalid.forEach((field) => field.setAttribute("aria-invalid", "true"));
        invalid[0].focus();
        status.classList.add("error");
        status.textContent = "Vérifiez les champs obligatoires et le format de l'adresse e-mail.";
        return;
      }

      const values = Object.fromEntries(new FormData(form).entries());
      const subject = `Vérifier un projet Readiness Industry : ${values.company}`;
      const body = [
        `Nom : ${values.name}`,
        `Entreprise : ${values.company}`,
        `Fonction : ${values.role}`,
        `E-mail : ${values.email}`,
        `Téléphone : ${values.phone || "Non renseigné"}`,
        "",
        "Contexte non sensible :",
        values.message
      ].join("\n");

      if (CONTACT_EMAIL) {
        if (typeof window.gtag === "function") {
          window.gtag("event", "generate_lead", {
            method: "contact_form"
          });
        }
        window.location.href = `mailto:${encodeURIComponent(CONTACT_EMAIL)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        status.classList.add("success");
        status.textContent = "Votre messagerie va s'ouvrir avec la demande préremplie.";
        return;
      }

      try {
        await navigator.clipboard.writeText(`${subject}\n\n${body}`);
        status.classList.add("success");
        status.textContent = "Demande copiée. L'adresse professionnelle de destination doit encore être validée avant l'envoi public.";
      } catch (_error) {
        status.classList.add("error");
        status.textContent = "L'envoi public n'est pas encore configuré. Aucune donnée n'a été transmise.";
      }
    });
  }

  function initYear() {
    const year = qs("#current-year");
    if (year) year.textContent = String(new Date().getFullYear());
  }

  document.addEventListener("DOMContentLoaded", () => {
    initAnalyticsConsent();
    initHeader();
    initReveal();
    initSimulation();
    initCalculator();
    initHistory();
    initWorkflow();
    initContactForm();
    initYear();
  });
})();
