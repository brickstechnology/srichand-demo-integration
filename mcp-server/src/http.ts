#!/usr/bin/env bun
/** Srichand advisor MCP server over Streamable HTTP — this is what a hub that asks for an "MCP URL" connects to.
 *
 *    bun run mcp:http            →  http://localhost:8787/mcp
 *
 *  Env:  SRICHAND_MCP_TOKEN   required. The hub's "Credential". Sent as `Authorization: Bearer <token>` (or `x-api-key`).
 *        PORT                 default 8787
 *        SRICHAND_READONLY=1  expose read tools only
 *        SRICHAND_CUSTOMER_ARG  name of the argument your hub injects the customer id into (default line_user_id)
 *  Stateless: every request gets a fresh server + transport, so it scales horizontally and survives restarts. */
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js";
import { timingSafeEqual } from "node:crypto";
import { activeTools, buildServer } from "./server";

const TOKEN = process.env.SRICHAND_MCP_TOKEN ?? "";
const PORT = Number(process.env.PORT ?? 8787);
if (!TOKEN && process.env.SRICHAND_MCP_ALLOW_NO_AUTH !== "1") {
  console.error("Refusing to start without SRICHAND_MCP_TOKEN (put it in .env). This server can create orders and erase customer data.");
  process.exit(1);
}

function authorised(req: Request) {
  if (!TOKEN) return true;
  const header = req.headers.get("authorization") ?? "";
  const presented = header.replace(/^Bearer\s+/i, "").trim() || (req.headers.get("x-api-key") ?? "").trim();
  const a = Buffer.from(presented), b = Buffer.from(TOKEN);
  return a.length === b.length && timingSafeEqual(a, b);
}

const json = (status: number, body: unknown) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

Bun.serve({
  port: PORT,
  idleTimeout: 60,
  async fetch(req) {
    const { pathname } = new URL(req.url);
    if (pathname === "/health") return json(200, { ok: true, server: "srichand-advisor", tools: activeTools().length });
    if (pathname !== "/mcp") return json(404, { error: "Not found. The MCP endpoint is /mcp" });
    if (!authorised(req)) return json(401, { jsonrpc: "2.0", error: { code: -32001, message: "Unauthorized: send the credential as 'Authorization: Bearer <token>'" }, id: null });
    if (req.method !== "POST") return json(405, { jsonrpc: "2.0", error: { code: -32000, message: "Stateless server: use POST" }, id: null });
    const server = buildServer();
    const transport = new WebStandardStreamableHTTPServerTransport({ sessionIdGenerator: undefined, enableJsonResponse: true });
    await server.connect(transport);
    const res = await transport.handleRequest(req);
    queueMicrotask(() => { transport.close(); server.close(); });
    return res;
  },
});
console.error(`srichand-advisor MCP server ready (HTTP) — ${activeTools().length} tools at http://localhost:${PORT}/mcp`);
