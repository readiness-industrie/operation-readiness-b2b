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
    const attentionSummary = metricAttention.closest(".attention-summary");
    const attentionBox = qs("#attention-box");
    const attentionCopy = qs("#attention-copy");
    const filter = qs("#status-filter");
    const prevButton = qs("#sim-prev");
    const nextButton = qs("#sim-next");
    const playButton = qs("#sim-play");
    const playLabel = qs("[data-play-label]", playButton);
    const dialog = qs("#prerequisite-dialog");
    const dialogId = qs("#dialog-id");
    const dialogTitle = qs("#dialog-title");
    const dialogBody = qs("#dialog-body");

    let currentIndex = 0;
    let playTimer = null;
    let currentFilter = "all";

    const eventDays = new Set(data.activities.map((activity) => activity.day));

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

    function snapshotFor(prerequisite, day) {
      const visibleChanges = prerequisite.changes.filter((change) => change.day <= day);
      return visibleChanges.length ? visibleChanges[visibleChanges.length - 1] : null;
    }

    function activePrerequisites(day) {
      return data.prerequisites
        .filter((prerequisite) => prerequisite.activeFrom <= day)
        .map((prerequisite) => ({ prerequisite, snapshot: snapshotFor(prerequisite, day) }));
    }

    function matchesFilter(item) {
      const status = item.snapshot.status;
      if (currentFilter === "closed") return status === "closed";
      if (currentFilter === "obtain") return ["launch", "progress", "followup"].includes(status);
      if (currentFilter === "received") return status === "received";
      if (currentFilter === "nonconform") return ["incomplete", "contradictory"].includes(status);
      if (currentFilter === "attention") return ["validate", "blocked", "decision"].includes(status);
      return true;
    }

    function renderPrerequisiteRow(item, day) {
      const { prerequisite, snapshot } = item;
      const status = data.statusMeta[snapshot.status];
      const isNew = prerequisite.isAdded && prerequisite.activeFrom === day;
      const row = document.createElement("article");
      row.className = `prerequisite-row${isNew ? " is-new" : ""}`;
      row.innerHTML = `
        <span class="prerequisite-id">${escapeHtml(prerequisite.id)}</span>
        <div class="prerequisite-name">
          <strong title="${escapeHtml(prerequisite.title)}">${escapeHtml(prerequisite.title)}</strong>
          <small>${escapeHtml(prerequisite.company)} · Échéance ${escapeHtml(prerequisite.due)}</small>
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
      const visible = data.activities
        .filter((activity) => activity.day <= day)
        .slice(-7)
        .reverse();

      activityFeed.innerHTML = "";
      if (!visible.length) {
        const empty = document.createElement("li");
        empty.className = "activity-empty";
        empty.textContent = "Les actions apparaîtront ici au fil de la simulation.";
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
      dialogBody.innerHTML = `
        <div class="dialog-status-row">
          <span class="status-pill ${status.className}">${escapeHtml(status.label)}</span>
          <small>Échéance ${escapeHtml(prerequisite.due)} · Criticité ${escapeHtml(prerequisite.criticality)}</small>
        </div>
        <dl class="dialog-grid">
          <div><dt>Responsable</dt><dd>${escapeHtml(prerequisite.responsible)}<br>${escapeHtml(prerequisite.company)}</dd></div>
          <div><dt>Contacts</dt><dd>${escapeHtml(prerequisite.primary)}<br>Backup : ${escapeHtml(prerequisite.backup)}</dd></div>
          <div><dt>Preuve attendue</dt><dd>${escapeHtml(prerequisite.proof)}</dd></div>
          <div><dt>Canal</dt><dd>${escapeHtml(prerequisite.channel)}</dd></div>
          <div><dt>Contrôle documentaire</dt><dd>Présence, référence, version, date, signature, validité et complétude selon la grille convenue.</dd></div>
          <div><dt>Validation technique</dt><dd>Reste chez la personne compétente désignée par le client lorsqu'elle est nécessaire.</dd></div>
          <div><dt>Dernière information</dt><dd>${escapeHtml(snapshot.info)}</dd></div>
          <div><dt>Source</dt><dd>${escapeHtml(snapshot.source)}</dd></div>
          <div><dt>Prochaine action</dt><dd>${escapeHtml(snapshot.nextAction)} · ${escapeHtml(snapshot.nextDate)}</dd></div>
          <div><dt>Règle d'escalade</dt><dd>${escapeHtml(prerequisite.escalation)}</dd></div>
          <div><dt>Impact potentiel</dt><dd>${escapeHtml(prerequisite.impact)}</dd></div>
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
      const closedItems = activeItems.filter((item) => item.snapshot.status === "closed");
      const attentionItems = activeItems.filter(
        (item) => item.snapshot.status === "validate" ||
          (item.snapshot.attention && ["decision", "blocked"].includes(item.snapshot.status))
      );
      const actionsCount = data.activities.filter((activity) => activity.day <= currentDay.day).length;

      dayLabel.textContent = `${dayCode(currentDay.day)} : ${currentDay.label}`;
      metricTotal.textContent = String(activeItems.length);
      metricClosed.textContent = String(closedItems.length);
      metricActions.textContent = String(actionsCount);
      metricAttention.textContent = attentionItems.length
        ? `${attentionItems.length} action${attentionItems.length > 1 ? "s" : ""}`
        : "0 action";
      attentionSummary.classList.toggle("has-attention", attentionItems.length > 0);
      attentionBox.classList.toggle("has-attention", attentionItems.length > 0);
      attentionCopy.textContent = attentionItems.length
        ? attentionItems.map((item) => item.prerequisite.title).join(" · ")
        : "Aucune validation ou décision nécessaire à ce stade.";

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
      qsa(".timeline-day", timeline).forEach((button, index) => {
        const active = index === currentIndex;
        button.classList.toggle("active", active);
        button.setAttribute("aria-current", active ? "step" : "false");
      });
      qs(".timeline-day.active", timeline)?.scrollIntoView({ inline: "center", block: "nearest", behavior: prefersReducedMotion ? "auto" : "smooth" });

      prevButton.disabled = currentIndex === 0;
      nextButton.disabled = currentIndex === data.days.length - 1;
    }

    function stopPlayback() {
      if (playTimer) window.clearInterval(playTimer);
      playTimer = null;
      playButton.setAttribute("aria-pressed", "false");
      playLabel.textContent = currentIndex === data.days.length - 1 ? "Revoir la simulation" : "Lancer la simulation";
    }

    function startPlayback() {
      if (playTimer) {
        stopPlayback();
        return;
      }
      if (currentIndex === data.days.length - 1) currentIndex = 0;
      playButton.setAttribute("aria-pressed", "true");
      playLabel.textContent = "Mettre en pause";
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

    prevButton.addEventListener("click", () => {
      stopPlayback();
      currentIndex = Math.max(0, currentIndex - 1);
      render();
    });

    nextButton.addEventListener("click", () => {
      stopPlayback();
      currentIndex = Math.min(data.days.length - 1, currentIndex + 1);
      render();
    });

    playButton.addEventListener("click", startPlayback);
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
