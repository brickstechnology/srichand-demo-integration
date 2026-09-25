#!/usr/bin/env python3
"""Step 8 — build docs/schema-page.html (single-file, Bricks-branded) with live numbers from the database."""
import base64, json, sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
CI = Path.home() / ".claude/skills/bricks-ci/assets"
con = sqlite3.connect(ROOT / "db/srichand.db")
q = lambda s: con.execute(s).fetchone()[0]
prov = {p["table_name"]: p for p in json.load(open(ROOT / "db/seed/data_provenance.json"))}
b64 = lambda p: base64.b64encode(p.read_bytes()).decode()
fonts = "".join(f'@font-face{{font-family:"{fam}";font-weight:{w};src:url(data:font/otf;base64,{b64(CI / "fonts" / f)}) format("opentype");font-display:swap}}'
                for fam, w, f in [("BricksDisplay", 400, "BricksDisplay-Regular.otf"), ("BricksText", 400, "BricksText-Regular.otf"), ("BricksText", 600, "BricksText-SemiBold.otf")])
logo = b64(CI / "logo" / "bricks-logo-red.png")

DOMAINS = [
 ("Catalogue", "What Srichand sells, exactly as srichand.com states it.", ["brands", "product_lines", "categories", "products", "product_variants", "bundle_components", "site_listings", "product_images", "product_claims"]),
 ("Ingredients", "Full INCI lists from official product pages, linked to a plain-language dictionary.", ["ingredients", "product_ingredients", "product_hero_ingredients", "ingredient_interactions"]),
 ("Advisor knowledge", "How products map to concerns, skin types and routine steps — and where the range stops.", ["skin_types", "skin_concerns", "product_concerns", "product_skin_types", "routine_steps", "product_routine_steps", "range_gaps", "range_gap_concerns"]),
 ("Commerce", "Stock, customers, carts, orders, payment, delivery, promotions.", ["warehouses", "inventory", "inventory_movements", "customers", "customer_addresses", "promotions", "promotion_variants", "coupons", "carts", "cart_items", "orders", "order_items", "payments", "shipments", "shipment_events"]),
 ("Srichand Rewards", "Official rule (฿25 = 1 point, single level); balances simulated.", ["loyalty_tiers", "loyalty_accounts", "loyalty_transactions", "rewards_catalog", "reward_redemptions"]),
 ("Advisor sessions", "Consent trail, skin analyses, recommendations, routines, gap log. No image is ever stored.", ["consent_records", "customer_skin_profiles", "face_analysis_sessions", "analysis_findings", "recommendations", "routines", "routine_items", "range_gap_events"]),
]
LABEL = {"real_sourced": ("real", "Real"), "derived": ("derived", "Derived"), "curated_knowledge": ("curated", "Curated"), "mock": ("mock", "Simulated")}
totals = {}
for t, p in prov.items():
    k = LABEL[p["origin"]][0]
    n = q(f"SELECT COUNT(*) FROM {t}")
    a = totals.setdefault(k, [0, 0]); a[0] += 1; a[1] += n

def domain_html(name, blurb, tables):
    rows = "".join(f'<li class="t {LABEL[prov[t]["origin"]][0]}" title="{prov[t]["description"]}"><span class="tn">{t}</span><span class="n">{q(f"SELECT COUNT(*) FROM {t}"):,}</span></li>' for t in tables)
    return f'<section class="domain"><h3>{name}</h3><p>{blurb}</p><ul>{rows}</ul></section>'

swap = "".join(f"<tr><td><code>{t}</code></td><td>{p['production_source']}</td></tr>" for t, p in prov.items()
               if p["origin"] == "mock" and p["production_source"] and t in ("inventory", "customers", "orders", "payments", "shipments", "loyalty_accounts", "consent_records", "face_analysis_sessions", "range_gap_events", "promotions"))
S = dict(listings=q("SELECT COUNT(*) FROM site_listings"), products=q("SELECT COUNT(*) FROM products"), skus=q("SELECT COUNT(*) FROM product_variants"),
         inci=q("SELECT COUNT(*) FROM product_ingredients"), inci_p=q("SELECT COUNT(DISTINCT product_id) FROM product_ingredients"),
         tables=len(prov), rows=sum(v[1] for v in totals.values()), sal=q("SELECT COUNT(DISTINCT product_id) FROM product_ingredients WHERE lower(inci_as_listed)='salicylic acid'"),
         gaps=q("SELECT COUNT(*) FROM range_gap_events"), onsale=q("SELECT COUNT(*) FROM product_variants WHERE sale_price IS NOT NULL"))

html = f"""<title>Srichand Advisor Blueprint</title>
<style>
{fonts}
:root{{--white:#FFFFFF;--red:#FD0145;--ice:#AFF0E8;--grey:#F1F1F1;--ink:#1A1A1A;--rule:#D9D9D9}}
*{{box-sizing:border-box}}
body{{background:var(--white);color:var(--ink);font:400 16px/1.55 "BricksText","DM Sans",Arial,Helvetica,sans-serif;padding-inline:clamp(16px,5vw,64px);padding-block:32px 72px}}
.wrap{{max-width:1120px;margin-inline:auto;display:grid;gap:64px}}
h1,h2,h3{{font-family:"BricksDisplay","DM Sans",Arial,sans-serif;font-weight:400;margin:0;text-wrap:balance;letter-spacing:-.01em}}
h1{{font-size:clamp(2.2rem,6vw,4rem);line-height:1.02}} h1 em{{font-style:normal;color:var(--red)}}
h2{{font-size:clamp(1.5rem,3.2vw,2.1rem);line-height:1.1}} h3{{font-size:1.2rem}}
p{{margin:0;max-width:68ch}} code{{font:600 .86em ui-monospace,Menlo,monospace}}
.label{{font:600 .72rem/1 "BricksText",Arial,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--red)}}
header{{display:grid;gap:28px}} header img{{width:112px;height:auto;display:block}}
.lede{{font-size:1.15rem;max-width:60ch}}
.head{{display:grid;gap:12px;margin-bottom:24px}}
.funnel{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));border-top:2px solid var(--ink)}}
.funnel div{{padding:18px 16px 18px 0;border-bottom:1px solid var(--rule)}}
.funnel b{{display:block;font:400 2.4rem/1 "BricksDisplay",Arial,sans-serif;font-variant-numeric:tabular-nums}} .funnel div:nth-child(3) b{{color:var(--red)}}
.funnel span{{font-size:.86rem}}
.legend{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}}
.legend div{{padding:16px;display:grid;gap:6px;font-size:.9rem}} .legend b{{font-weight:600}} .legend small{{font-variant-numeric:tabular-nums}}
.real{{background:var(--ink);color:var(--white)}} .derived{{background:var(--ice);color:var(--ink)}} .curated{{background:var(--grey);color:var(--ink)}} .mock{{background:var(--white);color:var(--ink);outline:1.5px dashed var(--ink);outline-offset:-1.5px}}
.map{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:32px 28px}}
.domain{{display:grid;gap:10px;align-content:start;border-top:2px solid var(--ink);padding-top:14px}} .domain p{{font-size:.9rem;min-height:2.8em}}
.domain ul{{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:4px}}
.t{{display:flex;justify-content:space-between;gap:12px;padding:7px 10px;font-size:.84rem}} .tn{{font-family:ui-monospace,Menlo,monospace;overflow-wrap:anywhere}} .n{{font-variant-numeric:tabular-nums}}
.arch{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0;border:2px solid var(--ink)}}
.arch div{{padding:18px 16px;border-right:1px solid var(--rule);border-bottom:1px solid var(--rule);display:grid;gap:6px;align-content:start;font-size:.88rem}}
.arch b{{font:400 1.05rem "BricksDisplay",Arial,sans-serif}} .arch .hot{{background:var(--red);color:var(--white)}} .arch .ice{{background:var(--ice)}}
.scroll{{overflow-x:auto}} table{{border-collapse:collapse;width:100%;font-size:.9rem;min-width:620px}}
th{{text-align:left;font-weight:600;border-bottom:2px solid var(--ink);padding:10px 12px 10px 0}} td{{vertical-align:top;border-bottom:1px solid var(--rule);padding:10px 12px 10px 0}}
tr:nth-child(even) td{{background:var(--grey)}} td:first-child,th:first-child{{padding-left:8px}}
.fix td:nth-child(1){{width:34%}} .was{{text-decoration:line-through;text-decoration-color:var(--red)}}
.tools{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:6px 24px;list-style:none;padding:0;margin:0;font-size:.88rem}}
.tools li{{padding:8px 0;border-bottom:1px solid var(--rule)}} .tools code{{display:block}} .w code::after{{content:" · writes";color:var(--red);font-weight:400}}
pre.mermaid{{margin:0;background:var(--white);min-width:760px}}
footer{{font-size:.84rem;border-top:2px solid var(--ink);padding-top:16px;display:grid;gap:6px}}
</style>
<div class="wrap">
<header>
  <img alt="bricks" src="data:image/png;base64,{logo}">
  <span class="label">Srichand · AI beauty advisor on LINE · prototype data layer</span>
  <h1>Every product fact is <em>read</em>, never recalled.</h1>
  <p class="lede">This is the map of the database behind the advisor: what is copied from srichand.com, what we derived from it, what Bricks curated, and what is simulated until Srichand's own systems are plugged in. Snapshot: 18 September 2026.</p>
  <div class="funnel">
    <div><b>{S['listings']}</b><span>listings on srichand.com, all read from the official store API</span></div>
    <div><b>{S['products']}</b><span>canonical products once packs, sets and clearance lots are untangled</span></div>
    <div><b>{S['skus']}</b><span>SKUs with official code, list price, sale price, stock flag</span></div>
    <div><b>{S['inci']:,}</b><span>ingredient rows — full INCI for {S['inci_p']} products, from the official pages</span></div>
    <div><b>{S['tables']}</b><span>tables, {S['rows']:,} rows, foreign keys verified</span></div>
  </div>
</header>

<section><div class="head"><span class="label">Provenance</span><h2>Four kinds of data, never mixed up</h2>
  <p>Srichand's executives know their own products. One invented ingredient would cost more trust than ten blanks — so product facts are sourced or left empty, and every table carries one of these marks.</p></div>
  <div class="legend">
    <div class="real"><b>Real — sourced</b><span>Copied from srichand.com (3 ingredient lists from retailers, flagged).</span><small>{totals['real'][0]} tables · {totals['real'][1]:,} rows</small></div>
    <div class="derived"><b>Derived</b><span>Computed from real data by a written rule: English names, categories, set contents, promotions seen on site.</span><small>{totals['derived'][0]} tables · {totals['derived'][1]:,} rows</small></div>
    <div class="curated"><b>Curated</b><span>Bricks' advisor knowledge: concerns, skin types, ingredient dictionary, product mapping, range gaps.</span><small>{totals['curated'][0]} tables · {totals['curated'][1]:,} rows</small></div>
    <div class="mock"><b>Simulated</b><span>Stock quantities, customers, orders, points, analyses. Fictional people, real SKUs and prices.</span><small>{totals['mock'][0]} tables · {totals['mock'][1]:,} rows</small></div>
  </div>
</section>

<section><div class="head"><span class="label">The map</span><h2>Six domains, {S['tables'] - 2} tables</h2><p>Row counts are live from the built database. Hover a table for its description.</p></div>
  <div class="map">{''.join(domain_html(*d) for d in DOMAINS)}</div>
</section>

<section><div class="head"><span class="label">Architecture</span><h2>How the agent reaches the data</h2>
  <p>Facts travel through tools; guidance travels through documents. The language model writes the words — it does not choose the products, set the prices or decide what is in stock.</p></div>
  <div class="arch">
    <div><b>Customer on LINE</b><span>Photo, questions, orders, "where is my parcel?"</span></div>
    <div><b>Agent engine</b><span>Bricks' existing engine on Elysia.js / Bun. Vision model reads the photo.</span></div>
    <div class="hot"><b>25 tools (MCP)</b><span>Typed calls: search, product detail, shade match, stock, routine, cart, order, consent, gap log.</span></div>
    <div><b>SQL database</b><span>SQLite file for the demo; PostgreSQL schema included for production.</span></div>
    <div class="ice"><b>20 journeys · 15 knowledge files</b><span>In the Hub: journeys are procedures the agent follows, knowledge files are the facts and rules it looks up. Kept strictly apart and checked by a validator.</span></div>
  </div>
</section>

<section><div class="head"><span class="label">Relationships</span><h2>The spine of the schema</h2><p>A simplified view; the full diagrams are in <code>docs/erd.md</code>.</p></div>
<div class="scroll"><pre class="mermaid">
erDiagram
  brands ||--o{{ products : owns
  product_lines ||--o{{ products : groups
  categories ||--o{{ products : classifies
  products ||--o{{ product_variants : "sold as SKU"
  products ||--o{{ product_ingredients : "INCI list"
  ingredients ||--o{{ product_ingredients : explains
  products ||--o{{ product_concerns : addresses
  skin_concerns ||--o{{ product_concerns : "mapped to"
  skin_concerns ||--o{{ range_gap_concerns : triggers
  range_gaps ||--o{{ range_gap_concerns : covers
  range_gaps ||--o{{ range_gap_events : "logged as"
  product_variants ||--o{{ inventory : "stocked in"
  product_variants ||--o{{ order_items : "bought as"
  customers ||--o{{ orders : places
  orders ||--o{{ order_items : contains
  orders ||--o{{ payments : "paid by"
  orders ||--o{{ shipments : "delivered by"
  customers ||--o{{ loyalty_transactions : earns
  customers ||--o{{ consent_records : grants
  consent_records ||--o{{ face_analysis_sessions : permits
  face_analysis_sessions ||--o{{ analysis_findings : observes
  face_analysis_sessions ||--o{{ recommendations : produces
  products ||--o{{ recommendations : "is recommended"
</pre></div></section>

<section><div class="head"><span class="label">One conversation</span><h2>Ploy, 27, shiny by 2 pm</h2><p>A demo persona's journey, and what each step touches.</p></div>
<div class="scroll"><table><thead><tr><th>She says / sends</th><th>Tool</th><th>Tables</th><th>What makes it trustworthy</th></tr></thead><tbody>
<tr><td>Adds the LINE account</td><td><code>get_customer</code></td><td>customers, loyalty_accounts</td><td>Age gate: under-20s get a no-photo questionnaire by default</td></tr>
<tr><td>Agrees to photo analysis</td><td><code>record_consent</code> ×3</td><td>consent_records</td><td>Exact Thai consent text stored; photo, profile and cross-border consents are separate</td></tr>
<tr><td>Sends three photos</td><td><code>save_skin_analysis</code></td><td>face_analysis_sessions, analysis_findings</td><td>No image in the database; reference expires in 24 h; findings are observations with confidence, never diagnoses</td></tr>
<tr><td>"Oil and blackheads bother me most"</td><td><code>recommend_routine</code></td><td>product_concerns, product_skin_types, product_variants, inventory</td><td>Deterministic: the same answers always give the same routine</td></tr>
<tr><td>"Anything stronger for blackheads?"</td><td><code>log_range_gap</code></td><td>range_gaps, range_gap_events</td><td>Honest answer + generic option, no competitor named; demand logged for R&amp;D ({S['gaps']} simulated events so far)</td></tr>
<tr><td>"Which cushion shade?"</td><td><code>match_shade</code>, <code>check_stock</code></td><td>product_variants, inventory</td><td>Shade 110 Vanilla — three left; restock date shown</td></tr>
<tr><td>"I'll take the sunscreen and powder"</td><td><code>cart_add_item</code>, <code>create_order</code></td><td>carts, orders, payments, inventory</td><td>Real prices; official rules — free shipping from ฿599, ฿25 = 1 point; no cash on delivery because the site has none. Stock is reserved, becomes a sale on payment, and is released if the QR expires</td></tr>
<tr><td>"Where is my parcel?"</td><td><code>get_order_status</code></td><td>shipments, shipment_events</td><td>Latest courier event in Thai</td></tr>
<tr><td>"ลบข้อมูลของฉัน"</td><td><code>withdraw_consent_and_erase</code></td><td>consent_records, sessions, findings, profile</td><td>Skin data erased in one call; orders kept by law</td></tr>
</tbody></table></div></section>

<section><div class="head"><span class="label">Verification</span><h2>What checking the sources changed</h2><p>Earlier pitch notes were rechecked against the official site and ingredient lists. Six claims did not survive; the full audit is in <code>docs/verification-report.md</code>.</p></div>
<div class="scroll"><table class="fix"><thead><tr><th>Earlier note</th><th>What the data says</th></tr></thead><tbody>
<tr><td class="was">No BHA anywhere in the range</td><td>Salicylic acid is on the official INCI of <b>{S['sal']} products</b> — Sunlution Acne Care and 12 SASI products, two of them leave-on toner pads. The true gap: no SRICHAND-brand leave-on BHA, and no stated strength anywhere.</td></tr>
<tr><td class="was">Super C is the range's AHA</td><td>Glycolic acid is ingredient #26 of 36 in the serum (after the fragrance) and #24 of 29 in the gel cream — a trace, not an exfoliating dose.</td></tr>
<tr><td class="was">Two Sunlution filters aren't approved in the US</td><td>The US FDA cleared Tinosorb S in June 2026. Uvinul A Plus and Uvinul T150 are still not permitted there. Still a strong story — told accurately.</td></tr>
<tr><td class="was">Acne Care sunscreen contains niacinamide and ethyl vitamin C</td><td>That is the Skin Whitening formula; a mislabelled third-party listing caused the mix-up. The six UV filters were right.</td></tr>
<tr><td class="was">Bare to Perfect is the heritage purple powder</td><td>The hero is the classic Translucent Powder. Both have purple packaging; neither powder is purple.</td></tr>
<tr><td class="was">฿269 is the price</td><td>It is the sale price. List prices are ฿435–495; {S['onsale']} of {S['skus']} SKUs were discounted at snapshot, so both are stored.</td></tr>
</tbody></table></div></section>

<section><div class="head"><span class="label">Tools</span><h2>What the agent can do</h2><p>Thirteen read tools are declared read-only to the hub and proven so by test; twelve write tools are marked, and only the PDPA erase is flagged destructive.</p></div>
<ul class="tools">
<li><code>list_reference_data</code>Concern, skin-type and step vocabularies with safe Thai wording</li><li><code>search_products</code>Thai or English text, ingredient, concern, budget, stock</li>
<li><code>get_product</code>Copy, SKUs, shades, INCI with source, claims, how to use</li><li><code>match_shade</code>Undertone + depth → ranked shades with stock</li>
<li><code>check_stock</code>Web flag, warehouse quantities, restock date</li><li><code>get_promotions</code>Coupons, gifts, distance to free shipping</li>
<li><code>recommend_routine</code>Deterministic routine, layering cautions, gaps, refer-out rules</li><li><code>check_ingredient_conflicts</code>What not to layer, what needs sunscreen</li>
<li><code>get_range_gaps</code>Gap list with demand counts</li><li><code>get_customer</code>Profile, points, consents, routine, orders, cart</li>
<li><code>get_order_status</code>Order, payment, courier events</li><li><code>get_loyalty</code>Balance, ledger, affordable rewards</li><li><code>cart_view</code>Live cart with shipping rule</li>
<li class="w"><code>register_member</code>New Srichand Rewards member; returns the number the hub pairs</li><li class="w"><code>cart_add_item</code>Refuses items that cannot ship</li><li class="w"><code>cart_update_item</code>Change quantity or remove</li><li class="w"><code>create_order</code>Coupon, points, shipping, stock reservation, payment</li>
<li class="w"><code>confirm_payment_mock</code>Stands in for the gateway webhook</li><li class="w"><code>record_consent</code>Blocks photo consent for minors without a guardian</li>
<li class="w"><code>set_marketing_preference</code>Promotions on or off, instantly</li><li class="w"><code>withdraw_consent_and_erase</code>PDPA erasure in one call</li><li class="w"><code>save_skin_profile</code>The questionnaire answers a photo cannot show</li><li class="w"><code>save_skin_analysis</code>Requires photo + cross-border consent</li>
<li class="w"><code>save_routine</code>Products or gap slots, 4-week review date</li><li class="w"><code>log_range_gap</code>The R&amp;D demand signal</li>
</ul></section>

<section><div class="head"><span class="label">Production</span><h2>What replaces the simulated tables</h2><p>The schema is the contract. Each simulated table names the Srichand system that would feed it.</p></div>
<div class="scroll"><table><thead><tr><th>Table</th><th>Fed in production by</th></tr></thead><tbody>{swap}</tbody></table></div></section>

<footer><span>Prepared by Bricks. Catalogue facts © Srichand United Dispensary Co., Ltd., read from srichand.com on 18 Sep 2026; prices change frequently.</span>
<span>Regulatory guidance in the knowledge base is a draft for legal review. Loyalty redemption values are demo assumptions — Srichand publishes none.</span></footer>
</div>
"""
out = ROOT / "docs" / "schema-page.html"
out.write_text(html)
print("written", out, f"{len(html) / 1024:.0f} KB", totals)
