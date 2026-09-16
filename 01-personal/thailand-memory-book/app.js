const MEDIA_BASE = "media/optimized";

const WEEKDAY_FORMAT = new Intl.DateTimeFormat("en-US", { weekday: "short" });
const DAY_FORMAT = new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" });

function formatDate(iso) {
  const d = new Date(`${iso}T12:00:00`);
  return `${WEEKDAY_FORMAT.format(d)}, ${DAY_FORMAT.format(d)}`;
}

function formatDateRange(startIso, endIsoExclusive) {
  const end = new Date(`${endIsoExclusive}T12:00:00`);
  end.setDate(end.getDate() - 1);
  const endIso = end.toISOString().slice(0, 10);
  return `${DAY_FORMAT.format(new Date(`${startIso}T12:00:00`))} – ${DAY_FORMAT.format(end)}`;
}

function legLabel(legId, tripMeta) {
  const leg = tripMeta.legs.find((l) => l.id === legId);
  if (leg) return leg.name;
  if (legId === "flight-out") return "Flying out";
  if (legId === "flight-return") return "Flying home";
  return "Other";
}

function mediaThumb(item) {
  const src = `${MEDIA_BASE}/${item.filename}`;
  if (item.type === "video") {
    return `<video src="${src}" muted playsinline preload="metadata"></video>`;
  }
  return `<img src="${src}" loading="lazy" alt="">`;
}

function mediaFull(item) {
  const src = `${MEDIA_BASE}/${item.filename}`;
  if (item.type === "video") {
    return `<video src="${src}" controls autoplay playsinline></video>`;
  }
  return `<img src="${src}" alt="">`;
}

function emptyState(command) {
  return `
    <div class="empty-state">
      <p>No photos here yet.</p>
      <p>Drop files into <code>media/originals/</code>, then run
      <code>${command}</code>.</p>
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

function renderHero(tripMeta) {
  document.getElementById("heroDates").textContent =
    `${formatDate(tripMeta.tripStart)} – ${formatDate(tripMeta.tripEnd)}, 2026`;
  document.getElementById("heroStatement").textContent = tripMeta.heroStatement;
  document.getElementById("heroRoute").textContent = tripMeta.route;
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
          <p class="timeline-date">${formatDate(date)} · ${leg}</p>
          <div class="grid">
            ${items.map((item) => `<figure data-id="${item.id}">${mediaThumb(item)}</figure>`).join("")}
          </div>
        </div>`;
    })
    .join("");
}

function renderLocations(photos, tripMeta) {
  const byLeg = groupBy(photos, (p) => p.leg);
  const content = document.getElementById("locationsContent");

  content.innerHTML = tripMeta.legs
    .map((leg) => {
      const items = byLeg.get(leg.id) || [];
      return `
        <section class="leg" data-leg="${leg.id}">
          <div class="leg-header">
            <h2 class="leg-name">${leg.name}</h2>
            <p class="leg-meta">${formatDateRange(leg.start, leg.end)} · ${leg.hotel}</p>
            <p class="leg-reflection">${leg.reflection}</p>
          </div>
          ${items.length
            ? `<div class="grid">${items
                .map((item) => `<figure data-id="${item.id}">${mediaThumb(item)}</figure>`)
                .join("")}</div>`
            : emptyState("python scripts/process_media.py")}
        </section>`;
    })
    .join("");

  const filter = document.getElementById("locationFilter");
  filter.innerHTML =
    `<button type="button" data-leg="all" class="is-active">All</button>` +
    tripMeta.legs.map((leg) => `<button type="button" data-leg="${leg.id}">${leg.name}</button>`).join("");

  filter.addEventListener("click", (e) => {
    const button = e.target.closest("button");
    if (!button) return;
    filter.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
    button.classList.add("is-active");
    const legId = button.dataset.leg;
    content.querySelectorAll(".leg").forEach((section) => {
      section.style.display = legId === "all" || section.dataset.leg === legId ? "" : "none";
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

async function init() {
  const [tripMeta, photos] = await Promise.all([
    fetch("data/trip-meta.json").then((r) => r.json()),
    fetch("data/photo-index.json")
      .then((r) => (r.ok ? r.json() : []))
      .catch(() => []),
  ]);

  renderHero(tripMeta);
  renderTimeline(photos, tripMeta);
  renderLocations(photos, tripMeta);
  setupViewToggle();
  setupLightbox(new Map(photos.map((p) => [p.id, p])));
}

init();
