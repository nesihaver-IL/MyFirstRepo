const MEDIA_BASE = "media/optimized";
const LANG_KEY = "haventure-lang";

const I18N = {
  en: {
    timeline: "Timeline",
    route: "The Route",
    allStops: "All stops",
    stop: "Stop",
    flyingOut: "Flying out",
    flyingHome: "Flying home",
    other: "Other",
    footer: "Nineteen days, four stops, more photos than we could choose from.",
    emptyTitle: "No photos here yet.",
    emptyBody: (cmd) => `Drop files into <code>media/originals/</code>, then run <code>${cmd}</code>.`,
    days: "days",
    stops: "stops",
    loadError: "Couldn't load the trip data. Try refreshing the page.",
    soundtrack: "Our trip soundtrack",
  },
  he: {
    timeline: "ציר זמן",
    route: "המסלול",
    allStops: "כל התחנות",
    stop: "תחנה",
    flyingOut: "טיסת הלוך",
    flyingHome: "טיסת חזור",
    other: "אחר",
    footer: "תשעה עשר ימים, ארבע תחנות, יותר תמונות ממה שיכולנו לבחור.",
    emptyTitle: "אין עדיין תמונות כאן.",
    emptyBody: (cmd) => `שימו קבצים בתוך <code>media/originals/</code>, ואז הריצו <code>${cmd}</code>.`,
    days: "ימים",
    stops: "תחנות",
    loadError: "טעינת נתוני הטיול נכשלה. נסו לרענן את הדף.",
    soundtrack: "הפסקול של הטיול שלנו",
  },
};

let LANG = localStorage.getItem(LANG_KEY) || "en";
let TRIP_META = null;
let PHOTOS = [];

const HTML_ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => HTML_ESCAPES[ch]);
}

function t(key, ...args) {
  const entry = I18N[LANG][key];
  return typeof entry === "function" ? entry(...args) : entry;
}

function dateFormatters() {
  const locale = LANG === "he" ? "he-IL" : "en-US";
  return {
    weekday: new Intl.DateTimeFormat(locale, { weekday: "short" }),
    day: new Intl.DateTimeFormat(locale, { month: "short", day: "numeric" }),
  };
}

function formatDate(iso) {
  const { weekday, day } = dateFormatters();
  const d = new Date(`${iso}T12:00:00`);
  return `${weekday.format(d)}, ${day.format(d)}`;
}

function formatDateRange(startIso, endIsoExclusive) {
  const { day } = dateFormatters();
  const end = new Date(`${endIsoExclusive}T12:00:00`);
  end.setDate(end.getDate() - 1);
  return `${day.format(new Date(`${startIso}T12:00:00`))} – ${day.format(end)}`;
}

function legName(leg) {
  return LANG === "he" ? leg.nameHe : leg.nameEn;
}

function legLabel(legId, tripMeta) {
  const leg = tripMeta.legs.find((l) => l.id === legId);
  if (leg) return legName(leg);
  if (legId === "flight-out") return t("flyingOut");
  if (legId === "flight-return") return t("flyingHome");
  return t("other");
}

function mediaThumb(item) {
  const src = `${MEDIA_BASE}/${escapeHtml(item.thumb)}`;
  const img = `<img src="${src}" loading="lazy" alt="">`;
  if (item.type === "video") {
    return `${img}<span class="play-badge" aria-hidden="true">▶</span>`;
  }
  if (item.source === "video-frame") {
    return `${img}<span class="clip-badge" aria-hidden="true" title="From a short clip">✦</span>`;
  }
  return img;
}

function mediaFull(item) {
  const src = `${MEDIA_BASE}/${escapeHtml(item.filename)}`;
  if (item.type === "video") {
    return `<video src="${src}" controls autoplay playsinline></video>`;
  }
  return `<img src="${src}" alt="">`;
}

function emptyState(command) {
  return `
    <div class="empty-state">
      <p>${t("emptyTitle")}</p>
      <p>${t("emptyBody", command)}</p>
    </div>`;
}

function groupBy(items, keyFn) {
  const map = new Map();
  for (const item of items) {
    const key = keyFn(item);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(item);
  }
  return map;
}

function tripDayCount(tripMeta) {
  const start = new Date(`${tripMeta.tripStart}T00:00:00`);
  const end = new Date(`${tripMeta.tripEnd}T00:00:00`);
  return Math.round((end - start) / 86400000) + 1;
}

function renderHero(tripMeta) {
  document.getElementById("heroDates").textContent =
    `${formatDate(tripMeta.tripStart)} – ${formatDate(tripMeta.tripEnd)}, 2026`;
  document.getElementById("heroSubtitle").textContent =
    LANG === "he" ? tripMeta.subtitleHe : tripMeta.subtitleEn;
  document.getElementById("heroStatement").textContent =
    LANG === "he" ? tripMeta.heroStatementHe : tripMeta.heroStatementEn;

  const highlight = tripMeta.tripHighlight || { value: "", labelEn: "", labelHe: "" };
  const highlightLabel = LANG === "he" ? highlight.labelHe : highlight.labelEn;
  document.getElementById("statStrip").innerHTML = `
    <div class="stat"><b>${tripDayCount(tripMeta)}</b><span>${t("days")}</span></div>
    <div class="stat"><b>${tripMeta.legs.length}</b><span>${t("stops")}</span></div>
    <div class="stat"><b>${escapeHtml(highlight.value)}</b><span>${escapeHtml(highlightLabel)}</span></div>`;
}

function renderTimeline(photos, tripMeta) {
  const container = document.getElementById("timelineView");
  if (photos.length === 0) {
    container.innerHTML = emptyState("python scripts/process_media.py");
    return;
  }
  const byDate = groupBy(photos, (p) => p.date);
  const dates = [...byDate.keys()].sort();
  container.innerHTML = dates
    .map((date) => {
      const items = byDate.get(date);
      const leg = legLabel(items[0].leg, tripMeta);
      return `
        <div class="timeline-day">
          <p class="timeline-date">${formatDate(date)} · ${escapeHtml(leg)}</p>
          <div class="mosaic">
            ${items.map((item) => `<figure data-id="${escapeHtml(item.id)}">${mediaThumb(item)}</figure>`).join("")}
          </div>
        </div>`;
    })
    .join("");
}

const STOP_COLORS = ["--stop-1", "--stop-2", "--stop-3", "--stop-4"];

function renderLocations(photos, tripMeta) {
  const byLeg = groupBy(photos, (p) => p.leg);
  const content = document.getElementById("locationsContent");

  content.innerHTML = tripMeta.legs
    .map((leg, index) => {
      const items = byLeg.get(leg.id) || [];
      const colorVar = STOP_COLORS[index % STOP_COLORS.length];
      const style = `--stop-color: var(${colorVar}); --stop-soft: var(${colorVar}-soft);`;
      const reflection = LANG === "he" ? leg.reflectionHe : leg.reflectionEn;
      return `
        <section class="stop" data-leg="${escapeHtml(leg.id)}" style="${style}">
          <div class="stop-dot"></div>
          <div class="folder">
            <span class="folder-tab">${t("stop")} ${index + 1}</span>
            <h2 class="leg-name">${escapeHtml(legName(leg))}</h2>
            <p class="leg-meta">${formatDateRange(leg.start, leg.end)} · ${escapeHtml(leg.hotel)}</p>
            <p class="leg-reflection">${escapeHtml(reflection)}</p>
            ${items.length
              ? `<div class="mosaic">${items
                  .map((item) => `<figure data-id="${escapeHtml(item.id)}">${mediaThumb(item)}</figure>`)
                  .join("")}</div>`
              : emptyState("python scripts/process_media.py")}
          </div>
        </section>`;
    })
    .join("");

  const filter = document.getElementById("locationFilter");
  const activeLeg = filter.querySelector("button.is-active")?.dataset.leg || "all";
  filter.innerHTML =
    `<button type="button" data-leg="all" class="${activeLeg === "all" ? "is-active" : ""}">${t("allStops")}</button>` +
    tripMeta.legs
      .map((leg) => `<button type="button" data-leg="${escapeHtml(leg.id)}" class="${activeLeg === leg.id ? "is-active" : ""}">${escapeHtml(legName(leg))}</button>`)
      .join("");

  content.querySelectorAll(".stop").forEach((section) => {
    section.hidden = activeLeg !== "all" && section.dataset.leg !== activeLeg;
  });
}

function setupLocationFilter() {
  const filter = document.getElementById("locationFilter");
  filter.addEventListener("click", (e) => {
    const button = e.target.closest("button");
    if (!button) return;
    filter.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
    button.classList.add("is-active");
    const legId = button.dataset.leg;
    document.querySelectorAll("#locationsContent .stop").forEach((section) => {
      section.hidden = legId !== "all" && section.dataset.leg !== legId;
    });
  });
}

function setupViewToggle() {
  const buttons = document.querySelectorAll(".view-toggle button");
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("is-active"));
      button.classList.add("is-active");
      document.querySelectorAll(".view").forEach((view) => view.classList.remove("is-active"));
      document.getElementById(`${button.dataset.view}View`).classList.add("is-active");
    });
  });
}

function setupLightbox(photosById) {
  const lightbox = document.getElementById("lightbox");
  const lightboxContent = document.getElementById("lightboxContent");

  function open(id) {
    const item = photosById.get(id);
    if (!item) return;
    lightboxContent.innerHTML = mediaFull(item);
    lightbox.classList.add("is-open");
  }

  function close() {
    lightbox.classList.remove("is-open");
    lightboxContent.innerHTML = "";
  }

  document.body.addEventListener("click", (e) => {
    const figure = e.target.closest("figure[data-id]");
    if (figure) open(figure.dataset.id);
  });

  document.getElementById("lightboxClose").addEventListener("click", close);
  lightbox.addEventListener("click", (e) => {
    if (e.target === lightbox) close();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") close();
  });
}

function applyStaticI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
}

function renderAll() {
  document.documentElement.lang = LANG;
  document.documentElement.dir = LANG === "he" ? "rtl" : "ltr";
  applyStaticI18n();
  renderHero(TRIP_META);
  renderTimeline(PHOTOS, TRIP_META);
  renderLocations(PHOTOS, TRIP_META);
}

function setupLangToggle() {
  const nav = document.getElementById("langToggle");
  nav.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      LANG = button.dataset.lang;
      localStorage.setItem(LANG_KEY, LANG);
      nav.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
      button.classList.add("is-active");
      renderAll();
    });
  });
  nav.querySelectorAll("button").forEach((b) => b.classList.toggle("is-active", b.dataset.lang === LANG));
}

async function init() {
  const [tripMeta, photos] = await Promise.all([
    fetch("data/trip-meta.json")
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null),
    fetch("data/photo-index.json")
      .then((r) => (r.ok ? r.json() : []))
      .catch(() => []),
  ]);

  if (!tripMeta) {
    document.getElementById("timelineView").innerHTML = `<div class="empty-state"><p>${t("loadError")}</p></div>`;
    return;
  }

  TRIP_META = tripMeta;
  PHOTOS = photos;

  renderAll();
  setupViewToggle();
  setupLocationFilter();
  setupLangToggle();
  setupLightbox(new Map(photos.map((p) => [p.id, p])));
}

init();
