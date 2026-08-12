# Focus Funnel

A single-file, zero-dependency productivity web app. Brain-dump tasks, funnel the 3
that matter into "Today," and run the top one on a Pomodoro timer with ambient focus
sound. Built for personal daily use.

> **✓ Cross-device sync — DONE (Phase 2 shipped 2026-07-06, confirmed on laptop+phone).** Footer
> **☁️ Sync** panel: paste Worker URL + key (stored under a separate localStorage key
> `focus-funnel.sync`, NOT in `state`, never pushed). Engine hooks `save()` → pull-on-open +
> debounced push + ~20s periodic pull, last-write-wins by timestamp (`{updatedAt,state}` blob),
> offline cache, footer status dot. Worker `sync-worker/worker.js` live at
> `https://focus-funnel-sync.samxiangli.workers.dev/` (header `x-sync-key`). Full details +
> URL/key/KV-id in the `focus-funnel-cloud-sync` auto-memory.

## What it is

- **Core app is one file: `index.html`.** All HTML, CSS, and JavaScript inline. No build
  step, no server, no npm, no internet required. Open the file in a browser and it runs.
- Vanilla JavaScript (ES5-ish style, IIFE-wrapped, `"use strict"`). No frameworks.
- State persists to the browser's `localStorage` under the key `focus-funnel.v2`
  (migrates from `focus-funnel.v1` if present).
- **Installable PWA.** Ships a web app manifest + icons so it can be added to a phone's
  home screen and run full-screen. The only non-`index.html` files are these static
  assets (no build tooling):
  - `manifest.webmanifest` — PWA manifest (name, icons, standalone display).
  - `icon.svg` — favicon (browser tabs).
  - `icon-192.png`, `icon-512.png` — PWA / Android icons (also maskable).
  - `apple-touch-icon.png` — 180x180 iOS home-screen icon.
  - `make-icons.py` — regenerates all icons from scratch (stdlib only): `python3 make-icons.py`.
  - NOTE: PWA install needs HTTPS — works on the live GitHub Pages site, not from `file://`.

## How to run / use

- Open `index.html` directly in a browser: `open index.html` (macOS).
- IMPORTANT: data only persists when opened from a STABLE address (a real `file://`
  path or a fixed host). Temporary preview servers get a fresh localStorage bucket on
  each reload, so tasks won't stick there — use the real file for actual use.

## Features

- **Brain Dump → Today funnel** with drag-and-drop; max 3 tasks in Today.
- **Notepad** — sticky-note scratch space (`state.notes: [{id, text}]`) below the funnel.
  Quick capture before organizing; each note has **→ To-do** (converts to a Brain Dump
  task, parsing inline #tags) and ×; double-click a note to edit. Reverse path: each
  Brain Dump task has a 📝 button (and tasks can be dragged onto the Notepad card) —
  `taskToNote` folds tags back in as inline #tags and sub-tasks into the note text
  (est/priority are dropped).
- **Drag-to-reorder within Today** — the top task (green border) is what the timer runs.
- **Sub-tasks** per task (expandable checklist with progress count).
- **Time estimates** per task (minutes); Today header sums them.
- **Priority grading** per task — ⚑ flag cycles none → P1 (red) → P2 (amber) → P3 (blue);
  stored as `pri: 1|2|3|null`. "⇅ Priority" in the Brain Dump header sorts the dump P1-first.
- **Due dates** per task (`due: "YYYY-MM-DD"|null`) — 📅 pill opens a native date picker
  (hidden `#duePicker` + `showPicker()`); `dueState()` colors it overdue (red) / today / soon
  (amber); `fmtDue()` shows Today/Tmrw/short date. Part of the Phase-1 reliability roadmap.
- **Auto-backup** — rolling ring of the last 12 timestamped state snapshots in a SEPARATE
  localStorage key `focus-funnel.backups` (never in `state`, never synced). Snapshots taken once
  per day on open and right before every destructive action — clear-all, import, and an incoming
  cloud-sync overwrite (`pushBackup` before `applyRemote`), so a sync clobber is recoverable.
  Footer **🗄 Backups** panel lists them with per-row Restore (safe `fromObject` path, takes a
  "before restore" snapshot first) + Download. Quota-safe writes (drop-oldest-and-retry).
  Roadmap note: recurring tasks + reminders were consciously SKIPPED by Sam (2026-07-06); due
  dates + auto-backup shipped. Remaining phases: cloud sync ✅, integrations, AI.
- **Tags** per task — type `#tag` inline when adding (parsed out of the text), or click the 🏷
  pill to open a **tag picker** popover: all existing tags shown as selectable chips (click to
  add/remove), plus an input to create a new one. Tags render as deterministically-colored chips;
  clicking a chip filters Brain Dump, Today, and Done to that tag (filter bar with clear button).
  `state.*[].tags: string[]`. Each task row has a **done checkbox** (`.task-check`, after the
  drag grip) that toggles `done` in place (strikethrough, counts toward streak/done-today);
  the title is no longer click-to-complete. Rename a task by double-clicking its title.
  Delete a tag everywhere via the × on its picker chip. **Bulk-tag mode:** the ☑ Select toggle
  (Brain Dump header) turns Brain Dump + Today rows into checkboxes; a fixed bottom bar shows
  "N selected" + 🏷 Tag (opens the picker in `pickerMode="bulk"`, applying tags to all selected),
  Clear, and Done. Ephemeral `selectMode`/`selected` (not persisted).
- **Pomodoro timer** — Focus 25 / Break 5 / Long 15 modes. Spacebar toggles start/pause.
- **Completed-today counter & streak.** Streak = consecutive days that are "active" =
  a day with >=1 task completion OR >=1 completed focus session (`activeDaySet()`), so
  using the timer keeps the streak alive even without finishing a task.
- **Focus session tracking.** When a Focus-mode timer reaches 0, a session is recorded
  (`state.sessions: [{ts, mins, task}]`). Stats show "⏱ N sessions today"; a Focus Log card
  lists every session newest-first grouped by day (time-of-day + duration + task), with a
  today summary (count, focus minutes, morning/afternoon/evening split). "clear log" empties it.
- **Trash** — deleting a task (× on dump/today rows, or × on a Done item) moves it to
  `state.trash` with `deletedAt`/`from`, shown in a 🗑 Trash card at the bottom. ↩ Restore
  returns it to its origin (dump or Done); × there deletes forever; "empty trash" wipes all.
  Entries auto-purge after 30 days (filtered in `fromObject`). Bulk "clear" actions
  (clear finished / clear all data) remain permanent and bypass the trash.
- **Done list** — finishing the top task archives it to `state.done` (newest first) instead
  of deleting it; each item can be **↩ Restored** (un-finishes, returns to Brain Dump,
  decrements the completion credit for its `doneDate`) or removed (keeps the credit).
- **Ambient sound** while the timer runs, all synthesized live via WebAudio (no asset files),
  shared volume slider + 🔊 mute. Two separate selectors: **Focus** (`state.soundType`) —
  brown / pink / rain / ocean / stream / wind / campfire / ticks + 4 tick variants
  (ticksoft / tickwood / tickdeep / tickwatch, all from the `makeTicker(opts)` factory); **Break** (`state.breakSound`) —
  ticks / chimes / ocean / rain / silent. `BUILDERS` map keys each sound; `startFocusSound`
  picks `soundType` in focus mode, `breakSound` otherwise. The single `audio.tickTimer` slot is
  reused by timer-driven builders (ticks/fire/chime).
- **Alarm** (two-tone WebAudio) when a focus session ends; a brighter ascending chime
  (`breakOverChime`) when a break ends.
- **Pomodoro flow (manual):** NO auto-start. When a phase reaches 0, `finishTimer` logs the
  focus session (focus only), switches to the next mode, and plays one end sound. Focus uses
  `alarm()` once; break uses `breakOverChime()` once. The next phase waits for Start and there
  is no repeating alarm or stop-alarm button.
- **Light / dark theme** toggle.

## ⚠️ CURRENT DESIGN: "Gallery V3" (2026-07-20, branch `redesign/gallery-v3`)

The app now renders the **Gallery V3** design from `~/Downloads/design_handoff_focus_funnel/`
(README.md is the spec; `main-view-dark.png` the primary reference). This **supersedes the
Cockpit theme** described further down — that text is kept for history.

- **Look:** near-black "gallery" surface (`#111310` dark / `#F4F3EE` light) floating on a
  `#C9C8C1` page, one glowing lime accent `#BEE800` (`#A8CE00` for lime-as-text on light),
  **square corners everywhere**, 1px hairline dividers between sections.
- **Type:** Hanken Grotesk (display/UI) + Space Mono (all labels, metas, buttons, eyebrows),
  both **embedded as base64 woff2** in `index.html` — deliberately NOT Google Fonts, because
  Sam is in China where `fonts.gstatic.com` is commonly blocked and the app must work offline.
  Cost ≈ +83KB (144KB → 227KB). Hanken is one variable font covering weights 400–800.
- **Layout:** single centred column, `max-width:1180px`, padding `52/52/40`. Order:
  top bar (Converge logo + wordmark + real `#syncDot` state) → hero (`Focus Funnel.` 80px,
  lime period, + funnel swatch row) → timer block (label/task/giant lime clock left,
  START/RESET/FINISH + `25|5|15` segmented right) → Today (3 cards, top one lime) →
  All to-dos · Feishu (3-col area board) → footer.
- **Logo:** "Converge" — three stacked bars of decreasing width → a lime dot. Inline SVG in
  the top bar (bars use `currentColor`) and in `icon.svg`.
- **Implementation:** all of it is ONE appended CSS block (`/* GALLERY V3 */`) at the end of
  `<style>` that overrides the Cockpit theme, plus small markup edits (header, pill labels
  `25/5/15`, `#syncDot` moved to the top bar). JS logic is untouched except `paint()`, which
  now wraps the `:` in `<span class="csep">` so digits are lime and the separator is muted.
- **Hidden, NOT deleted:** Brain Dump, Notepad, Done, Focus Log, Trash and Performance are
  `display:none` in the gallery layout (last rule of the block). Their markup, JS and
  **localStorage data are fully intact** — delete that one CSS rule to bring them back.
  Sam chose "match the design exactly"; hiding rather than deleting keeps his notes,
  completed history and streak data safe.

## Layout (desktop, 2-column grid) — superseded by Gallery V3 above

Row order in `.wrap`: **Timer hero** (full-width, "Bold Statement" design: vivid indigo→violet
gradient panel, white 138px clock (190px in zen), task shown as a translucent pill, high-contrast
white/ghost controls; break mode swaps to a teal→green gradient via `.timer-card:has(.clock.break)`),
then **Brain Dump | Today**, **Notepad | Done**,
**Performance | Focus Log**, **Trash** (full-width). Left column = capture, right column =
execution/results. Cards pair via plain grid auto-placement (only `.timer-card`/`.trash-card`
span `1 / -1`). Mobile (<820px) stacks to one column.

Grid is capped at `max-width: 1400px` (centered) so task cards aren't full-bleed.
**Compact task rows:** Brain Dump/Today rows stay one line at rest — action buttons (🏷, 📝,
move, ×, and empty +est) carry class `.hover-action` (hidden via CSS until `.task:hover` or
focus-within); always shown on touch via `@media (hover: none)`. Status bits (checkbox,
priority, title, tags, set estimate, subtask count) remain visible.
**Collapsible cards:** Done and Focus Log have `.collapsible` + a chevron in their `h2[data-collapse]`;
clicking the header toggles `.collapsed` (CSS hides all non-`h2` children). State persists in
`state.collapsed` ({done,log}); `applyCollapsed()` runs at boot. Easy to extend to other cards via `COLLAPSE_CARDS`.

**Zen mode:** while the timer runs, `body.zen` is set (added in `startTimer`, removed in
`pauseTimer`): the clock grows to 150px and header/footer/other cards fade to 35% opacity
(hover restores a card to full opacity so lists stay usable mid-session). The clock is 100px
at rest with a gradient text fill (text→accent; break mode uses good→text).

**"✓ Finish top task" does NOT stop the timer** — it archives the task and re-renders; the
next top task takes over the running countdown. (It used to reset; users hated that.)

## Code map (within `index.html`)

- `<style>` — all CSS; theming via CSS custom properties on `[data-theme]`. Design system is the
  **Cockpit theme** matching Sam's `🏠 Daily Cockpit.html`: soft-grey page (`#e9eaed` / dark `#0f1014`),
  white paper tiles, hairline dividers (`--line`), near-black ink, ONE lime accent (`--lime #c8f000`,
  `--lime-deep #8fb800`). `--accent` = the *readable* lime (deep on light, bright on dark) for accent-text;
  fills use `--lime` with black text. Primary buttons = black-on-lime; ghosts = paper + hairline. Timer
  is a constant **lime hero band** with a giant black clock. Task rows are **flat hairline rows** (not
  filled cards). Tags are neutral outline chips (one-accent discipline; `paintChip` no longer hue-colors).
  Priority P1/P2/P3 keep red/amber/blue as a functional exception. 🌙/☀️ toggle switches to cockpit-dark.
- `<script>` IIFE:
  - State + persistence: `defaults()`, `loadState()`, `save()`, `normalizeTask()`.
  - Task ops: `addTask`, `moveTask`, `deleteTask`, `toggleDone`, `editEst`, sub-task fns.
  - Drag & drop: `dragAfter()`, `wireDropZone()`.
  - Timer: `startTimer`/`pauseTimer`/`finishTimer`/`setMode` + `MODES` map.
  - Audio engine: `BUILDERS` (one per ambience), `startFocusSound`, `stopFocusSound`,
    `setLiveVolume`, `alarm`.
  - Stats/streak: `recordCompletion`, `computeStreak`, `renderStats`.

## Conventions

- Keep it a single self-contained file — no external dependencies or assets.
- After changing the `<script>`, sanity-check bracket balance (no node installed locally).
- Bump the `STORAGE_KEY` version and add a migration in `loadState()` when the saved
  data shape changes, so existing users don't lose data.

## Task sync (Feishu)

- Sam retired Trello entirely on 2026-07-07 — **all Trello code was removed** from `index.html`
  (the old ⚙ Trello UI, `state.trello`, `trelloPull`/`trelloMoveToDone`/`trelloUrl`). Feishu is
  now the only task-sync integration. Legacy saved data containing `trello` fields still loads —
  the fields are silently dropped by `fromObject`/`normalizeTask`.
- **Feishu sync** (footer **⤓ Pull from Feishu** + **⚙ Feishu**): pulls 🔥 Now tasks into Brain
  Dump and ticks completed ones ✅ Done, via a tiny Cloudflare "bridge" Worker (`feishu-bridge/
  worker.js`) that holds the Feishu app key safely. Config (`state.feishu`: `url`, `secret`) is
  entered at runtime and lives ONLY in localStorage. `task.feishu` stamps the record id.
- Not to be confused with **☁️ Sync** (whole-state cross-device sync, separate `focus-funnel.sync`
  key) or **🗄 Backups** (local snapshots) — those are independent systems.

## Ideas / backlog (not yet built)

- Auto-complete a task when all its sub-tasks are checked.
- 7-day completion mini-chart.
