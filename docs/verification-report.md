# Verification report

Snapshot date **18 Sep 2026**. Two jobs: (A) recheck the sources and claims carried over from the earlier chat and the draft catalogue JSON, and (B) audit the database built here.

**Headline:** the draft's product names, sizes and sale prices were mostly right, but six of its *analytical* claims were wrong or out of date — including the two the pitch leaned on hardest ("no BHA anywhere", "the AHA is inside Super C"). All are corrected in the database and knowledge docs.

## How things were verified
| Source | Used for | Reliability |
|---|---|---|
| srichand.com public Store API (`/wp-json/wc/store/v1/products`) — 345 listings, 1,339 variations, archived in `research/raw/` | Names, SKUs, list and sale prices, stock flags, Thai copy, images | Official, machine-read |
| srichand.com product pages — "ส่วนผสม" and "วิธีใช้" tabs, 149 pages, archived in `research/raw/official_tabs_2026-09-18.json` | Full INCI lists (120 products), directions (132) | Official |
| Watsons TH, Internet Archive, INCIDecoder, SkinSort, Cosmenet | Cross-checks; fallback for 3 products whose official tab is empty | Retailer / third-party |
| srichand.com policy, membership and campaign pages + an anonymous live test cart | Rewards rules, shipping, payment, returns, campaigns | Official |
| Cosmetics Act, Thai FDA advertising manual, PDPA, PDPC notifications, law-firm summaries | Knowledge docs 02–03 | Primary + secondary (flagged) |
Three research agents did the legwork; two of them independently cross-checked 41 key INCI lists against a second source (37 had one; every second source agreed with the primary list except one two-ingredient ordering swap).

---
## A. Claims from the earlier chat and the draft JSON

### A1. Wrong or out of date — corrected
| # | Claim | Finding | Evidence |
|---|---|---|---|
| 1 | "**No BHA anywhere in the range** … the real gap for oily skin" | **Wrong.** Salicylic acid is on the official INCI of **13 products**: Sunlution Acne Care (#32 of 54; the official page itself advertises "Salicylic Acid Sphere") and 12 SASI products, including two **leave-on toner pads**. The accurate gap: no *SRICHAND-brand* leave-on BHA treatment, and no stated BHA strength anywhere. | `product_ingredients`; official pages |
| 2 | "The range **does have an AHA** — glycolic acid sits inside the Super C serum… this IS the range's AHA" | **Misleading.** Glycolic acid is #26 of 36 in the serum — *after* the fragrance (#25) — and #24 of 29 in the gel cream. Those are trace / pH-adjuster positions, not an exfoliating dose. The three vitamin-C forms in the serum (#29–31) also sit after the fragrance. Do not present Super C as an exfoliant. | Official INCI |
| 3 | Sunlution Acne Care "also contains niacinamide, 3-O-ethyl ascorbic acid, tocopherol, palmitoyl tetrapeptide-10" | **Wrong product.** Those belong to Sunlution *Skin Whitening*. A mislabelled INCIDecoder upload (July 2022) copies the Whitening list under the Acne Care name and ranks first in web search. The real list has gluconolactone, tocopheryl acetate, ascorbic acid, palmitoyl tripeptide-5, ceramides — and salicylic acid. | Official INCI = Watsons = SkinSort |
| 4 | "Two of those filters aren't even **approved for sale in the United States**" | **Out of date / imprecise.** The US FDA finalised its bemotrizinol (Tinosorb S) order on 9 Jun 2026. Today: DHHB (Uvinul A Plus) and ethylhexyl triazone (Uvinul T150) are still not permitted as US OTC sunscreen actives; Tinosorb S now is. Say "not permitted as sunscreen actives under the US OTC monograph", not "approved for sale". | FDA press release (via research agent; effective date from secondary summaries) |
| 5 | "**Bare To Perfect** Translucent Powder — the heritage hero, the purple powder they're known for" | **Wrong product.** The heritage hero is the classic **Srichand Translucent Powder** (relaunched 2014). Bare to Perfect is a separate, later line with a different formula. Both have purple *packaging*; neither powder is purple. The pastel multi-colour one is *Bare to Perfect Correcting Loose Powder*. "Reef-safe / fungal-acne-safe" were SkinSort's algorithmic tags, meaningless for a face powder. At snapshot, both Bare to Perfect translucent sizes were **out of stock**; the classic was in stock. | Store API, official images, Watsons |
| 6 | Draft prices marked `price_confirmed: true` (฿269, ฿149, ฿395, ฿129) | **Right numbers, wrong label.** They are *sale* prices. List prices are ฿435–495 for core skincare (e.g. Gel Cream 120 ml: list ฿790, sale ฿395). The schema now stores both. | Store API |
| 7 | Cleanser URL in the draft points to the 50 ml page while the entry describes the 100 ml at ฿149 | Mismatch. 100 ml: list ฿189 / sale ฿149; 50 ml: ฿99 / ฿79. | Store API |
| 8 | Skin Moisture Burst line = "niacinamide + hyaluronic acid + trehalose + centella" · Barrier Boost = "panthenol + ectoin + dipotassium glycyrrhizate" | **No single product has the full set.** Essence: niacinamide, panthenol, HA. Serum: niacinamide, HA. Gel cream: trehalose, centella, HA. Line-wide commons are glyceryl glucoside + sodium hyaluronate. Barrier Boost: true for the three leave-ons; the cleanser has ectoin only. | Official INCI |
| 9 | Range gaps "standalone higher-strength niacinamide" | **Weak.** Phyto Camellia serum and gel cream and Super C gel cream all disclose **5% niacinamide**. Dropped from the gap list. | Official copy |

### A2. Confirmed
| Claim | Evidence |
|---|---|
| Resurface = hydroxypinacolone retinoate (#17) + retinyl palmitate (#30), niacinamide, ceramides NP/AP/EOP, phytosphingosine, cholesterol, bisabolol, acetyl hexapeptide-1, multi-weight HA; fragrance-free | Official INCI (59 ingredients) + second source. *Added:* it also lists Alcohol (#23) and BHT. |
| Super C Intense Serum contains SAP, ascorbic acid, ascorbyl glucoside, niacinamide, tranexamic acid, alpha-arbutin, glycolic acid, allantoin, tocopherol, parfum | All present (see A1-2 for what the positions mean) |
| Sunlution Acne Care's six UV filters (avobenzone, octisalate, ethylhexyl triazone, DHHB, bemotrizinol, titanium dioxide) | Exact match, official INCI |
| Sunlution Skin Whitening is hybrid and fragrance-free | INCI. "Matte" is a third-party descriptor; the brand says "micro-blur primer, absorbs oil" |
| Sizes: Acne Care 40 ml + 15 ml + 7 ml sachet; Gel Cream 50/120 ml; Day to Glow 3.2 g ฿129 (list ฿199) | Store API |
| No azelaic acid; no dedicated eye product | 0 INCI rows; 0 catalogue matches |
| Watsons TH stocks Sunlution and Resurface | 14 Watsons listings matched official INCI in order |

### A3. Missing from the draft (now in the database)
Timeless Anti-Aging (bakuchiol) · Advanced Anti-Melasma Serum · Super C Essence and Gel Cream · Barrier Boost Essence · both 15X Ampoule Masks · Sunlution Rosia, Moisture Burst Watery and Tone Up · Original Powder Mask · the classic Translucent Powder · the full base range (Skin Essential Fine Smooth 2026 renewal, Super Coverage, Enchanted, Skin Booster, Super Fix, Porefect) · all colour and lip · **all of SASI (67 products)** · Baby · 32 sets · gift items. Draft: 17 products → database: 190 products / 598 SKUs.

---
## B. Audit of this database

### B1. Integrity checks (all pass)
| Check | Result |
|---|---|
| Foreign-key check on the built DB | 0 violations |
| Every one of 345 site listings mapped to a canonical product | 0 unmapped |
| Variants with an official SKU | 598 / 598 |
| Variant prices vs raw API (list and sale, THB) | Copied programmatically; no manual entry |
| INCI coverage | 123 of 149 single products have a full INCI list (120 from the official product page, 3 retailer fallback, marked per row). Of the 135 *active* single products, 122 are covered; 13 have no list published anywhere we could cite and are left empty |
| Key INCI positions re-derived and matched against an independent agent's reading | HPR #17/59 · salicylic #32/54 · glycolic #24/29 and #26/36 · fragrance #25/36 — all match (a tokenizer bug that shifted positions by one was found and fixed during this check) |
| Demo smoke test (`bun run mcp:smoke`) | 23 / 23 pass, incl. determinism (same input twice → byte-identical routine) |
| Mock data uses only payment methods the site really offers | Yes — no COD rows |
| Mock orders honour the real shipping rule (free ≥ ฿599, else ฿50) and earn rate (฿25 = 1 pt) | Yes |

### B2. Errors I made and corrected during the build
1. Assumed product pages carried no INCI (the Store API omits it). A research agent found the ingredient tab; I then scraped all 149 pages, replacing third-party lists with official ones.
2. Initial demo assumptions of loyalty tiers, cash on delivery, ฿499 free-shipping and a welcome bonus were all **contradicted by official policy** and removed.
3. First-draft Thai wording for acne and melasma concerns ("ช่วยลดสาเหตุของการเกิดสิว", "ช่วยให้ฝ้า กระ แลดูจางลง") would breach the Thai FDA guideline; rewritten.
4. Rated the Barrier Boost cleanser "ideal" for sensitive skin before seeing that its INCI contains Parfum and two colourants; downgraded, and `is_fragrance_free` is now computed from INCI, not marketing copy.
5. Seven gift-with-purchase thresholds printed on gift listings were loaded as active; a live test cart showed only the ฿499 gift triggers, so the rest are stored inactive.
6. A "mini size" rule mislabelled the 50 ml Gel Cream as a mini; fixed (≤ 20 ml/g only).

### B2b. Tool-logic audit (second pass, after connecting to the hub)
| Finding | Fix |
|---|---|
| The server sent no MCP annotations, so a hub had to treat all tools as Write | 13 tools now declare `readOnlyHint: true`; 9 declare write, with `destructiveHint` / `idempotentHint` set honestly |
| Four "read" tools could insert a customer when auto-registration was on | Reads never create; the smoke test fingerprints the whole DB around every read tool |
| `get_order_status` returned any order by number — and numbers are sequential | Lookups are scoped to the injected customer |
| `confirm_payment_mock` claimed to move stock but did not; reservations could silently reserve nothing or use the retail depot | Reserve → sale / release lifecycle tracked in `inventory_movements`, online warehouses only |
| Expired PromptPay orders held stock and points forever | Expired orders cannot be paid; they are cancelled on the next cart/order write, with stock, points, coupon and cart restored |
| Coupons: no max-use, date-window, owner or discount-cap checks; points could exceed the order value | All validated |
| `cart_add_item` ignored quantity already in the cart; accepted gifts and unlisted SKUs | Fixed |
| `recommend_routine` filled optional steps on skin-type fit alone, counted trace glycolic acid as an AHA step, returned an arbitrary shade | Optional steps need a matched concern; exfoliating acids count only in the first half of the INCI (or when brand-named); shade products return `needs_shade_match` |
| PDPA erase kept routines; photo analysis did not require the cross-border consent; no tool stored questionnaire answers; demo script notes leaked to the agent | Fixed; `save_skin_profile` added; `persona_brief` no longer returned |

### B2c. Membership registration (added after the hub pairing model was confirmed)
`register_member` creates the customer and Srichand Rewards account and returns the member number the hub pairs with. It is deliberately not customer-bound (unpaired chats must be able to call it), refuses duplicate mobile numbers without disclosing the existing account, requires explicit terms acceptance, stores marketing consent separately, enforces 16+ with a guardian for 16–19 (the client's own documents conflict: T&C 20+, LINE form 16+), and marks the phone as unverified because the prototype sends no OTP. `customers.line_user_id` became nullable: the hub, not this database, owns the LINE ↔ member mapping.

### B3. Known limitations — read before presenting
| Item | Detail |
|---|---|
| **Prices move.** | 453 of 598 SKUs were on sale at snapshot. Re-run `scripts/01_build_catalog.py` against a fresh API pull before any demo. |
| Set contents | `bundle_components` is text-matched from official copy; quantities only where printed in the listing name. Verify against the client's BOM. |
| English names and summaries | The official site is Thai-only. English names come from URL slugs (+ hand fixes); 33 core products have a Bricks-written English summary; the rest have Thai copy only. |
| Shade undertone / depth | Derived from shade names and numbering — approximate. 5 products publish official "suits skin tone" lines (28 shades), stored verbatim. |
| Shade-specific INCI | For colour products the brand lists INCI per shade group; the DB stores the first group and flags it in `shade_scope`. |
| 3 retailer-sourced INCI lists | Moisture Burst Watery Sunscreen (official tab holds marketing copy with an "XX hours" placeholder), Bi-Phase Cleansing Water (Internet Archive copy of Watsons), Super Fix powder (two sources disagree on the order of two ingredients). |
| 13 active products without any published INCI | Mostly SASI/older colour items and the BamBam lip balms. Left NULL. |
| Barcodes | Not published anywhere; NULL. |
| 462 hidden variations | The API exposes variations whose parent listing is unpublished (old multipacks, merchandise, the discontinued Selene line). Excluded, except the Sunlution Acne Care 40 ml single (live SKU `41044002`, ฿299, sold on-site only as a twin pack) — kept with `is_listed_on_site = 0`. |
| Lifecycle | "clearance_only" and "all variants out of stock" are observations, not confirmed discontinuations. |
| Loyalty redemption | Srichand publishes no point value or reward list; 1 pt = ฿0.50 and the 4 rewards are **assumptions**, flagged `assumed_for_demo`. |
| Regulatory docs | Drafts. The 2567 (2024) FDA manual could not be opened directly; those rows rely on secondary transcriptions. 19 items are listed for counsel in `research/findings/thai_regulatory.md` §5. |
| FDA bemotrizinol date | Order finalised 9 Jun 2026 per FDA press release; the 9 Aug 2026 effective date is from secondary summaries. |

### B4. Things found on srichand.com that the client may want to know
A by-product of reading every page — useful goodwill in the room, handle tactfully:
1. The legacy Fine Smooth Foundation 30 ml page shows a **powder** ingredient list; the Matte Primer 6 g page shows the **Glow** Primer's copy and list; the new 30 g foundation's list is cut off mid-word for shade 120; the Moisture Burst Watery ingredient tab contains marketing copy with a placeholder "**XX hours**".
2. Typos in published INCI ("PEG/PPG-17/6 COPOLYMER 6920", "Pentaeryth rityl", "Glycereth -26") — Watsons has copied them.
3. Moisture Burst Watery markets a "15HYA complex"; 12 hyaluronic-type ingredients are declared.
4. The classic Translucent Powder's list includes methylisothiazolinone (restricted in EU leave-on products) — label not physically checked.
5. SASI Acne Sol cleansing gel claims "SLS-free" and is SLES-based; it also claims fragrance-free while containing tea tree oil.
6. Several live product descriptions use phrasing the 2567 FDA guideline appears to restrict ("ลดการสร้างเม็ดสีเมลานิน", "กระตุ้นการสร้างคอลลาเจน", "ช่วยลดการเกิดฝ้า กระ").
7. Srichand Rewards: T&Cs say members must be 20+, the LINE sign-up form says 16+.
8. The Store API publicly exposes hidden/unpublished variations, including low-stock counters.
