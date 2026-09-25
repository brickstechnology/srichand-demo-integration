/**
 * Srichand advisor tools. Plain functions + zod input shapes, so they can be
 *   (a) served over MCP (see index.ts), or
 *   (b) imported directly by the Elysia.js engine:  import { TOOLS } from "./tools"
 * Every read returns rows from the database — the agent never recalls product facts from model memory.
 */
import { z } from "zod";
import { all, db, json, nextId, nowIso, one, run, STORE } from "./db";

type Shape = Record<string, z.ZodTypeAny>;
export interface ToolDef<S extends Shape = Shape> {
  name: string;
  /** "read" handlers must never change the database (asserted by the smoke test) → readOnlyHint: true. */
  kind: "read" | "write";
  /** write tools only: may overwrite or delete existing data (default false = additive). */
  destructive?: boolean;
  /** write tools only: calling twice with the same arguments has no further effect. */
  idempotent?: boolean;
  title?: string;
  description: string;
  input: S;
  /** Optional MCP outputSchema. Declaring it makes the returned fields (image_url included) part of the
   *  tool's advertised contract, so a hub that renders from the schema knows they exist. When present,
   *  server.ts also sends the result as `structuredContent` — the SDK requires that and validates it,
   *  so every shape here is deliberately permissive: unknown keys pass through, and anything the
   *  handler may omit or null out is optional/nullable. */
  output?: Shape;
  handler: (args: z.infer<z.ZodObject<S>>) => unknown;
}
const tool = <S extends Shape>(t: ToolDef<S>) => t as unknown as ToolDef;

// ───────────────────────────── output shapes (see ToolDef.output)
const nul = <T extends z.ZodTypeAny>(t: T) => t.nullable().optional();
/** Loose object: declared keys are documented, undeclared ones still pass validation. */
const loose = (shape: Shape) => z.object(shape).passthrough();

/** One product card as search_products returns it. */
const productCardOut = loose({
  id: z.number(), slug: nul(z.string()), name_en: nul(z.string()), name_th: nul(z.string()),
  brand: nul(z.string()), line: nul(z.string()), category: nul(z.string()),
  official_url: nul(z.string()),
  image_url: nul(z.string()).describe("Official product photo from srichand.com — show this in carousels and cards."),
  price_from: nul(z.number()), variant_count: nul(z.number()), variants_in_stock: nul(z.number()),
});

/** One variant/SKU card, as variantCard() builds it. */
const variantCardOut = loose({
  variant_id: nul(z.number()), sku: nul(z.string()), label: nul(z.string()), pack_format: nul(z.string()),
  shade: nul(z.string()), list_price: nul(z.number()), sale_price: nul(z.number()), current_price: nul(z.number()),
  web_in_stock: nul(z.boolean()), qty_available_online: nul(z.number()),
  image_url: nul(z.string()).describe("Official product photo from srichand.com."),
});

/** One line in a cart or an order. */
const lineItemOut = loose({
  variant_id: nul(z.number()), sku: nul(z.string()), name_en: nul(z.string()), name_th: nul(z.string()),
  variant_label: nul(z.string()), quantity: nul(z.number()), current_price: nul(z.number()),
  unit_price: nul(z.number()), line_total: nul(z.number()),
  image_url: nul(z.string()).describe("Official product photo from srichand.com."),
});

const price = (v: { list_price: number; sale_price: number | null }) => v.sale_price ?? v.list_price;
const like = (s: string) => `%${s.trim().toLowerCase()}%`;

/** One free-text term of search_products, matched across name, line, marketing copy, hero ingredients and INCI.
 *  Takes 7 bind params — termParams() supplies them. */
const TERM_MATCH = `(lower(p.name_en) LIKE ? OR lower(p.name_th) LIKE ? OR lower(COALESCE(l.name_en,'')) LIKE ? OR lower(COALESCE(p.summary_en,'')) LIKE ? OR lower(COALESCE(p.description_th,'')) LIKE ?
        OR EXISTS (SELECT 1 FROM product_hero_ingredients h WHERE h.product_id = p.id AND lower(h.hero_name) LIKE ?)
        OR EXISTS (SELECT 1 FROM product_ingredients pi WHERE pi.product_id = p.id AND lower(pi.inci_as_listed) LIKE ?))`;
const termParams = (t: string) => Array(7).fill(like(t));
/** The joins every catalogue query needs, so the search and its per-term diagnosis stay in step. */
const CATALOGUE_FROM = `FROM products p JOIN brands b ON b.id = p.brand_id LEFT JOIN product_lines l ON l.id = p.line_id
      JOIN categories c ON c.id = p.category_id LEFT JOIN categories pc ON pc.id = c.parent_id`;

/** Resolve the customer key the hub injects. Accepts, in order: numeric customers.id ("5"), Srichand Rewards member
 *  number ("SCR0260005"), or a LINE userId ("U…"). Identity mapping (LINE account → customer) is the hub's job, so an
 *  unknown key is an error. READ tools never create anything; only WRITE tools pass { create: true }, and even then a
 *  customer is created only when SRICHAND_AUTO_REGISTER=1. */
function customerByLine(customerKey: string, opts: { create?: boolean } = {}) {
  const key = String(customerKey ?? "").trim();
  let c = /^\d+$/.test(key) ? one("SELECT * FROM customers WHERE id = ?", Number(key))
    : /^SCR\d+$/i.test(key) ? one("SELECT c.* FROM customers c JOIN loyalty_accounts a ON a.customer_id = c.id WHERE a.member_number = ?", key.toUpperCase())
    : one("SELECT * FROM customers WHERE line_user_id = ?", key);
  if (!c && opts.create && process.env.SRICHAND_AUTO_REGISTER === "1" && /^U[0-9a-f]{32}$/i.test(key)) {
    const id = nextId("customers"), now = nowIso();
    run("INSERT INTO customers (id, line_user_id, preferred_language, marketing_opt_in, is_demo_persona, created_at) VALUES (?,?,?,?,?,?)", id, key, "th", 0, 0, now);
    run("INSERT INTO loyalty_accounts (customer_id, member_number, tier_id, points_balance, lifetime_points, spend_this_period, joined_at) VALUES (?,?,?,?,?,?,?)", id, `SCR${String(260000 + id).padStart(7, "0")}`, 1, 0, 0, 0, now);
    c = one("SELECT * FROM customers WHERE id = ?", id);
  }
  if (!c) throw new Error(`No Srichand customer matches "${key}". This LINE account is probably not paired to a customer yet (hub → Accounts). Product, stock and promotion tools still work without a customer.`);
  return c;
}

/** A session id supplied by the agent is only trusted if it belongs to this customer. */
const ownSession = (customerId: number, sessionId?: number | null) =>
  sessionId != null && one("SELECT id FROM face_analysis_sessions WHERE id = ? AND customer_id = ?", sessionId, customerId) ? sessionId : null;

/** Active ingredient classes of a product: everything the brand names as a hero, plus INCI actives — except that an
 *  exfoliating acid only counts when it sits in the first half of the INCI list (trace glycolic acid used as a pH adjuster
 *  is not an "AHA step"). */
const activeClasses = (productId: number): string[] => all(`
  SELECT DISTINCT i.ingredient_class AS k FROM product_hero_ingredients h JOIN ingredients i ON i.id = h.ingredient_id WHERE h.product_id = ?
  UNION
  SELECT DISTINCT i.ingredient_class FROM product_ingredients pi JOIN ingredients i ON i.id = pi.ingredient_id
   WHERE pi.product_id = ? AND pi.is_key_active = 1
     AND (i.ingredient_class NOT IN ('aha','bha') OR pi.position * 2 <= (SELECT MAX(z.position) FROM product_ingredients z WHERE z.product_id = pi.product_id))
  ORDER BY 1`, productId, productId).map((r) => r.k);

/** Age in whole years, or null when we have no birth date (auto-registered LINE users). */
const ageOf = (c: any): number | null => (c.birth_date ? Math.floor((Date.now() - Date.parse(c.birth_date)) / 31557600000) : null);

function availability(variantId: number) {
  const s = one<{ qty_available_online: number }>("SELECT qty_available_online FROM v_stock_available WHERE variant_id = ?", variantId);
  return s?.qty_available_online ?? 0;
}

/** Product shot for a variant. Images live on products, not variants: rows from v_variant_catalog
 *  already carry it, rows straight out of product_variants are looked up by product_id. */
const productImage = (productId: number | null | undefined) =>
  productId == null ? null : (one<{ image_url: string | null }>("SELECT image_url FROM products WHERE id = ?", productId)?.image_url ?? null);

function variantCard(v: any) {
  return {
    variant_id: v.id ?? v.variant_id, sku: v.sku, label: v.variant_label, pack_format: v.pack_format,
    shade: v.shade_code || v.shade_name ? `${v.shade_code ?? ""} ${v.shade_name ?? ""}`.trim() : null,
    list_price: v.list_price, sale_price: v.sale_price, current_price: price(v),
    web_in_stock: !!v.web_in_stock, qty_available_online: availability(v.id ?? v.variant_id),
    image_url: v.image_url ?? productImage(v.product_id),
  };
}

// ───────────────────────────────────────────── reference
const listReferenceData = tool({
  name: "list_reference_data", kind: "read",
  description: "Slugs the other tools accept: skin concerns (with photo cues, Thai-FDA-safe wording and refer-out rules), skin types, routine steps, brands, categories. Call once per conversation.",
  input: {},
  handler: () => ({
    skin_concerns: all("SELECT slug, name_en, name_th, concern_group, photo_detectable, photo_cues_en, cosmetic_wording_th, refer_out_when_en FROM skin_concerns ORDER BY id"),
    skin_types: all("SELECT slug, name_en, name_th, description_en FROM skin_types ORDER BY id"),
    routine_steps: all("SELECT slug, name_en, name_th, step_order, applies_am, applies_pm, is_makeup FROM routine_steps ORDER BY step_order"),
    brands: all("SELECT slug, name_en, name_th, positioning, target_audience FROM brands"),
    categories: all("SELECT c.slug, c.name_en, c.name_th, p.slug AS parent FROM categories c LEFT JOIN categories p ON p.id = c.parent_id ORDER BY c.sort_order"),
  }),
});

// ───────────────────────────────────────────── catalogue
const searchProducts = tool({
  name: "search_products", kind: "read",
  description: [
    "Search the SRICHAND / SASI catalogue by free text (Thai or English) and/or filters.",
    "",
    "ALL FREE TEXT GOES IN `queries` — an ARRAY, always, even for a single term. There is no `query` argument.",
    "`queries` takes 1 to 5 terms and returns their UNION: a product is returned if it matches ANY term, deduplicated, with the ones matching the most terms first. Each hit carries `matched_terms` saying which terms it answered.",
    "  queries: ['cushion']                 → one term, still an array.",
    "  queries: ['ล้างหน้า','กันแดด']      → 3 cleansers + 9 sunscreens = 11 products in ONE result list (the one product matching both appears once, first). That is the two searches you would otherwise make one after the other.",
    "So never call this tool twice for one question. Looking for several different products at once — a whole routine, a comparison, 'do you have X and Y?' — is ONE call with every term in `queries`. Repeated terms are ignored. Omit `queries` entirely to browse by filters alone (category, concern, brand, price).",
    "`per_term` reports how many products each term matched, so a term that matched nothing is visible immediately — that one is a range gap (get_range_gaps / log_range_gap), even when the other terms returned plenty.",
    "Set match: 'all' to switch to the INTERSECTION instead — only products matching EVERY term, for narrowing one product down by two facets (ingredient + format, concern + texture). The default 'any' is what you want for finding several different products.",
    "",
    "ONE CALL ALSO ANSWERS THE PRODUCT QUESTION — every hit already carries everything get_product would return: variants with SKU, price, shade and live stock, hero ingredients, key actives, official Thai claims, concerns, skin types, routine step, how to use and provenance. Only call get_product when you have an id or slug and did not search.",
    "",
    "detail: 'card' returns name, brand, price range and stock counts only — use it with a larger limit to browse widely. include_full_inci: true adds the complete INCI list of every hit.",
  ].join("\n"),
  input: {
    queries: z.array(z.string().min(1)).min(1).max(5).optional().describe("THE ONLY free-text input, and always an ARRAY — one term is ['cushion'], not 'cushion'. By default a product is returned if it matches ANY term (union / OR), deduplicated, best matches first: ['ล้างหน้า','กันแดด'] returns the cleansers and the sunscreens together in one list, which is the pair of searches you would otherwise make one after the other. Use one call with every term instead of several calls. Duplicates are ignored. 1-5 terms. Omit it to search by filters alone."),
    match: z.enum(["any", "all"]).default("any").describe("'any' (default) = UNION: a hit matches at least one term — use it to find several different products in one call. 'all' = INTERSECTION: a hit matches every term — use it only to narrow ONE product down by two facets, e.g. ['niacinamide','เซรั่ม'] for niacinamide serums."),
    // Not a real argument: `query` used to exist, and a plain z.object() would silently DROP it and hand back an
    // unfiltered search. z.never() makes the mistake loud and names the fix instead.
    query: z.never({ invalid_type_error: "search_products has no `query` argument — free text goes in `queries`, always as an array: queries: ['niacinamide'] for one term, queries: ['niacinamide','เซรั่ม'] for several (a hit must match every term)." })
      .optional().describe("NOT AN ARGUMENT — removed. Use `queries: [...]`, an array, even for a single term. Sending this is an error."),
    brand: z.enum(["srichand", "sasi", "srichand-baby"]).optional(),
    category: z.string().optional().describe("Category slug or parent slug, e.g. 'serum', 'sunscreen', 'base-makeup'"),
    concern: z.string().optional().describe("Skin concern slug"),
    skin_type: z.string().optional().describe("Skin type slug; excludes products marked 'caution' for it"),
    max_price: z.number().optional().describe("Max current price in THB for at least one variant"),
    in_stock_only: z.boolean().default(true),
    include_sets: z.boolean().default(false),
    detail: z.enum(["full", "card"]).default("full").describe("'full' (default) embeds the whole get_product payload in every hit — no follow-up call needed. 'card' returns name, brand, price range and stock counts only; use it with a large limit when browsing."),
    include_full_inci: z.boolean().default(false).describe("Only with detail: 'full' — add the complete INCI list of every hit (long). Key actives are always included either way."),
    limit: z.number().int().min(1).max(30).optional().describe("Caps the COMBINED result, not each term — with several terms in `queries` raise it, or the terms ranked lower are cut off. Defaults to 5 with detail: 'full' (each hit is a whole product) and 10 with detail: 'card'."),
  },
  output: { count: z.number(), products: z.array(productCardOut),
            terms: z.array(z.string()).optional().describe("The free-text terms that were searched, in the order applied."),
            match: z.enum(["any", "all"]).optional().describe("How the terms were combined: 'any' = union, 'all' = intersection."),
            per_term: z.array(loose({ term: z.string(), matches: z.number() })).optional().describe("With more than one term: how many products each term matches on its own, under the same filters. 0 means that term is a range gap."),
            advice: nul(z.string()) },
  handler: (a) => {
    // Terms are ORed by default (union): a hit matches ANY term, deduplicated by product, most terms matched first.
    // match: "all" switches to AND (intersection). `queries` is the only source of free text.
    const terms = (a.queries ?? []).map((t) => t.trim()).filter(Boolean)
      .filter((t, i, xs) => xs.findIndex((y) => y.toLowerCase() === t.toLowerCase()) === i);
    const filters: string[] = ["p.lifecycle_status = 'active'"], fParams: any[] = [];
    filters.push(a.include_sets ? "p.product_type IN ('single','set')" : "p.product_type = 'single'");
    if (a.brand) { filters.push("b.slug = ?"); fParams.push(a.brand); }
    if (a.category) { filters.push("(c.slug = ? OR pc.slug = ?)"); fParams.push(a.category, a.category); }
    if (a.concern) { filters.push("EXISTS (SELECT 1 FROM product_concerns x JOIN skin_concerns s ON s.id = x.concern_id WHERE x.product_id = p.id AND s.slug = ?)"); fParams.push(a.concern); }
    if (a.skin_type) { filters.push("NOT EXISTS (SELECT 1 FROM product_skin_types x JOIN skin_types s ON s.id = x.skin_type_id WHERE x.product_id = p.id AND s.slug = ? AND x.suitability = 'caution')"); fParams.push(a.skin_type); }
    if (a.in_stock_only) filters.push("EXISTS (SELECT 1 FROM product_variants v WHERE v.product_id = p.id AND v.web_in_stock = 1 AND v.is_listed_on_site = 1)");
    if (a.max_price != null) { filters.push("EXISTS (SELECT 1 FROM product_variants v WHERE v.product_id = p.id AND COALESCE(v.sale_price, v.list_price) <= ?)"); fParams.push(a.max_price); }
    // One flag column per term, so a union result can say WHICH terms each product answered and rank by how many.
    const flags = terms.map((_, i) => `${TERM_MATCH} AS m${i}`).join(", ");
    const termWhere = terms.map(() => TERM_MATCH).join(a.match === "all" ? " AND " : " OR ");
    const rank = terms.length > 1 ? `(${terms.map((_, i) => `m${i}`).join(" + ")}) DESC, ` : "";
    const rows = all(`SELECT p.id, p.slug, p.name_en, p.name_th, b.name_en AS brand, l.name_en AS line, c.name_en AS category, p.spf_value, p.pa_rating,
        p.finish, p.coverage, p.is_fragrance_free, p.summary_en, p.tagline_th, p.official_url, p.image_url,
        (SELECT MIN(COALESCE(v.sale_price, v.list_price)) FROM product_variants v WHERE v.product_id = p.id AND v.pack_format IN ('full_size','mini')) AS price_from,
        (SELECT COUNT(*) FROM product_variants v WHERE v.product_id = p.id) AS variant_count,
        (SELECT COUNT(*) FROM product_variants v WHERE v.product_id = p.id AND v.web_in_stock = 1) AS variants_in_stock
        ${flags ? "," + flags : ""}
      ${CATALOGUE_FROM}
      WHERE ${[...(termWhere ? [`(${termWhere})`] : []), ...filters].join(" AND ")} ORDER BY ${rank}(p.summary_en IS NULL), p.review_count_site DESC, p.id LIMIT ?`,
      ...terms.flatMap(termParams), ...terms.flatMap(termParams), ...fParams, a.limit ?? (a.detail === "full" ? 5 : 10));
    // Which terms each hit answered; the flag columns themselves never leave the tool.
    for (const r of rows) {
      r.matched_terms = terms.filter((_, i) => r[`m${i}`]);
      for (let i = 0; i < terms.length; i++) delete r[`m${i}`];
    }
    // With several terms, always say what each one matched on its own: a term at 0 is a range gap even when the
    // others returned plenty, and the agent sees it without a second search.
    const per_term = terms.length > 1
      ? terms.map((t) => ({ term: t, matches: one<{ n: number }>(`SELECT COUNT(*) AS n ${CATALOGUE_FROM} WHERE ${[TERM_MATCH, ...filters].join(" AND ")}`, ...termParams(t), ...fParams)!.n }))
      : undefined;
    const dead = per_term?.filter((x) => x.matches === 0).map((x) => x.term) ?? [];
    const advice = dead.length
      ? `The range has nothing matching ${dead.map((t) => `"${t}"`).join(" or ")} — treat that as a range gap (get_range_gaps / log_range_gap).`
        + (rows.length ? " The other terms are answered above." : " No term matched anything, so there is nothing to offer from the range.")
      : !rows.length && terms.length > 1 && a.match === "all"
        ? "Each term matches on its own but no product matches them all. Drop a term, or use the default match: 'any' to get the closest hits for each."
        : null;
    const meta = { terms, match: a.match, ...(per_term ? { per_term } : {}), ...(advice ? { advice } : {}) };
    if (a.detail === "card") return { count: rows.length, products: rows, ...meta };
    // Card fields win over the product row (brand / line / category stay the readable names the card carries).
    const products = rows.map((r) => {
      const full = one("SELECT * FROM products WHERE id = ?", r.id)!;
      const { brand, line, ...sections } = productDetail(full, a.include_full_inci);
      return { ...full, free_from: json(full.free_from), ...r, brand_th: brand?.name_th ?? null, line_positioning_en: line?.positioning_en ?? null, ...sections };
    });
    return { count: products.length, products, ...meta };
  },
});

/** Every section get_product returns apart from the product row itself. search_products embeds the same
 *  sections (detail: "full") so answering a product question costs one tool call, not one per result. */
function productDetail(p: any, includeFullInci: boolean) {
  const inci = all("SELECT pi.position, pi.inci_as_listed, pi.is_key_active, pi.shade_scope, i.common_name, i.ingredient_class, i.what_it_does_en, i.caution_en, s.name AS source, pi.source_url FROM product_ingredients pi LEFT JOIN ingredients i ON i.id = pi.ingredient_id JOIN data_sources s ON s.id = pi.source_id WHERE pi.product_id = ? ORDER BY pi.position", p.id);
  return {
    brand: one("SELECT name_en, name_th FROM brands WHERE id = ?", p.brand_id), line: p.line_id ? one("SELECT name_en, positioning_en FROM product_lines WHERE id = ?", p.line_id) : null,
    variants: all("SELECT * FROM product_variants WHERE product_id = ? ORDER BY pack_format, size_value, shade_depth_rank, id", p.id).map((v) => ({ ...variantCard(v), undertone: v.shade_undertone, depth_rank: v.shade_depth_rank, shade_guidance_th: v.shade_guidance_th, listed_on_site: !!v.is_listed_on_site })),
    hero_ingredients: all("SELECT h.hero_name, h.official_benefit_th, i.inci_name, i.what_it_does_en, i.caution_en FROM product_hero_ingredients h LEFT JOIN ingredients i ON i.id = h.ingredient_id WHERE h.product_id = ?", p.id),
    inci: { available: inci.length > 0, count: inci.length, source: inci[0]?.source ?? null, source_url: inci[0]?.source_url ?? null, shade_scope: inci[0]?.shade_scope ?? null,
            key_actives: inci.filter((r) => r.is_key_active).map((r) => ({ position: r.position, of: inci.length, inci: r.inci_as_listed, class: r.ingredient_class })),
            full_list: includeFullInci ? inci.map((r) => r.inci_as_listed) : undefined },
    official_claims_th: all("SELECT claim_type, claim_th FROM product_claims WHERE product_id = ?", p.id),
    concerns: all("SELECT s.slug, s.name_en, x.relevance, x.basis, x.rationale_en FROM product_concerns x JOIN skin_concerns s ON s.id = x.concern_id WHERE x.product_id = ? ORDER BY x.relevance DESC", p.id),
    skin_types: all("SELECT s.slug, x.suitability, x.basis FROM product_skin_types x JOIN skin_types s ON s.id = x.skin_type_id WHERE x.product_id = ?", p.id),
    routine: all("SELECT r.slug AS step, x.use_am, x.use_pm, x.frequency_en, x.usage_note_en FROM product_routine_steps x JOIN routine_steps r ON r.id = x.step_id WHERE x.product_id = ?", p.id),
    sets_containing_this: all("SELECT DISTINCT bp.id AS product_id, bp.name_th, COALESCE(bv.sale_price, bv.list_price) AS price, bv.web_in_stock FROM bundle_components bc JOIN product_variants bv ON bv.id = bc.bundle_variant_id JOIN products bp ON bp.id = bv.product_id WHERE bc.component_product_id = ?", p.id),
  };
}

const getProduct = tool({
  name: "get_product", kind: "read",
  description: "Everything known about one product: official Thai copy, English summary, variants (SKU, price, shade, stock), hero ingredients, full INCI with source, official claims, concerns, skin types, routine step, how to use, provenance.",
  input: { product_id: z.number().int().optional(), slug: z.string().optional(), include_full_inci: z.boolean().default(true) },
  output: { product: loose({ id: z.number(), name_en: nul(z.string()), name_th: nul(z.string()), official_url: nul(z.string()),
              image_url: nul(z.string()).describe("Official product photo from srichand.com.") }),
            variants: z.array(variantCardOut) },
  handler: (a) => {
    const p = a.product_id ? one("SELECT * FROM products WHERE id = ?", a.product_id) : one("SELECT * FROM products WHERE slug = ?", a.slug ?? "");
    if (!p) throw new Error("Product not found");
    return { product: { ...p, free_from: json(p.free_from) }, ...productDetail(p, a.include_full_inci) };
  },
});

const matchShade = tool({
  name: "match_shade", kind: "read",
  description: "Rank a base product's shades for an observed undertone and depth. Uses official shade numbering (depth) and shade names (undertone). Always tell the customer a photo-based match is approximate and lighting-dependent.",
  input: {
    product_id: z.number().int(),
    undertone: z.enum(["cool_pink", "neutral", "warm_yellow", "warm_golden", "peach"]),
    depth: z.enum(["fair", "light", "light-medium", "medium", "tan", "deep"]),
  },
  output: { best: nul(variantCardOut), alternatives: z.array(variantCardOut).optional() },
  handler: (a) => {
    const vs = all("SELECT * FROM product_variants WHERE product_id = ? AND shade_code IS NOT NULL AND pack_format IN ('full_size','mini') ORDER BY size_value DESC", a.product_id);
    if (!vs.length) throw new Error("This product has no shade variants");
    const maxSize = Math.max(...vs.map((v) => v.size_value ?? 0));
    const shades = vs.filter((v) => (v.size_value ?? 0) === maxSize);
    const ranks = shades.map((v) => v.shade_depth_rank).filter((r) => r != null);
    const n = Math.max(...ranks, shades.length);
    const target = { fair: 0.0, light: 0.2, "light-medium": 0.45, medium: 0.65, tan: 0.85, deep: 1.0 }[a.depth] * (n - 1) + 1;
    const near: Record<string, string[]> = { cool_pink: ["neutral"], neutral: ["cool_pink", "warm_yellow"], warm_yellow: ["neutral", "warm_golden"], warm_golden: ["warm_yellow"], peach: ["neutral", "warm_yellow"] };
    const scored = shades.map((v, i) => {
      const rank = v.shade_depth_rank ?? i + 1;
      const tone = v.shade_undertone == null ? 0.5 : v.shade_undertone === a.undertone ? 0 : near[a.undertone]?.includes(v.shade_undertone) ? 1 : 2;
      return { ...variantCard(v), undertone: v.shade_undertone, depth_rank: rank, official_guidance_th: v.shade_guidance_th, score: Math.abs(rank - target) * 1.5 + tone };
    }).sort((x, y) => x.score - y.score || x.variant_id - y.variant_id);
    const deepest = Math.max(...scored.map((s) => s.depth_rank));
    return {
      best: scored[0], alternatives: scored.slice(1, 3),
      caveat: "Approximate: undertone is DERIVED from the official shade name and depth from shade numbering. Recommend swatching on the jawline in daylight.",
      range_limit: a.depth === "deep" || (a.depth === "tan" && deepest <= 4) ? "The deepest shade in this product may still be too light for this skin depth — say so honestly." : null,
    };
  },
});

const checkStock = tool({
  name: "check_stock", kind: "read",
  description: "Live availability for a SKU or variant: srichand.com flag (real, at snapshot time) plus simulated warehouse quantities and restock date.",
  input: { variant_id: z.number().int().optional(), sku: z.string().optional() },
  // NB: `variant` here is a raw v_variant_catalog row (web_in_stock is 0/1, not a boolean), not a variantCard.
  output: { variant: nul(loose({ variant_id: nul(z.number()), sku: nul(z.string()), name_en: nul(z.string()), current_price: nul(z.number()),
              image_url: nul(z.string()).describe("Official product photo from srichand.com.") })),
            available_to_order_online: nul(z.number()), warehouses: z.array(loose({})).optional() },
  handler: (a) => {
    const v = a.variant_id ? one("SELECT * FROM v_variant_catalog WHERE variant_id = ?", a.variant_id) : one("SELECT * FROM v_variant_catalog WHERE sku = ?", a.sku ?? "");
    if (!v) throw new Error("Variant not found");
    const wh = all("SELECT w.code, w.name, w.serves, i.qty_on_hand, i.qty_reserved, i.qty_on_hand - i.qty_reserved AS qty_available, i.next_restock_date FROM inventory i JOIN warehouses w ON w.id = i.warehouse_id WHERE i.variant_id = ?", v.variant_id);
    const online = wh.filter((w) => w.serves === "online_orders").reduce((s, w) => s + w.qty_available, 0);
    return { variant: v, available_to_order_online: online, low_stock: online > 0 && online <= 5, next_restock_date: wh.map((w) => w.next_restock_date).filter(Boolean).sort()[0] ?? null, warehouses: wh, note: "Warehouse quantities are SIMULATED in this prototype." };
  },
});

const getPromotions = tool({
  name: "get_promotions", kind: "read",
  description: "Active promotions. Pass a basket subtotal to see which coupons / gifts apply and how far the basket is from free shipping (official rule: free from ฿599, else ฿50).",
  input: { basket_subtotal: z.number().optional() },
  handler: (a) => {
    const promos = all("SELECT p.id, p.code, p.name_th, p.name_en, p.promo_type, p.mechanics_en, p.min_spend, p.discount_type, p.discount_value, p.ends_at, p.origin, (SELECT group_concat(c.code) FROM coupons c WHERE c.promotion_id = p.id) AS coupon_codes FROM promotions p WHERE p.is_active = 1 AND (p.starts_at IS NULL OR p.starts_at <= ?) AND (p.ends_at IS NULL OR p.ends_at >= ?) ORDER BY p.promo_type, p.min_spend", nowIso(), nowIso());
    const s = a.basket_subtotal;
    return {
      promotions: promos,
      for_basket: s == null ? null : {
        subtotal: s, shipping_fee: s >= STORE.freeShippingThreshold ? 0 : STORE.flatShippingFee,
        add_for_free_shipping: Math.max(0, STORE.freeShippingThreshold - s),
        applicable: promos.filter((p) => p.min_spend != null && s >= p.min_spend && ["coupon", "gift_with_purchase", "free_shipping"].includes(p.promo_type)),
        next_threshold: promos.filter((p) => p.min_spend != null && s < p.min_spend).sort((x, y) => x.min_spend - y.min_spend)[0] ?? null,
      },
    };
  },
});

// ───────────────────────────────────────────── advisor
const STEP_PLAN: Record<string, string[]> = {
  minimal_3_steps: ["cleanse", "moisturise", "sunscreen"],
  standard_5_steps: ["cleanse", "essence", "treatment-serum", "moisturise", "sunscreen"],
  full_layering: ["makeup-removal", "cleanse", "toner-pad", "essence", "treatment-serum", "moisturise", "mask", "sunscreen"],
};
const MAKEUP_STEPS = ["primer", "base", "conceal", "powder"];

const recommendRoutine = tool({
  name: "recommend_routine", kind: "read",
  description: "DETERMINISTIC product selection: same inputs → same routine. Scores every in-stock product against the customer's ranked concerns, skin type, sensitivity, budget and routine appetite; fills each routine step; returns layering cautions and any RANGE GAPS the advisor must be honest about. The LLM writes the wording; this tool decides the products.",
  input: {
    concerns: z.array(z.string()).min(1).describe("Concern slugs in priority order"),
    skin_type: z.string().describe("Skin type slug"),
    sensitivity: z.enum(["low", "medium", "high"]).default("low"),
    budget_per_product: z.number().optional(),
    routine_appetite: z.enum(["minimal_3_steps", "standard_5_steps", "full_layering"]).default("standard_5_steps"),
    include_makeup: z.boolean().default(false),
    brand: z.enum(["srichand", "sasi", "any"]).default("any"),
    fragrance_free_only: z.boolean().default(false),
    pregnant_or_nursing: z.boolean().default(false),
    outdoor_water_resistant: z.boolean().default(false).describe("Customer sweats or swims outdoors (running, cycling, beach): prefer sunscreens whose official copy claims water resistance"),
  },
  handler: (a) => {
    const concernRows = all("SELECT id, slug FROM skin_concerns");
    const unknown = a.concerns.filter((c) => !concernRows.find((r) => r.slug === c));
    if (unknown.length) throw new Error(`Unknown concern slug(s): ${unknown.join(", ")} — call list_reference_data`);
    const st = one("SELECT id FROM skin_types WHERE slug = ?", a.skin_type);
    if (!st) throw new Error(`Unknown skin_type ${a.skin_type}`);
    const steps = [...STEP_PLAN[a.routine_appetite], ...(a.include_makeup ? MAKEUP_STEPS : [])];
    // congestion / blemish concerns earn the exfoliating toner-pad slot even in a standard routine
    const poreFocus = a.concerns.some((c) => ["blackheads-congestion", "acne-breakouts", "enlarged-pores"].includes(c));
    if (poreFocus && a.routine_appetite === "standard_5_steps") steps.splice(steps.indexOf("essence"), 0, "toner-pad");
    const weight = (slug: string) => { const i = a.concerns.indexOf(slug); return i < 0 ? 0 : 1 / (i + 1); };
    const candidates = all(`SELECT p.id, p.name_en, p.name_th, p.is_fragrance_free, p.is_water_resistant_claimed, p.finish, b.slug AS brand, r.slug AS step, x.use_am, x.use_pm, x.frequency_en, x.usage_note_en
      FROM products p JOIN brands b ON b.id = p.brand_id JOIN product_routine_steps x ON x.product_id = p.id JOIN routine_steps r ON r.id = x.step_id
      WHERE p.product_type = 'single' AND p.lifecycle_status = 'active'`);
    const picks: any[] = [], unfilled: any[] = [];
    const skipped: Record<string, string> = {};
    for (const step of steps) {
      const scored = candidates.filter((c) => c.step === step && (a.brand === "any" || c.brand === a.brand)).map((c) => {
        // full size first, then cheapest; with a budget, the first orderable pack that fits it (a mini or sachet box can qualify)
        const variants = all("SELECT * FROM product_variants WHERE product_id = ? AND web_in_stock = 1 AND is_listed_on_site = 1 AND pack_format IN ('full_size','mini','multipack','sachet_box') ORDER BY (pack_format = 'full_size') DESC, COALESCE(sale_price, list_price), id", c.id)
          .filter((v) => availability(v.id) > 0);
        if (!variants.length) { skipped[step] ??= "out_of_stock"; return null; }
        const variant = a.budget_per_product == null ? variants[0] : variants.find((v) => price(v) <= a.budget_per_product!);
        if (!variant) { skipped[step] = "over_budget"; return null; }
        if (a.fragrance_free_only && c.is_fragrance_free !== 1) { skipped[step] ??= "not_fragrance_free"; return null; }
        const classes = activeClasses(c.id);
        if (a.pregnant_or_nursing && classes.includes("retinoid")) return null;
        const rel = all("SELECT s.slug, x.relevance, x.basis, x.rationale_en FROM product_concerns x JOIN skin_concerns s ON s.id = x.concern_id WHERE x.product_id = ? ORDER BY x.relevance DESC, s.slug", c.id);
        let score = rel.reduce((sum, r) => sum + weight(r.slug) * r.relevance, 0);
        const suit = one("SELECT suitability FROM product_skin_types WHERE product_id = ? AND skin_type_id = ?", c.id, st.id)?.suitability;
        score += suit === "ideal" ? 1.5 : suit === "good" ? 0.75 : suit === "caution" ? -3 : 0;
        if (a.sensitivity === "high" && c.is_fragrance_free === 0) score -= 2;
        if (a.outdoor_water_resistant && step === "sunscreen" && c.is_water_resistant_claimed === 1) score += 2;
        if (a.brand === "any" && c.brand === "srichand") score += 0.25;      // house-brand tie-break; SASI still wins when it fits better or the budget needs it
        if (a.sensitivity === "high" && (classes.includes("retinoid") || classes.includes("aha") && rel.some((r) => r.slug === "rough-texture"))) score -= 1;
        return { c, variant, score: Math.round(score * 100) / 100, matched: rel.filter((r) => weight(r.slug) > 0), suit, classes };
      }).filter(Boolean).sort((x: any, y: any) => y.score - x.score || price(x.variant) - price(y.variant) || x.c.id - y.c.id) as any[];
      const essential = ["cleanse", "moisturise", "sunscreen"].includes(step);
      const best = scored[0];
      // cleanse / moisturise / sunscreen are always filled (best skin-type fit). Every other step must earn its place:
      // at least one of the customer's concerns matched, not just a good skin-type fit.
      if (best && (essential || (best.matched.length > 0 && best.score >= 1.5))) {
        const hasShades = !!(best.variant.shade_code || best.variant.shade_name);
        picks.push({ step, product_id: best.c.id, name_en: best.c.name_en, name_th: best.c.name_th, brand: best.c.brand, use_am: !!best.c.use_am, use_pm: !!best.c.use_pm,
          frequency: best.c.frequency_en, usage_note: best.c.usage_note_en, variant: hasShades ? { ...variantCard(best.variant), variant_id: null, sku: null, shade: null } : variantCard(best.variant),
          needs_shade_match: hasShades || undefined, shade_note: hasShades ? "Price shown is per shade. Call match_shade to choose the shade before adding to the cart." : undefined, score: best.score, skin_type_fit: best.suit ?? "not rated",
          why: best.matched.map((m: any) => ({ concern: m.slug, relevance: m.relevance, basis: m.basis, rationale: m.rationale_en })),
          contains_fragrance: best.c.is_fragrance_free === 0, active_classes: best.classes.filter((k: string) => ["retinoid", "retinoid_alternative", "aha", "bha", "vitamin_c", "brightener"].includes(k)),
          runner_up: scored[1] ? { product_id: scored[1].c.id, name_en: scored[1].c.name_en, score: scored[1].score } : null });
      } else {
        unfilled.push({ step, essential, reason: best ? "no_concern_match (optional step left out on purpose)" : skipped[step] ?? "no_product_for_filters" });
      }
    }
    const classesInRoutine = new Set(picks.flatMap((p) => p.active_classes).concat(picks.some((p) => p.step === "sunscreen") ? ["uv_filter"] : []));
    const cautions = all("SELECT class_a, class_b, interaction, advice_en, advice_th FROM ingredient_interactions").filter((i) => classesInRoutine.has(i.class_a) && classesInRoutine.has(i.class_b));
    const gaps = all(`SELECT DISTINCT g.id, g.slug, g.title_en, g.severity, g.why_it_matters_en, g.closest_in_range_limits_en, g.generic_external_option_en, g.generic_external_option_th, p.name_en AS closest_in_range
      FROM range_gaps g JOIN range_gap_concerns gc ON gc.gap_id = g.id JOIN skin_concerns s ON s.id = gc.concern_id LEFT JOIN products p ON p.id = g.closest_in_range_product_id
      WHERE s.slug IN (${a.concerns.map(() => "?").join(",")})`, ...a.concerns)
      .filter((g) => g.slug !== "medical-acne-care" || a.concerns.indexOf("acne-breakouts") === 0);
    const refer = all(`SELECT slug, refer_out_when_en FROM skin_concerns WHERE refer_out_when_en IS NOT NULL AND slug IN (${a.concerns.map(() => "?").join(",")})`, ...a.concerns);
    const total = picks.reduce((s, p) => s + p.variant.current_price, 0);
    return { inputs: a, routine: picks, basket_total: total, shipping_fee: total >= STORE.freeShippingThreshold ? 0 : STORE.flatShippingFee, layering_cautions: cautions,
      unfilled_steps: unfilled, range_gaps: gaps, gap_policy: "Be honest that Srichand has no product for this. You MAY mention the generic external option; NEVER name a competitor brand or product. Then call log_range_gap.",
      refer_out_rules: refer, deterministic: true };
  },
});

const checkIngredientConflicts = tool({
  name: "check_ingredient_conflicts", kind: "read",
  description: "Layering rules that apply to a set of products (from their INCI and hero ingredients): what not to combine in one session, what needs sunscreen, what pairs well.",
  input: { product_ids: z.array(z.number().int()).min(1) },
  handler: (a) => {
    const byProduct = a.product_ids.map((id) => ({ product_id: id, name: one("SELECT name_en FROM products WHERE id = ?", id)?.name_en,
      classes: activeClasses(id) }));
    const present = new Set(byProduct.flatMap((p) => p.classes));
    return { products: byProduct, rules: all("SELECT * FROM ingredient_interactions").filter((r) => present.has(r.class_a) && present.has(r.class_b)) };
  },
});

const getRangeGaps = tool({
  name: "get_range_gaps", kind: "read",
  description: "The honest-gap list with demand counts from logged events — the R&D / range-planning signal.",
  input: {},
  handler: () => ({
    gaps: all("SELECT g.slug, g.title_en, g.missing_category, g.severity, g.why_it_matters_en, g.generic_external_option_en, g.commercial_read_en, d.events, d.distinct_customers, d.last_seen FROM range_gaps g JOIN v_gap_demand d ON d.gap = g.slug ORDER BY d.events DESC"),
    by_skin_type: all("SELECT g.slug AS gap, s.name_en AS skin_type, COUNT(*) AS events FROM range_gap_events e JOIN range_gaps g ON g.id = e.gap_id LEFT JOIN skin_types s ON s.id = e.customer_skin_type_id GROUP BY g.slug, s.name_en ORDER BY events DESC LIMIT 15"),
    note: "Events are SIMULATED in this prototype.",
  }),
});

// ───────────────────────────────────────────── customer, orders, loyalty
const getCustomer = tool({
  name: "get_customer", kind: "read",
  description: "Customer 360 for the paired customer: profile, Srichand Rewards points, consents, self-reported skin profile, latest analysis, active routine, recent orders, open cart.",
  input: { line_user_id: z.string() },
  handler: (a) => {
    const c = customerByLine(a.line_user_id);
    const age = ageOf(c);
    const session = one("SELECT id, created_at, summary_th, photo_quality, image_deleted_at, observed_undertone, observed_depth FROM face_analysis_sessions WHERE customer_id = ? AND status = 'completed' ORDER BY created_at DESC LIMIT 1", c.id);
    const routine = one("SELECT * FROM routines WHERE customer_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1", c.id);
    return {
      customer: { id: c.id, line_display_name: c.line_display_name, first_name: c.first_name, age, is_minor_under_20: age == null ? null : age < 20,
        age_note: age == null ? "Age unknown — ask the customer to confirm they are 20+ BEFORE offering photo analysis; otherwise use the questionnaire path." : undefined, preferred_language: c.preferred_language,
        member_since: c.created_at, registration_channel: c.registration_channel, phone_verified: !!c.phone_verified },
      loyalty: one("SELECT a.member_number, t.name AS tier, a.points_balance, a.spend_this_period FROM loyalty_accounts a JOIN loyalty_tiers t ON t.id = a.tier_id WHERE a.customer_id = ?", c.id),
      consents: all("SELECT consent_type, policy_version, granted_at, withdrawn_at FROM consent_records WHERE customer_id = ? ORDER BY granted_at DESC", c.id),
      skin_profile: (() => { const p = one("SELECT sp.*, st.slug AS skin_type FROM customer_skin_profiles sp LEFT JOIN skin_types st ON st.id = sp.self_reported_skin_type_id WHERE sp.customer_id = ?", c.id); return p ? { ...p, goals: json(p.goals) } : null; })(),
      latest_analysis: session ? { ...session, findings: all("SELECT s.slug AS concern, f.face_zone, f.severity, f.confidence, f.observation_en FROM analysis_findings f JOIN skin_concerns s ON s.id = f.concern_id WHERE f.session_id = ?", session.id) } : null,
      active_routine: routine ? { ...routine, items: all("SELECT ri.period, r.slug AS step, p.name_en AS product, g.slug AS gap, ri.frequency_en, ri.instruction_en FROM routine_items ri JOIN routine_steps r ON r.id = ri.step_id LEFT JOIN products p ON p.id = ri.product_id LEFT JOIN range_gaps g ON g.id = ri.gap_id WHERE ri.routine_id = ? ORDER BY ri.period, r.step_order", routine.id) } : null,
      recent_orders: all("SELECT id, order_number, status, grand_total, placed_at FROM orders WHERE customer_id = ? ORDER BY placed_at DESC LIMIT 5", c.id)
        .map(({ id, ...o }) => ({ ...o, payment_expired: o.status === "pending_payment" ? !!paymentOf(id)?.is_expired : undefined })),
      open_cart: viewCart(c.id),
    };
  },
});

function viewCart(customerId: number) {
  const cart = one("SELECT * FROM carts WHERE customer_id = ? AND status = 'open' ORDER BY updated_at DESC LIMIT 1", customerId);
  if (!cart) return null;
  const items = all("SELECT ci.variant_id, ci.quantity, ci.added_from, v.sku, v.name_en, v.variant_label, v.current_price, v.web_in_stock, v.image_url FROM cart_items ci JOIN v_variant_catalog v ON v.variant_id = ci.variant_id WHERE ci.cart_id = ? ORDER BY ci.variant_id", cart.id)
    .map((i) => ({ ...i, qty_available_online: availability(i.variant_id), line_total: i.current_price * i.quantity }));
  const subtotal = items.reduce((s, i) => s + i.line_total, 0);
  return { cart_id: cart.id, items, subtotal, shipping_fee: subtotal >= STORE.freeShippingThreshold ? 0 : STORE.flatShippingFee, add_for_free_shipping: Math.max(0, STORE.freeShippingThreshold - subtotal) };
}

/** Latest payment of an order, with `is_expired` computed at read time (nothing is written). */
function paymentOf(orderId: number) {
  const p = one("SELECT id, method, status, amount, expires_at, paid_at, qr_payload_ref FROM payments WHERE order_id = ? ORDER BY id DESC LIMIT 1", orderId);
  return p ? { ...p, is_expired: p.status === "pending" && !!p.expires_at && p.expires_at < nowIso() } : null;
}

const getOrderStatus = tool({
  name: "get_order_status", kind: "read",
  description: "Order tracking for the paired customer: status, items, payment state (incl. whether the payment window has expired) and courier events. Returns their latest order, or a specific one by order number. Orders of other customers are never returned.",
  input: { line_user_id: z.string(), order_number: z.string().optional().describe("e.g. SC-260916-0002; omit for the latest order") },
  output: { order: nul(loose({ items: z.array(lineItemOut).optional() })) },
  handler: (a) => {
    const c = customerByLine(a.line_user_id);
    const o = a.order_number ? one("SELECT * FROM orders WHERE order_number = ? AND customer_id = ?", a.order_number.trim().toUpperCase(), c.id)
      : one("SELECT * FROM orders WHERE customer_id = ? ORDER BY placed_at DESC LIMIT 1", c.id);
    if (!o) throw new Error(a.order_number ? `This customer has no order ${a.order_number}.` : "This customer has no orders yet.");
    const shipment = one("SELECT * FROM shipments WHERE order_id = ?", o.id);
    const payment = paymentOf(o.id);
    return {
      order: o,
      items: all("SELECT v.name_th, v.name_en, v.variant_label, v.image_url, oi.quantity, oi.unit_price, oi.is_gift FROM order_items oi JOIN v_variant_catalog v ON v.variant_id = oi.variant_id WHERE oi.order_id = ? ORDER BY oi.id", o.id),
      payment,
      next_step: o.status === "pending_payment" && payment?.is_expired ? "The payment window has passed, so this order can no longer be paid. It is cancelled automatically on the customer's next cart or order action, its items go back into the cart, and any points or coupon are restored. Offer to place the order again." : undefined,
      shipment: shipment ? { ...shipment, events: all("SELECT status, location, description_th, occurred_at FROM shipment_events WHERE shipment_id = ? ORDER BY occurred_at DESC", shipment.id) } : null,
      policy_note: "Official policy: problems must be reported within 3 days of delivery (wrong/defective items only); orders can be cancelled only before 'Ready to Ship'. Contact 02-300-1661, daily 9:00–18:00.",
    };
  },
});

const getLoyalty = tool({
  name: "get_loyalty", kind: "read",
  description: "Srichand Rewards: points balance, recent ledger, programme rules (official: ฿25 net spend = 1 point, single level) and rewards the customer can afford (reward catalogue is ASSUMED for the demo).",
  input: { line_user_id: z.string() },
  handler: (a) => {
    const c = customerByLine(a.line_user_id);
    const acct = one("SELECT a.*, t.name AS tier, t.benefits_en FROM loyalty_accounts a JOIN loyalty_tiers t ON t.id = a.tier_id WHERE a.customer_id = ?", c.id);
    return { account: acct, ledger: all("SELECT txn_type, points, description, expires_on, created_at FROM loyalty_transactions WHERE customer_id = ? ORDER BY created_at DESC, id DESC LIMIT 10", c.id),
      rewards: all("SELECT id, name_th, name_en, reward_type, points_cost, origin FROM rewards_catalog WHERE is_active = 1 ORDER BY points_cost").map((r) => ({ ...r, affordable: (acct?.points_balance ?? 0) >= r.points_cost })),
      redemption_value_baht_per_point: STORE.bahtPerPointRedeemed, redemption_value_origin: "assumed_for_demo — Srichand publishes no point value",
      how_to_join: "Add LINE @srichand1948 (or @sasidiary) and register with SMS OTP." };
  },
});

// ───────────────────────────────────────────── stock + order lifecycle helpers (write paths only)
const movement = (variantId: number, warehouseId: number, type: string, qty: number, ref: string, now: string) =>
  run("INSERT INTO inventory_movements (id, variant_id, warehouse_id, movement_type, quantity, reference, created_at) VALUES (?,?,?,?,?,?,?)", nextId("inventory_movements"), variantId, warehouseId, type, qty, ref, now);

/** Reserve from the online-order warehouses only, splitting across them if needed. Throws (→ transaction rolls back) if stock ran out. */
function reserveStock(variantId: number, qty: number, ref: string, now: string) {
  let left = qty;
  for (const r of all("SELECT i.warehouse_id, i.qty_on_hand - i.qty_reserved AS free FROM inventory i JOIN warehouses w ON w.id = i.warehouse_id WHERE i.variant_id = ? AND w.serves = 'online_orders' AND i.qty_on_hand - i.qty_reserved > 0 ORDER BY i.warehouse_id", variantId)) {
    const take = Math.min(left, r.free);
    run("UPDATE inventory SET qty_reserved = qty_reserved + ?, updated_at = ? WHERE variant_id = ? AND warehouse_id = ?", take, now, variantId, r.warehouse_id);
    movement(variantId, r.warehouse_id, "reservation", take, ref, now);
    if ((left -= take) === 0) return;
  }
  throw new Error(`Stock for variant ${variantId} changed while the order was being placed. Nothing was ordered or charged — check the cart again.`);
}

/** Turn an order's reservations into a sale (payment received) or release them (order cancelled). */
function settleReservations(order: any, as: "sale" | "release", now: string) {
  let held = all("SELECT variant_id, warehouse_id, SUM(quantity) AS q FROM inventory_movements WHERE reference = ? AND movement_type = 'reservation' GROUP BY variant_id, warehouse_id", order.order_number);
  if (!held.length)   // orders seeded before reservations were tracked: assume the main warehouse
    held = all("SELECT variant_id, 1 AS warehouse_id, SUM(quantity) AS q FROM order_items WHERE order_id = ? GROUP BY variant_id", order.id);
  for (const h of held) {
    if (as === "sale") run("UPDATE inventory SET qty_reserved = MAX(0, qty_reserved - ?), qty_on_hand = MAX(0, qty_on_hand - ?), updated_at = ? WHERE variant_id = ? AND warehouse_id = ?", h.q, h.q, now, h.variant_id, h.warehouse_id);
    else run("UPDATE inventory SET qty_reserved = MAX(0, qty_reserved - ?), updated_at = ? WHERE variant_id = ? AND warehouse_id = ?", h.q, now, h.variant_id, h.warehouse_id);
    movement(h.variant_id, h.warehouse_id, as, as === "sale" ? -h.q : h.q, order.order_number, now);
  }
}

/** Cancel an unpaid order: expire the payment, release stock, give back points and the coupon use, and put the items back in the cart. */
function cancelUnpaidOrder(o: any, now: string) {
  run("UPDATE payments SET status = 'expired' WHERE order_id = ? AND status = 'pending'", o.id);
  run("UPDATE orders SET status = 'cancelled', updated_at = ? WHERE id = ?", now, o.id);
  settleReservations(o, "release", now);
  if (o.points_redeemed > 0) {
    run("INSERT INTO loyalty_transactions (id, customer_id, txn_type, points, order_id, description, created_at) VALUES (?,?,?,?,?,?,?)", nextId("loyalty_transactions"), o.customer_id, "adjust", o.points_redeemed, o.id, `คืนแต้มจากคำสั่งซื้อที่ยกเลิก ${o.order_number}`, now);
    run("UPDATE loyalty_accounts SET points_balance = points_balance + ? WHERE customer_id = ?", o.points_redeemed, o.customer_id);
  }
  if (o.coupon_id) run("UPDATE coupons SET used_count = MAX(0, used_count - 1) WHERE id = ?", o.coupon_id);
  let cart = one("SELECT id FROM carts WHERE customer_id = ? AND status = 'open' ORDER BY updated_at DESC LIMIT 1", o.customer_id);
  if (!cart) { cart = { id: nextId("carts") }; run("INSERT INTO carts (id, customer_id, status, created_at, updated_at) VALUES (?,?,?,?,?)", cart.id, o.customer_id, "open", now, now); }
  for (const it of all("SELECT variant_id, quantity FROM order_items WHERE order_id = ? AND is_gift = 0", o.id))
    run("INSERT INTO cart_items (cart_id, variant_id, quantity, added_from) VALUES (?,?,?,'reorder') ON CONFLICT(cart_id, variant_id) DO UPDATE SET quantity = MAX(quantity, excluded.quantity)", cart.id, it.variant_id, it.quantity);
  run("UPDATE carts SET updated_at = ? WHERE id = ?", now, cart.id);
}

/** Housekeeping a scheduler would do in production: runs at the start of every cart / order WRITE, never in a read. */
function sweepExpiredOrders(now: string): string[] {
  const stale = all("SELECT o.* FROM orders o WHERE o.status = 'pending_payment' AND EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.id AND p.status = 'pending' AND p.expires_at IS NOT NULL AND p.expires_at < ?) AND NOT EXISTS (SELECT 1 FROM payments p WHERE p.order_id = o.id AND p.status = 'succeeded')", now);
  for (const o of stale) cancelUnpaidOrder(o, now);
  return stale.map((o) => o.order_number);
}

const addedFrom = z.enum(["advisor_recommendation", "search", "reorder", "promotion"]);

const cartAddItem = tool({
  name: "cart_add_item", kind: "write",
  description: [
    "Add purchasable SKUs to the customer's open cart, creating the cart if they do not have one.",
    "",
    "ADD THE WHOLE BASKET IN ONE CALL — do not call this tool once per SKU.",
    "`items` takes up to 20 lines of { variant_id, quantity, added_from } and adds them all together.",
    "  items: [{variant_id: 571, quantity: 2}, {variant_id: 412, quantity: 1}]  → both in the cart, one call.",
    "Use it whenever the customer says yes to more than one thing — a recommended routine, a set of suggestions, a reorder of a past order, an 'I'll take both'. `variant_id` + `quantity` is the single-item form and is only for a genuine single item; `items` wins if both are given.",
    "",
    "ONE BAD LINE DOES NOT BLOCK THE REST. Every line is judged on its own: the ones that pass come back in `added`, the ones refused come back in `rejected`, each with its own reason and the alternative to offer — so a rejected SKU costs no retry of the whole basket. `ok` is true only when nothing was rejected. The updated cart, with live prices, stock and the distance to free shipping, comes back in `cart` either way.",
    "Reasons you may get per line: not_for_sale (a gift, or a size not sold on its own — look for the pack or set in get_product → sets_containing_this), out_of_stock, insufficient_stock (with qty_available_online and next_restock_date), quantity_limit (bulk / reseller buying — hand over to staff), variant_not_found.",
    "",
    "Quantities are checked against what the cart ALREADY holds and what earlier lines of the SAME call added, so repeating a variant_id adds up and cannot slip past the per-item cap. Always read the cart back to the customer from `cart`, never from your own arithmetic.",
  ].join("\n"),
  input: {
    line_user_id: z.string(),
    items: z.array(z.object({
      variant_id: z.number().int(),
      quantity: z.number().int().min(1).max(10).default(1),
      added_from: addedFrom.optional().describe("Defaults to the call-level added_from."),
    })).min(1).max(20).optional().describe("SEVERAL SKUs in a single call — use this whenever there is more than one item, instead of calling the tool again and again. Each line is added or refused on its own. Repeating a variant_id adds up. Max 20 lines."),
    variant_id: z.number().int().optional().describe("Single-item form, for ONE item only. If the customer is taking more than one thing, put every SKU in `items` instead. Ignored when `items` is given."),
    quantity: z.number().int().min(1).max(10).default(1).describe("Single-item form only — the quantity of `variant_id`. Quantities for `items` go inside each line."),
    added_from: addedFrom.default("search").describe("Where the item came from; the default for every line in `items`."),
  },
  handler: (a) => db.transaction(() => {
    const lines = a.items?.length
      ? a.items.map((i) => ({ variant_id: i.variant_id, quantity: i.quantity, added_from: i.added_from ?? a.added_from }))
      : a.variant_id != null ? [{ variant_id: a.variant_id, quantity: a.quantity, added_from: a.added_from }] : [];
    if (!lines.length) throw new Error("Pass `items` (several SKUs) or `variant_id` (one).");
    const now = nowIso();
    const c = customerByLine(a.line_user_id, { create: true });
    sweepExpiredOrders(now);
    let cart = one("SELECT id FROM carts WHERE customer_id = ? AND status = 'open' ORDER BY updated_at DESC LIMIT 1", c.id);
    /** Units of a variant already spoken for: what the cart held when the call started, plus what earlier lines added. */
    const committed = new Map<number, number>();
    const added: any[] = [], rejected: any[] = [];
    for (const l of lines) {
      const v = one("SELECT v.*, p.product_type, p.name_en, p.name_th FROM product_variants v JOIN products p ON p.id = v.product_id WHERE v.id = ?", l.variant_id);
      const line = { variant_id: l.variant_id, quantity: l.quantity, sku: v?.sku ?? null, name_en: v?.name_en ?? null, variant_label: v?.variant_label ?? null };
      if (!v) { rejected.push({ ...line, ok: false, reason: "variant_not_found" }); continue; }
      if (!["single", "set", "accessory"].includes(v.product_type) || !v.is_listed_on_site) {
        rejected.push({ ...line, ok: false, reason: "not_for_sale", detail: v.is_listed_on_site ? "Gift-with-purchase items cannot be bought." : "This size is not sold on its own on srichand.com — look for the pack or set that contains it (get_product → sets_containing_this / variants)." });
        continue;
      }
      const inCart = committed.get(v.id) ?? (cart ? one("SELECT quantity FROM cart_items WHERE cart_id = ? AND variant_id = ?", cart.id, v.id)?.quantity ?? 0 : 0);
      if (inCart + l.quantity > STORE.maxUnitsPerItem) {
        rejected.push({ ...line, ok: false, reason: "quantity_limit", max_units_per_item: STORE.maxUnitsPerItem, already_in_cart: inCart, advice: "Larger quantities are handled by staff (bulk / reseller orders) — hand over." });
        continue;
      }
      const avail = availability(v.id);
      if (avail < inCart + l.quantity) {
        rejected.push({ ...line, ok: false, reason: avail === 0 ? "out_of_stock" : "insufficient_stock", qty_available_online: avail, already_in_cart: inCart, next_restock_date: one("SELECT MIN(next_restock_date) AS d FROM inventory WHERE variant_id = ?", v.id)?.d ?? null });
        continue;
      }
      if (!cart) { cart = { id: nextId("carts") }; run("INSERT INTO carts (id, customer_id, status, created_at, updated_at) VALUES (?,?,?,?,?)", cart.id, c.id, "open", now, now); }
      run("INSERT INTO cart_items (cart_id, variant_id, quantity, added_from) VALUES (?,?,?,?) ON CONFLICT(cart_id, variant_id) DO UPDATE SET quantity = quantity + excluded.quantity", cart.id, v.id, l.quantity, l.added_from);
      committed.set(v.id, inCart + l.quantity);
      added.push({ ...line, ok: true, quantity_added: l.quantity, quantity_in_cart: inCart + l.quantity });
    }
    if (added.length) run("UPDATE carts SET updated_at = ? WHERE id = ?", now, cart!.id);
    const result = { ok: rejected.length === 0, added, rejected, cart: viewCart(c.id) };
    // One item in, one verdict out: keep the flat shape callers of the single-item form already read.
    return lines.length === 1 && rejected.length ? { ...rejected[0], ...result } : result;
  })(),
});

const cartUpdateItem = tool({
  name: "cart_update_item", kind: "write", idempotent: true,
  description: "Set the quantity of an item already in the customer's open cart. quantity 0 removes it. Refuses a quantity beyond what can ship.",
  input: { line_user_id: z.string(), variant_id: z.number().int(), quantity: z.number().int().min(0).max(10) },
  handler: (a) => db.transaction(() => {
    const c = customerByLine(a.line_user_id), now = nowIso();
    sweepExpiredOrders(now);
    const cart = one("SELECT id FROM carts WHERE customer_id = ? AND status = 'open' ORDER BY updated_at DESC LIMIT 1", c.id);
    const line = cart ? one("SELECT quantity FROM cart_items WHERE cart_id = ? AND variant_id = ?", cart.id, a.variant_id) : null;
    if (!cart || !line) return { ok: false, reason: "not_in_cart", cart: viewCart(c.id) };
    if (a.quantity === 0) run("DELETE FROM cart_items WHERE cart_id = ? AND variant_id = ?", cart.id, a.variant_id);
    else {
      const avail = availability(a.variant_id);
      if (avail < a.quantity) return { ok: false, reason: avail === 0 ? "out_of_stock" : "insufficient_stock", qty_available_online: avail, already_in_cart: line.quantity };
      run("UPDATE cart_items SET quantity = ? WHERE cart_id = ? AND variant_id = ?", a.quantity, cart.id, a.variant_id);
    }
    run("UPDATE carts SET updated_at = ? WHERE id = ?", now, cart.id);
    return { ok: true, cart: viewCart(c.id) ?? { cart_id: cart.id, items: [], subtotal: 0 } };
  })(),
});

const clearCartItem = tool({
  name: "clear_cart_item", kind: "write", destructive: true, idempotent: true,
  description: [
    "Remove items from the customer's open cart — several at once, or the whole basket.",
    "",
    "REMOVE EVERYTHING THE CUSTOMER DROPPED IN ONE CALL.",
    "`variant_ids` takes up to 20 SKUs and removes them all together: variant_ids: [571, 412].",
    "`all: true` empties the cart completely — only when the customer clearly asked for that ('ล้างตะกร้า', 'start over', 'cancel the whole thing'), never to tidy up on your own initiative.",
    "Pass exactly one of the two. Passing neither is an error, so a mistyped call can never wipe a basket by accident.",
    "",
    "Idempotent: a SKU that is not in the cart comes back in `not_in_cart` and is not an error, so repeating the call is safe. Use cart_update_item to CHANGE a quantity — this tool only removes. Nothing here touches an order that was already placed (those cannot be edited — hand over to a person).",
    "The remaining cart, with live prices, stock and the distance to free shipping, comes back in `cart`; read totals back from it, never from your own arithmetic.",
  ].join("\n"),
  input: {
    line_user_id: z.string(),
    variant_ids: z.array(z.number().int()).min(1).max(20).optional().describe("The SKUs to remove — several in one call. Duplicates are ignored. Mutually exclusive with `all`."),
    all: z.boolean().optional().describe("true empties the whole cart. Only on an explicit request from the customer. Mutually exclusive with `variant_ids`."),
  },
  output: { ok: z.boolean(), removed: z.array(loose({ variant_id: z.number() })), not_in_cart: z.array(z.number()),
            cart: nul(loose({ items: z.array(lineItemOut).optional() })), reason: nul(z.string()) },
  handler: (a) => db.transaction(() => {
    if ((a.all === true) === (a.variant_ids != null))
      return { ok: false, reason: a.all ? "pass_either_variant_ids_or_all" : "nothing_to_remove", removed: [], not_in_cart: [],
        advice: "Pass `variant_ids` with the SKUs to drop, or `all: true` to empty the cart — one or the other, never both and never neither.", cart: viewCart(customerByLine(a.line_user_id).id) };
    const now = nowIso();
    const c = customerByLine(a.line_user_id);
    sweepExpiredOrders(now);
    const cart = one("SELECT id FROM carts WHERE customer_id = ? AND status = 'open' ORDER BY updated_at DESC LIMIT 1", c.id);
    if (!cart) return { ok: true, removed: [], not_in_cart: a.variant_ids ?? [], note: "This customer has no open cart — nothing to remove.", cart: { cart_id: null, items: [], subtotal: 0 } };
    const wanted = a.all
      ? all("SELECT variant_id FROM cart_items WHERE cart_id = ?", cart.id).map((r) => r.variant_id)
      : [...new Set(a.variant_ids!)];
    const removed: any[] = [], not_in_cart: number[] = [];
    for (const variantId of wanted) {
      const line = one("SELECT ci.quantity, v.sku, v.name_en, v.variant_label, v.current_price FROM cart_items ci JOIN v_variant_catalog v ON v.variant_id = ci.variant_id WHERE ci.cart_id = ? AND ci.variant_id = ?", cart.id, variantId);
      if (!line) { not_in_cart.push(variantId); continue; }   // already gone: idempotent, not an error
      run("DELETE FROM cart_items WHERE cart_id = ? AND variant_id = ?", cart.id, variantId);
      removed.push({ variant_id: variantId, sku: line.sku, name_en: line.name_en, variant_label: line.variant_label, quantity_removed: line.quantity });
    }
    if (removed.length) run("UPDATE carts SET updated_at = ? WHERE id = ?", now, cart.id);
    return { ok: true, emptied: !!a.all, removed, not_in_cart, cart: viewCart(c.id) ?? { cart_id: cart.id, items: [], subtotal: 0 } };
  })(),
});

const createOrder = tool({
  name: "create_order", kind: "write",
  description: "Turn the open cart into an order: validates the coupon and points, applies the official shipping rule, reserves stock and opens a payment (PromptPay QR is a MOCK reference). Returns the amount to pay. Always read the total back to the customer and get a clear yes BEFORE calling this.",
  input: { line_user_id: z.string(), payment_method: z.enum(STORE.paymentMethods), coupon_code: z.string().optional(), redeem_points: z.number().int().min(0).default(0), source_session_id: z.number().int().optional() },
  handler: (a) => db.transaction(() => {
    const now = nowIso();
    const c = customerByLine(a.line_user_id, { create: true });
    const auto_cancelled_expired_orders = sweepExpiredOrders(now);
    const cart = viewCart(c.id);
    if (!cart || !cart.items.length) return { ok: false, reason: "cart_empty" };
    const short = cart.items.filter((i) => i.qty_available_online < i.quantity);
    if (short.length) return { ok: false, reason: "insufficient_stock", items: short };
    let discount = 0, couponId: number | null = null, freeShip = false;
    if (a.coupon_code) {
      const cp = one(`SELECT c.id, c.customer_id, c.used_count, c.max_uses, c.expires_at, p.min_spend, p.discount_type, p.discount_value, p.starts_at, p.ends_at
                      FROM coupons c JOIN promotions p ON p.id = c.promotion_id WHERE c.code = ? AND p.is_active = 1`, a.coupon_code.trim().toUpperCase());
      if (!cp || (cp.customer_id != null && cp.customer_id !== c.id)) return { ok: false, reason: "coupon_not_found" };
      if ((cp.expires_at && cp.expires_at < now) || (cp.ends_at && cp.ends_at < now)) return { ok: false, reason: "coupon_expired" };
      if (cp.starts_at && cp.starts_at > now) return { ok: false, reason: "coupon_not_started_yet", starts_at: cp.starts_at };
      if (cp.used_count >= cp.max_uses) return { ok: false, reason: "coupon_fully_redeemed" };
      if ((cp.min_spend ?? 0) > cart.subtotal) return { ok: false, reason: "coupon_min_spend_not_met", min_spend: cp.min_spend, subtotal: cart.subtotal };
      discount = cp.discount_type === "percent" ? Math.round(cart.subtotal * cp.discount_value) / 100 : cp.discount_type === "amount" ? cp.discount_value : 0;
      discount = Math.min(discount, cart.subtotal);
      freeShip = cp.discount_type === "shipping"; couponId = cp.id;
    }
    const balance = one("SELECT points_balance FROM loyalty_accounts WHERE customer_id = ?", c.id)?.points_balance ?? 0;
    if (a.redeem_points > balance) return { ok: false, reason: "not_enough_points", points_balance: balance };
    const maxRedeemable = Math.floor((cart.subtotal - discount) / STORE.bahtPerPointRedeemed);
    if (a.redeem_points > maxRedeemable) return { ok: false, reason: "points_exceed_order_value", max_redeemable_points: Math.min(maxRedeemable, balance) };
    const pointsDiscount = a.redeem_points * STORE.bahtPerPointRedeemed;
    const net = Math.round((cart.subtotal - discount - pointsDiscount) * 100) / 100;
    const shipping = freeShip || net >= STORE.freeShippingThreshold ? 0 : STORE.flatShippingFee;
    const total = Math.round((net + shipping) * 100) / 100;
    const id = nextId("orders"), day = now.slice(2, 10).replace(/-/g, "");
    const seq = (one<{ n: number | null }>("SELECT MAX(CAST(substr(order_number, -4) AS INTEGER)) AS n FROM orders WHERE order_number LIKE ?", `SC-${day}-%`)!.n ?? 0) + 1;
    const orderNumber = `SC-${day}-${String(seq).padStart(4, "0")}`;
    run(`INSERT INTO orders (id, order_number, customer_id, channel, status, shipping_address_id, subtotal, discount_total, shipping_fee, points_redeemed, points_discount, grand_total, coupon_id, points_earned, source_session_id, placed_at, updated_at)
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, id, orderNumber, c.id, "line_oa_agent", "pending_payment", one("SELECT id FROM customer_addresses WHERE customer_id = ? AND is_default = 1", c.id)?.id ?? null,
      cart.subtotal, discount, shipping, a.redeem_points, pointsDiscount, total, couponId, 0, ownSession(c.id, a.source_session_id), now, now);
    for (const i of cart.items) {
      run("INSERT INTO order_items (id, order_id, variant_id, quantity, unit_price, line_total, is_gift) VALUES (?,?,?,?,?,?,0)", nextId("order_items"), id, i.variant_id, i.quantity, i.current_price, i.line_total);
      reserveStock(i.variant_id, i.quantity, orderNumber, now);
    }
    // gift-with-purchase: highest threshold reached, only if the promotion is inside its dates and the gift is actually in stock
    const gift = all("SELECT gift_variant_id, name_en FROM promotions WHERE promo_type = 'gift_with_purchase' AND is_active = 1 AND min_spend <= ? AND (starts_at IS NULL OR starts_at <= ?) AND (ends_at IS NULL OR ends_at >= ?) ORDER BY min_spend DESC", net, now, now)
      .find((g) => availability(g.gift_variant_id) > 0);
    if (gift) {
      run("INSERT INTO order_items (id, order_id, variant_id, quantity, unit_price, line_total, is_gift) VALUES (?,?,?,?,0,0,1)", nextId("order_items"), id, gift.gift_variant_id, 1);
      reserveStock(gift.gift_variant_id, 1, orderNumber, now);
    }
    if (couponId) run("UPDATE coupons SET used_count = used_count + 1 WHERE id = ?", couponId);
    if (a.redeem_points) {
      run("INSERT INTO loyalty_transactions (id, customer_id, txn_type, points, order_id, description, created_at) VALUES (?,?,?,?,?,?,?)", nextId("loyalty_transactions"), c.id, "redeem", -a.redeem_points, id, "ใช้แต้มเป็นส่วนลด", now);
      run("UPDATE loyalty_accounts SET points_balance = points_balance - ? WHERE customer_id = ?", a.redeem_points, c.id);
    }
    const expires = new Date(Date.now() + STORE.paymentQrMinutes * 60000).toISOString().replace(/\.\d{3}Z$/, "Z");
    run("INSERT INTO payments (id, order_id, method, status, amount, gateway_ref, qr_payload_ref, expires_at, created_at) VALUES (?,?,?,?,?,?,?,?,?)", nextId("payments"), id, a.payment_method, "pending", total, `MOCK-${Date.now()}`,
      a.payment_method === "promptpay_qr" ? `mockqr://promptpay/${String(id).padStart(6, "0")}` : null, expires, now);
    run("UPDATE carts SET status = 'converted', updated_at = ? WHERE id = ?", now, cart.cart_id);
    return { ok: true, order_number: orderNumber, subtotal: cart.subtotal, coupon_discount: discount, points_discount: pointsDiscount, shipping_fee: shipping, amount_to_pay: total, free_gift: gift?.name_en ?? null,
      payment: { method: a.payment_method, status: "pending", expires_at: expires, qr: a.payment_method === "promptpay_qr" ? "MOCK QR — no real payment is taken in this prototype" : null },
      points_to_earn_when_paid: Math.floor(net / STORE.earnBahtPerPoint), auto_cancelled_expired_orders: auto_cancelled_expired_orders.length ? auto_cancelled_expired_orders : undefined };
  })(),
});

const confirmPayment = tool({
  name: "confirm_payment_mock", kind: "write", idempotent: true,
  description: "DEMO ONLY: stands in for the payment gateway's success webhook. Marks the customer's order paid, turns its stock reservation into a sale and awards Srichand Rewards points at the official rate (฿25 net = 1 point). Refuses an order whose payment window has expired (that order is cancelled and its items return to the cart).",
  input: { line_user_id: z.string(), order_number: z.string() },
  handler: (a) => db.transaction(() => {
    const now = nowIso();
    const c = customerByLine(a.line_user_id);
    const o = one("SELECT * FROM orders WHERE order_number = ? AND customer_id = ?", a.order_number.trim().toUpperCase(), c.id);
    if (!o) throw new Error(`This customer has no order ${a.order_number}.`);
    if (o.status !== "pending_payment") return { ok: false, reason: `order_is_${o.status}` };
    if (paymentOf(o.id)?.is_expired) {
      cancelUnpaidOrder(o, now);
      return { ok: false, reason: "payment_expired", detail: "The payment window had passed. The order was cancelled, stock released, points and coupon restored, and the items are back in the cart — offer to place the order again.", cart: viewCart(c.id) };
    }
    const earned = Math.floor((o.subtotal - o.discount_total - o.points_discount) / STORE.earnBahtPerPoint);
    run("UPDATE payments SET status = 'succeeded', paid_at = ? WHERE order_id = ? AND status = 'pending'", now, o.id);
    run("UPDATE orders SET status = 'paid', points_earned = ?, updated_at = ? WHERE id = ?", earned, now, o.id);
    settleReservations(o, "sale", now);
    if (earned) run("INSERT INTO loyalty_transactions (id, customer_id, txn_type, points, order_id, description, expires_on, created_at) VALUES (?,?,?,?,?,?,?,?)", nextId("loyalty_transactions"), o.customer_id, "earn", earned, o.id, `สะสมแต้มจากคำสั่งซื้อ ${o.order_number}`, new Date(Date.now() + 365 * 864e5).toISOString().slice(0, 10), now);
    run("UPDATE loyalty_accounts SET points_balance = points_balance + ?, lifetime_points = lifetime_points + ?, spend_this_period = spend_this_period + ? WHERE customer_id = ?", earned, earned, o.grand_total, o.customer_id);
    return { ok: true, order_number: o.order_number, status: "paid", points_earned: earned, note: "Official T&C: points post within 17 days on srichand.com orders; the demo posts them instantly." };
  })(),
});

// ───────────────────────────────────────────── membership
const normalisePhone = (raw: string) => {
  const d = raw.replace(/[^\d+]/g, "").replace(/^\+?66/, "0");
  return /^0[689]\d{8}$/.test(d) ? d : null;
};
const maskPhone = (p: string) => `${p.slice(0, 3)}-xxx-${p.slice(-4)}`;

const registerMember = tool({
  name: "register_member", kind: "write",
  description: "Sign a NEW person up for Srichand Rewards: creates the customer record and their Rewards account (0 points, earning ฿25 = 1 point) and returns the member number. "
    + "This tool is deliberately NOT bound to a customer id — it is for chats that are not paired to a member yet. If get_customer already works in this chat, the person IS a member: do not call this. "
    + "Before calling: collect first name, Thai mobile number and birth date, show the Rewards terms + privacy notice and get an explicit yes (accept_terms), and ask separately whether they want promotions on LINE (marketing_opt_in — never assume yes). "
    + "After it succeeds: tell the customer their member number, and that points and order tools start working once staff link this LINE chat to it (hub → Accounts, paste the member number). "
    + "If the mobile number is already registered the tool refuses and reveals nothing about that account — hand over to staff to link it.",
  input: {
    first_name: z.string().trim().min(1).max(60), last_name: z.string().trim().max(60).optional(),
    phone: z.string().describe("Thai mobile number, any common format: 0812345678, 081-234-5678, +66812345678"),
    birth_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/).describe("YYYY-MM-DD in the Gregorian calendar (convert Buddhist-era years: 2540 → 1997)"),
    email: z.string().email().optional(), gender: z.enum(["female", "male", "non_binary", "undisclosed"]).optional(),
    preferred_language: z.enum(["th", "en"]).default("th"),
    accept_terms: z.boolean().describe("true only after the customer explicitly agreed to the Srichand Rewards terms and privacy notice in this chat"),
    terms_text_th: z.string().min(20).describe("The exact Thai sentence the customer agreed to (stored as the consent record)"),
    marketing_opt_in: z.boolean().default(false),
    guardian_confirmed: z.boolean().default(false).describe("Required when the customer is 16–19: a parent or guardian has confirmed in the chat"),
    line_display_name: z.string().max(80).optional(),
  },
  handler: (a) => db.transaction(() => {
    if (!a.accept_terms) return { ok: false, reason: "terms_not_accepted", advice: "Show the terms and privacy notice and get an explicit yes first." };
    const phone = normalisePhone(a.phone);
    if (!phone) return { ok: false, reason: "invalid_phone", advice: "Ask for a 10-digit Thai mobile number starting 06, 08 or 09." };
    const born = Date.parse(`${a.birth_date}T00:00:00Z`);
    if (Number.isNaN(born) || born > Date.now() || a.birth_date < "1900-01-01") return { ok: false, reason: "invalid_birth_date", advice: "Use YYYY-MM-DD in the Gregorian calendar; convert Buddhist-era years by subtracting 543." };
    const age = Math.floor((Date.now() - born) / 31557600000);
    if (age < STORE.minMemberAge) return { ok: false, reason: "under_minimum_age", minimum_age: STORE.minMemberAge };
    if (age < STORE.adultAge && !a.guardian_confirmed) return { ok: false, reason: "minor_requires_guardian", advice: `Members aged ${STORE.minMemberAge}–${STORE.adultAge - 1} need a parent or guardian to confirm in the chat.` };
    if (one("SELECT id FROM customers WHERE phone = ?", phone))
      return { ok: false, reason: "phone_already_registered", advice: "This mobile number already has a Rewards account. Do not reveal anything about it. Staff can link this LINE chat to the existing member after verifying the customer (hub → Accounts)." };
    if (a.email && one("SELECT id FROM customers WHERE lower(email) = lower(?)", a.email)) return { ok: false, reason: "email_already_registered", advice: "Ask for another email or leave it out; staff can link an existing account." };

    const id = nextId("customers"), now = nowIso(), memberNumber = `SCR${String(260000 + id).padStart(7, "0")}`;
    run(`INSERT INTO customers (id, line_user_id, line_display_name, first_name, last_name, phone, email, birth_date, gender, preferred_language, marketing_opt_in, phone_verified, registration_channel, is_demo_persona, created_at)
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, id, null, a.line_display_name ?? null, a.first_name, a.last_name ?? null, phone, a.email ?? null, a.birth_date, a.gender ?? null, a.preferred_language, a.marketing_opt_in ? 1 : 0, 0, "line_oa_agent", 0, now);
    run("INSERT INTO loyalty_accounts (customer_id, member_number, tier_id, points_balance, lifetime_points, spend_this_period, tier_expires_on, joined_at) VALUES (?,?,?,?,?,?,?,?)", id, memberNumber, 1, 0, 0, 0, null, now);
    const minor = age < STORE.adultAge ? 1 : 0;
    run("INSERT INTO consent_records (id, customer_id, consent_type, policy_version, consent_text_th, granted_at, channel, is_minor_flow) VALUES (?,?,?,?,?,?,?,?)", nextId("consent_records"), id, "rewards_terms", "srichand-rewards-terms-demo-v1", a.terms_text_th, now, "line_oa", minor);
    if (a.marketing_opt_in) run("INSERT INTO consent_records (id, customer_id, consent_type, policy_version, consent_text_th, granted_at, channel, is_minor_flow) VALUES (?,?,?,?,?,?,?,?)", nextId("consent_records"), id, "marketing", "srichand-rewards-terms-demo-v1", "ฉันยินยอมรับข่าวสาร โปรโมชั่น และสิทธิพิเศษจากศรีจันทร์ผ่าน LINE", now, "line_oa", minor);
    const tier = one("SELECT name, earn_rate_baht_per_point FROM loyalty_tiers WHERE id = 1")!;
    return {
      ok: true, member_number: memberNumber, customer_id: id, programme: tier.name, points_balance: 0,
      earn_rule: `Every ฿${tier.earn_rate_baht_per_point} of net spend (after discounts, excluding shipping) earns 1 point; points last one year.`,
      registered: { first_name: a.first_name, phone: maskPhone(phone), age, marketing_opt_in: a.marketing_opt_in },
      phone_verified: false, phone_verification_note: "PROTOTYPE: no SMS OTP is sent. The real Srichand Rewards sign-up verifies the mobile number by OTP — production must do the same before points can be redeemed.",
      pairing: { id_to_pair_in_hub: memberNumber, how: "Hub → Integrations → Account id · Srichand MCP → pair this LINE account with the member number, then press verify (it calls get_customer). Until then customer-bound tools fail closed for this chat." },
      say_to_customer_th: `สมัครสมาชิก Srichand Rewards เรียบร้อยแล้วค่ะ หมายเลขสมาชิกของคุณคือ ${memberNumber} เจ้าหน้าที่จะเชื่อมบัญชี LINE นี้กับหมายเลขสมาชิกให้ หลังจากนั้นจะตรวจสอบแต้มและคำสั่งซื้อผ่านแชตนี้ได้เลยค่ะ`,
    };
  })(),
});

// ───────────────────────────────────────────── PDPA + advisor writes
const recordConsent = tool({
  name: "record_consent", kind: "write",
  description: "Store an explicit PDPA consent with the exact Thai text the customer agreed to. Required BEFORE save_skin_analysis. For customers under 20 the default is the no-photo questionnaire path; photo consent then needs a guardian (is_minor_flow).",
  input: { line_user_id: z.string(), consent_type: z.enum(["rewards_terms", "face_photo_analysis", "skin_profile_storage", "marketing", "cross_border_processing"]), consent_text_th: z.string().min(20), policy_version: z.string().default("advisor-privacy-notice-v0.3-demo"), guardian_confirmed: z.boolean().default(false),
    age_confirmed_20_plus: z.boolean().default(false).describe("Set true only after the customer has explicitly confirmed they are 20 or older (needed when we hold no birth date)") },
  handler: (a) => {
    const c = customerByLine(a.line_user_id, { create: true });
    const age = ageOf(c);
    if (age == null && a.consent_type === "face_photo_analysis" && !a.age_confirmed_20_plus && !a.guardian_confirmed) return { ok: false, reason: "age_unknown", advice: "Ask the customer to confirm they are 20 or older. If they are under 20, offer the questionnaire path instead of a photo." };
    if (age != null && age < 20 && a.consent_type === "face_photo_analysis" && !a.guardian_confirmed) return { ok: false, reason: "minor_requires_guardian", advice: "Offer the questionnaire path instead of a photo." };
    const id = nextId("consent_records");
    run("INSERT INTO consent_records (id, customer_id, consent_type, policy_version, consent_text_th, granted_at, channel, is_minor_flow) VALUES (?,?,?,?,?,?,?,?)", id, c.id, a.consent_type, a.policy_version, a.consent_text_th, nowIso(), "line_oa", (age != null && age < 20) || a.guardian_confirmed ? 1 : 0);
    if (a.consent_type === "marketing") run("UPDATE customers SET marketing_opt_in = 1 WHERE id = ?", c.id);
    return { ok: true, consent_id: id };
  },
});

const setMarketingPreference = tool({
  name: "set_marketing_preference", kind: "write", idempotent: true,
  description: "Turn promotional messages on LINE on or off for the paired customer. PDPA: opting out must be as easy as opting in — do it immediately when asked, no questions. opt_in: true needs the exact Thai sentence the customer agreed to.",
  input: { line_user_id: z.string(), opt_in: z.boolean(), consent_text_th: z.string().min(20).optional().describe("Required when opt_in is true") },
  handler: (a) => db.transaction(() => {
    const c = customerByLine(a.line_user_id), now = nowIso();
    if (a.opt_in) {
      if (!a.consent_text_th) return { ok: false, reason: "consent_text_required", advice: "Pass the exact Thai sentence the customer agreed to." };
      const age = ageOf(c);
      if (!one("SELECT id FROM consent_records WHERE customer_id = ? AND consent_type = 'marketing' AND withdrawn_at IS NULL", c.id))
        run("INSERT INTO consent_records (id, customer_id, consent_type, policy_version, consent_text_th, granted_at, channel, is_minor_flow) VALUES (?,?,?,?,?,?,?,?)", nextId("consent_records"), c.id, "marketing", "advisor-privacy-notice-v0.3-demo", a.consent_text_th, now, "line_oa", age != null && age < 20 ? 1 : 0);
    } else {
      run("UPDATE consent_records SET withdrawn_at = ? WHERE customer_id = ? AND consent_type = 'marketing' AND withdrawn_at IS NULL", now, c.id);
    }
    run("UPDATE customers SET marketing_opt_in = ? WHERE id = ?", a.opt_in ? 1 : 0, c.id);
    return { ok: true, marketing_opt_in: a.opt_in, note: a.opt_in ? undefined : "Order and service messages continue; only promotions stop." };
  })(),
});

const withdrawConsent = tool({
  name: "withdraw_consent_and_erase", kind: "write", destructive: true, idempotent: true,
  description: "PDPA erasure ('ลบข้อมูลของฉัน'): withdraws photo/profile/cross-border consents, removes image references, and deletes findings, recommendations, saved routines and the skin profile. Orders, payments and points are kept (legal/accounting basis). Confirm with the customer once before calling — this cannot be undone.",
  input: { line_user_id: z.string() },
  handler: (a) => db.transaction(() => {
    const c = customerByLine(a.line_user_id), now = nowIso();
    const sessions = all("SELECT id FROM face_analysis_sessions WHERE customer_id = ?", c.id).map((s) => s.id);
    run("UPDATE consent_records SET withdrawn_at = ? WHERE customer_id = ? AND withdrawn_at IS NULL AND consent_type IN ('face_photo_analysis','skin_profile_storage','cross_border_processing')", now, c.id);
    for (const s of sessions) { run("DELETE FROM analysis_findings WHERE session_id = ?", s); run("DELETE FROM recommendations WHERE session_id = ?", s); }
    run("UPDATE face_analysis_sessions SET image_ref = NULL, image_sha256 = NULL, image_deleted_at = COALESCE(image_deleted_at, ?), summary_th = NULL, status = 'consent_withdrawn' WHERE customer_id = ?", now, c.id);
    run("DELETE FROM customer_skin_profiles WHERE customer_id = ?", c.id);
    const routines = all("SELECT id FROM routines WHERE customer_id = ?", c.id).length;     // routines are derived from the skin analysis
    run("DELETE FROM routine_items WHERE routine_id IN (SELECT id FROM routines WHERE customer_id = ?)", c.id);
    run("DELETE FROM routines WHERE customer_id = ?", c.id);
    run("UPDATE range_gap_events SET customer_id = NULL, session_id = NULL WHERE customer_id = ?", c.id);
    return { ok: true, sessions_erased: sessions.length, routines_erased: routines, kept: "orders, payments and loyalty ledger (contract / legal obligation)", respond_within: "Confirm to the customer now; PDPA allows up to 30 days." };
  })(),
});

const saveSkinAnalysis = tool({
  name: "save_skin_analysis", kind: "write",
  description: "Persist the result of a photo (or questionnaire) analysis: observed skin type, undertone/depth, findings per face zone. With image_count > 0 it requires active face_photo_analysis AND cross_border_processing consents; with image_count = 0 (questionnaire path) it requires skin_profile_storage. The image itself is never stored here — only an opaque reference that expires in 24 hours.",
  input: {
    line_user_id: z.string(), image_count: z.number().int().min(0).max(8), image_ref: z.string().optional(), photo_quality: z.enum(["good", "usable", "poor"]).optional(), quality_flags: z.array(z.string()).default([]),
    observed_skin_type: z.string(), observed_undertone: z.string().optional(), observed_depth: z.string().optional(), summary_th: z.string(),
    findings: z.array(z.object({ concern: z.string(), face_zone: z.enum(["forehead", "nose", "t_zone", "cheeks", "under_eye", "chin_jaw", "lips", "overall"]), severity: z.number().int().min(0).max(4), confidence: z.enum(["high", "medium", "low"]), observation_en: z.string().optional() })),
  },
  handler: (a) => db.transaction(() => {
    const c = customerByLine(a.line_user_id);
    const activeConsent = (type: string) => one("SELECT id FROM consent_records WHERE customer_id = ? AND consent_type = ? AND withdrawn_at IS NULL ORDER BY granted_at DESC LIMIT 1", c.id, type);
    const needed = a.image_count > 0 ? ["face_photo_analysis", "cross_border_processing"] : ["skin_profile_storage"];
    const missing = needed.filter((t) => !activeConsent(t));
    if (missing.length) return { ok: false, reason: "no_active_consent", missing_consents: missing, advice: "Call record_consent for each missing consent first." };
    const consent = activeConsent(needed[0])!;
    const st = one("SELECT id FROM skin_types WHERE slug = ?", a.observed_skin_type);
    if (!st) throw new Error("Unknown skin type slug");
    const id = nextId("face_analysis_sessions"), now = nowIso();
    run(`INSERT INTO face_analysis_sessions (id, customer_id, consent_id, image_ref, image_count, image_expires_at, photo_quality, quality_flags, model_version, observed_skin_type_id, observed_undertone, observed_depth, summary_th, status, created_at)
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`, id, c.id, consent.id, a.image_ref ?? null, a.image_count, new Date(Date.now() + 864e5).toISOString().replace(/\.\d{3}Z$/, "Z"), a.photo_quality ?? null, JSON.stringify(a.quality_flags), "advisor-vision-0.4-demo", st.id, a.observed_undertone ?? null, a.observed_depth ?? null, a.summary_th, "completed", now);
    for (const f of a.findings) {
      const cn = one("SELECT id FROM skin_concerns WHERE slug = ?", f.concern);
      if (!cn) throw new Error(`Unknown concern slug ${f.concern}`);
      run("INSERT INTO analysis_findings (id, session_id, concern_id, face_zone, severity, confidence, observation_en) VALUES (?,?,?,?,?,?,?)", nextId("analysis_findings"), id, cn.id, f.face_zone, f.severity, f.confidence, f.observation_en ?? null);
    }
    return { ok: true, session_id: id, image_expires_in_hours: 24 };
  })(),
});

const saveSkinProfile = tool({
  name: "save_skin_profile", kind: "write", idempotent: true,
  description: "Save what the customer TOLD us — the things a photo cannot show: skin type, sensitivity, reactions, ranked goals, current routine, routine appetite, budget, makeup habits, environment, pregnancy/nursing. Replaces their previous profile. Requires an active skin_profile_storage consent.",
  input: {
    line_user_id: z.string(), skin_type: z.string().describe("Skin type slug"), sensitivity_level: z.enum(["low", "medium", "high"]).optional(), known_reactions: z.string().optional(),
    goals: z.array(z.string()).max(5).default([]).describe("Concern slugs in priority order"), current_routine: z.string().optional(),
    routine_appetite: z.enum(["minimal_3_steps", "standard_5_steps", "full_layering"]).optional(), budget_per_product: z.number().positive().optional(),
    wears_makeup: z.enum(["never", "sometimes", "daily"]).optional(), environment: z.string().optional(), is_pregnant_or_nursing: z.boolean().optional(),
  },
  handler: (a) => db.transaction(() => {
    const c = customerByLine(a.line_user_id);
    const consent = one("SELECT id FROM consent_records WHERE customer_id = ? AND consent_type = 'skin_profile_storage' AND withdrawn_at IS NULL ORDER BY granted_at DESC LIMIT 1", c.id);
    if (!consent) return { ok: false, reason: "no_active_consent", missing_consents: ["skin_profile_storage"], advice: "Call record_consent first." };
    const st = one("SELECT id FROM skin_types WHERE slug = ?", a.skin_type);
    if (!st) throw new Error(`Unknown skin type slug ${a.skin_type} — call list_reference_data`);
    const bad = a.goals.filter((g) => !one("SELECT id FROM skin_concerns WHERE slug = ?", g));
    if (bad.length) throw new Error(`Unknown concern slug(s): ${bad.join(", ")} — call list_reference_data`);
    run(`INSERT OR REPLACE INTO customer_skin_profiles (customer_id, consent_id, self_reported_skin_type_id, sensitivity_level, known_reactions, goals, current_routine, routine_appetite, budget_per_product, wears_makeup, environment, is_pregnant_or_nursing, updated_at)
         VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`, c.id, consent.id, st.id, a.sensitivity_level ?? null, a.known_reactions ?? null, JSON.stringify(a.goals), a.current_routine ?? null, a.routine_appetite ?? null,
      a.budget_per_product ?? null, a.wears_makeup ?? null, a.environment ?? null, a.is_pregnant_or_nursing == null ? null : a.is_pregnant_or_nursing ? 1 : 0, nowIso());
    return { ok: true };
  })(),
});

const saveRoutine = tool({
  name: "save_routine", kind: "write",
  description: "Save the routine the customer accepted (deactivates the previous one). Items reference a product OR a range gap slot.",
  input: {
    line_user_id: z.string(), session_id: z.number().int().optional(), name: z.string(), goal_en: z.string().optional(),
    items: z.array(z.object({ period: z.enum(["am", "pm"]), step: z.string(), product_id: z.number().int().optional(), gap_slug: z.string().optional(), frequency_en: z.string(), instruction_en: z.string().optional(), instruction_th: z.string().optional() })).min(1),
  },
  handler: (a) => db.transaction(() => {
    const c = customerByLine(a.line_user_id), id = nextId("routines"), now = nowIso();
    for (const it of a.items) {
      if (!!it.product_id === !!it.gap_slug) throw new Error("Each routine item needs exactly one of product_id or gap_slug");
      if (it.product_id && !one("SELECT id FROM products WHERE id = ?", it.product_id)) throw new Error(`Unknown product_id ${it.product_id}`);
      if (it.gap_slug && !one("SELECT id FROM range_gaps WHERE slug = ?", it.gap_slug)) throw new Error(`Unknown gap_slug ${it.gap_slug}`);
    }
    run("UPDATE routines SET is_active = 0 WHERE customer_id = ?", c.id);
    run("INSERT INTO routines (id, customer_id, session_id, name, goal_en, is_active, review_after, created_at) VALUES (?,?,?,?,?,1,?,?)", id, c.id, ownSession(c.id, a.session_id), a.name, a.goal_en ?? null, new Date(Date.now() + 28 * 864e5).toISOString().slice(0, 10), now);
    for (const it of a.items) {
      const step = one("SELECT id FROM routine_steps WHERE slug = ?", it.step);
      if (!step) throw new Error(`Unknown step ${it.step}`);
      const gap = it.gap_slug ? one("SELECT id FROM range_gaps WHERE slug = ?", it.gap_slug) : null;
      run("INSERT INTO routine_items (id, routine_id, period, step_id, product_id, gap_id, frequency_en, instruction_en, instruction_th) VALUES (?,?,?,?,?,?,?,?,?)", nextId("routine_items"), id, it.period, step.id, it.product_id ?? null, gap?.id ?? null, it.frequency_en, it.instruction_en ?? null, it.instruction_th ?? null);
    }
    return { ok: true, routine_id: id, review_after_days: 28 };
  })(),
});

const logRangeGap = tool({
  name: "log_range_gap", kind: "write",
  description: "Record that a customer needed something the range does not have. Call this EVERY time you tell a customer about a gap — it is the R&D demand signal. Anonymous by design: it is not bound to a customer (so it also works in chats that are not linked to a member) and stores no identity — only the gap, the concern, and optionally the skin type and age band.",
  input: {
    gap_slug: z.string().describe("Gap code from get_range_gaps or the routine result"),
    concern: z.string().optional().describe("Concern slug that led to the gap"),
    skin_type: z.string().optional().describe("Skin type slug, if known"),
    age_band: z.enum(["10s", "20s", "30s", "40s", "50s", "60s+"]).optional(),
    generic_option_mentioned: z.boolean().default(true),
  },
  handler: (a) => {
    const gap = one("SELECT id FROM range_gaps WHERE slug = ?", a.gap_slug);
    if (!gap) throw new Error("Unknown gap slug — call get_range_gaps");
    const concern = a.concern ? one("SELECT id FROM skin_concerns WHERE slug = ?", a.concern) : null;
    if (a.concern && !concern) throw new Error(`Unknown concern slug ${a.concern} — call list_reference_data`);
    const st = a.skin_type ? one("SELECT id FROM skin_types WHERE slug = ?", a.skin_type) : null;
    if (a.skin_type && !st) throw new Error(`Unknown skin type slug ${a.skin_type} — call list_reference_data`);
    const id = nextId("range_gap_events");
    run("INSERT INTO range_gap_events (id, gap_id, customer_id, session_id, concern_id, customer_age_band, customer_skin_type_id, generic_option_mentioned, created_at) VALUES (?,?,?,?,?,?,?,?,?)",
      id, gap.id, null, null, concern?.id ?? null, a.age_band ?? null, st?.id ?? null, a.generic_option_mentioned ? 1 : 0, nowIso());
    return { ok: true, event_id: id, total_events_for_gap: one("SELECT COUNT(*) AS n FROM range_gap_events WHERE gap_id = ?", gap.id)!.n };
  },
});

const viewCartTool = tool({
  name: "cart_view", kind: "read",
  description: "The customer's open cart with live prices, stock, shipping fee and distance to free shipping.",
  input: { line_user_id: z.string() },
  output: { cart_id: nul(z.number()), items: z.array(lineItemOut), subtotal: nul(z.number()),
            shipping_fee: nul(z.number()), add_for_free_shipping: nul(z.number()) },
  handler: (a) => viewCart(customerByLine(a.line_user_id).id) ?? { cart_id: null, items: [], subtotal: 0 },
});

const demoLinkPersona = tool({
  name: "demo_link_persona", kind: "write", destructive: true,
  description: "DEMO ONLY: make a real LINE account 'become' one of the scripted personas (1 Ploy · 2 Mint · 3 Nok · 4 Beam · 5 Fern · 6 Dao · 41 Por) so their orders, points, routine and analysis appear for that account. Rebuild the database to undo.",
  input: { line_user_id: z.string(), persona_id: z.number().int().refine((n) => [1, 2, 3, 4, 5, 6, 41].includes(n), "not a persona id") },
  handler: (a) => db.transaction(() => {
    const key = a.line_user_id.trim();
    if (/^\d+$/.test(key)) throw new Error("Pass the real LINE userId, not a numeric customer id");
    const existing = one("SELECT id, is_demo_persona FROM customers WHERE line_user_id = ?", key);
    if (existing?.id === a.persona_id) return { ok: true, note: "already linked" };
    if (existing) {
      const busy = one("SELECT (SELECT COUNT(*) FROM orders WHERE customer_id = ?) + (SELECT COUNT(*) FROM face_analysis_sessions WHERE customer_id = ?) AS n", existing.id, existing.id)!.n;
      if (existing.is_demo_persona || busy > 0) return { ok: false, reason: "this LINE account already has its own history; rebuild the database first" };
      for (const tbl of ["loyalty_transactions", "consent_records", "cart_items WHERE cart_id IN (SELECT id FROM carts", "carts", "loyalty_accounts", "customer_addresses"])
        tbl.startsWith("cart_items") ? run("DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE customer_id = ?)", existing.id) : run(`DELETE FROM ${tbl} WHERE customer_id = ?`, existing.id);
      run("DELETE FROM customers WHERE id = ?", existing.id);
    }
    run("UPDATE customers SET line_user_id = ? WHERE id = ?", key, a.persona_id);
    const p = one("SELECT line_display_name, persona_brief FROM customers WHERE id = ?", a.persona_id)!;
    return { ok: true, now_acting_as: p.line_display_name, brief: p.persona_brief };
  })(),
});

export const TOOLS: ToolDef[] = [
  listReferenceData, searchProducts, getProduct, matchShade, checkStock, getPromotions,
  recommendRoutine, checkIngredientConflicts, getRangeGaps,
  getCustomer, getOrderStatus, getLoyalty, viewCartTool,
  registerMember, cartAddItem, cartUpdateItem, clearCartItem, createOrder, confirmPayment, recordConsent, setMarketingPreference, withdrawConsent, saveSkinProfile, saveSkinAnalysis, saveRoutine, logRangeGap,
  ...(process.env.SRICHAND_DEMO_TOOLS === "1" ? [demoLinkPersona] : []),   // off by default: the hub owns identity mapping
];
