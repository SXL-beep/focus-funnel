# Focus Funnel — Cloudflare Sync Worker · deploy guide

Goal: stand up the tiny sync server. ~5 minutes in the Cloudflare dashboard,
same style as your `feishu-bridge`. You need: a Cloudflare account (you have one).

> Cloudflare occasionally renames menu items — if a label is slightly different,
> look for the nearest match. The **bold** names are the important ones.

---

## Step 2 — Create the KV store (where your data lives)
1. Go to **dash.cloudflare.com** → left sidebar **Storage & Databases** → **KV**
   (older UI: **Workers & Pages → KV**).
2. Click **Create instance / Create namespace**.
3. Name it `focus-funnel` → **Create**.
   *(That's it — you don't need to open it or add anything inside.)*

## Step 3 — Create the Worker
1. Left sidebar **Workers & Pages** → **Create** → **Create Worker**.
2. Name it `focus-funnel-sync` → **Deploy** (it deploys a hello-world first — fine).
3. Click **Edit code** (top right). Select-all, delete, and **paste the entire
   contents of `worker.js`** (the file next to this guide). Click **Deploy**.

## Step 4 — Connect the KV + set your secret
Open the worker → **Settings**.
1. **Bindings** (older UI: *Variables → KV Namespace Bindings*) → **Add binding**:
   - Type: **KV namespace**
   - Variable name: `FUNNEL_KV`   ← must be exactly this
   - KV namespace: pick `focus-funnel`
   - **Save**.
2. **Variables and Secrets** → **Add**:
   - Name: `SYNC_SECRET`
   - Value: **a passphrase you invent** — long and random, e.g. `funnel-sync-7Xq2p9Kv...`
     (this is your key; you'll type it into the app on each device)
   - Type: **Secret / Encrypt**
   - **Save**.
3. If prompted, **Deploy** again so the binding + secret take effect.

## Step 5 — Grab the URL + hand back to me
1. On the worker's page, copy its URL — looks like
   `https://focus-funnel-sync.YOUR-NAME.workers.dev`
2. **Quick self-check:** open that URL in a browser. You should see
   `{"error":"unauthorized"}` — that's *correct*! It means the worker is live and
   the lock is on (you didn't send the key).
3. **Tell me the URL** (you keep the secret — you'll enter it in the app). I'll
   run a proper test, then wire the app to it.

---

### What you invented / where it goes
| Thing | Value | Lives in |
|---|---|---|
| KV namespace | `focus-funnel` | Cloudflare |
| KV binding name | `FUNNEL_KV` | Worker settings |
| Secret name | `SYNC_SECRET` | Worker settings (encrypted) |
| Secret value | *(your passphrase)* | Cloudflare + you type it into the app |
| Worker URL | `…workers.dev` | you give it to me + type into the app |

Never paste the secret value into code or the repo — only Cloudflare's encrypted
box and the app's Sync panel (which stores it locally on each device).
