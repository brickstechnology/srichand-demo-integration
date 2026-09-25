# Srichand AI Beauty Advisor — prototype data layer

Database, tool server and guideline documents for a **personalised beauty advisor on LINE OA** for Srichand (srichand.com): a customer sends a face photo, the agent describes what is visible, recommends Srichand / SASI products and a routine, and also handles product questions, stock, orders, payment, tracking and Srichand Rewards points.

Built by Bricks for a C-level pitch. Snapshot date: **18 Sep 2026**.

> **One rule shaped everything:** facts about Srichand's real products are *never invented*. They are copied from srichand.com (with the source recorded) or left empty. Only operational data — stock quantities, customers, orders, points — is simulated, and every table says which kind it is.

## What's in the box
| Folder | What it is | For whom |
|---|---|---|
| `db/srichand.db` | The SQLite database, ready to query (51 tables, ~12,300 rows) | Developers, analysts |
| `db/schema.sql` · `db/schema.postgres.sql` | The schema (SQLite / PostgreSQL flavours) | Developers |
| `db/seed/*.json` | Every table as readable JSON — the database is rebuilt from these | Developers |
| `mcp-server/` | 26 tools over MCP (stdio or HTTP), each annotated Read or Write (or import `TOOLS` straight into the Elysia.js engine) | Developers |
| `hub/` | **What goes into the Integration Hub.** `hub/journeys` — 20 procedures (the Hub's *Journeys*, like skills); `hub/knowledge` — 15 reference files (the Hub's *Knowledge*, like RAG); `hub/system-prompt.md` — the always-on rules. Open `hub/copy-sheet.html` for copy buttons per Hub field; `hub/hub-content.json` for bulk import; `hub/INDEX.md` for the coverage matrix | Whoever configures the agent |
| `docs/team-guidelines/` | Long-form guidelines for people (brand, legal, engineering): reasoning, output blocklist, vendor terms, lawyer-review lists. The agent does not read these | Legal, brand team, developers |
| `exports/srichand-catalogue.xlsx` | The catalogue as a spreadsheet: products, SKUs and prices, full ingredient lists, advisor mapping, gaps | Everyone |
| `docs/verification-report.md` | **Read this first before presenting.** What was checked, what earlier notes got wrong, known limitations, site errors the client may want to know about | Pitch team |
| `docs/data-dictionary.md` · `docs/erd.md` | Every table and column explained, with real / derived / curated / mock badges; diagrams | Developers, client IT |
| `research/` | Raw snapshot of the official API and product pages, plus three research dossiers with sources | Audit trail |
| `scripts/` | The pipeline that produced everything (Python) | Developers |

## The numbers
- **345** listings on srichand.com → **190** canonical products (SRICHAND 120 · SASI 67 · Baby 3) → **598** SKUs with official SKU codes, list price, sale price and web stock flag
- **4,204** ingredient rows: full INCI for 123 products (120 from the official product page), each linked to a 66-entry ingredient dictionary
- 132 brand-named hero ingredients · 213 verbatim official claims · 132 official how-to-use texts
- Advisor layer: 21 skin concerns · 7 skin types · 16 routine steps · 242 product→concern links (each stating its basis) · 12 layering rules · 5 honest range gaps
- Simulated operations: 41 customers (7 scripted demo personas) · 153 orders · 3 warehouses · 147 gap events · PDPA consent trail

## Quick start
```bash
bun install
bun run db:build      # clean rebuild of db/srichand.db from schema + seed JSON (restart the server afterwards)
bun run db:sync       # apply seed changes to the existing DB in place — keeps live demo rows, no restart
bun run mcp:smoke     # 51-check demo + logic test (builds its own fresh DB; never touches live data), runs on a copy of the DB
bun run mcp           # start the MCP server on stdio
```
Connect from any MCP client:
```json
{ "mcpServers": { "srichand": { "command": "bun", "args": ["run", "mcp-server/src/index.ts"], "cwd": "/path/to/Srichand" } } }
```
### Connecting a hub that asks for an "MCP URL"
```bash
bun run mcp:http      # http://localhost:8787/mcp  (Streamable HTTP, stateless)
```
- The credential is `SRICHAND_MCP_TOKEN` in `.env` (git-ignored; the server refuses to start without one). Hubs send it as `Authorization: Bearer <token>`; `x-api-key` also works.
- `GET /health` needs no credential and returns the tool count.
- After code changes: `bun run mcp:restart` (stops only the process *listening* on the port, then starts the server). Do not use a bare `lsof -ti tcp:8787 | xargs kill` — it also matches ngrok's connection to the port and takes the tunnel down.
- A hub on another machine needs a public HTTPS address: for a demo, `ngrok http 8787`; for the team, deploy the `Dockerfile` (not yet built or tested) to any container host.
- **Customer identity belongs to the hub.** The hub pairs a LINE account with a customer (Accounts page) and injects that key; every customer tool accepts a numeric `customers.id` (`5`), a Rewards member number (`SCR0260005`) or a LINE userId. An unpaired account gets a clear "not paired yet" error — catalogue, stock, routine and promotion tools still work without a customer.
- **New members:** `register_member` is the one customer-facing tool that is *not* bound to a customer id — it is for chats the hub has not paired yet. It creates the customer + Srichand Rewards account and returns the member number (`SCR…`); staff paste that into hub → Accounts and press verify (which calls `get_customer`). It refuses a mobile number that already has an account without revealing anything about it, requires explicit acceptance of the terms, records marketing consent separately, and needs a guardian for ages 16–19. No SMS OTP is sent in the prototype (`phone_verified = 0`) — production must add it.
- The injected argument is called `line_user_id` by default; if your hub injects under another name, set `SRICHAND_CUSTOMER_ARG=<that name>`.
- Off by default, opt-in for standalone demos: `SRICHAND_AUTO_REGISTER=1` (create a customer on first contact from a LINE userId) and `SRICHAND_DEMO_TOOLS=1` (adds `demo_link_persona`). `bun run db:build` resets all demo writes.
- **Adding a persona:** append to `late_personas` (+ their `persona_sessions` / `persona_orders` / `persona_carts` with the new customer id) in `scripts/mock_config.json`, then `python3 scripts/04_generate_mock.py && bun run db:sync`. Late personas use their own random seed, so existing customers' data does not change.

Set `SRICHAND_READONLY=1` to expose only the 13 read tools; `SRICHAND_DB=/path/to.db` to use another file. Inside the Elysia.js engine you can skip MCP: `import { TOOLS } from "./mcp-server/src/tools"` — each tool is `{ name, description, input (zod shape), handler }`.

Refresh the catalogue (prices change weekly): re-download the Store API pages into `research/raw/` (see `docs/verification-report.md`), then `bun run data:all`.

## Tools
| Read | Write |
|---|---|
| `list_reference_data` · `search_products` · `get_product` · `match_shade` · `check_stock` · `get_promotions` | `register_member` · `cart_add_item` · `cart_update_item` · `clear_cart_item` · `create_order` · `confirm_payment_mock` |
| `recommend_routine` *(deterministic)* · `check_ingredient_conflicts` · `get_range_gaps` | `record_consent` · `set_marketing_preference` · `withdraw_consent_and_erase` |
| `get_customer` · `get_order_status` · `get_loyalty` · `cart_view` | `save_skin_profile` · `save_skin_analysis` · `save_routine` · `log_range_gap` |

**Read vs Write is declared, not guessed.** Every tool carries MCP annotations: the 13 read tools send `readOnlyHint: true`; the 13 write tools send `readOnlyHint: false` with `destructiveHint` (`withdraw_consent_and_erase` and `clear_cart_item`, which can empty a basket in one call) and `idempotentHint` (`confirm_payment_mock`, `save_skin_profile`, `withdraw_consent_and_erase`, `cart_update_item`, `clear_cart_item`). Descriptions are prefixed `[READ]` / `[WRITE]` for hubs that ignore annotations. The smoke test fingerprints the whole database around every read tool to prove reads change nothing — so a hub can safely let read tools run without approval.

Order lifecycle: `create_order` reserves stock (online warehouses only, split across them if needed) → `confirm_payment_mock` turns the reservation into a sale and awards points → if the 30-minute payment window passes, the order can no longer be paid and is cancelled on the customer's next cart/order action: stock released, points and coupon restored, items returned to the cart. Customer tools only ever return that customer's own orders.

Design choices worth pointing out in the room:
- **Consistency.** `recommend_routine` scores products in SQL/TypeScript, not in the language model: the same customer inputs always return the same routine (the smoke test asserts byte-identical output). The model only explains.
- **No hallucinated products.** The agent reads names, prices, shades, stock and ingredients from the database every time.
- **Honest gaps become a product.** When Srichand has nothing for a need, the advisor says so, may suggest a *generic* option (never a competitor), and logs it — `v_gap_demand` is a ready-made R&D signal.
- **PDPA by design.** No image is stored in the database; explicit, separate consents; under-20s default to a no-photo questionnaire; one call erases a customer's skin data.
- **Claims guardrails.** Thai FDA-safe wording per concern, verbatim official claims, and an output blocklist.

## Hub content: Journeys and Knowledge
The Hub has two mechanisms and the content keeps them strictly apart:
- **Journeys** are *procedures*: when to use (a `ใช้เมื่อ…` line built from words customers really say — the model selects on this line, not on the name), goal, steps, branches, which tools to call, which knowledge files to open. They contain no prices, thresholds or policy numbers.
- **Knowledge** files are *reference*: rules, wording tables, consent texts, policies, ingredient facts, glossaries. They name no tools and contain no procedures.

`python3 scripts/09_build_hub.py` enforces this and fails if a journey points at something that does not exist, a tool has no journey, a knowledge file is never opened, a knowledge file names a tool, or a journey states a fact. Edit the Markdown in `hub/journeys` and `hub/knowledge`, re-run the script, then paste from `hub/copy-sheet.html`.

Journeys are advisory — the model may not follow them. Anything that must hold (consent before photo analysis, ownership of orders, stock, coupon and age rules, no duplicate members) is enforced inside the tools, and Read/Write is declared by annotation so the Hub can gate the write tools.

## Demo personas (`customers.is_demo_persona = 1`)
| # | Persona | Shows |
|---|---|---|
| 1 | **Ploy**, 27, oily T-zone, Silom office | Photo analysis → BHA gap handled honestly → order in transit |
| 2 | **Mint**, 17, breakouts, ฿150 budget | Age gate → no-photo path; SASI budget routine; refer-out wording |
| 3 | **Nok**, 42, melasma-type patches, sensitive | Non-diagnostic wording; fragrance-free routine; azelaic gap |
| 4 | **Beam**, 31, first routine, 3 steps max | Minimal routine; his PromptPay QR has expired → order auto-cancels, items return to the cart, one-step re-order |
| 5 | **Fern**, 35, makeup lover, top spender | Shade match (110 Vanilla, 3 left); reorder; points redemption |
| 6 | **Dao**, 56, dry skin, fine lines | Bakuchiol first, slow retinoid ramp-up; eye-care gap |
| 41 | **Por**, 33, runner, combination skin, stings after shaving | Men's two-minute routine; INCI-checked fragrance-free picks; water-resistant sunscreen; body-sunscreen gap; parcel in transit with free gift; open cart |

## Before this goes in front of the client
1. Read `docs/verification-report.md` — especially §A1 (claims from earlier notes that turned out wrong) and §B3 (limitations).
2. Re-pull prices the day before.
3. Have legal look at `hub/knowledge/claim-wording-thai-fda.md` and `hub/knowledge/privacy-consent-and-data-rules.md` (and their long-form versions in `docs/team-guidelines/02` and `03`); all are drafts.
4. Swap the placeholder loyalty redemption value and reward list for Srichand's real ones if they share them.
# srichand-demo-integration
