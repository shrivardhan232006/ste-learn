---
name: ste-learning
description: Teach the user any topic as a study-manual web page written in ASD-STE100 Simplified Technical English, with drawn diagrams, real photos, charts, interactive models and a check-in question per chapter, published to the user's GitHub Pages repo (ste-learn) with the README listing every page URL. Use when the user says "teach me", "help me learn/understand/explore X", "make a study manual", "STE lesson", or /ste-learning.
---

# STE Learning — study manuals in Simplified Technical English

You turn any topic into a **study manual**: one web page, written in strict
ASD-STE100, with visuals and check-ins, published to
`https://shrivardhan232006.github.io/ste-learn/lessons/<slug>/`.
The repo README and home page list every lesson URL.

### Step 0 — get the toolkit (every run)

The scripts and design files live in two places: this skill's folder (if it was
installed from the .zip) and the `toolkit/` folder of the lessons repo. Set `T`:

1. If `scripts/publish.sh` exists next to this SKILL.md → `T` = this skill's folder.
2. Else: call `add_repo` (owner `shrivardhan232006`, repo `ste-learn`, access `push`),
   then `git clone --depth 1 https://github.com/shrivardhan232006/ste-learn /home/claude/ste-learn`
   (skip the clone if `git -C /home/claude/ste-learn rev-parse HEAD` works) → `T` = `/home/claude/ste-learn/toolkit`.

Always run publish with `STE_WORKDIR=/home/claude/ste-learn` when that clone exists.
All paths below are relative to `T`.

Files in the toolkit:

| Path | Use |
|---|---|
| `references/ste-rules.md` | The STE rules you must follow. **Read it before you write.** |
| `assets/lesson-template.html` | Page skeleton with every component. Copy it, fill it, delete unused parts. |
| `assets/manual.css`, `assets/manual.js` | Shared design and behavior (sidebar, scroll-spy, check-ins, progress, theme, chart helper). Never inline-edit them per lesson. |
| `scripts/ste_lint.py` | Heuristic STE checker. Must report 0 errors before publish. |
| `scripts/preview.py` | Local screenshots (light, dark, phone). |
| `scripts/publish.sh` | Copies lesson + assets into the repo, rebuilds README and home page, pushes, turns on Pages. |
| `scripts/build_index.py` | Called by publish.sh. Generates README.md + index.html from `lessons/*/meta.json`. |
| `scripts/inline_assets.py` | Fallback: one self-contained HTML file to publish as an Artifact. |

---

## Workflow

Make a task list with these steps. Tick them off as you go.

### 1. Ask before you build (scope and level)

The user wants questions **before** the lesson. Use `AskUserQuestion` once, with up
to 4 questions. Skip a question if the message already answers it. Good set:

1. **What do you know now?** — "New to it" / "Know the basics" / "Studied it in a course" / "Use it at work"
2. **Why do you want it?** — "Exam / course" / "A project" / "Curiosity" / "Interview prep"
3. **How deep?** — "15-min overview" / "30-min working knowledge" / "60-min deep dive (equations, edge cases)"
4. **Which angles?** (multiSelect) — 3–4 sub-areas specific to the topic, e.g. for "transformers": attention math / training / inference & KV cache / interpretability.

If the user is not present (scheduled run, no answer), pick: "Know the basics", "Curiosity", "30-min", the two most central angles — and say so in one line at the top of your reply.

Use what you already know about the user's background to choose examples and analogies. Never write personal details into the page or the repo — both are public.

### 2. Research

- Run 3–8 `WebSearch` calls (more for a deep dive). Search for current facts, standard equations, real numbers, and good public-domain or CC images.
- Prefer primary sources: textbooks, university notes, official docs, papers, standards bodies, Wikipedia for orientation.
- Keep a list of sources with URLs. They go in the "Go further" chapter.
- Never invent data for a chart. Either cite the data source or **calculate** it from a stated formula and say so in the caption ("Calculated values, not measured values…").

### 3. Plan the manual

Write a short plan (in your head or scratch file), not shown unless the user asks:

- **Title** (serif H1), **short name** (sidebar, 2–3 words), **slug** (kebab-case).
- **The one idea**: the single sentence the learner must keep if they forget all else.
- **4–7 chapters** for 15–30 min, up to 9 for a deep dive. Order: Summary → mental model/parts → mechanism → explore (interactive) → quantitative (equations, chart) → practice/procedure → checklist → go further → glossary.
- **One visual per concept chapter at minimum.** Use the table below.
- **One check-in per teaching chapter** (not for Summary, Checklist, Go further, Glossary).

| The idea is about… | Use |
|---|---|
| Parts and how they connect | Labeled inline SVG section/block diagram with leader lines (Figure 1 style) |
| A sequence or cycle | `fig-grid` of 2–4 panels (A, B, C, D) or a flow diagram with arrows and pills |
| Something that changes with a parameter | Interactive widget (range slider → redraw SVG), with live readout chips |
| Numbers, trends, a relationship | Chart (Chart.js via `Manual.chart`) — data cited or calculated |
| What the real thing looks like | Real photo (see Photos) |
| A comparison | Table in `.table-wrap` |
| Steps the reader does | `ol.steps` with WARNING / CAUTION callouts before the step |

### 4. Write the page

1. Copy `assets/lesson-template.html` to `/home/claude/lessons/<slug>/index.html` — **outside** the repo clone, because `publish.sh` resets the clone to `origin/main`. Write `meta.json` next to it:
   ```json
   {"title": "...", "short": "...", "summary": "one line", "date": "YYYY-MM-DD",
    "level": "Intro|Intermediate|Advanced", "minutes": 20, "tags": ["...", "..."]}
   ```
2. Replace every `{{…}}`. Delete component examples you do not use. Each chapter is
   `<section class="chapter" id="<slug>" data-short="<sidebar label>">` with an empty
   `<span class="num">` (the script numbers it) and an `<h2>`.
3. **Write all prose in STE** (`references/ste-rules.md`). The hard limits:
   - Descriptive sentence ≤ 25 words. Procedure sentence ≤ 20 words. Paragraph ≤ 6 sentences.
   - Active voice. Simple present / past / future only. No "-ing" verb forms.
   - One topic per sentence. One instruction per step, imperative, condition first.
   - No semicolons. No phrasal verbs. One word = one meaning, the same term everywhere.
   - Technical nouns and verbs of the topic are allowed: mark the first use with
     `<dfn data-term="term">term</dfn>` and define every one in the Glossary (one STE sentence each).
4. Make the top of each chapter say its main point first (top-down).
5. Put formulas in plain HTML (`<sup>`, `<sub>`, `·`, `−`, `×`) or `<code>`. Explain each symbol in a sentence.

### 5. Visuals

**Design language** — match the existing manuals (warm white, terracotta, flat):

- Colors only through CSS variables / helper classes: `--accent` (terracotta) for the thing to look at, `--accent-soft`/`--accent-tint` for fills, `--panel`/`--panel-2` for neutral surfaces, `--ink` for strokes and text, `--blue`/`--blue-soft` for a second series (cool, e.g. fresh gas, data flow B), `--muted` for secondary.
- SVG text uses the sans font; use `class="mono"` for values, coordinates, code names.
- Labels: bold 16–18 px text with a thin `--muted` leader line and an accent dot at the target. Or orange pills (`<g class="pill">`). Or numbered circles (`<g class="callout-num">`) with a legend in the caption.
- Flat shapes, rounded corners (rx 10–14), 2–2.5 px strokes. No drop shadows inside SVG. Heat maps may use blurred accent/blue blobs.
- Every SVG has `viewBox`, `role="img"` and `aria-label` or `<title>`. Every figure gets a caption written in STE. Use `figure.numbered` for automatic "Figure N." labels.
- If the same drawing appears several times (static figure, panels, widget), write **one JS draw function** and call it with different parameters — as in the sample lesson.

**Photos**

- In chat, you may call `image_search` to show the user photos while you discuss.
- On the page, embed only images you can credit with a free license: Wikimedia Commons (use `https://commons.wikimedia.org/wiki/Special:FilePath/<File_name>?width=1280` as `src`, link the file page in the credit), NASA, NOAA, USGS, or other public-domain/CC sources.
- Confirm the author and license before you embed. The Commons file page may block WebFetch: open it in the browser and run `({author: document.querySelector('#fileinfotpl_aut')?.nextElementSibling?.innerText, license: [...document.querySelectorAll('.licensetpl_short')].map(e => e.innerText)})`. If you cannot confirm the license, do not embed the photo; show it in chat with `image_search` instead.
- Always add `<span class="credit" data-ste="skip">Photo: <a href="file page">title/author</a>, license, via source</span>` in the caption.
- Never use photos of real private people, photos of anyone under 18, film/TV/game stills, artworks, logos, or copyrighted characters.

**Charts** — load Chart.js from cdnjs (already in the template) and draw with:
```js
Manual.chart("canvasId", (c) => ({ type: "line", data: {...}, options: {...} }));
```
`c` holds theme colors (`c.accent`, `c.blue`, `c.line`, `c.series[]`…). The helper redraws on theme change.

**Interactive widgets** — `.widget` > `.stage` (SVG) + `.controls` (`.control` rows with `input[type=range]` + `<output>`), readouts as `.chip`s, optional `.btn` Play/Pause with `requestAnimationFrame`. Keep all state in JS variables (no storage).

### 6. Check-ins (one at the end of each teaching chapter)

```html
<div class="check" data-answer="b">
  <span class="label">Check-in · Chapter short name</span>
  <p class="q">One clear question on the main idea of the chapter.</p>
  <div class="opts">
    <button class="opt" type="button" data-k="a"><span class="k">A</span><span>…</span></button>
    <button class="opt" type="button" data-k="b"><span class="k">B</span><span>…</span></button>
    <button class="opt" type="button" data-k="c"><span class="k">C</span><span>…</span></button>
  </div>
  <div class="why"><p>Why the answer is correct, and why the trap answer is wrong.</p></div>
</div>
```
- Test understanding, not recall of a word: predict, compare, calculate, or find the error.
- Distractors must be plausible: the most common misconception, a near-miss number (e.g. forget the exponent).
- Vary the position of the correct answer.
- The page counts correct check-ins plus `ul.checklist` boxes in the sidebar "Learning checklist".
- End with a Checklist chapter: 3–6 "I can …" statements that match the learning goals.

### 7. Check the page

1. `python3 scripts/ste_lint.py <lesson>/index.html` → fix every ERROR. Fix every WARN unless it is a defined technical noun (then add the `dfn`/glossary entry so the linter allows it).
2. `python3 scripts/preview.py <lesson> <scratch>/shots` → open the PNGs with Read. Look for: clipped SVGs, overlapping labels, unreadable dark mode, broken phone layout, JS errors. Fix and repeat.
3. Re-read the page once top-down as a learner. Does every chapter answer "why should I care" in its first sentence?

### 8. Publish

```bash
STE_WORKDIR=/home/claude/ste-learn STE_COMMIT_TRAILER="<attribution lines from the session, if any>" \
bash $T/scripts/publish.sh /home/claude/lessons/<slug> ste-learn
```
- The script prints `HOME_URL`, `LESSON_URL`, `REPO_URL`. It regenerates `README.md` (table with the URL of each page) and `index.html` (home page with lesson cards).
- The repo `shrivardhan232006/ste-learn` exists and GitHub Pages is on (main, root).
- **If the repo is not reachable** (exit 3, or "sessions are bound to their configured repositories"): call `add_repo` (owner `shrivardhan232006`, repo `ste-learn`, access `push`), clone it to the path it gives, set `STE_WORKDIR` to that path, and run again. A `push_check: refused` note from add_repo can be wrong — try the push and check with `git ls-remote origin`.
- `gh api` calls may be blocked by the session proxy. That is fine: the push is what matters. If the site 404s after 2 minutes, check Settings → Pages in the browser.
- GitHub Pages needs ~1 minute after a push. Then load `LESSON_URL` (browser `get_page_text`, or `WebFetch`) to confirm the page is live, and look at one screenshot in the browser to confirm fonts, photos and charts load.
- **If GitHub publishing is not possible at all**: run `scripts/inline_assets.py` and publish the result with the Artifact tool, and say in one line why.

### 9. Reply in chat

Keep it short, and in STE:
1. One line: what the manual covers + the lesson link.
2. **Ask the first check-in question in chat** (from chapter 2), so the user can start now. When they answer, give the result and the next chapter's question, one at a time.
3. Offer the three "Go further" directions as the next lesson options.
4. Sources list.

---

## Updating a lesson

Copy `lessons/<slug>/` from the repo clone to `/home/claude/lessons/<slug>/`, edit it there, bump `Rev N` in the sidebar and footer, lint, preview, and run `publish.sh` with that folder. To change the design of all pages, change `toolkit/assets/manual.css` / `manual.js` in the repo (and in the skill folder if installed from the .zip), commit, and republish any lesson (the script copies the assets every time).

## Quality bar

- Strict STE prose, 0 linter errors.
- Every concept chapter has a visual. At least one interactive widget and one chart where the topic has a parameter or numbers.
- Every number is cited or calculated. Every photo is credited.
- One check-in per teaching chapter, with an explanation.
- Works in light and dark mode and at phone width.
