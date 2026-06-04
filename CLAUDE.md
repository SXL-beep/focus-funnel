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
- **Drag-to-reorder within Today** — the top task (green border) is what the timer runs.
- **Sub-tasks** per task (expandable checklist with progress count).
- **Time estimates** per task (minutes); Today header sums them.
- **Pomodoro timer** — Focus 25 / Break 5 / Long 15 modes. Spacebar toggles start/pause.
- **Completed-today counter & streak** (consecutive days with >=1 completion).
- **Ambient focus sound** while the timer runs — selectable: brown noise / rain / ocean /
  ticking clock — plus a volume slider. All synthesized live via WebAudio (no asset files).
- **Alarm** (two-tone WebAudio) when a session ends.
- **Light / dark theme** toggle.

## Code map (within `index.html`)

- `<style>` — all CSS; theming via CSS custom properties on `[data-theme]`.
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

## Ideas / backlog (not yet built)

- Export / Import data as JSON (backup + move between browsers/machines).
- Auto-complete a task when all its sub-tasks are checked.
- 7-day completion mini-chart.
- Per-mode sound (silence on breaks).
