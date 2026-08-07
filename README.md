# Focus Funnel

Focus Funnel is Sam's single-file, zero-dependency productivity PWA. It combines
a Pomodoro focus timer, a three-task Today funnel, task capture, local backups,
cross-device state sync, and Feishu task integration.

## Start here

- Open `index.html` directly for local use.
- Read `CLAUDE.md` before making implementation changes; it contains the code map,
  conventions, and integration details.
- Read `docs/history/PROJECT-HANDOFF.md` before resuming development in a new AI
  conversation.
- The live app is published from the `main` branch at
  <https://sxl-beep.github.io/focus-funnel/>.

There is no build step, package manager, framework, or application server. The
core HTML, CSS, and JavaScript all live in `index.html`.

## Repository layout

```text
index.html                  Core application
manifest.webmanifest        PWA metadata
icon.svg                    Current browser icon
icon-*.png                  Installed-app icons
apple-touch-icon.png        iOS home-screen icon
sync-worker/                Cloudflare whole-state sync worker
feishu-bridge/              Cloudflare Feishu bridge
brand/                      Brand exploration and render assets
docs/history/               Migration record and development handoff
CLAUDE.md                   Detailed implementation guide
```

The local `.private/conversations/` directory contains redacted conversation
exports from earlier development work. It is intentionally excluded through
`.git/info/exclude` because this is a public repository.

## Safe working routine

1. Confirm the ORICO drive is mounted.
2. Run `git status --short --branch` before changing anything.
3. Work on a feature branch for non-trivial changes.
4. Test the app from a stable local path so browser storage is not mistaken for
   missing data.
5. Never commit runtime credentials or conversation archives.
6. Push finished work to GitHub so the external drive is not the only copy.
