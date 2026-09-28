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
    backToBook: "← Full book",
    tryStories: "Try the Stories view ↗",
    byDay: "By day",
    byLocation: "By location",
    explorePhotos: "Explore all our Thailand photos",
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
    backToBook: "→ הספר המלא",
    tryStories: "נסו את תצוגת הסטוריז ↗",
    byDay: "לפי יום",
    byLocation: "לפי מיקום",
    explorePhotos: "גלו את כל התמונות שלנו מתאילנד",
  },
};

let LANG = localStorage.getItem(LANG_KEY) || "en";

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

function mediaFull(item) {
  const src = `${MEDIA_BASE}/${escapeHtml(item.filename)}`;
  const thumbSrc = `${MEDIA_BASE}/${escapeHtml(item.thumb)}`;
  if (item.type === "video") {
    // poster shows the already-cached thumbnail instantly instead of a
    // blank/black box while the (much larger) video buffers on a slow
    // connection.
    return `<video src="${src}" poster="${thumbSrc}" controls autoplay playsinline></video>`;
  }
  // The full-resolution photo can be 1-1.5MB, which is slow to appear on
  // mobile data. Show the already-cached thumbnail as a blurred
  // placeholder immediately, fading the sharp version in once it loads,
  // so something is visible right away instead of a blank frame. The
  // width/height attributes let the browser reserve the right aspect
  // ratio before the full image has even started downloading.
  const dims = item.width && item.height ? ` width="${item.width}" height="${item.height}"` : "";
  return `
    <div class="media-frame">
      <img class="media-placeholder" src="${thumbSrc}" alt="" aria-hidden="true">
      <img class="media-hero" src="${src}"${dims} alt="" decoding="async" fetchpriority="high">
    </div>`;
}

// The page's CSP has no script-src 'unsafe-inline', so an inline onload=""
// attribute on the hero image is silently blocked — the fade-in has to be
// wired up from here instead, right after mediaFull()'s HTML is inserted.
function wireMediaFade(container) {
  const hero = container.querySelector(".media-hero");
  if (!hero) return;
  if (hero.complete) {
    hero.classList.add("is-loaded");
  } else {
    hero.addEventListener("load", () => hero.classList.add("is-loaded"), { once: true });
  }
}

function preloadMedia(item) {
  if (!item || item.type === "video") return;
  const img = new Image();
  img.src = `${MEDIA_BASE}/${item.filename}`;
}

function applyStaticI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
}

function setupMusicPlayback() {
  const button = document.getElementById("musicToggle");
  const music = document.getElementById("bgMusic");
  music.volume = 0.4;
  let wasPlayingBeforeVideo = false;

  function updateButton() {
    button.classList.toggle("is-playing", !music.paused);
    button.textContent = music.paused ? "🎵" : "🔇";
  }

  function tryPlay() {
    music.play().then(updateButton).catch(() => updateButton());
  }

  // Starts on the visitor's very first tap/click anywhere on the page —
  // true autoplay on load isn't possible (browsers require a user
  // gesture before unmuted audio can play), so this is the closest
  // approximation. The button itself is excluded here and handles its
  // own taps below: without this, a first tap landing on the button
  // would fire both listeners — this one starts playback, then the
  // button's own handler would read `music.paused` as already false
  // and immediately pause it again.
  document.addEventListener("click", (e) => {
    if (e.target.closest("#musicToggle")) return;
    tryPlay();
  }, { once: true });

  button.addEventListener("click", () => {
    if (music.paused) {
      tryPlay();
    } else {
      music.pause();
      updateButton();
    }
  });

  return {
    pauseForVideo() {
      wasPlayingBeforeVideo = !music.paused;
      if (!music.paused) {
        music.pause();
        updateButton();
      }
    },
    resumeAfterVideo() {
      if (wasPlayingBeforeVideo) {
        wasPlayingBeforeVideo = false;
        tryPlay();
      }
    },
  };
}

function setupLangToggle(onChange) {
  const nav = document.getElementById("langToggle");
  nav.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      LANG = button.dataset.lang;
      localStorage.setItem(LANG_KEY, LANG);
      nav.querySelectorAll("button").forEach((b) => b.classList.remove("is-active"));
      button.classList.add("is-active");
      onChange();
    });
  });
  nav.querySelectorAll("button").forEach((b) => b.classList.toggle("is-active", b.dataset.lang === LANG));
}

async function loadTripData() {
  const [tripMeta, photos] = await Promise.all([
    fetch("data/trip-meta.json")
      .then((r) => (r.ok ? r.json() : null))
      .catch(() => null),
    fetch("data/photo-index.json")
      .then((r) => (r.ok ? r.json() : []))
      .catch(() => []),
  ]);
  return { tripMeta, photos };
}
