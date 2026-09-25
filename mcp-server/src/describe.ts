/** Prints the tool catalogue as JSON (name, kind, hints, whether it takes the hub-injected customer id).
 *  Used by scripts/09_build_hub.py to generate hub/TOOL-SETTINGS.md.   Run: bun run mcp-server/src/describe.ts */
import { TOOLS } from "./tools";
console.log(JSON.stringify(TOOLS.filter((t) => t.name !== "demo_link_persona").map((t) => ({
  name: t.name, kind: t.kind, destructive: !!t.destructive, idempotent: !!t.idempotent,
  customer_arg: "line_user_id" in t.input ? "line_user_id" : null,
  customer_arg_required: "line_user_id" in t.input ? !t.input.line_user_id.isOptional() : false,
  description: t.description,
})), null, 1));
