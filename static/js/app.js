/* ==========================================================================
   Susrutha Health Partner - front-end application
   Plain vanilla JS (no build step) so the prototype runs anywhere Python runs.
   ========================================================================== */
(() => {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const CHRONIC_OPTIONS = [
    "Diabetes", "Heart disease", "Asthma / COPD", "Kidney disease",
    "Liver disease", "Cancer / low immunity", "Sickle cell disease", "High blood pressure",
  ];

  const state = {
    meta: null,
    groups: [],
    selected: new Set(),
    library: [],
    chronic: new Set(),
    facilities: [],
    map: null,
    markers: [],
    hereMarker: null,
    userLatLng: null,
    chatStarted: false,
    step: 1,
  };

  /* --------------------------------- utils -------------------------------- */
  async function api(path, options = {}) {
    const res = await fetch(path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) throw new Error(`Request failed (${res.status}) for ${path}`);
    return res.json();
  }

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function fmt(text) {
    return esc(text)
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/(^|\n)### (.+)/g, "$1<h3>$2</h3>")
      .replace(/(^|\n)_(.+?)_(?=\n|$)/g, "$1<em>$2</em>");
  }

  let toastTimer;
  function toast(message) {
    const el = $("#toast");
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
  }

  /* --------------------------------- modal -------------------------------- */
  function openModal(html) {
    const root = $("#modalRoot");
    root.innerHTML = `<div class="modal" data-close="1"><div class="modal-card">${html}</div></div>`;
    root.classList.add("open");
    root.querySelector(".modal").addEventListener("click", (e) => {
      if (e.target.dataset.close === "1") closeModal();
    });
  }
  function closeModal() {
    $("#modalRoot").classList.remove("open");
    $("#modalRoot").innerHTML = "";
  }

  /* ---------------------------------- tabs -------------------------------- */
  function showTab(name) {
    $$(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === `tab-${name}`));
    $$(".navlink").forEach((btn) => btn.classList.toggle("active", btn.dataset.tab === name));
    window.scrollTo({ top: 0, behavior: "smooth" });
    if (name === "care") {
      setTimeout(() => {
        initMap();
        if (state.map) {
          // Leaflet cannot size a hidden container, and the facility list may already have
          // loaded at boot - so re-measure and (re)draw the pins when the tab becomes visible.
          state.map.invalidateSize();
          renderMarkers();
        }
      }, 140);
    }
    // The condition list is prefetched at boot for the Find Care filters, so the grid itself
    // may still be empty the first time this tab is opened.
    if (name === "library" && !$("#libGrid").children.length) loadLibrary();
  }

  /* --------------------------------- theme -------------------------------- */
  function initTheme() {
    const saved = localStorage.getItem("susrutha-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = saved || (prefersDark ? "dark" : "light");
    document.documentElement.dataset.theme = theme;
    $("#themeBtn").textContent = theme === "dark" ? "☀️" : "🌙";
  }
  $("#themeBtn").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("susrutha-theme", next);
    $("#themeBtn").textContent = next === "dark" ? "☀️" : "🌙";
  });

  /* ---------------------------------- meta -------------------------------- */
  async function loadMeta() {
    try {
      const meta = await api("/api/meta");
      state.meta = meta;
      const stats = $$("#statStrip .stat strong");
      const values = [meta.stats.conditions, meta.stats.symptoms, meta.stats.facilities, meta.stats.sources.length];
      stats.forEach((el, i) => (el.textContent = values[i] ?? "—"));
      $("#sourceChips").innerHTML = meta.stats.sources
        .map((s) => `<span>${esc(s)}</span>`)
        .join("");
      $("#emgList").innerHTML = meta.emergency_numbers
        .map((n) => `<div><span>${esc(n.label)}</span><b>${esc(n.number)}</b></div>`)
        .join("");
      $("#footDisclaimer").textContent = meta.disclaimer;
    } catch (err) {
      console.error(err);
    }
  }

  /* ------------------------------ symptom checker -------------------------- */
  function renderSymptoms() {
    const wrap = $("#symGroups");
    wrap.innerHTML = state.groups
      .map((group, index) => `
        <section class="sym-group ${index === 0 ? "open" : ""}" data-group="${esc(group.id)}">
          <button class="sym-group-head" type="button" aria-expanded="${index === 0}">
            <span class="chev">▶</span><span>${esc(group.icon)} ${esc(group.name)}</span>
            <span class="sg-count">${group.symptoms.length} symptoms</span>
          </button>
          <div class="sym-group-body">
            <div class="chip-row">
              ${group.symptoms.map(chipHtml).join("")}
            </div>
          </div>
        </section>`)
      .join("");

    wrap.querySelectorAll(".sym-group-head").forEach((head) => {
      head.addEventListener("click", () => {
        const group = head.parentElement;
        group.classList.toggle("open");
        head.setAttribute("aria-expanded", group.classList.contains("open"));
      });
    });
    wrap.querySelectorAll(".chip").forEach((chip) => {
      chip.addEventListener("click", () => toggleSymptom(chip.dataset.id));
    });
  }

  function chipHtml(sym) {
    const searchText = [sym.label, sym.id.replace(/_/g, " "), ...(sym.keywords || [])]
      .join(" ").toLowerCase();
    return `<button type="button" class="chip ${sym.emergency ? "emergency" : ""}"
      data-id="${esc(sym.id)}" data-emergency="${sym.emergency ? "1" : "0"}"
      data-search="${esc(searchText)}"
      title="${sym.emergency ? "Red-flag symptom: this alone means urgent care" : "Select if you have this"}"
      >${esc(sym.label)}</button>`;
  }

  function toggleSymptom(id) {
    if (state.selected.has(id)) state.selected.delete(id);
    else state.selected.add(id);
    syncSymptoms();
  }

  function syncSymptoms() {
    $$("#symGroups .chip").forEach((chip) => {
      chip.classList.toggle("selected", state.selected.has(chip.dataset.id));
    });
    const tray = $("#selectedTray");
    const counter = $("#symCounter");
    counter.textContent = `${state.selected.size} selected`;
    if (!state.selected.size) {
      tray.innerHTML = `<span class="tray-empty">Nothing selected yet — tick the symptoms that apply to you.</span>`;
      return;
    }
    tray.innerHTML = Array.from(state.selected).map((id) => {
      const sym = findSym(id);
      const emergency = sym && sym.emergency;
      return `<button type="button" class="chip small ${emergency ? "emergency" : ""} selected" data-remove="${esc(id)}">
        ${esc(sym ? sym.label : id)} <span class="x">✕</span></button>`;
    }).join("");
    tray.querySelectorAll("[data-remove]").forEach((btn) =>
      btn.addEventListener("click", () => toggleSymptom(btn.dataset.remove)));
  }

  function findSym(id) {
    for (const g of state.groups) {
      const hit = g.symptoms.find((s) => s.id === id);
      if (hit) return hit;
    }
    return null;
  }

  function filterSymptoms(query) {
    // Token based, so "behind eyes" still finds "Pain behind the eyes", and keywords
    // are searched too ("loose motion" finds Diarrhoea).
    const tokens = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    $$("#symGroups .sym-group").forEach((group) => {
      let visible = 0;
      group.querySelectorAll(".chip").forEach((chip) => {
        const haystack = chip.dataset.search || chip.textContent.toLowerCase();
        const match = !tokens.length || tokens.every((t) => haystack.includes(t));
        chip.style.display = match ? "" : "none";
        if (match) visible++;
      });
      group.style.display = visible ? "" : "none";
      if (tokens.length && visible) group.classList.add("open");
    });
  }

  function renderChronicChips() {
    $("#chronicChips").innerHTML = CHRONIC_OPTIONS
      .map((name) => `<button type="button" class="chip" data-chronic="${esc(name)}">${esc(name)}</button>`)
      .join("");
    $$("#chronicChips .chip").forEach((chip) =>
      chip.addEventListener("click", () => {
        const name = chip.dataset.chronic;
        if (state.chronic.has(name)) state.chronic.delete(name);
        else state.chronic.add(name);
        chip.classList.toggle("selected", state.chronic.has(name));
      }));
  }

  function setStep(step) {
    state.step = step;
    [1, 2, 3].forEach((n) => $(`#step${n}`).classList.toggle("hidden", n !== step));
    $$(".stepdot").forEach((dot) => dot.classList.toggle("active", Number(dot.dataset.step) === step));
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function runAssessment() {
    const btn = $("#runAssess");
    btn.disabled = true;
    btn.textContent = "Analysing…";
    const days = $("#pDays").value;
    const profile = {
      age: $("#pAge").value,
      duration_days: days,
      severity: $("#pSeverity").value,
      pregnant: $("#pPregnant").checked,
      chronic: Array.from(state.chronic),
    };
    try {
      const result = await api("/api/assess", {
        method: "POST",
        body: JSON.stringify({ symptoms: Array.from(state.selected), profile }),
      });
      renderResult(result);
      setStep(3);
    } catch (err) {
      console.error(err);
      toast("Something went wrong. Please try again.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Get my guidance →";
    }
  }

  /* --------------------------- result rendering ---------------------------- */
  function careToneClass(tone) {
    return { critical: "tone-critical", high: "tone-high", medium: "tone-medium", low: "tone-low" }[tone] || "tone-low";
  }

  function renderResult(r) {
    const care = r.care;
    const parts = [];

    if (care.level === "emergency") {
      parts.push(`
        <div class="emg-alert">
          <h3>🚨 This pattern needs emergency care now</h3>
          <p>${esc(care.headline)}. Call <a href="tel:108">108</a> for an ambulance or <a href="tel:112">112</a>.</p>
          ${r.emergency_symptoms.length ? `<ul>${r.emergency_symptoms.map((s) => `<li>${esc(s.label)}</li>`).join("")}</ul>` : ""}
          <p style="margin-top:.6rem">Do not wait for an appointment or test result. Go to the nearest emergency department.</p>
        </div>`);
    }

    parts.push(`
      <div class="urgency ${careToneClass(care.tone)}">
        <div class="urgency-top">
          <span class="urgency-badge">${esc(care.label)}</span>
          ${r.risk_factors.length && care.level !== "emergency" ? `<span class="pill warn">Risk factors considered: ${esc(r.risk_factors.join(", "))}</span>` : ""}
        </div>
        <h3>${esc(care.headline)}</h3>
        <p>${esc(care.guidance)}</p>
      </div>`);

    if (r.insufficient_data) {
      parts.push(`<div class="notice">⚠️ You selected fewer than two symptoms, so the guidance above is deliberately cautious.
        Add more symptoms (and how long you have had them) for a more useful pattern comparison.</div>`);
    }
    if (r.ambiguity_warning && care.level !== "emergency") {
      parts.push(`<div class="notice">🔀 More than one condition fits your symptoms almost equally well.
        That is normal — many illnesses share the same early symptoms. A clinician may need a test to tell them apart.</div>`);
    }
    if (r.risk_note) parts.push(`<div class="notice">🧭 ${esc(r.risk_note)}</div>`);

    const left = [];
    left.push(`
      <div class="card">
        <h4>🧭 What to do now</h4>
        <ul class="kv-list">${r.next_steps.map((s) => `<li>${esc(s)}</li>`).join("")}</ul>
        <div class="pill-row" style="margin-top:.9rem">
          ${r.primary_id ? `<button class="btn btn-primary" data-goto-care="${esc(r.primary_id)}">🏥 Find care for this</button>` : ""}
          <button class="btn btn-ghost" data-ask="I have ${esc(r.selected.map((s) => s.label.toLowerCase()).slice(0, 3).join(", "))}. What should I do?">💬 Ask Susrutha</button>
        </div>
      </div>`);

    if (r.red_flags.length) {
      left.push(`
        <div class="card">
          <h4>🚩 Red flags — go to an emergency department if any of these happen</h4>
          <ul class="kv-list">${r.red_flags.map((f) => `<li style="color:var(--danger)">${esc(f)}</li>`).join("")}</ul>
        </div>`);
    }
    if (r.precautions.length) {
      left.push(`
        <div class="card">
          <h4>🛡️ Precautions</h4>
          <ul class="kv-list">${r.precautions.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
        </div>`);
    }
    if (r.self_care.length) {
      left.push(`
        <div class="card">
          <h4>🏠 Care you can start at home</h4>
          <ul class="kv-list">${r.self_care.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
        </div>`);
    }

    const right = [];
    right.push(`
      <div class="card">
        <h4>🔬 How your pattern lines up</h4>
        <p class="small muted">Ranked by how many of your symptoms appear in each condition's published
          description. This is a similarity score, <strong>not a probability or a diagnosis</strong>.</p>
        ${r.matches.map((m) => `
          <div class="match">
            <div class="match-head">
              <span class="match-name">${esc(m.name)} <span>· ${esc(m.category)}</span></span>
              <span class="band">${esc(m.band)}</span>
            </div>
            <div class="bar"><div class="bar-fill" data-width="${m.match_percent}"></div></div>
            <small>${m.matched.length} of your symptoms match: ${esc(m.matched_labels.join(", ")) || "none"}
              ${m.missing_key.length ? ` · usually also seen with: ${esc(m.missing_key.join(", "))}` : ""}</small>
          </div>`).join("")}
      </div>`);

    if (r.tests.length) {
      right.push(`<div class="card"><h4>🧪 Tests a doctor may advise</h4>
        <div class="pill-row">${r.tests.map((t) => `<span class="pill">${esc(t)}</span>`).join("")}</div>
        <p class="small muted" style="margin-top:.6rem">Tests are ordered by a clinician based on your timeline — never start treatment on a guess.</p></div>`);
    }
    if (r.specialties.length) {
      right.push(`<div class="card"><h4>👩‍⚕️ Who to see in Hyderabad</h4>
        <div class="pill-row">${r.specialties.map((s) => `<span class="pill">${esc(s)}</span>`).join("")}</div></div>`);
    }
    right.push(`
      <div class="card">
        <h4>📋 Your input</h4>
        <div class="pill-row">${r.selected.map((s) => `<span class="pill">${esc(s.label)}</span>`).join("")}</div>
        <p class="small muted" style="margin-top:.6rem">Only used to compute this result. Nothing was saved or shared.</p>
      </div>`);
    if (r.sources.length) {
      right.push(`<div class="card"><h4>📚 Source for this guidance</h4>
        <div class="kv-list">${r.sources.map((s) => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>`).join("")}</div>
        <p class="src-line">${esc(r.disclaimer)}</p></div>`);
    }

    $("#resultRoot").innerHTML = `
      ${parts.join("")}
      <div class="result-grid" style="margin-top:1rem">
        <div>${left.join("")}</div>
        <div>${right.join("")}</div>
      </div>`;

    requestAnimationFrame(() => {
      $$("#resultRoot .bar-fill").forEach((bar) => (bar.style.width = `${bar.dataset.width}%`));
    });

    $$("#resultRoot [data-goto-care]").forEach((btn) =>
      btn.addEventListener("click", () => {
        showTab("care");
        $("#careCondition").value = btn.dataset.gotoCare;
        $("#careSpecialty").value = "All";
        loadFacilities();
      }));
    $$("#resultRoot [data-ask]").forEach((btn) =>
      btn.addEventListener("click", () => {
        openChat();
        sendChat(btn.dataset.ask);
      }));
  }

  /* -------------------------------- find care ------------------------------ */
  function initMap() {
    if (state.map || typeof L === "undefined") {
      if (typeof L === "undefined") $("#mapFallback").classList.remove("hidden");
      return;
    }
    state.map = L.map("map", { scrollWheelZoom: true }).setView([17.4126, 78.4448], 11.5);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(state.map);
  }

  function typeClass(type) {
    if (type === "Government") return { cls: "badge-govt", color: "#16a34a" };
    if (type === "Private") return { cls: "badge-private", color: "#5561f0" };
    return { cls: "badge-lab", color: "#d97706" };
  }

  function renderFacilities() {
    const list = $("#facilityList");
    const data = state.facilities;
    $("#facilityCount").textContent = `${data.length} shown`;
    if (!data.length) {
      list.innerHTML = `<p class="muted small">No facility matched that filter. Try “All specialties” or a different type.</p>`;
      return;
    }
    list.innerHTML = data.map((f) => {
      const badge = typeClass(f.type);
      return `
      <article class="fac-card">
        <div class="fac-top">
          <div>
            <div class="fac-name">${esc(f.name)}</div>
            <div class="fac-area">${esc(f.area)}</div>
          </div>
          <span class="badge ${badge.cls}">${esc(f.type)}</span>
        </div>
        ${f.tier ? `<div style="margin-top:.25rem"><span class="pill ${f.tier === "Best match" ? "best" : ""}">${esc(f.tier)}</span></div>` : ""}
        <div class="fac-addr">${esc(f.address)}</div>
        <div class="fac-tags">
          ${(f.matched_specialties.length ? f.matched_specialties : f.specialties).slice(0, 4)
            .map((s) => `<span class="pill">${esc(s)}</span>`).join("")}
        </div>
        <div class="fac-foot">
          <span class="dist">${f.distance_km !== null ? `📍 ${f.distance_km} km away` : "📍 see map"}</span>
          <span class="fac-actions"><a href="${esc(f.maps_url)}" target="_blank" rel="noopener">Directions →</a></span>
        </div>
        <div class="fac-note">${esc(f.note)}</div>
      </article>`;
    }).join("");
  }

  function renderMarkers() {
    if (!state.map || typeof L === "undefined") return;
    state.markers.forEach((m) => state.map.removeLayer(m));
    state.markers = [];
    state.facilities.forEach((f) => {
      const { color } = typeClass(f.type);
      const marker = L.circleMarker([f.lat, f.lng], {
        radius: 9, color: "#ffffff", weight: 2, fillColor: color, fillOpacity: 0.95,
      }).addTo(state.map);
      marker.bindPopup(`
        <b>${esc(f.name)}</b>
        ${esc(f.type)} · ${esc(f.area)}<br />
        ${esc(f.address)}<br />
        ${f.distance_km !== null ? `<b>${f.distance_km} km</b> from your area<br />` : ""}
        <a href="${esc(f.maps_url)}" target="_blank" rel="noopener">Get directions →</a>`);
      state.markers.push(marker);
    });
    if (state.markers.length) {
      const group = L.featureGroup(state.markers);
      state.map.fitBounds(group.getBounds().pad(0.18));
    }
  }

  async function loadFacilities() {
    const condition = $("#careCondition").value;
    const specialty = $("#careSpecialty").value;
    const sector = $("#careSector").value;
    const order = $("#careOrder").value;
    const locality = $("#careLocality").value;
    const params = new URLSearchParams();
    if (condition) params.set("condition", condition);
    if (specialty && specialty !== "All") params.set("specialty", specialty);
    if (sector) params.set("sector", sector);
    if (order) params.set("order", order);

    let origin = state.userLatLng;
    if (!origin && locality) {
      const loc = (state.meta && state.meta.__localities || []).find((l) => l.name === locality);
      if (loc) origin = { lat: loc.lat, lng: loc.lng };
    }
    if (origin) {
      params.set("lat", origin.lat);
      params.set("lng", origin.lng);
    }

    $("#facilityList").innerHTML = `<div class="skeleton-row"></div><div class="skeleton-row"></div>`;
    try {
      const data = await api(`/api/facilities?${params.toString()}`);
      state.facilities = data.results;
      $("#facilityTitle").textContent = data.condition ? `Care for ${data.condition}` : (specialty !== "All" ? specialty : "All facilities");
      const focused = Boolean(condition) || (specialty && specialty !== "All");
      const how = data.sorted_by === "distance" ? "nearest first" : "best specialty match first";
      $("#careMeta").textContent = focused
        ? `${data.total} facilities match · ${how}` + (origin ? "" : " · add your area for distances")
        : `Showing all ${data.total} mapped facilities` + (origin ? " · nearest first" : " · pick a condition or your area to narrow this down");
      renderFacilities();
      renderMarkers();
    } catch (err) {
      console.error(err);
      $("#facilityList").innerHTML = `<p class="muted small">Could not load facilities. Is the Python server running?</p>`;
    }
  }

  async function loadCareOptions() {
    const [lib, specs, fac] = await Promise.all([
      api("/api/library"),
      api("/api/specialties"),
      api("/api/facilities?limit=1"),
    ]);
    state.library = lib.items;
    state.meta.__localities = fac.localities;
    $("#careCondition").innerHTML =
      `<option value="">Any condition</option>` +
      lib.items.map((c) => `<option value="${esc(c.id)}">${esc(c.name)}</option>`).join("");
    $("#careSpecialty").innerHTML =
      `<option value="All">All specialties</option>` +
      specs.specialties.map((s) => `<option value="${esc(s)}">${esc(s)}</option>`).join("");
    $("#careLocality").innerHTML =
      `<option value="">My area / all</option>` +
      fac.localities.map((l) => `<option value="${esc(l.name)}">${esc(l.name)}</option>`).join("");
    $("#libFilters").innerHTML =
      `<button class="chip small selected" data-filter="All">All</button>` +
      Array.from(new Set(lib.items.map((c) => c.category)))
        .sort()
        .map((c) => `<button class="chip small" data-filter="${esc(c)}">${esc(c)}</button>`).join("");
  }

  function useLocation() {
    if (!navigator.geolocation) {
      toast("Geolocation is not available in this browser.");
      return;
    }
    const btn = $("#useLocation");
    let settled = false;
    // Some browsers never call either callback (permission prompt dismissed, or no
    // location provider available). Without this guard the button would stay on
    // "Locating…" forever and the list would never refresh.
    const giveUp = setTimeout(() => {
      if (settled) return;
      settled = true;
      btn.textContent = "📍 Use my exact location";
      toast("No location received — pick your area from the list instead.");
    }, 12000);

    btn.textContent = "📍 Locating…";
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        if (settled) return;
        settled = true;
        clearTimeout(giveUp);
        state.userLatLng = { lat: +pos.coords.latitude.toFixed(4), lng: +pos.coords.longitude.toFixed(4) };
        btn.textContent = "📍 Using your exact location";
        if (state.map && typeof L !== "undefined") {
          if (state.hereMarker) state.map.removeLayer(state.hereMarker);
          state.hereMarker = L.circleMarker([state.userLatLng.lat, state.userLatLng.lng], {
            radius: 7, color: "#fff", weight: 2, fillColor: "#0f172a", fillOpacity: 1,
          }).addTo(state.map).bindPopup("You are here");
        }
        loadFacilities();
      },
      () => {
        if (settled) return;
        settled = true;
        clearTimeout(giveUp);
        btn.textContent = "📍 Use my exact location";
        toast("Location not available — pick your area from the list instead.");
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 }
    );
  }

  /* --------------------------------- library ------------------------------- */
  async function loadLibrary(query = "") {
    const grid = $("#libGrid");
    grid.innerHTML = `<div class="skeleton-row"></div><div class="skeleton-row"></div><div class="skeleton-row"></div>`;
    try {
      const data = await api(`/api/library${query ? `?q=${encodeURIComponent(query)}` : ""}`);
      state.library = data.items;
      $("#libCount").textContent = `${data.items.length} conditions`;
      grid.innerHTML = data.items.map((c) => `
        <article class="lib-card" data-cond="${esc(c.id)}">
          <span class="lib-cat">${esc(c.category)}${c.aka ? ` · ${esc(c.aka)}` : ""}</span>
          <span class="lib-name">${esc(c.name)}</span>
          <span class="care-pill cp-${esc(c.care_level)}">${esc(c.care_label)}</span>
          <p>${esc(c.overview.slice(0, 150))}…</p>
          <span class="flink">Read the guide →</span>
        </article>`).join("");
      grid.querySelectorAll("[data-cond]").forEach((card) =>
        card.addEventListener("click", () => openCondition(card.dataset.cond)));
    } catch (err) {
      console.error(err);
      grid.innerHTML = `<p class="muted small">Could not load the library.</p>`;
    }
  }

  async function openCondition(id) {
    try {
      const c = await api(`/api/conditions/${id}`);
      openModal(`
        <div class="modal-head">
          <div>
            <span class="lib-cat">${esc(c.category)}${c.aka ? ` · ${esc(c.aka)}` : ""}</span>
            <h2 style="margin:.2rem 0 .4rem">${esc(c.name)}</h2>
            <span class="care-pill cp-${esc(c.care_level)}">${esc(c.care_label)}</span>
          </div>
          <button class="iconbtn" data-close="1" aria-label="Close">✕</button>
        </div>
        <div class="modal-body">
          <p>${esc(c.overview)}</p>

          <h4>Commonly reported symptoms</h4>
          <div class="pill-row">${c.symptom_labels.map((s) =>
            `<span class="pill">${esc(s.label)}</span>`).join("")}</div>

          <h4 style="margin-top:1.1rem;color:var(--danger)">Red flags — see a doctor immediately</h4>
          <ul class="kv-list">${c.red_flags.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>

          <h4 style="margin-top:1.1rem">Precautions</h4>
          <ul class="kv-list">${c.precautions.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>

          ${c.self_care && c.self_care.length ? `
            <h4 style="margin-top:1.1rem">Home care for mild cases</h4>
            <ul class="kv-list">${c.self_care.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>` : ""}

          <h4 style="margin-top:1.1rem">Tests a doctor may advise</h4>
          <div class="pill-row">${c.tests.map((t) => `<span class="pill">${esc(t)}</span>`).join("")}</div>

          <h4 style="margin-top:1.1rem">Specialties / where to go in Hyderabad</h4>
          <div class="pill-row">${c.specialties.map((s) => `<span class="pill">${esc(s)}</span>`).join("")}</div>

          <div class="pill-row" style="margin-top:1.2rem">
            <button class="btn btn-primary" data-care="${esc(c.id)}">🏥 Find facilities for ${esc(c.name)}</button>
            <button class="btn btn-ghost" data-tab="${esc("checker")}">🩺 Check my symptoms</button>
          </div>

          <p class="src-line">Source: ${c.sources.map((s) =>
            `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>`).join(" · ")}<br />
            ${esc((state.meta && state.meta.disclaimer) || "")}</p>
        </div>`);
      const root = $("#modalRoot");
      root.querySelectorAll("[data-close]").forEach((b) => b.addEventListener("click", closeModal));
      const careBtn = root.querySelector("[data-care]");
      if (careBtn) careBtn.addEventListener("click", () => {
        closeModal();
        showTab("care");
        $("#careCondition").value = careBtn.dataset.care;
        loadFacilities();
      });
      const checkBtn = root.querySelector("[data-tab]");
      if (checkBtn) checkBtn.addEventListener("click", () => { closeModal(); showTab("checker"); });
    } catch (err) {
      console.error(err);
      toast("Could not open that guide.");
    }
  }

  /* ---------------------------------- chat --------------------------------- */
  function openChat() {
    $("#chatPanel").classList.add("open");
    $("#chatFab").classList.add("hidden");
    if (!state.chatStarted) {
      state.chatStarted = true;
      sendChat("");
    }
    setTimeout(() => $("#chatInput").focus(), 120);
  }
  function closeChatPanel() {
    $("#chatPanel").classList.remove("open");
    $("#chatFab").classList.remove("hidden");
  }

  function pushMessage(role, text, extra = {}) {
    const body = $("#chatBody");
    const div = document.createElement("div");
    div.className = `msg ${role}${extra.urgent ? " urgent" : ""}`;
    div.innerHTML = fmt(text) + (extra.actions || []).map((a) =>
      `<button class="action-btn" data-action='${esc(JSON.stringify(a))}'>${esc(a.label)}</button>`).join("");
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
    div.querySelectorAll(".action-btn").forEach((btn) =>
      btn.addEventListener("click", () => {
        const action = JSON.parse(btn.dataset.action);
        if (action.type === "tab") { closeChatPanel(); showTab(action.target); }
        if (action.type === "facilities") {
          closeChatPanel();
          showTab("care");
          setTimeout(() => { $("#careCondition").value = action.target; loadFacilities(); }, 200);
        }
      }));
    return div;
  }

  function pushTyping() {
    const body = $("#chatBody");
    const div = document.createElement("div");
    div.className = "msg bot";
    div.id = "typingMsg";
    div.innerHTML = `<span class="typing"><i></i><i></i><i></i></span>`;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
    return div;
  }

  function renderSuggestions(list) {
    $("#chatSuggest").innerHTML = (list || [])
      .map((s) => `<button type="button" data-suggest="${esc(s)}">${esc(s)}</button>`).join("");
    $$("#chatSuggest button").forEach((btn) =>
      btn.addEventListener("click", () => sendChat(btn.dataset.suggest)));
  }

  async function sendChat(message) {
    if (message) pushMessage("user", message);
    const typing = pushTyping();
    try {
      const data = await api("/api/chat", { method: "POST", body: JSON.stringify({ message }) });
      typing.remove();
      pushMessage("bot", data.reply, { urgent: data.urgent, actions: data.actions });
      renderSuggestions(data.suggestions);
      if (data.urgent) toast("Emergency guidance shown — call 108 if this is happening now.");
    } catch (err) {
      console.error(err);
      typing.remove();
      pushMessage("bot", "Sorry, I could not reach the server. Please make sure the Python app is running.");
    }
  }

  /* ---------------------------------- wiring ------------------------------- */
  function wire() {
    $$("[data-tab]").forEach((el) =>
      el.addEventListener("click", (e) => {
        e.preventDefault();
        showTab(el.dataset.tab);
      }));
    $$("[data-feature]").forEach((el) =>
      el.addEventListener("click", () => { if (el.dataset.feature === "chat") openChat(); }));

    $("#emergencyBtn").addEventListener("click", () => {
      const numbers = (state.meta && state.meta.emergency_numbers) || [];
      openModal(`
        <div class="modal-head">
          <h2 style="margin:0">🚨 Emergency help</h2>
          <button class="iconbtn" data-close="1">✕</button>
        </div>
        <div class="modal-body">
          <p><strong>If someone is unconscious, not breathing, has chest pain, heavy bleeding,
            a seizure or sudden weakness, call for help immediately.</strong></p>
          <div class="emg-list">${numbers.map((n) => `<div><span>${esc(n.label)}</span><b>${esc(n.number)}</b></div>`).join("")}</div>
          <p class="small muted" style="margin-top:.9rem">Then open <strong>Find Care</strong> to see the
            nearest emergency departments in Hyderabad, or use Google Maps for turn-by-turn directions.</p>
          <div class="pill-row"><button class="btn btn-primary" data-close="1">I understand</button></div>
        </div>`);
      $$("#modalRoot [data-close]").forEach((b) => b.addEventListener("click", closeModal));
    });
    $("#emergencyBtn2").addEventListener("click", () => $("#emergencyBtn").click());

    // symptom checker
    $("#symSearch").addEventListener("input", (e) => filterSymptoms(e.target.value));
    $("#clearSymptoms").addEventListener("click", () => { state.selected.clear(); syncSymptoms(); });
    $("#toStep2").addEventListener("click", () => {
      if (!state.selected.size) return toast("Please select at least one symptom first.");
      setStep(2);
    });
    $("#backToStep1").addEventListener("click", () => setStep(1));
    $("#editAnswers").addEventListener("click", () => setStep(2));
    $("#runAssess").addEventListener("click", runAssessment);
    $("#restart").addEventListener("click", () => {
      state.selected.clear(); state.chronic.clear();
      $("#pAge").value = ""; $("#pDays").value = ""; $("#pSeverity").value = "moderate";
      $("#pPregnant").checked = false;
      renderChronicChips(); syncSymptoms(); setStep(1);
    });

    // find care
    ["careCondition", "careSpecialty", "careSector", "careLocality", "careOrder"].forEach((id) =>
      $(`#${id}`).addEventListener("change", () => {
        if (id === "careLocality") state.userLatLng = null;
        loadFacilities();
      }));
    $("#useLocation").addEventListener("click", useLocation);

    // library
    let libTimer;
    $("#libSearch").addEventListener("input", (e) => {
      clearTimeout(libTimer);
      libTimer = setTimeout(() => loadLibrary(e.target.value), 260);
    });
    $("#libFilters").addEventListener("click", (e) => {
      const btn = e.target.closest("[data-filter]");
      if (!btn) return;
      $$("#libFilters .chip").forEach((c) => c.classList.toggle("selected", c === btn));
      const category = btn.dataset.filter;
      const items = category === "All" ? state.library : state.library.filter((c) => c.category === category);
      $("#libGrid").innerHTML = items.map((c) => `
        <article class="lib-card" data-cond="${esc(c.id)}">
          <span class="lib-cat">${esc(c.category)}</span>
          <span class="lib-name">${esc(c.name)}</span>
          <span class="care-pill cp-${esc(c.care_level)}">${esc(c.care_label)}</span>
          <p>${esc(c.overview.slice(0, 150))}…</p>
          <span class="flink">Read the guide →</span>
        </article>`).join("");
      $$("#libGrid [data-cond]").forEach((card) =>
        card.addEventListener("click", () => openCondition(card.dataset.cond)));
    });

    // chat
    $("#chatFab").addEventListener("click", openChat);
    $("#chatClose").addEventListener("click", closeChatPanel);
    $("#chatForm").addEventListener("submit", (e) => {
      e.preventDefault();
      const input = $("#chatInput");
      const value = input.value.trim();
      if (!value) return;
      input.value = "";
      sendChat(value);
    });
    $("#heroChatInput").addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const value = e.target.value.trim();
        if (!value) return;
        e.target.value = "";
        openChat();
        setTimeout(() => sendChat(value), 250);
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { closeModal(); closeChatPanel(); }
    });

    // first-run safety notice
    if (!localStorage.getItem("susrutha-notice")) {
      setTimeout(() => {
        openModal(`
          <div class="modal-head">
            <div><h2 style="margin:.1rem 0 .3rem">Welcome to Susrutha Health Partner</h2>
            <span class="lib-cat">Healthcare accessibility &amp; early assistance · Hyderabad</span></div>
          </div>
          <div class="modal-body">
            <p>This tool helps you <strong>understand symptoms, learn what they could mean and find
              the right facility</strong> in Hyderabad. Before you start, please note:</p>
            <ul class="kv-list">
              <li>✅ It gives general information from <strong>WHO, CDC, NHS and MedlinePlus</strong> sources.</li>
              <li>❌ It is <strong>not a diagnosis</strong> and cannot rule out serious illness.</li>
              <li>🔒 It stores nothing — no login, no database, nothing shared.</li>
              <li>🚑 For emergencies call <strong>108 / 112</strong> or reach the nearest emergency department.</li>
            </ul>
            <p class="small muted">By continuing you understand that a qualified doctor must confirm any
              condition and prescribe treatment.</p>
            <div class="pill-row">
              <button class="btn btn-primary" id="noticeOk">I understand — continue</button>
              <button class="btn btn-ghost" id="noticeEmg">🚑 Emergency numbers</button>
            </div>
          </div>`);
        $("#noticeOk").addEventListener("click", () => {
          localStorage.setItem("susrutha-notice", "1");
          closeModal();
        });
        $("#noticeEmg").addEventListener("click", () => { closeModal(); $("#emergencyBtn").click(); });
      }, 700);
    }
  }

  /* ----------------------------------- boot -------------------------------- */
  async function boot() {
    initTheme();
    wire();
    try {
      const [meta, symptoms] = await Promise.all([api("/api/meta"), api("/api/symptoms")]);
      state.meta = meta;
      state.groups = symptoms.groups;
      renderSymptoms();
      renderChronicChips();
      syncSymptoms();
      await loadMeta();
      await loadCareOptions();
      await loadFacilities();
    } catch (err) {
      console.error(err);
      toast("Could not load the knowledge base. Is the Python server running?");
    }
  }

  boot();
})();
