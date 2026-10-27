/* STE Study Manual — shared behavior
   - builds the numbered sidebar from <section class="chapter" id=... data-short=...>
   - scroll-spy, mobile drawer, light/dark toggle
   - check-in questions (.check) and checklist (ul.checklist) with a progress card
   - Manual.colors() / Manual.chart() helpers for Chart.js in theme colors
   All storage is optional: if localStorage fails, the page still works. */
(function () {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const KEY = "ste-manual:" + location.pathname;
  const store = {
    get() { try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) { return {}; } },
    set(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* ignore */ } },
  };
  let state = store.get();
  state.checks = state.checks || {};
  state.boxes = state.boxes || {};

  // ---------- theme ----------
  try { const t = localStorage.getItem("ste-manual:theme"); if (t) document.documentElement.dataset.theme = t; } catch (e) {}
  function toggleTheme() {
    const cur = document.documentElement.dataset.theme ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("ste-manual:theme", next); } catch (e) {}
    document.dispatchEvent(new CustomEvent("manual:theme"));
  }

  function pad(n) { return String(n).padStart(2, "0"); }

  function init() {
    // ---------- chapters + toc ----------
    const chapters = $$("section.chapter[id]");
    const toc = $(".toc");
    chapters.forEach((sec, i) => {
      const n = pad(i + 1);
      const h2 = $("h2", sec);
      const short = sec.dataset.short || (h2 ? h2.textContent.trim() : sec.id);
      const head = $(".chapter-head .num", sec);
      if (head && !head.textContent.trim()) head.textContent = n;
      if (toc) {
        const li = document.createElement("li");
        li.innerHTML = `<a href="#${sec.id}"><span class="n">${n}</span><span>${short}</span></a>`;
        toc.appendChild(li);
      }
    });
    const links = toc ? $$("a", toc) : [];
    if ("IntersectionObserver" in window && chapters.length) {
      const vis = new Map();
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => vis.set(e.target.id, e.isIntersecting ? e.boundingClientRect.top : null));
        let best = null;
        for (const sec of chapters) {
          const r = sec.getBoundingClientRect();
          if (r.top < window.innerHeight * 0.35) best = sec.id;
        }
        links.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + best));
      }, { rootMargin: "0px 0px -60% 0px", threshold: [0, 0.01, 1] });
      chapters.forEach((s) => io.observe(s));
      window.addEventListener("scroll", () => {
        let best = null;
        for (const sec of chapters) if (sec.getBoundingClientRect().top < window.innerHeight * 0.35) best = sec.id;
        links.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + best));
      }, { passive: true });
    }
    links.forEach((a) => a.addEventListener("click", () => document.body.classList.remove("nav-open")));

    // ---------- drawer + theme buttons ----------
    $$("[data-action=menu]").forEach((b) => b.addEventListener("click", () => document.body.classList.toggle("nav-open")));
    $$(".scrim").forEach((s) => s.addEventListener("click", () => document.body.classList.remove("nav-open")));
    $$("[data-action=theme]").forEach((b) => b.addEventListener("click", toggleTheme));
    $$("[data-action=reset]").forEach((b) => b.addEventListener("click", () => {
      state = { checks: {}, boxes: {} }; store.set(state); location.reload();
    }));

    // ---------- check-ins ----------
    $$(".check").forEach((box, i) => {
      const id = box.id || "check-" + (i + 1);
      box.id = id;
      const answer = (box.dataset.answer || "").trim();
      const why = $(".why", box);
      const opts = $$(".opt", box);
      const lbl = $(".label", box);
      if (lbl && !lbl.dataset.done) { lbl.dataset.done = 1; }
      function finish(choice, restoring) {
        const right = choice === answer;
        opts.forEach((o) => {
          o.disabled = true;
          if (o.dataset.k === answer) o.classList.add("right");
          if (o.dataset.k === choice && !right) o.classList.add("wrong");
        });
        box.classList.add("answered");
        box.classList.toggle("missed", !right);
        if (why) {
          let v = $("b.v", why);
          if (!v) { v = document.createElement("b"); v.className = "v"; why.prepend(v); }
          v.textContent = right ? "Correct. " : "Not correct. ";
          let r = $(".retry", why);
          if (!right && !r) {
            r = document.createElement("button");
            r.className = "btn ghost retry"; r.type = "button"; r.textContent = "Try again";
            r.addEventListener("click", reset);
            why.appendChild(r);
          }
          if (right && r) r.remove();
        }
        if (!restoring) { state.checks[id] = { choice, right }; store.set(state); update(); }
      }
      function reset() {
        opts.forEach((o) => { o.disabled = false; o.classList.remove("right", "wrong"); });
        box.classList.remove("answered", "missed");
        delete state.checks[id]; store.set(state); update();
      }
      opts.forEach((o) => o.addEventListener("click", () => finish(o.dataset.k, false)));
      if (state.checks[id]) finish(state.checks[id].choice, true);
    });

    // ---------- checklist boxes ----------
    $$("ul.checklist input[type=checkbox]").forEach((cb, i) => {
      const id = cb.id || "box-" + (i + 1);
      cb.id = id;
      if (state.boxes[id]) cb.checked = true;
      cb.addEventListener("change", () => { state.boxes[id] = cb.checked; store.set(state); update(); });
    });

    update();
  }

  function update() {
    const checks = $$(".check");
    const boxes = $$("ul.checklist input[type=checkbox]");
    const total = checks.length + boxes.length;
    const done = checks.filter((c) => state.checks[c.id] && state.checks[c.id].right).length +
      boxes.filter((b) => b.checked).length;
    $$(".progress-card .count").forEach((el) => (el.textContent = `${done} / ${total}`));
    $$(".progress-card .bar > i").forEach((el) => (el.style.width = total ? (100 * done / total) + "%" : "0"));
  }

  // ---------- chart helpers ----------
  function colors() {
    const cs = getComputedStyle(document.documentElement);
    const v = (n) => cs.getPropertyValue(n).trim();
    return {
      ink: v("--ink"), muted: v("--muted"), line: v("--line"), bg: v("--bg"), panel: v("--panel"),
      accent: v("--accent"), accentInk: v("--accent-ink"), accentSoft: v("--accent-soft"), accentTint: v("--accent-tint"),
      blue: v("--blue"), ok: v("--ok"), warn: v("--warn"), danger: v("--danger"),
      series: [v("--accent"), v("--blue"), v("--ok"), v("--warn"), v("--muted")],
      sans: v("--sans"), mono: v("--mono"),
    };
  }
  // Manual.chart(canvas, makeConfig) — makeConfig(colors) returns a Chart.js config.
  // Re-renders automatically when the theme changes.
  function chart(canvas, makeConfig) {
    if (typeof canvas === "string") canvas = document.getElementById(canvas);
    let inst = null;
    function draw() {
      if (!window.Chart) return;
      const c = colors();
      Chart.defaults.font.family = c.sans; Chart.defaults.color = c.muted; Chart.defaults.borderColor = c.line;
      if (inst) inst.destroy();
      const cfg = makeConfig(c);
      cfg.options = Object.assign({ responsive: true, maintainAspectRatio: false, animation: { duration: 300 } }, cfg.options || {});
      inst = new Chart(canvas, cfg);
    }
    draw();
    document.addEventListener("manual:theme", draw);
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", draw);
    return { redraw: draw, get instance() { return inst; } };
  }

  window.Manual = { colors, chart, update };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
