// Builds db/srichand.db from db/schema.sql + db/seed/*.json.   Usage: bun run db:build
import { Database } from "bun:sqlite";
import { existsSync, readFileSync, unlinkSync } from "node:fs";
import { join } from "node:path";
import { TABLES } from "./tables";

const DB_DIR = import.meta.dir;
const DB_PATH = process.env.SRICHAND_DB ?? join(DB_DIR, "srichand.db");
const SEED = join(DB_DIR, "seed");


for (const suffix of ["", "-wal", "-shm"]) if (existsSync(DB_PATH + suffix)) unlinkSync(DB_PATH + suffix);
const db = new Database(DB_PATH, { create: true });
db.exec(readFileSync(join(DB_DIR, "schema.sql"), "utf8"));
db.exec("PRAGMA foreign_keys = ON;");

let total = 0;
for (const table of TABLES) {
  const file = join(SEED, `${table}.json`);
  if (!existsSync(file)) { console.warn(`  (no seed for ${table})`); continue; }
  const rows: Record<string, unknown>[] = JSON.parse(readFileSync(file, "utf8"));
  if (rows.length === 0) { console.log(`  ${table.padEnd(28)} 0`); continue; }
  const cols = Object.keys(rows[0]);
  const stmt = db.prepare(`INSERT INTO ${table} (${cols.join(",")}) VALUES (${cols.map(() => "?").join(",")})`);
  const insertAll = db.transaction((items: Record<string, unknown>[]) => {
    for (const r of items) stmt.run(...cols.map((c) => {
      const v = r[c];
      return v === undefined ? null : typeof v === "boolean" ? (v ? 1 : 0) : typeof v === "object" && v !== null ? JSON.stringify(v) : (v as any);
    }));
  });
  insertAll(rows);
  total += rows.length;
  console.log(`  ${table.padEnd(28)} ${rows.length}`);
}
const fk = db.query("PRAGMA foreign_key_check").all();
if (fk.length) { console.error("Foreign-key violations:", fk.slice(0, 10)); process.exit(1); }
db.exec("VACUUM;");
db.close();
console.log(`\nBuilt ${DB_PATH} — ${TABLES.length} tables, ${total} rows, foreign keys OK.`);
