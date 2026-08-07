# Focus Funnel project handoff

Updated: 2026-08-07 (Asia/Taipei)

## Verified repository state

- Permanent workspace: `/Volumes/ORICO/Projects/focus-funnel`
- Migration source: `/Users/sxlmacmini/Migration-Inbox/MacBook-2026-07-28/Projects/focus-funnel`
- Branch: `main`, tracking `origin/main`
- Remote: `https://github.com/SXL-beep/focus-funnel.git`
- Verified HEAD: `32ac3d0b39884cc43df810ca5f212e7e7dd0fa7a`
- Commit count at migration: 63
- Verification performed: source/destination checksum comparison, matching HEAD,
  matching commit count, clean `git status`, and clean `git fsck --full`

The original Migration-Inbox copy was deliberately retained as a recovery copy
after verification. Continue development only in the ORICO workspace.

## Current product state

Focus Funnel is a single-file PWA whose current visual system is Gallery V3. Its
major systems include:

- Focus, short-break, and long-break timers with synthesized ambient audio and a
  persistent session-end alarm.
- Brain Dump, Today, Done, Focus Log, Trash, notes, tags, priorities, due dates,
  subtasks, estimates, streaks, and performance statistics.
- A three-slot Today workflow and a Feishu task board with Focus, Dump, Done,
  selection, batch-send, grouping, and collapsible area sections.
- Whole-state cross-device sync through a Cloudflare Worker, plus a separate
  rolling local backup ring.
- A self-contained offline design using embedded Hanken Grotesk and Space Mono
  fonts, the lime `#BEE800` Gallery palette, and the Converge mark.

Read `CLAUDE.md` for function names, state keys, and integration behavior. Verify
claims against `index.html` before changing data structures or integrations.

## Known documentation conflict

One migrated memory note says recurring tasks and reminders were later shipped,
while `CLAUDE.md`, the Git history, and the migrated `index.html` say they were
skipped and contain no matching implementation. Treat recurring tasks and
reminders as **not implemented** unless a future code inspection proves otherwise.
The repository itself outranks the memory summary.

## Known open work

These items were explicitly left open in the migrated project material:

1. Regenerate `icon-192.png`, `icon-512.png`, and `apple-touch-icon.png` with the
   Converge mark. The browser SVG is current, but installed-app PNG icons are still
   described as the old orange funnel.
2. Consider a browser-tab countdown such as `24:58 · Focus`; it was proposed but
   not approved or built.
3. Calendar integration remains a later integration phase.
4. AI assistance remains a later phase and would require an explicitly approved
   API design and credentials.

Do not assume the first item is still visually stale without opening the PNGs and
comparing them with `icon.svg`.

## Private conversation archive

Readable historical conversations are stored at:

`.private/conversations/`

This directory is intentionally local-only and ignored through
`.git/info/exclude`. Start with `.private/conversations/INDEX.md`; load a full
conversation only when its context is needed. The archive includes the most
complete canonical versions of duplicated sessions covering:

- Core product development and product-definition discussions.
- Daily Cockpit visual direction and cloud sync.
- Feishu migration and Focus Funnel integration.
- Design-skill previews and Gallery/brand work.
- Cloud-sync Phase 2 and related integration work.
- Logo typography and the later Converge/Gallery direction.
- Mac migration context.
- The 2026-08-07 workspace-migration conversation.

All exported dialogue is automatically scrubbed for credential-shaped strings.
Raw tool payloads and raw JSONL were intentionally not copied into the public
project tree.

## Starting the next conversation

Open `/Volumes/ORICO/Projects/focus-funnel` as the new Codex workspace, then use:

> Continue the Focus Funnel project from this workspace. First read `README.md`,
> `CLAUDE.md`, and `docs/history/PROJECT-HANDOFF.md`; check `git status` and inspect
> the current code before proposing changes. Use `.private/conversations/INDEX.md`
> only when historical context is needed. Do not expose or commit private history.

No feature direction was selected during migration. The next conversation should
ask what outcome Sam wants to work on, or offer the verified open items above.
