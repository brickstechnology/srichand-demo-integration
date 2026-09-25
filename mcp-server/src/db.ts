import { Database } from "bun:sqlite";
import { join } from "node:path";

const DB_PATH = process.env.SRICHAND_DB ?? join(import.meta.dir, "..", "..", "db", "srichand.db");

export const db = new Database(DB_PATH, { readwrite: true, create: false });
db.exec("PRAGMA foreign_keys = ON; PRAGMA journal_mode = WAL;");

export const all = <T = any>(sql: string, ...params: any[]) => db.query(sql).all(...params) as T[];
export const one = <T = any>(sql: string, ...params: any[]) => (db.query(sql).get(...params) ?? null) as T | null;
export const run = (sql: string, ...params: any[]) => db.query(sql).run(...params);

export const nowIso = () => new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
export const nextId = (table: string, col = "id") => (one<{ n: number }>(`SELECT COALESCE(MAX(${col}),0)+1 AS n FROM ${table}`)!.n);
export const json = (s: string | null) => { try { return s ? JSON.parse(s) : null; } catch { return s; } };

/** Official store rules (source: research/findings/rewards_policies_brand.md). */
export const STORE = {
  freeShippingThreshold: 599,   // published on srichand.com
  flatShippingFee: 50,          // observed in the live cart
  earnBahtPerPoint: 25,         // Srichand Rewards T&C
  bahtPerPointRedeemed: 0.5,    // ASSUMED for the demo — no value is published
  paymentQrMinutes: 30,
  maxUnitsPerItem: 10,          // per SKU per cart; larger (reseller / bulk) orders go to staff
  minMemberAge: 16,             // the LINE sign-up form says 16+; the published T&C say 20+ (conflict flagged to the client) — under 20 needs a guardian
  adultAge: 20,                 // Thai civil-law majority; PDPA treats under-20s as minors
  paymentMethods: ["promptpay_qr", "credit_card", "mobile_banking", "truemoney"] as const,   // COD is not offered
};
