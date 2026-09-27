let TRIP_META = null;
let PHOTOS = [];

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

function emptyState(command) {
  return `
    <div class="empty-state">
      <p>${t("emptyTitle")}</p>
      <p>${t("emptyBody", command)}</p>
    </div>`;
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

function setupLightbox(photosById, musicControls) {
  const lightbox = document.getElementById("lightbox");
  const lightboxContent = document.getElementById("lightboxContent");

  function open(id) {
    const item = photosById.get(id);
    if (!item) return;
    lightboxContent.innerHTML = mediaFull(item);
    lightbox.classList.add("is-open");
    if (item.type === "video") {
      musicControls.pauseForVideo();
    }
  }

  function close() {
    lightbox.classList.remove("is-open");
    lightboxContent.innerHTML = "";
    musicControls.resumeAfterVideo();
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

function renderAll() {
  document.documentElement.lang = LANG;
  document.documentElement.dir = LANG === "he" ? "rtl" : "ltr";
  applyStaticI18n();
  renderHero(TRIP_META);
  renderTimeline(PHOTOS, TRIP_META);
  renderLocations(PHOTOS, TRIP_META);
}

async function init() {
  const { tripMeta, photos } = await loadTripData();

  if (!tripMeta) {
    document.getElementById("timelineView").innerHTML = `<div class="empty-state"><p>${t("loadError")}</p></div>`;
    return;
  }

  TRIP_META = tripMeta;
  PHOTOS = photos;

  renderAll();
  setupViewToggle();
  setupLocationFilter();
  setupLangToggle(renderAll);
  const musicControls = setupMusicPlayback();
  setupLightbox(new Map(photos.map((p) => [p.id, p])), musicControls);
}

init();
