/** Smoke test = the demo script. Calls the tool functions directly (no MCP transport) on a COPY of the DB.
 *  Run: bun run mcp:smoke */
import { Database } from "bun:sqlite";
import { existsSync, unlinkSync } from "node:fs";
import { join } from "node:path";
const tmp = join(import.meta.dir, "..", "..", "db", "srichand.smoke.db");
// Build a FRESH database from schema + seeds for the test, so results never depend on (or touch) live demo data.
for (const s of ["", "-wal", "-shm"]) if (existsSync(tmp + s)) unlinkSync(tmp + s);
{ const b = Bun.spawnSync(["bun", "run", join(import.meta.dir, "..", "..", "db", "build.ts")], { env: { ...process.env, SRICHAND_DB: tmp } });
  if (b.exitCode !== 0) { console.error(b.stderr.toString()); process.exit(1); } }
process.env.SRICHAND_DB = tmp;
process.env.SRICHAND_DEMO_TOOLS = "1";
const { TOOLS } = await import("./tools");
const { one, all } = await import("./db");
const { z } = await import("zod");

const call = (name: string, args: Record<string, unknown> = {}) => {
  const t = TOOLS.find((x) => x.name === name)!;
  return t.handler(z.object(t.input).parse(args)) as any;
};
let failed = 0;
const check = (label: string, ok: boolean, detail?: unknown) => { console.log(`${ok ? "✓" : "✗"} ${label}${detail !== undefined ? "  → " + (typeof detail === "string" ? detail : JSON.stringify(detail)) : ""}`); if (!ok) failed++; };

const ploy = one("SELECT line_user_id FROM customers WHERE id = 1")!.line_user_id;
const mint = one("SELECT line_user_id FROM customers WHERE id = 2")!.line_user_id;
const beam = one("SELECT line_user_id FROM customers WHERE id = 4")!.line_user_id;
const fern = one("SELECT line_user_id FROM customers WHERE id = 5")!.line_user_id;

const kinds = TOOLS.reduce((k: any, t) => ((k[t.kind] = (k[t.kind] ?? 0) + 1), k), {});
check("tool kinds: 13 read, 13 write (+1 demo tool enabled for this test)", kinds.read === 13 && kinds.write === 14, kinds);
const fingerprint = () => all("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name").map((t: any) => `${t.name}:${one(`SELECT COUNT(*) AS n FROM ${t.name}`)!.n}`).join("|")
  + "|" + JSON.stringify(one("SELECT SUM(qty_reserved) r, SUM(qty_on_hand) h FROM inventory")) + JSON.stringify(one("SELECT SUM(points_balance) p FROM loyalty_accounts")) + JSON.stringify(one("SELECT SUM(used_count) u FROM coupons"));

const ref = call("list_reference_data");
check("reference data", ref.skin_concerns.length >= 20 && ref.skin_types.length === 7);

const s1 = call("search_products", { queries: ["กันแดด"], category: "sunscreen" });
check("search Thai 'กันแดด'", s1.count >= 5, s1.products.map((p: any) => p.name_en).slice(0, 3));
const s2 = call("search_products", { queries: ["salicylic"], in_stock_only: false });
check("search by INCI 'salicylic' finds BHA products across brands", s2.count >= 3, s2.products.map((p: any) => p.name_en));
check("search_products returns the whole product inline — variants, claims, concerns, key actives, how-to-use (no get_product turn needed)",
  s1.products.every((p: any) => p.variants?.length && Array.isArray(p.official_claims_th) && Array.isArray(p.concerns) && Array.isArray(p.skin_types) && Array.isArray(p.routine) && p.inci && "how_to_use" in p && "description_th" in p),
  `${s1.products[0].name_en}: ${s1.products[0].variants.length} variants, ${s1.products[0].inci.key_actives.length} key actives, ${s1.products[0].official_claims_th.length} claims`);
const cln = call("search_products", { queries: ["cleansing"], detail: "card", limit: 30 });
const sun = call("search_products", { queries: ["sunscreen"], detail: "card", limit: 30 });
const union = call("search_products", { queries: ["cleansing", "sunscreen"], detail: "card", limit: 30 });
const ids = (r: any) => new Set(r.products.map((p: any) => p.id));
const dedup = new Set([...ids(cln), ...ids(sun)]);
check("queries: several terms in one call return the UNION — the two searches you would otherwise make one after the other, deduplicated",
  union.count === dedup.size && union.products.every((p: any) => dedup.has(p.id))
  && union.products.every((p: any) => p.matched_terms.length >= 1 && p.matched_terms.every((t: string) => ["cleansing", "sunscreen"].includes(t)))
  && JSON.stringify(union.terms) === JSON.stringify(["cleansing", "sunscreen"]) && union.match === "any",
  { cleansing: cln.count, sunscreen: sun.count, union: union.count });
const nia = call("search_products", { queries: ["niacinamide"], detail: "card", limit: 30 });
const ser = call("search_products", { queries: ["เซรั่ม"], detail: "card", limit: 30 });
const isect = call("search_products", { queries: ["niacinamide", "เซรั่ม"], match: "all", detail: "card", limit: 30 });
check("match: 'all' is the opt-in INTERSECTION — every hit matches every term, and it is narrower than the union",
  isect.match === "all" && isect.count > 0 && isect.count < Math.min(nia.count, ser.count)
  && isect.products.every((p: any) => ids(nia).has(p.id) && ids(ser).has(p.id) && p.matched_terms.length === 2)
  && call("search_products", { queries: ["niacinamide", "เซรั่ม"], detail: "card", limit: 30 }).count > isect.count,
  { niacinamide: nia.count, "เซรั่ม": ser.count, intersection: isect.count });
const multi = call("search_products", { queries: ["sunscreen", "cushion"], detail: "card", limit: 30 });
check("a union hit says WHICH terms it answered, and products matching more terms rank first",
  multi.products.every((p: any) => p.matched_terms.length > 0)
  && multi.products.map((p: any) => p.matched_terms.length).every((n: number, i: number, xs: number[]) => i === 0 || xs[i - 1] >= n),
  multi.products.slice(0, 4).map((p: any) => `${p.name_en} [${p.matched_terms.join("+")}]`));
let legacyQuery = "";
try { call("search_products", { query: "เซรั่ม" } as any); } catch (e) { legacyQuery = (e as z.ZodError).issues?.[0]?.message ?? (e as Error).message; }
check("`queries` is the ONLY free-text input: a legacy `query` is REFUSED with the fix named, never silently ignored",
  legacyQuery.includes("no `query` argument") && legacyQuery.includes("queries")
  && call("search_products", { queries: ["Serum", "serum", "SERUM"], detail: "card" }).terms.length === 1
  && call("search_products", { category: "sunscreen", detail: "card" }).count > 0,   // filters alone still work
  legacyQuery.slice(0, 80));
const liveAndDead = call("search_products", { queries: ["sunscreen", "azelaic acid"], detail: "card", limit: 30 });
const allDead = call("search_products", { queries: ["azelaic acid", "tretinoin"], detail: "card" });
const missAll = call("search_products", { queries: ["vitamin c", "serum", "brighten"], match: "all", detail: "card" });
check("per_term names a range gap without a second call — even when the other terms returned plenty",
  liveAndDead.count > 0 && liveAndDead.per_term.find((x: any) => x.term === "azelaic acid").matches === 0
  && liveAndDead.advice.includes("range gap") && liveAndDead.advice.includes("other terms are answered above")
  && allDead.count === 0 && allDead.advice.includes("nothing to offer from the range")
  && missAll.count === 0 && missAll.per_term.every((x: any) => x.matches > 0) && missAll.advice.includes("match: 'any'"),
  { live_plus_dead: liveAndDead.per_term.map((x: any) => `${x.term}=${x.matches}`), all_dead: allDead.count });
check("full INCI stays opt-in (key actives always there), and detail:'card' returns the compact card only",
  s1.products.every((p: any) => p.inci.full_list === undefined)
  && call("search_products", { queries: ["กันแดด"], category: "sunscreen", include_full_inci: true }).products.some((p: any) => p.inci.full_list?.length)
  && s1.count === 5   // detail:'full' defaults to 5 hits; the same search as cards defaults to 10
  && (() => { const card = call("search_products", { queries: ["กันแดด"], category: "sunscreen", detail: "card" });
              return card.count > s1.count && card.products.every((p: any) => p.variants === undefined && p.official_claims_th === undefined && p.name_en); })());

const acne = s1.products.find((p: any) => p.name_en.includes("Acne Care"));
const gp = call("get_product", { product_id: acne.id });
check("get_product: Sunlution Acne Care has official INCI with UV filters", gp.inci.available && gp.inci.key_actives.some((k: any) => k.class === "uv_filter"), `${gp.inci.count} INCI, source: ${gp.inci.source}`);

const r1 = call("recommend_routine", { concerns: ["excess-sebum-shine", "blackheads-congestion", "enlarged-pores"], skin_type: "oily", routine_appetite: "standard_5_steps", include_makeup: true });
const r2 = call("recommend_routine", { concerns: ["excess-sebum-shine", "blackheads-congestion", "enlarged-pores"], skin_type: "oily", routine_appetite: "standard_5_steps", include_makeup: true });
check("recommend_routine is deterministic (same input twice → identical output)", JSON.stringify(r1) === JSON.stringify(r2));
check("oily routine picks", r1.routine.length >= 5, r1.routine.map((p: any) => `${p.step}: ${p.name_en} ฿${p.variant.current_price}`));
check("BHA gap surfaced with generic option, no brand names", r1.range_gaps.some((g: any) => g.slug === "dedicated-bha-treatment"), r1.range_gaps.map((g: any) => g.generic_external_option_en));

const r3 = call("recommend_routine", { concerns: ["melasma", "sensitivity-redness"], skin_type: "sensitive", sensitivity: "high", fragrance_free_only: true });
check("sensitive + fragrance-free routine excludes fragranced products", r3.routine.every((p: any) => !p.contains_fragrance), r3.routine.map((p: any) => `${p.step}: ${p.name_en}`));
check("melasma triggers refer-out rule", r3.refer_out_rules.some((x: any) => x.slug === "melasma"));
const r4 = call("recommend_routine", { concerns: ["fine-lines-wrinkles"], skin_type: "dry", pregnant_or_nursing: true });
check("pregnancy excludes retinoid (Resurface)", !r4.routine.some((p: any) => p.name_en.includes("Resurface")), r4.routine.map((p: any) => p.name_en));

const cushion = call("search_products", { queries: ["Skin Essential Fine Smooth Cushion"] }).products[0];
const shade = call("match_shade", { product_id: cushion.id, undertone: "neutral", depth: "light" });
check("shade match returns a best shade + low-stock info", !!shade.best, `${shade.best.shade} (avail ${shade.best.qty_available_online}); alt ${shade.alternatives.map((x: any) => x.shade)}`);
const stock = call("check_stock", { variant_id: shade.best.variant_id });
check("check_stock", stock.available_to_order_online >= 0, { online: stock.available_to_order_online, low: stock.low_stock, restock: stock.next_restock_date });

const promo = call("get_promotions", { basket_subtotal: 520 });
check("promotions: basket ฿520 → ฿50 shipping, ฿79 to free shipping, gift at 499", promo.for_basket.shipping_fee === 50 && promo.for_basket.add_for_free_shipping === 79, promo.for_basket.applicable.map((p: any) => p.code));

const cust = call("get_customer", { line_user_id: ploy });
check("customer 360 (Ploy)", cust.loyalty.points_balance >= 0 && !!cust.active_routine, { points: cust.loyalty.points_balance, orders: cust.recent_orders.length });
const track = call("get_order_status", { line_user_id: ploy });
check("order tracking (Ploy's latest)", !!track.shipment, `${track.order.order_number} ${track.order.status} via ${track.shipment?.carrier}: ${track.shipment?.events[0]?.description_th}`);
// every READ tool, run against real and unknown customers with auto-registration ON, must leave the database byte-for-byte the same
process.env.SRICHAND_AUTO_REGISTER = "1";
const before = fingerprint();
const sampleArgs: Record<string, any> = { search_products: { queries: ["serum"] }, get_product: { product_id: acne.id }, match_shade: { product_id: cushion.id, undertone: "neutral", depth: "light" },
  check_stock: { variant_id: shade.best.variant_id }, get_promotions: { basket_subtotal: 700 }, recommend_routine: { concerns: ["dehydration"], skin_type: "dry" }, check_ingredient_conflicts: { product_ids: [acne.id] } };
for (const t of TOOLS.filter((t) => t.kind === "read")) {
  for (const who of [fern, "U" + "9f".repeat(16)]) {
    try { call(t.name, "line_user_id" in t.input ? { ...(sampleArgs[t.name] ?? {}), line_user_id: who } : sampleArgs[t.name] ?? {}); } catch { /* unknown customer → error is the correct read behaviour */ }
  }
}
check("all 13 READ tools leave the database unchanged (even with SRICHAND_AUTO_REGISTER=1 and an unknown customer)", fingerprint() === before);
delete process.env.SRICHAND_AUTO_REGISTER;

let foreign = ""; try { call("get_order_status", { line_user_id: ploy, order_number: track.order.order_number.replace(/\d{4}$/, "9999") }); } catch (e) { foreign = (e as Error).message; }
const fernOrder = call("get_order_status", { line_user_id: fern }).order.order_number;
let notMine = ""; try { call("get_order_status", { line_user_id: ploy, order_number: fernOrder }); } catch (e) { notMine = (e as Error).message; }
check("order lookup is scoped to the customer: Ploy cannot read Fern's order by guessing its number", notMine.includes("no order") && foreign.includes("no order"), `${fernOrder} → "${notMine}"`);

const pending = call("get_order_status", { line_user_id: beam });
const beamVariant = one("SELECT variant_id FROM order_items WHERE order_id = ? LIMIT 1", pending.order.id)!.variant_id;
const reservedBefore = one("SELECT SUM(qty_reserved) AS r FROM inventory WHERE variant_id = ?", beamVariant)!.r;
check("Beam's unpaid order: read tool flags the expired payment window without changing anything", pending.payment.status === "pending" && pending.payment.is_expired === true && !!pending.next_step && reservedBefore >= 1, pending.order.order_number);
const expired = call("confirm_payment_mock", { line_user_id: beam, order_number: pending.order.order_number });
const reservedAfter = one("SELECT SUM(qty_reserved) AS r FROM inventory WHERE variant_id = ?", beamVariant)!.r;
check("expired payment cannot be confirmed: order cancelled, stock released, items back in the cart", expired.ok === false && expired.reason === "payment_expired" && reservedAfter === reservedBefore - 1 && expired.cart.items.length === 3
  && call("get_order_status", { line_user_id: beam, order_number: pending.order.order_number }).order.status === "cancelled", { cart_subtotal: expired.cart.subtotal });
const reorder = call("create_order", { line_user_id: beam, payment_method: "promptpay_qr" });
const onHandBefore = one("SELECT SUM(qty_on_hand) AS h FROM inventory WHERE variant_id = ?", beamVariant)!.h;
const paid = call("confirm_payment_mock", { line_user_id: beam, order_number: reorder.order_number });
const stockAfter = one("SELECT SUM(qty_on_hand) AS h, SUM(qty_reserved) AS r FROM inventory WHERE variant_id = ?", beamVariant)!;
check("re-order → payment: points at ฿25/pt on the net amount (shipping excluded), reservation becomes a sale (on-hand −1, reserved back to baseline)", reorder.ok && paid.ok && paid.points_earned === Math.floor((reorder.amount_to_pay - reorder.shipping_fee) / 25)
  && stockAfter.h === onHandBefore - 1 && stockAfter.r === reservedAfter, { order: reorder.order_number, pay: reorder.amount_to_pay, points: paid.points_earned });
const again = call("confirm_payment_mock", { line_user_id: beam, order_number: reorder.order_number });
check("confirming twice is a no-op (idempotent)", again.ok === false && again.reason === "order_is_paid");

const minor = call("record_consent", { line_user_id: mint, consent_type: "face_photo_analysis", consent_text_th: "ฉันยินยอมโดยชัดแจ้งให้ศรีจันทร์ใช้ภาพถ่ายใบหน้า" });
check("minor (17) blocked from photo consent without guardian", minor.ok === false && minor.reason === "minor_requires_guardian");

const add = call("cart_add_item", { line_user_id: fern, variant_id: shade.best.variant_id, quantity: 1, added_from: "advisor_recommendation" });
check("cart add", add.ok, { subtotal: add.cart?.subtotal, to_free_shipping: add.cart?.add_for_free_shipping });
const tooMany = call("cart_add_item", { line_user_id: fern, variant_id: shade.best.variant_id, quantity: 3 });
check("cart counts what is already in it: 1 in cart + 3 more > 3 available → refused", tooMany.ok === false && tooMany.reason === "insufficient_stock" && tooMany.already_in_cart >= 1, { avail: tooMany.qty_available_online, in_cart: tooMany.already_in_cart });
const giftVariant = one("SELECT v.id FROM product_variants v JOIN products p ON p.id = v.product_id WHERE p.product_type = 'gift_with_purchase' LIMIT 1")!.id;
const hiddenVariant = one("SELECT id FROM product_variants WHERE is_listed_on_site = 0 LIMIT 1")!.id;
check("gifts and SKUs not sold on the site cannot be added to a cart", call("cart_add_item", { line_user_id: fern, variant_id: giftVariant }).reason === "not_for_sale" && call("cart_add_item", { line_user_id: fern, variant_id: hiddenVariant }).reason === "not_for_sale");
check("coupon rules: unknown code, minimum spend, and points capped at the order value", call("create_order", { line_user_id: fern, payment_method: "promptpay_qr", coupon_code: "NOPE" }).reason === "coupon_not_found"
  && call("create_order", { line_user_id: fern, payment_method: "promptpay_qr", coupon_code: "SEP150" }).reason === "coupon_min_spend_not_met"
  && call("create_order", { line_user_id: fern, payment_method: "promptpay_qr", redeem_points: 999999 }).reason === "not_enough_points");
const order = call("create_order", { line_user_id: fern, payment_method: "promptpay_qr", coupon_code: "SEP30", redeem_points: 40 });
check("create order with coupon + points", order.ok, order.ok ? { no: order.order_number, pay: order.amount_to_pay, ship: order.shipping_fee, gift: order.free_gift } : order);
const gap = call("log_range_gap", { gap_slug: "eye-care", concern: "under-eye-darkness", skin_type: "combination", age_band: "30s" });
check("gap logged anonymously (no customer id accepted or stored)", gap.ok && !("line_user_id" in TOOLS.find((t) => t.name === "log_range_gap")!.input) && one("SELECT customer_id FROM range_gap_events WHERE id = ?", gap.event_id)!.customer_id === null, `events for gap: ${gap.total_events_for_gap}`);
const gaps = call("get_range_gaps");
check("gap demand report", gaps.gaps[0].events > 0, gaps.gaps.map((g: any) => `${g.slug}=${g.events}`));
const erase = call("withdraw_consent_and_erase", { line_user_id: ploy });
const after = call("get_customer", { line_user_id: ploy });
check("PDPA erase removes profile, findings AND routines; keeps orders", erase.ok && after.skin_profile === null && after.latest_analysis === null && after.active_routine === null && after.recent_orders.length > 0, erase);
const noConsent = call("save_skin_profile", { line_user_id: ploy, skin_type: "oily", goals: ["excess-sebum-shine"] });
call("record_consent", { line_user_id: ploy, consent_type: "skin_profile_storage", consent_text_th: "ฉันยินยอมให้ศรีจันทร์เก็บข้อมูลสภาพผิว เป้าหมาย และประวัติการแพ้" });
const profile = call("save_skin_profile", { line_user_id: ploy, skin_type: "oily", sensitivity_level: "low", goals: ["excess-sebum-shine", "blackheads-congestion"], routine_appetite: "standard_5_steps", budget_per_product: 400, wears_makeup: "daily" });
check("save_skin_profile needs consent, then stores the questionnaire answers", noConsent.reason === "no_active_consent" && profile.ok && call("get_customer", { line_user_id: ploy }).skin_profile.goals.length === 2);
call("record_consent", { line_user_id: ploy, consent_type: "face_photo_analysis", consent_text_th: "ฉันยินยอมโดยชัดแจ้งให้ศรีจันทร์ใช้ภาพถ่ายใบหน้า" });
const noXborder = call("save_skin_analysis", { line_user_id: ploy, image_count: 2, observed_skin_type: "oily", summary_th: "ผิวมันบริเวณทีโซน", findings: [] });
check("photo analysis needs BOTH photo and cross-border consents", noXborder.ok === false && noXborder.missing_consents?.[0] === "cross_border_processing");


const byId = call("get_loyalty", { line_user_id: "5" }), byMember = call("get_loyalty", { line_user_id: "SCR0260005" });
check("hub-injected keys: customer id and Rewards member number resolve to the same customer", byId.account.customer_id === 5 && byMember.account.customer_id === 5);
const por = call("get_customer", { line_user_id: "41" });
check("late persona Por: profile, routine with a body-sunscreen gap slot, parcel in transit, open cart", por.customer.line_display_name.startsWith("Por") && por.active_routine.items.some((i: any) => i.gap === "body-sun-care") && por.recent_orders[0].status === "shipped" && por.open_cart.items.length === 1, { points: por.loyalty.points_balance });
const porRoutine = call("recommend_routine", { concerns: ["post-acne-marks", "dark-spots-sun", "daily-uv-protection"], skin_type: "combination", sensitivity: "medium", fragrance_free_only: true, outdoor_water_resistant: true });
check("Por's inputs → fragrance-free routine, water-resistant sunscreen, body-sunscreen gap surfaced", porRoutine.routine.every((p: any) => !p.contains_fragrance) && porRoutine.routine.find((p: any) => p.step === "sunscreen")?.name_en.includes("Rosia") && porRoutine.range_gaps.some((g: any) => g.slug === "body-sun-care"), porRoutine.routine.map((p: any) => `${p.step}: ${p.name_en}`));
const REAL = "U" + "ab12".repeat(8);
let unpaired = ""; try { call("get_customer", { line_user_id: REAL }); } catch (e) { unpaired = (e as Error).message; }
check("unpaired LINE account → clear error, no customer created", unpaired.includes("not paired") && one("SELECT COUNT(*) AS n FROM customers")!.n === 41, unpaired.slice(0, 60));
process.env.SRICHAND_AUTO_REGISTER = "1";
let stillRead = ""; try { call("get_customer", { line_user_id: REAL }); } catch (e) { stillRead = (e as Error).message; }
const firstWrite = call("record_consent", { line_user_id: REAL, consent_type: "marketing", consent_text_th: "ฉันยินยอมรับข่าวสาร โปรโมชั่น และสิทธิพิเศษจากศรีจันทร์ผ่าน LINE" });
const fresh = call("get_customer", { line_user_id: REAL });
check("opt-in auto-registration happens only through a WRITE tool, never a read", stillRead.includes("not paired") && firstWrite.ok && fresh.customer.age === null && fresh.loyalty?.points_balance === 0, { id: fresh.customer.id, member: fresh.loyalty?.member_number });
const noAge = call("record_consent", { line_user_id: REAL, consent_type: "face_photo_analysis", consent_text_th: "ฉันยินยอมโดยชัดแจ้งให้ศรีจันทร์ใช้ภาพถ่ายใบหน้า" });
check("photo consent blocked until age is confirmed", noAge.ok === false && noAge.reason === "age_unknown");
const okAge = call("record_consent", { line_user_id: REAL, consent_type: "face_photo_analysis", consent_text_th: "ฉันยินยอมโดยชัดแจ้งให้ศรีจันทร์ใช้ภาพถ่ายใบหน้า", age_confirmed_20_plus: true });
check("photo consent accepted after 20+ confirmation", okAge.ok === true);
const REAL2 = "U" + "cd34".repeat(8);
const link = call("demo_link_persona", { line_user_id: REAL2, persona_id: 6 });
const asDao = call("get_customer", { line_user_id: REAL2 });
check("demo_link_persona: a real LINE id now sees Dao's history", link.ok && asDao.recent_orders.length >= 2 && !!asDao.active_routine, link.now_acting_as);

// ── membership registration (not bound to a customer: it is for chats the hub has not paired yet)
const terms = "ฉันยอมรับข้อกำหนดและเงื่อนไขของ Srichand Rewards และนโยบายความเป็นส่วนตัว";
const reg = (extra: Record<string, unknown>) => call("register_member", { first_name: "ภาวิณี", phone: "081-234-5678", birth_date: "1996-03-14", accept_terms: true, terms_text_th: terms, ...extra });
check("register_member has no customer-id argument (must work for unpaired chats)", !("line_user_id" in TOOLS.find((t) => t.name === "register_member")!.input));
check("registration refuses without explicit terms acceptance, a valid Thai mobile, or a sane birth date", reg({ accept_terms: false }).reason === "terms_not_accepted" && reg({ phone: "12345" }).reason === "invalid_phone" && reg({ birth_date: "2540-03-14" }).reason === "invalid_birth_date");
check("age rules: under 16 refused; 16–19 needs a guardian", reg({ birth_date: "2013-01-01" }).reason === "under_minimum_age" && reg({ birth_date: "2009-01-01" }).reason === "minor_requires_guardian" );
const taken = reg({ phone: one("SELECT phone FROM customers WHERE id = 5")!.phone });
check("existing mobile number → refused, and nothing about that member is revealed", taken.reason === "phone_already_registered" && !JSON.stringify(taken).includes("SCR"));
const membersBefore = one("SELECT COUNT(*) AS n FROM customers")!.n;
const joined = reg({ last_name: "วงศ์ทอง", phone: "+66 81 234 5678", marketing_opt_in: true, line_display_name: "PW.W" });
const row = one("SELECT c.*, a.member_number, a.points_balance FROM customers c JOIN loyalty_accounts a ON a.customer_id = c.id WHERE c.id = ?", joined.customer_id);
check("new member created: customer + Rewards account (0 pts) + terms & marketing consents, phone normalised, LINE id left to the hub", joined.ok && one("SELECT COUNT(*) AS n FROM customers")!.n === membersBefore + 1
  && row.phone === "0812345678" && row.line_user_id === null && row.registration_channel === "line_oa_agent" && row.phone_verified === 0 && row.points_balance === 0 && row.member_number === joined.member_number
  && all("SELECT consent_type FROM consent_records WHERE customer_id = ? ORDER BY consent_type", joined.customer_id).map((r: any) => r.consent_type).join() === "marketing,rewards_terms", { member: joined.member_number, pair: joined.pairing.id_to_pair_in_hub });
check("same mobile again → refused (one account per number)", reg({ phone: "0812345678" }).reason === "phone_already_registered");
const verified = call("get_customer", { line_user_id: joined.member_number });
check("hub 'verify' step works: get_customer resolves the new member number", verified.customer.first_name === "ภาวิณี" && verified.loyalty.points_balance === 0 && verified.customer.registration_channel === "line_oa_agent");
const v1 = one("SELECT v.id FROM product_variants v JOIN products p ON p.id = v.product_id WHERE p.name_en = 'Translucent Powder' AND v.size_value = 30")!.id;
call("cart_add_item", { line_user_id: joined.member_number, variant_id: v1, quantity: 2 });
const firstOrder = call("create_order", { line_user_id: joined.member_number, payment_method: "promptpay_qr" });
const firstPaid = call("confirm_payment_mock", { line_user_id: joined.member_number, order_number: firstOrder.order_number });
check("new member can shop straight away and earns points at ฿25 = 1", firstOrder.ok && firstPaid.ok && call("get_loyalty", { line_user_id: joined.member_number }).account.points_balance === Math.floor((firstOrder.amount_to_pay - firstOrder.shipping_fee) / 25), { paid: firstOrder.amount_to_pay, points: firstPaid.points_earned });

const v2 = one("SELECT v.id FROM product_variants v JOIN products p ON p.id = v.product_id WHERE p.name_en = 'Skin Moisture Burst Essence' AND v.size_value = 150")!.id;
call("cart_add_item", { line_user_id: joined.member_number, variant_id: v2, quantity: 1 });
const setTwo = call("cart_update_item", { line_user_id: joined.member_number, variant_id: v2, quantity: 2 });
const removed = call("cart_update_item", { line_user_id: joined.member_number, variant_id: v2, quantity: 0 });
check("cart_update_item: change quantity, remove with 0, refuse what is not in the cart", setTwo.ok && setTwo.cart.items[0].quantity === 2 && removed.ok && removed.cart.items.length === 0
  && call("cart_update_item", { line_user_id: joined.member_number, variant_id: v2, quantity: 1 }).reason === "not_in_cart");
const vBulk = one("SELECT v.id FROM product_variants v JOIN v_stock_available s ON s.variant_id = v.id JOIN products p ON p.id = v.product_id WHERE p.product_type = 'single' AND v.is_listed_on_site = 1 AND s.qty_available_online > 40 LIMIT 1")!.id;
call("cart_add_item", { line_user_id: joined.member_number, variant_id: vBulk, quantity: 4 });
call("cart_add_item", { line_user_id: joined.member_number, variant_id: vBulk, quantity: 4 });
const third = call("cart_add_item", { line_user_id: joined.member_number, variant_id: vBulk, quantity: 4 });
check("per-item cap holds across repeated small adds (4 + 4 + 4 → refused at 10)", third.ok === false && third.reason === "quantity_limit" && third.already_in_cart === 8);
call("cart_update_item", { line_user_id: joined.member_number, variant_id: vBulk, quantity: 0 });
const giftV = one("SELECT v.id FROM product_variants v JOIN products p ON p.id = v.product_id WHERE p.product_type = 'gift_with_purchase' LIMIT 1")!.id;
const batch = call("cart_add_item", { line_user_id: joined.member_number, added_from: "advisor_recommendation", items: [
  { variant_id: v1, quantity: 1 }, { variant_id: v2, quantity: 2 }, { variant_id: v1, quantity: 1 }, { variant_id: giftV, quantity: 1 }, { variant_id: 999999, quantity: 1 } ] });
check("cart_add_item takes a whole basket in one call: good lines added (a repeated SKU adds up), bad lines reported without blocking the rest",
  batch.ok === false && batch.added.length === 3 && batch.rejected.length === 2
  && batch.rejected.map((r: any) => r.reason).join() === "not_for_sale,variant_not_found"
  && batch.cart.items.length === 2 && batch.cart.items.find((i: any) => i.variant_id === v1).quantity === 2,
  { added: batch.added.map((r: any) => `${r.sku}x${r.quantity_added}`), rejected: batch.rejected.map((r: any) => r.reason), subtotal: batch.cart.subtotal });
const batchCap = call("cart_add_item", { line_user_id: joined.member_number, items: [{ variant_id: vBulk, quantity: 6 }, { variant_id: vBulk, quantity: 6 }] });
check("stock and the 10-unit cap count earlier lines of the SAME call, not just what was already in the cart",
  batchCap.added.length === 1 && batchCap.rejected[0].reason === "quantity_limit" && batchCap.rejected[0].already_in_cart === 6);
const beforeClear = call("cart_view", { line_user_id: joined.member_number });
const dropTwo = call("clear_cart_item", { line_user_id: joined.member_number, variant_ids: [beforeClear.items[0].variant_id, 999999] });
check("clear_cart_item removes several SKUs in one call; one that is not in the cart is reported, not an error (idempotent)",
  dropTwo.ok && dropTwo.removed.length === 1 && dropTwo.not_in_cart.join() === "999999"
  && dropTwo.cart.items.length === beforeClear.items.length - 1
  && call("clear_cart_item", { line_user_id: joined.member_number, variant_ids: [beforeClear.items[0].variant_id] }).removed.length === 0,
  { removed: dropTwo.removed.map((r: any) => r.sku), left: dropTwo.cart.items.length, subtotal: dropTwo.cart.subtotal });
const noArgs = call("clear_cart_item", { line_user_id: joined.member_number });
const bothArgs = call("clear_cart_item", { line_user_id: joined.member_number, variant_ids: [beforeClear.items[0].variant_id], all: true });
check("clear_cart_item cannot wipe a basket by accident: neither argument and both arguments are refused, cart untouched",
  noArgs.ok === false && noArgs.reason === "nothing_to_remove" && bothArgs.ok === false && bothArgs.reason === "pass_either_variant_ids_or_all"
  && call("cart_view", { line_user_id: joined.member_number }).items.length === dropTwo.cart.items.length);
const emptied = call("clear_cart_item", { line_user_id: joined.member_number, all: true });
check("clear_cart_item all:true empties the cart and says what it took out",
  emptied.ok && emptied.emptied === true && emptied.removed.length === dropTwo.cart.items.length && emptied.cart.items.length === 0 && emptied.cart.subtotal === 0,
  { removed: emptied.removed.length });
call("cart_update_item", { line_user_id: joined.member_number, variant_id: vBulk, quantity: 0 });
const optOut = call("set_marketing_preference", { line_user_id: joined.member_number, opt_in: false });
const afterOut = one("SELECT marketing_opt_in AS f, (SELECT COUNT(*) FROM consent_records WHERE customer_id = c.id AND consent_type = 'marketing' AND withdrawn_at IS NULL) AS active FROM customers c WHERE id = ?", joined.customer_id)!;
check("marketing opt-out is one call: flag off and the consent marked withdrawn; opting back in needs the agreed sentence", optOut.ok && afterOut.f === 0 && afterOut.active === 0
  && call("set_marketing_preference", { line_user_id: joined.member_number, opt_in: true }).reason === "consent_text_required"
  && call("set_marketing_preference", { line_user_id: joined.member_number, opt_in: true, consent_text_th: "ฉันยินยอมรับข่าวสาร โปรโมชั่น และสิทธิพิเศษจากศรีจันทร์ผ่าน LINE" }).ok);

console.log(failed ? `\n${failed} check(s) FAILED` : "\nAll checks passed.");
for (const s of ["", "-wal", "-shm"]) if (existsSync(tmp + s)) unlinkSync(tmp + s);
process.exit(failed ? 1 : 0);
