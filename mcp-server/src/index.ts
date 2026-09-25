#!/usr/bin/env bun
/** Srichand advisor MCP server over STDIO (for local MCP clients).  Run: bun run mcp
 *  For a hub that connects by URL, use the HTTP entry instead: bun run mcp:http */
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { activeTools, buildServer } from "./server";

await buildServer().connect(new StdioServerTransport());
console.error(`srichand-advisor MCP server ready (stdio) — ${activeTools().length} tools`);
