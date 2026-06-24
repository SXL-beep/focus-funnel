# Focus Funnel

A single-file, zero-dependency productivity web app. Brain-dump tasks, funnel the 3
that matter into "Today," and run the top one on a Pomodoro timer with ambient focus
sound. Built for personal daily use.

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
- **Pomodoro flow:** when a focus session completes, the Break 5 countdown auto-starts
  (~2s after the alarm; any manual click cancels via `clearAutoStart`). Breaks play a soft
  ticking countdown regardless of the chosen focus ambience; when the break ends it chimes
  and switches back to Focus mode (not auto-started).
- **Light / dark theme** toggle.

## Layout (desktop, 2-column grid)

Row order in `.wrap`: **Timer hero** (full-width, center-stage: task line, 76px clock, controls,
then mode pills + sound in `.t-secondary`), then **Brain Dump | Today**, **Notepad | Done**,
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

- `<style>` — all CSS; theming via CSS custom properties on `[data-theme]`. Design system is
  "Calm Minimal": soft indigo accent (`--accent`), `--accent-soft` tint for the active/top task
  and focus rings, light airy palette (light theme is primary) + a calm-dark counterpart.
  `--accent-2` (warm coral) is reserved for the brand "Funnel" word, matching the app icon.
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

## Trello sync (Sam's shared board)

- Optional two-way sync with Sam's Trello board "Marlin × Sam — What's Next". Footer has
  **⤓ Pull from Trello** + **⚙ Trello** (config). Config (`state.trello`: `key`, `token`,
  `pullListId`, `doneListId`) is entered at runtime and lives ONLY in localStorage —
  **never hardcode the token; the repo is public on GitHub Pages.** List IDs are pre-filled
  in `defaults()` (🔥 Now = pull source, ✅ Done = completion target; both non-secret).
- **Pull:** fetches cards from the Now list and adds any not-yet-imported ones to Brain Dump,
  stamping each task with its Trello card id (`task.trello`, preserved by `normalizeTask`).
- **Complete:** `finishTopTask()` calls `trelloMoveToDone(card)` → `PUT /cards/{id}` moving the
  card to the Done list. Fire-and-forget, non-blocking.
- Calls go direct from the browser to `api.trello.com` (CORS `allow-origin: *`, works from
  `file://`). Helpers near the export/import wiring: `trelloPull`, `trelloMoveToDone`, `trelloUrl`.

## Ideas / backlog (not yet built)

- Auto-complete a task when all its sub-tasks are checked.
- 7-day completion mini-chart.
