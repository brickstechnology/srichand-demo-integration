// Applies db/seed/*.json to the EXISTING db/srichand.db in place (upsert by primary key).   Usage: bun run db:sync
// Unlike db:build it does not delete the file, so a running MCP server sees the changes immediately and rows
// created during live demos (orders, consents, carts…) are kept. Use db:build for a clean reset.
import { Database } from "bun:sqlite";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { TABLES } from "./tables";

const DB_PATH = process.env.SRICHAND_DB ?? join(import.meta.dir, "srichand.db");
if (!existsSync(DB_PATH)) { console.error("No database yet — run `bun run db:build` first."); process.exit(1); }
const db = new Database(DB_PATH, { readwrite: true });
db.exec("PRAGMA busy_timeout = 5000; PRAGMA foreign_keys = OFF;");     // OFF only while replacing parent rows; checked below

let inserted = 0, updated = 0;
db.transaction(() => {
  for (const table of TABLES) {
    const file = join(import.meta.dir, "seed", `${table}.json`);
    if (!existsSync(file)) continue;
    const rows: Record<string, unknown>[] = JSON.parse(readFileSync(file, "utf8"));
    if (!rows.length) continue;
    const cols = Object.keys(rows[0]);
    const pk = (db.query(`PRAGMA table_info(${table})`).all() as any[]).filter((c) => c.pk > 0).sort((a, b) => a.pk - b.pk).map((c) => c.name);
    const exists = db.prepare(`SELECT ${cols.join(",")} FROM ${table} WHERE ${pk.map((k) => `${k} IS ?`).join(" AND ")}`);
    const upsert = db.prepare(`INSERT OR REPLACE INTO ${table} (${cols.join(",")}) VALUES (${cols.map(() => "?").join(",")})`);
    let ins = 0, upd = 0;
    for (const r of rows) {
      const vals = cols.map((c) => { const v = r[c]; return v === undefined ? null : typeof v === "boolean" ? (v ? 1 : 0) : typeof v === "object" && v !== null ? JSON.stringify(v) : (v as any); });
      const cur = exists.get(...pk.map((k) => r[k] as any)) as Record<string, unknown> | null;
      if (!cur) { upsert.run(...vals); ins++; }
      else if (cols.some((c, i) => String(cur[c] ?? "") !== String(vals[i] ?? ""))) { upsert.run(...vals); upd++; }
    }
    if (ins || upd) console.log(`  ${table.padEnd(28)} +${ins} new  ~${upd} updated`);
    inserted += ins; updated += upd;
  }
})();
const fk = db.query("PRAGMA foreign_key_check").all();
if (fk.length) { console.error("Foreign-key violations after sync:", fk.slice(0, 10)); process.exit(1); }
db.exec("PRAGMA wal_checkpoint(PASSIVE);");     // fold the write-ahead log into the main file so a copy of srichand.db is complete
db.close();
console.log(`\nSynced ${DB_PATH}: ${inserted} rows added, ${updated} updated, foreign keys OK. No restart needed.`);
