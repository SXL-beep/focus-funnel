// Focus Funnel — cross-device sync Worker (Cloudflare)
// -----------------------------------------------------
// Stores your whole app-state as ONE JSON blob in a KV store, guarded by a
// private secret. Every device pulls it on open and pushes it on change.
//
// It is deliberately "dumb": it does not understand your tasks — it just holds
// whatever JSON blob the app gives it. All the sync logic lives in the app.
//
// Requires (set in the Cloudflare dashboard — see SYNC-DEPLOY.md):
//   • KV namespace binding named  FUNNEL_KV
//   • Secret variable named        SYNC_SECRET  (a passphrase you invent)
//
// API (call the Worker URL directly, any path):
//   GET   → returns the stored blob (or the text "null" if nothing saved yet)
//   PUT   → body = JSON string; saved as the blob
//   both require header:  x-sync-key: <your SYNC_SECRET>

const STORE_KEY = "state";       // single KV key — one user, one blob
const MAX_BYTES = 2_000_000;     // ~2 MB guard

export default {
  async fetch(request, env) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, PUT, POST, OPTIONS",
      "Access-Control-Allow-Headers": "content-type, x-sync-key",
      "Access-Control-Max-Age": "86400",
    };
    const json = (obj, status = 200) =>
      new Response(JSON.stringify(obj), { status, headers: { ...cors, "content-type": "application/json" } });

    // CORS preflight
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });

    // Auth — constant-ish check against the secret
    const provided = request.headers.get("x-sync-key") || "";
    if (!env.SYNC_SECRET || provided !== env.SYNC_SECRET) {
      return json({ error: "unauthorized" }, 401);
    }

    if (!env.FUNNEL_KV) return json({ error: "KV binding FUNNEL_KV missing" }, 500);

    try {
      if (request.method === "GET") {
        const val = await env.FUNNEL_KV.get(STORE_KEY);
        // return the raw blob verbatim (or "null" when empty)
        return new Response(val ?? "null", { headers: { ...cors, "content-type": "application/json" } });
      }
      if (request.method === "PUT" || request.method === "POST") {
        const body = await request.text();
        if (body.length > MAX_BYTES) return json({ error: "payload too large" }, 413);
        // sanity: must be JSON (protects against garbage writes)
        try { JSON.parse(body); } catch { return json({ error: "body must be JSON" }, 400); }
        await env.FUNNEL_KV.put(STORE_KEY, body);
        return json({ ok: true });
      }
      return json({ error: "method not allowed" }, 405);
    } catch (e) {
      return json({ error: String(e && e.message || e) }, 500);
    }
  },
};
