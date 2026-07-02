# Deploy the Focus Funnel ↔ Feishu bridge (~10 min, one-time)

This puts the tiny "bridge" (`worker.js`) onto Cloudflare's free Workers plan so your
Focus Funnel (phone + laptop) can pull your 🔥 Now tasks and tick them ✅ Done.

You do this once. Nothing here is hard — it's copy/paste.

## 1. Make a free Cloudflare account
Go to **dash.cloudflare.com** → Sign up (free). No card needed for Workers.

## 2. Create the Worker
- Left sidebar → **Workers & Pages** → **Create application** → **Create Worker**.
- Name it **`funnel-feishu`** → **Deploy** (accept the default hello-world for now).
- Click **Edit code** → select-all the sample code, delete it, and **paste the entire
  contents of `worker.js`** (in this folder) → **Deploy**.

## 3. Add the 3 settings (this is where the key goes — safely)
On the worker page → **Settings** → **Variables and Secrets** → add these three:

| Name | Value | Type |
|---|---|---|
| `FEISHU_APP_ID` | `cli_aaa6222524781bef` | Plaintext |
| `FEISHU_APP_SECRET` | *(see below)* | **Secret / Encrypt** |
| `SHARED_SECRET` | *a password you invent* (long & random, e.g. `funnel-7Xq2...`) | **Secret / Encrypt** |

**Where to get `FEISHU_APP_SECRET`:** open the file
`~/.claude/channels/feishu/.env` on your Mac and copy the value after
`FEISHU_APP_SECRET=`. Paste it straight into Cloudflare's **encrypted** box.
👉 Never paste it into chat, into code, or anywhere public — only Cloudflare's secret box.

Save / Deploy after adding them.

## 4. Grab your Worker URL
On the worker's overview page you'll see its address, like:
`https://funnel-feishu.YOUR-NAME.workers.dev`

**Quick test:** open this in a browser (put your real password after `secret=`):
`https://funnel-feishu.YOUR-NAME.workers.dev/now?secret=YOUR_SHARED_SECRET`
You should see your 🔥 Now tasks as JSON. If you see `{"error":"unauthorized"}`, the
password doesn't match; if you see tasks, it works. ✅

## 5. Connect the Funnel
Open Focus Funnel → footer → **⚙ Feishu** →
- **Bridge URL** = your Worker URL (no `/now` on the end)
- **Shared password** = the `SHARED_SECRET` you invented
- **Save** → then hit **⤓ Pull from Feishu**.

Your Now tasks land in Brain Dump. Finish the top task on the timer → it flips to
✅ Done in the Base (and the row clears, colors + reminders keep working).

---

## Notes
- Free plan = 100,000 requests/day. You'll use a handful. No cost.
- The bridge only knows how to do two things (list Now, mark Done) — it can't read or
  change anything else in your Feishu.
- To update the bridge later, just paste a new `worker.js` and Deploy again.
- The Funnel change lives in `index.html`; it must be committed + pushed to GitHub Pages
  for your **phone** PWA to get the new buttons (works immediately when opened from the
  local file on your Mac).
