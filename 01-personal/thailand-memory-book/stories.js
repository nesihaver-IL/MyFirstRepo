const AUTO_ADVANCE_MS = 4000;

let TRIP_META = null;
let PHOTOS = [];
let GROUPING = "day";
let BLOCKS = [];
let musicControls = null;

let currentBlockIndex = -1;
let currentItemIndex = 0;
let advanceTimer = null;
let currentIsVideo = false;

function buildDayBlocks(photos, tripMeta) {
  const byDate = groupBy(photos, (p) => p.date);
  const dates = [...byDate.keys()].sort();
  return dates.map((date) => {
    const items = byDate.get(date);
    return {
      id: `day-${date}`,
      titleText: formatDate(date),
      subtitleText: legLabel(items[0].leg, tripMeta),
      items,
    };
  });
}

function buildLocationBlocks(photos, tripMeta) {
  const byLeg = groupBy(photos, (p) => p.leg);
  return tripMeta.legs
    .map((leg) => {
      const items = byLeg.get(leg.id) || [];
      if (!items.length) return null;
      return {
        id: `leg-${leg.id}`,
        titleText: legName(leg),
        subtitleText: formatDateRange(leg.start, leg.end),
        items,
      };
    })
    .filter(Boolean);
}

function viewedKey() {
  return `haventure-viewed-${GROUPING}`;
}

function getViewedSet() {
  try {
    return new Set(JSON.parse(localStorage.getItem(viewedKey()) || "[]"));
  } catch {
    return new Set();
  }
}

function markViewed(blockId) {
  const viewed = getViewedSet();
  viewed.add(blockId);
  try {
    localStorage.setItem(viewedKey(), JSON.stringify([...viewed]));
  } catch {
    // per-viewer convenience only — fine to lose silently
  }
}

function renderTray() {
  const viewed = getViewedSet();
  const tray = document.getElementById("storyTray");
  tray.innerHTML = BLOCKS.map((block, index) => {
    const avatarSrc = `${MEDIA_BASE}/${escapeHtml(block.items[0].thumb)}`;
    const isViewed = viewed.has(block.id);
    return `
      <button type="button" class="tray-item ${isViewed ? "is-viewed" : ""}" data-index="${index}">
        <span class="tray-ring"><img class="tray-avatar" src="${avatarSrc}" loading="lazy" alt=""></span>
        <span class="tray-label">${escapeHtml(block.titleText)}</span>
      </button>`;
  }).join("");
}

function setGrouping(grouping) {
  GROUPING = grouping;
  BLOCKS = grouping === "day" ? buildDayBlocks(PHOTOS, TRIP_META) : buildLocationBlocks(PHOTOS, TRIP_META);
  renderTray();
}

function setupGroupToggle() {
  const buttons = document.querySelectorAll("#groupToggle button");
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("is-active"));
      button.classList.add("is-active");
      setGrouping(button.dataset.group);
    });
  });
}

function setupTray() {
  document.getElementById("storyTray").addEventListener("click", (e) => {
    const button = e.target.closest(".tray-item");
    if (button) openBlock(Number(button.dataset.index));
  });
}

function clearAdvanceTimer() {
  if (advanceTimer) {
    clearTimeout(advanceTimer);
    advanceTimer = null;
  }
}

function openBlock(blockIndex) {
  const block = BLOCKS[blockIndex];
  if (!block) return;
  currentBlockIndex = blockIndex;
  currentIsVideo = false;
  markViewed(block.id);
  renderTray();

  const segmentsWrap = document.getElementById("storySegments");
  segmentsWrap.innerHTML = block.items.map(() => `<div class="segment"><span></span></div>`).join("");

  document.getElementById("storyTitle").textContent = block.titleText;
  document.getElementById("storySubtitle").textContent = block.subtitleText;
  document.getElementById("storyAvatar").src = `${MEDIA_BASE}/${block.items[0].thumb}`;

  document.getElementById("storyViewer").classList.add("is-open");
  showItem(0);
}

function closeViewer() {
  clearAdvanceTimer();
  document.getElementById("storyViewer").classList.remove("is-open");
  document.getElementById("storyMedia").innerHTML = "";
  if (currentIsVideo) {
    musicControls.resumeAfterVideo();
    currentIsVideo = false;
  }
  currentBlockIndex = -1;
}

function showItem(itemIndex) {
  const block = BLOCKS[currentBlockIndex];
  if (!block || itemIndex < 0) return; // already at the first item — ignore

  clearAdvanceTimer();
  if (itemIndex >= block.items.length) {
    closeViewer();
    return;
  }

  currentItemIndex = itemIndex;
  const item = block.items[itemIndex];

  const segmentsWrap = document.getElementById("storySegments");
  const segs = segmentsWrap.querySelectorAll(".segment");
  segs.forEach((seg, i) => {
    seg.classList.toggle("is-done", i < itemIndex);
    seg.classList.toggle("is-active", i === itemIndex);
    const span = seg.querySelector("span");
    span.style.transition = "none";
    span.style.width = i < itemIndex ? "100%" : "0%";
  });

  // Only pause/resume music on an actual transition into or out of a
  // video — calling pauseForVideo() again while already paused (e.g.
  // two videos back-to-back in the same block) would overwrite the
  // controller's "was it playing before" flag with the already-paused
  // state, permanently losing whether music was really playing before
  // the first video.
  const wasVideo = currentIsVideo;
  const isVideo = item.type === "video";
  if (isVideo && !wasVideo) musicControls.pauseForVideo();
  if (!isVideo && wasVideo) musicControls.resumeAfterVideo();
  currentIsVideo = isVideo;

  const mediaWrap = document.getElementById("storyMedia");
  mediaWrap.innerHTML = mediaFull(item);

  if (isVideo) {
    const videoEl = mediaWrap.querySelector("video");
    videoEl.addEventListener("ended", () => showItem(currentItemIndex + 1), { once: true });
    videoEl.addEventListener("timeupdate", () => {
      if (!videoEl.duration) return;
      const activeSpan = segmentsWrap.querySelector(".segment.is-active > span");
      if (activeSpan) activeSpan.style.width = `${(videoEl.currentTime / videoEl.duration) * 100}%`;
    });
  } else {
    const activeSpan = segmentsWrap.querySelector(".segment.is-active > span");
    if (activeSpan) {
      requestAnimationFrame(() => {
        activeSpan.style.transition = `width ${AUTO_ADVANCE_MS}ms linear`;
        activeSpan.style.width = "100%";
      });
    }
    advanceTimer = setTimeout(() => showItem(currentItemIndex + 1), AUTO_ADVANCE_MS);
  }
}

function setupStoryViewer() {
  const viewer = document.getElementById("storyViewer");
  document.getElementById("storyClose").addEventListener("click", closeViewer);
  document.getElementById("storyPrev").addEventListener("click", () => showItem(currentItemIndex - 1));
  document.getElementById("storyNext").addEventListener("click", () => showItem(currentItemIndex + 1));
  document.addEventListener("keydown", (e) => {
    if (!viewer.classList.contains("is-open")) return;
    if (e.key === "Escape") closeViewer();
    if (e.key === "ArrowRight") showItem(currentItemIndex + 1);
    if (e.key === "ArrowLeft") showItem(currentItemIndex - 1);
  });
}

function applyLangAndRerender() {
  document.documentElement.lang = LANG;
  document.documentElement.dir = LANG === "he" ? "rtl" : "ltr";
  applyStaticI18n();
  setGrouping(GROUPING);
}

async function init() {
  const { tripMeta, photos } = await loadTripData();

  if (!tripMeta) {
    document.getElementById("storyTray").innerHTML = `<div class="empty-state"><p>${t("loadError")}</p></div>`;
    return;
  }

  TRIP_META = tripMeta;
  PHOTOS = photos;

  applyLangAndRerender();
  setupGroupToggle();
  setupTray();
  setupStoryViewer();
  setupLangToggle(applyLangAndRerender);
  musicControls = setupMusicPlayback();
}

init();
