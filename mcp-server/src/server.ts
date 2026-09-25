/** Builds the MCP server object. Shared by the stdio entry (index.ts) and the HTTP entry (http.ts). */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { TOOLS } from "./tools";

const READONLY = process.env.SRICHAND_READONLY === "1";
/** Some hubs inject the customer's id under their own argument name. Set SRICHAND_CUSTOMER_ARG to that name
 *  (e.g. "customer_id") and every tool that takes `line_user_id` will accept it under the new name instead. */
const CUSTOMER_ARG = process.env.SRICHAND_CUSTOMER_ARG || "line_user_id";

const titleOf = (name: string) => name.replace(/_mock$/, " (demo)").replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());

export const activeTools = () => TOOLS.filter((t) => !(READONLY && t.kind === "write"));

export function buildServer() {
  const server = new McpServer({ name: "srichand-advisor", version: "0.3.0" });
  for (const t of activeTools()) {
    const shape: Record<string, z.ZodTypeAny> = { ...t.input };
    if (shape.line_user_id) {
      const described = shape.line_user_id.describe("Customer key — Srichand customer id (e.g. \"5\"), Rewards member number (e.g. \"SCR0260005\") or LINE userId. Injected by the hub from the paired account; never ask the customer for it or invent one.");
      delete shape.line_user_id;
      shape[CUSTOMER_ARG] = described;
    }
    // MCP tool annotations — this is what tells a hub whether a tool is Read or Write.
    //   read  → readOnlyHint: true   (the handler never changes the database; asserted by the smoke test)
    //   write → readOnlyHint: false, destructiveHint only for tools that delete/overwrite, idempotentHint where a repeat call is a no-op
    // openWorldHint is false everywhere: every tool only touches Srichand's own database.
    const annotations = t.kind === "read"
      ? { title: titleOf(t.name), readOnlyHint: true, openWorldHint: false }
      : { title: titleOf(t.name), readOnlyHint: false, destructiveHint: !!t.destructive, idempotentHint: !!t.idempotent, openWorldHint: false };
    // Tools that declare `output` advertise an MCP outputSchema, so a hub can see the fields it will get
    // (image_url among them) without calling first. The SDK then REQUIRES structuredContent on every
    // successful result and validates it against that schema — hence the permissive shapes in tools.ts.
    const config: Record<string, unknown> = { title: titleOf(t.name), description: `[${t.kind.toUpperCase()}] ${t.description}`, inputSchema: shape, annotations };
    if (t.output) config.outputSchema = t.output;
    server.registerTool(t.name, config as any, async (args: Record<string, unknown>) => {
      try {
        const a = { ...(args ?? {}) };
        if (CUSTOMER_ARG !== "line_user_id" && CUSTOMER_ARG in a) { a.line_user_id = a[CUSTOMER_ARG]; delete a[CUSTOMER_ARG]; }
        if (typeof a.line_user_id === "number") a.line_user_id = String(a.line_user_id);
        const parsed = z.object(t.input).parse(a);
        const result = t.handler(parsed);
        const out: Record<string, unknown> = { content: [{ type: "text" as const, text: JSON.stringify(result, null, 1) }] };
        // Only a plain object is a legal structuredContent payload.
        if (t.output && result !== null && typeof result === "object" && !Array.isArray(result)) out.structuredContent = result;
        return out as any;
      } catch (e) {
        return { isError: true, content: [{ type: "text" as const, text: `Error: ${(e as Error).message}` }] };
      }
    });
  }
  return server;
}
