// Focus Funnel ↔ Feishu To-Do bridge — Cloudflare Worker
// -------------------------------------------------------
// Why this exists: the Funnel is a public web app, and Feishu (unlike Trello)
// blocks direct browser calls and needs a SECRET app key. This tiny bridge holds
// that key (in Cloudflare's encrypted env, never in the app) and exposes two jobs:
//   GET  /now   -> returns the 🔥 Now tasks           (?secret=SHARED_SECRET)
//   GET  /all   -> returns ALL open tasks (not Done)   (?secret=SHARED_SECRET)
//   POST /add   -> quick-capture a new task at ⏭ Next  body: {secret, text}
//   POST /done  -> marks a task ✅ Done                 body: {secret, id}
//
// Required Cloudflare env vars (Settings → Variables and Secrets):
//   FEISHU_APP_ID       cli_aaa6222524781bef   (plain text — not secret)
//   FEISHU_APP_SECRET   <from ~/.claude/channels/feishu/.env>   (ENCRYPTED secret)
//   SHARED_SECRET       <a password you invent>                 (ENCRYPTED secret)
//
// The Base + table below are your "✅ Sam — Life To-Do" board (not secret).

const FEISHU = "https://open.feishu.cn/open-apis";
const BASE   = "M6iWbxfaBaYoNPs7sxEc4Mv5nLc";
const TABLE  = "tblWixf6lkHunqPZ";
const NOW_STATUS  = "🔥 Now";
const NEXT_STATUS = "⏭ Next";
const DONE_STATUS = "✅ Done";

function cors() {
  return {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}
function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: { "Content-Type": "application/json", ...cors() },
  });
}

async function tenantToken(env) {
  const r = await fetch(FEISHU + "/auth/v3/tenant_access_token/internal", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_id: env.FEISHU_APP_ID, app_secret: env.FEISHU_APP_SECRET }),
  });
  const j = await r.json();
  if (j.code !== 0) throw new Error("auth failed: " + (j.msg || j.code));
  return j.tenant_access_token;
}

// single-select can come back as a string or a 1-item array — normalize
function sel(v) { return Array.isArray(v) ? (v[0] || "") : (v || ""); }

export default {
  async fetch(req, env) {
    if (req.method === "OPTIONS") return new Response(null, { headers: cors() });

    const url = new URL(req.url);
    let secret = url.searchParams.get("secret");
    let body = {};
    if (req.method === "POST") {
      try { body = await req.json(); } catch (e) {}
      secret = secret || body.secret;
    }
    if (!env.SHARED_SECRET || secret !== env.SHARED_SECRET) {
      return json({ error: "unauthorized" }, 401);
    }

    try {
      const tok = await tenantToken(env);
      const H = { Authorization: "Bearer " + tok, "Content-Type": "application/json" };

      // ---- GET /now : list the 🔥 Now tasks ----
      if (req.method === "GET" && url.pathname.endsWith("/now")) {
        let items = [], pageToken = "";
        while (true) {
          const q = "?page_size=100" + (pageToken ? "&page_token=" + pageToken : "");
          const r = await fetch(FEISHU + "/bitable/v1/apps/" + BASE + "/tables/" + TABLE + "/records" + q, { headers: H });
          const j = await r.json();
          if (j.code !== 0) throw new Error("list failed: " + (j.msg || j.code));
          items = items.concat((j.data && j.data.items) || []);
          pageToken = j.data && j.data.page_token;
          if (!(j.data && j.data.has_more)) break;
        }
        const tasks = items
          .filter((it) => sel(it.fields.Status) === NOW_STATUS)
          .map((it) => ({
            id: it.record_id,
            text: sel(it.fields.Task),
            area: sel(it.fields.Area),
            pri: sel(it.fields.Priority),
            due: it.fields.Due ? new Date(it.fields.Due).toISOString().slice(0, 10) : null,
            notes: sel(it.fields.Notes),
          }));
        return json({ tasks: tasks });
      }

      // ---- GET /all : list ALL open tasks (every status except ✅ Done) for the category board ----
      if (req.method === "GET" && url.pathname.endsWith("/all")) {
        let items = [], pageToken = "";
        while (true) {
          const q = "?page_size=100" + (pageToken ? "&page_token=" + pageToken : "");
          const r = await fetch(FEISHU + "/bitable/v1/apps/" + BASE + "/tables/" + TABLE + "/records" + q, { headers: H });
          const j = await r.json();
          if (j.code !== 0) throw new Error("list failed: " + (j.msg || j.code));
          items = items.concat((j.data && j.data.items) || []);
          pageToken = j.data && j.data.page_token;
          if (!(j.data && j.data.has_more)) break;
        }
        const tasks = items
          .map((it) => ({
            id: it.record_id,
            text: sel(it.fields.Task),
            area: sel(it.fields.Area),
            pri: sel(it.fields.Priority),
            status: sel(it.fields.Status),
            due: it.fields.Due ? new Date(it.fields.Due).toISOString().slice(0, 10) : null,
          }))
          .filter((t) => t.text && t.status !== DONE_STATUS);
        return json({ tasks: tasks });
      }

      // ---- POST /add : quick-capture a new task into the Base at ⏭ Next ----
      if (req.method === "POST" && url.pathname.endsWith("/add")) {
        const text = String(body.text || "").trim();
        if (!text) return json({ error: "missing text" }, 400);
        const r = await fetch(
          FEISHU + "/bitable/v1/apps/" + BASE + "/tables/" + TABLE + "/records",
          { method: "POST", headers: H, body: JSON.stringify({ fields: { Task: text, Status: NEXT_STATUS } }) }
        );
        const j = await r.json();
        if (j.code !== 0) throw new Error("add failed: " + (j.msg || j.code));
        return json({ ok: true, id: j.data && j.data.record && j.data.record.record_id });
      }

      // ---- POST /done : flip a task to ✅ Done ----
      if (req.method === "POST" && url.pathname.endsWith("/done")) {
        if (!body.id) return json({ error: "missing id" }, 400);
        const r = await fetch(
          FEISHU + "/bitable/v1/apps/" + BASE + "/tables/" + TABLE + "/records/" + body.id,
          { method: "PUT", headers: H, body: JSON.stringify({ fields: { Status: DONE_STATUS } }) }
        );
        const j = await r.json();
        if (j.code !== 0) throw new Error("done failed: " + (j.msg || j.code));
        return json({ ok: true });
      }

      return json({ error: "unknown route — use GET /now, GET /all, POST /add, or POST /done" }, 404);
    } catch (e) {
      return json({ error: String((e && e.message) || e) }, 500);
    }
  },
};
