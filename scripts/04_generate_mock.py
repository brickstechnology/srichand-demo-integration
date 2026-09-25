#!/usr/bin/env python3
"""Step 4 — MOCK operational data (deterministic; seed 20260918).

Everything written by this script is simulated and is registered as `mock` in data_provenance:
warehouses, inventory, customers, addresses, consents, skin profiles, analysis sessions, findings,
recommendations, routines, gap events, carts, orders, payments, shipments, loyalty balances, coupons.
It only READS real catalogue data (variants, prices, stock flags) so that mock orders use real SKUs
at real prices. People, phone numbers, LINE ids and addresses are fictional."""
import json
import random
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "db" / "seed"
R = random.Random(20260918)
NOW = datetime(2026, 9, 18, 11, 0, tzinfo=timezone.utc)      # 18:00 Bangkok

CFG = json.load(open(ROOT / "scripts" / "mock_config.json"))


def load(n):
    return json.load(open(SEED / f"{n}.json"))


def dump(name, rows):
    (SEED / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    print(f"  {name}: {len(rows)} rows")


def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


products = {p["id"]: p for p in load("products")}
variants = load("product_variants")
cats = {c["id"]: c for c in load("categories")}
concerns = {c["slug"]: c for c in load("skin_concerns")}
skin_types = {s["slug"]: s for s in load("skin_types")}
steps = {s["slug"]: s for s in load("routine_steps")}
gaps = {g["slug"]: g for g in load("range_gaps")}
p_by_name = {p["name_en"]: p for p in products.values()}


def price(v):
    return v["sale_price"] if v["sale_price"] is not None else v["list_price"]


def cat_root(p):
    c = cats[p["category_id"]]
    return cats[c["parent_id"]]["slug"] if c["parent_id"] else c["slug"]


def variant_of(name, size=None, shade=None, fmt=("full_size", "mini")):
    p = p_by_name[name]
    c = [v for v in variants if v["product_id"] == p["id"] and v["pack_format"] in fmt]
    if size:
        c = [v for v in c if v["size_value"] == size]
    if shade:
        c = [v for v in c if v["shade_code"] == shade]
    c.sort(key=lambda v: (-v["web_in_stock"], v["id"]))
    return c[0]


# ───────────────────────────── warehouses & inventory
warehouses = [
    dict(id=1, code="BKK-DC", name="Bangkok Distribution Centre (Bang Phli)", province="Samut Prakan", serves="online_orders"),
    dict(id=2, code="NBI-FC", name="Nonthaburi E-commerce Fulfilment", province="Nonthaburi", serves="online_orders"),
    dict(id=3, code="CNX-RDC", name="Chiang Mai Regional Depot", province="Chiang Mai", serves="retail_replenishment"),
]
inventory, movements = [], []
HERO_WORDS = ["Sunlution", "Translucent Powder", "Skin Moisture Burst", "Super C", "Resurface", "Skin Essential Fine Smooth", "Acne Sol"]
for v in variants:
    p = products[v["product_id"]]
    hero = any(w in p["name_en"] for w in HERO_WORDS)
    for w in warehouses:
        if not v["web_in_stock"] and w["serves"] == "online_orders":
            qty = 0
        elif p["lifecycle_status"] != "active":
            qty = R.choice([0, 0, 0, 4, 9])
        else:
            base = {"full_size": 220, "mini": 300, "sachet_box": 160, "multipack": 60, "set": 35, "gift": 80}.get(v["pack_format"], 50)
            base = int(base * (1.8 if hero else 1.0) * (0.55 if w["id"] != 1 else 1.0))
            qty = max(0, int(R.gauss(base, base * 0.35)))
            if v["web_in_stock"] and w["id"] == 1:
                qty = max(qty, 6)
        reorder = 0 if qty == 0 and not v["web_in_stock"] else int({"full_size": 60, "mini": 80}.get(v["pack_format"], 20) * (1.5 if hero else 1))
        restock = None
        if qty <= reorder and p["lifecycle_status"] == "active":
            restock = (NOW + timedelta(days=R.randint(4, 21))).strftime("%Y-%m-%d")
        inventory.append(dict(variant_id=v["id"], warehouse_id=w["id"], qty_on_hand=qty, qty_reserved=0, reorder_point=reorder,
                              next_restock_date=restock, updated_at=iso(NOW - timedelta(minutes=R.randint(5, 600)))))
# scripted low-stock moments for the demo
for name, size, shade, qty in CFG["scripted_low_stock"]:
    v = variant_of(name, size, shade)
    for row in inventory:
        if row["variant_id"] == v["id"] and row["warehouse_id"] in (1, 2):
            row["qty_on_hand"] = qty if row["warehouse_id"] == 1 else 0
            row["next_restock_date"] = (NOW + timedelta(days=6)).strftime("%Y-%m-%d")
inv_idx = {(r["variant_id"], r["warehouse_id"]): r for r in inventory}

# ───────────────────────────── customers
FIRST_F = ["พลอยไพลิน", "ณัฐธิดา", "กมลชนก", "สุภาวดี", "ปาริชาติ", "วรัญญา", "ชนิดา", "อรวรรณ", "ศิริพร", "เบญจมาศ", "ธนพร", "พิมพ์ชนก", "จิราพร", "กัญญารัตน์", "มณีรัตน์", "ปวีณา", "รัตนาภรณ์", "สุนิสา", "อภิญญา", "นันทนา", "ดวงกมล", "ขวัญจิรา", "ลลิตา", "วิไลวรรณ", "ศศิธร", "อัญชลี"]
FIRST_M = ["ธนกฤต", "ภูมิพัฒน์", "กิตติพงษ์", "ณัฐวุฒิ", "ศุภชัย", "วีรภัทร", "อนุชา", "ปิยะพงษ์"]
LAST = ["ศรีสุวรรณ", "ทองประเสริฐ", "วงศ์สวัสดิ์", "จันทร์เพ็ญ", "บุญมา", "แก้วมณี", "สุขเจริญ", "พรหมมา", "อินทรวงศ์", "รุ่งเรืองกิจ", "ชัยวัฒน์", "ประเสริฐสุข", "มั่นคง", "ใจดี", "นาคสุข", "เพชรรัตน์", "สมบูรณ์ทรัพย์", "วัฒนกุล", "ธรรมรักษ์", "กาญจนวงศ์"]
NICK = ["Ploy", "Mint", "Nok", "Beam", "Fern", "Dao", "Bow", "Mook", "Pim", "Noon", "Fah", "Ice", "Praew", "Jane", "Kwan", "Gift", "Aom", "Bam", "Cream", "Earn", "View", "Mai", "Namwan", "Pang", "Toey", "Ying", "Nan", "Pear", "Bee", "June", "Tarn", "Pond", "Golf", "Bank", "Oat", "Tle", "Boss", "Arm", "Best", "Film"]
PLACES = [("แขวงจตุจักร", "เขตจตุจักร", "กรุงเทพมหานคร", "10900"), ("แขวงสีลม", "เขตบางรัก", "กรุงเทพมหานคร", "10500"), ("แขวงคลองตันเหนือ", "เขตวัฒนา", "กรุงเทพมหานคร", "10110"),
          ("แขวงบางนาใต้", "เขตบางนา", "กรุงเทพมหานคร", "10260"), ("ตำบลตลาดขวัญ", "อำเภอเมืองนนทบุรี", "นนทบุรี", "11000"), ("ตำบลบางพลีใหญ่", "อำเภอบางพลี", "สมุทรปราการ", "10540"),
          ("ตำบลสุเทพ", "อำเภอเมืองเชียงใหม่", "เชียงใหม่", "50200"), ("ตำบลในเมือง", "อำเภอเมืองขอนแก่น", "ขอนแก่น", "40000"), ("ตำบลหาดใหญ่", "อำเภอหาดใหญ่", "สงขลา", "90110"),
          ("ตำบลตลาดใหญ่", "อำเภอเมืองภูเก็ต", "ภูเก็ต", "83000"), ("ตำบลในเมือง", "อำเภอเมืองนครราชสีมา", "นครราชสีมา", "30000"), ("ตำบลแสนสุข", "อำเภอเมืองชลบุรี", "ชลบุรี", "20130")]
customers, addresses = [], []
PERSONAS = CFG["personas"]
def add_customer(cid, persona):
    i = cid - 1
    male = persona["gender"] == "male" if persona else (R.random() < 0.15)
    first = R.choice(FIRST_M if male else FIRST_F)
    last = R.choice(LAST)
    nick = persona["nick"] if persona else NICK[i % len(NICK)]
    age = persona["age"] if persona else R.choice([19, 22, 24, 26, 27, 29, 31, 33, 35, 38, 41, 45, 52])
    birth = datetime(NOW.year - age, R.randint(1, 12), R.randint(1, 28))
    created = NOW - timedelta(days=R.randint(20, 400))
    customers.append(dict(
        id=cid, line_user_id="U" + "".join(R.choice("0123456789abcdef") for _ in range(32)),
        line_display_name=(persona["line_name"] if persona else f"{nick} {R.choice(['🌷', '✨', '', '', '🐰', '☁️'])}".strip()),
        first_name=first, last_name=last, phone=f"08{R.randint(0, 9)}555{R.randint(1000, 9999)}", email=f"{nick.lower()}{cid}@example.com",
        birth_date=birth.strftime("%Y-%m-%d"), gender="male" if male else "female", preferred_language="th",
        marketing_opt_in=1 if R.random() < 0.7 else 0, phone_verified=1, registration_channel="line_rewards_form", is_demo_persona=1 if persona else 0,
        persona_brief=persona["brief"] if persona else None, created_at=iso(created)))
    sub, dist, prov, post = PLACES[persona["place"]] if persona else R.choice(PLACES)
    addresses.append(dict(id=cid, customer_id=cid, label="บ้าน", recipient=f"{first} {last}", phone=customers[-1]["phone"],
                          address_line=f"{R.randint(1, 399)}/{R.randint(1, 99)} ซอย{R.choice(['ลาดพร้าว', 'สุขุมวิท', 'พหลโยธิน', 'รามคำแหง', 'นิมมานเหมินท์', 'มิตรภาพ'])} {R.randint(1, 120)}",
                          subdistrict=sub, district=dist, province=prov, postal_code=post, is_default=1))


for _i in range(CFG["customer_count"]):
    add_customer(_i + 1, PERSONAS[_i] if _i < len(PERSONAS) else None)

# ───────────────────────────── loyalty programme (rules from mock_config.json: official where found, else assumed)
L = CFG["loyalty"]
tiers = [dict(id=i + 1, code=t["code"], name=t["name"], min_annual_spend=t["min_spend"], earn_rate_baht_per_point=t["baht_per_point"],
              benefits_en=t["benefits_en"], benefits_th=t.get("benefits_th"), origin=t["origin"]) for i, t in enumerate(L["tiers"])]
rewards = [dict(id=i + 1, name_th=r["name_th"], name_en=r["name_en"], reward_type=r["type"], points_cost=r["points"],
                variant_id=(variant_of(*r["variant"])["id"] if r.get("variant") else None), discount_value=r.get("discount"),
                min_tier_id=r.get("min_tier"), is_active=1, origin=r["origin"]) for i, r in enumerate(L["rewards"])]

# ───────────────────────────── promotions
promotions, promo_variants, coupons = [], [], []
idx = json.load(open(SEED / "_catalog_index.json"))


def add_promo(**kw):
    kw["id"] = len(promotions) + 1
    promotions.append(kw)
    return kw["id"]


sale_ids = [v["id"] for v in variants if v["sale_price"] is not None]
pid_sale = add_promo(code="SITE-SALE-2026-09", name_th="ราคาพิเศษหน้าเว็บ (THE MOONRISE FESTIVAL)", name_en="Site-wide sale prices (The Moonrise Festival)",
                     promo_type="sale_price", mechanics_en="Sale prices shown on srichand.com at snapshot time; stored per variant in product_variants.sale_price.",
                     min_spend=None, discount_type=None, discount_value=None, gift_variant_id=None, starts_at=None, ends_at=None, is_active=1, origin="observed_on_site")
promo_variants += [dict(promotion_id=pid_sale, variant_id=i) for i in sale_ids]
pid_bogo = add_promo(code="BOGO-SACHET", name_th="ซื้อ 1 แถม 1 สกินแคร์แบบซอง", name_en="Buy-1-get-1 skincare sachets",
                     promo_type="bogo", mechanics_en="[Bogo] listings: pay for 3 (or 6) sachets, receive 6 (or 12). Barrier Boost and Timeless sachets.",
                     min_spend=None, discount_type="percent", discount_value=50, gift_variant_id=None, starts_at=None, ends_at=None, is_active=1, origin="observed_on_site")
promo_variants += [dict(promotion_id=pid_bogo, variant_id=i) for i in idx["bogo_variant_ids"]]
for p in products.values():                        # gift-with-purchase thresholds are printed on the official gift listings
    if p["product_type"] in ("gift_with_purchase", "gift_card"):
        m = re.search(r"ซื้อครบ\s*([\d,\s]+)\s*\.?-", p.get("description_th") or "")
        if not m:
            continue
        spend = float(re.sub(r"[,\s]", "", m.group(1)))
        gv = next(v for v in variants if v["product_id"] == p["id"])
        lim = re.search(r"จำกัด\s*(\d+)", p["description_th"])
        add_promo(code=f"GWP-{int(spend)}-{p['id']}", name_th=p["name_th"][:120], name_en=p["name_en"][:120], promo_type="gift_with_purchase",
                  mechanics_en=f"Free gift when the basket reaches ฿{spend:,.0f}" + (f"; limited to {lim.group(1)} redemptions." if lim else ".") + (" Verified: auto-added in a live srichand.com test cart on 2026-09-18." if spend == 499 else " Threshold is printed on the official gift listing, but the gift was NOT auto-added in live test carts on 2026-09-18 — treated as inactive."),
                  min_spend=spend, discount_type="gift", discount_value=None, gift_variant_id=gv["id"], starts_at=None, ends_at=None,
                  is_active=1 if spend == 499 else 0, origin="observed_on_site")
for c in CFG["observed_coupons"]:        # real September 2026 website coupon tiers (code strings are placeholders)
    pid = add_promo(code=c["promo_code"], name_th=c["name_th"], name_en=c["name_en"], promo_type="coupon",
                    mechanics_en=f"Collectable website coupon: ฿{c['discount_value']} off when the basket reaches ฿{c['min_spend']:,}. Valid 1–30 Sep 2026.",
                    min_spend=c["min_spend"], discount_type="amount", discount_value=c["discount_value"], gift_variant_id=None,
                    starts_at="2026-08-31T17:00:00Z", ends_at="2026-09-30T16:59:59Z", is_active=1, origin="observed_on_site")
    coupons.append(dict(id=len(coupons) + 1, promotion_id=pid, code=c["coupon_code"], customer_id=None, max_uses=100000, used_count=0, expires_at="2026-09-30T16:59:59Z"))
for c in CFG["mock_coupons"]:
    pid = add_promo(code=c["promo_code"], name_th=c["name_th"], name_en=c["name_en"], promo_type=c["promo_type"], mechanics_en=c["mechanics_en"],
                    min_spend=c.get("min_spend"), discount_type=c["discount_type"], discount_value=c["discount_value"], gift_variant_id=None,
                    starts_at=iso(NOW - timedelta(days=30)), ends_at=iso(NOW + timedelta(days=45)), is_active=1, origin="mock")
    coupons.append(dict(id=len(coupons) + 1, promotion_id=pid, code=c["coupon_code"], customer_id=None, max_uses=c.get("max_uses", 5000),
                        used_count=0, expires_at=iso(NOW + timedelta(days=45))))
coupon_by_code = {c["code"]: c for c in coupons}
promo_by_id = {p["id"]: p for p in promotions}

# ───────────────────────────── orders, payments, shipments
SHIP = CFG["shipping"]
orderable = [v for v in variants if v["web_in_stock"] and v["is_listed_on_site"] and products[v["product_id"]]["product_type"] in ("single", "set", "accessory")
             and products[v["product_id"]]["lifecycle_status"] == "active"]
weights = []
for v in orderable:
    p = products[v["product_id"]]
    w = {"skincare": 3.0, "sunscreen": 4.0, "powder": 3.0, "base-makeup": 2.0, "lip": 1.2, "colour-makeup": 1.0, "sets": 0.8}.get(cat_root(p), 0.5)
    if any(h in p["name_en"] for h in HERO_WORDS):
        w *= 2
    if v["shade_code"]:
        w /= 3
    weights.append(w)
CARRIERS = [("Flash Express", "TH{:012d}A"), ("Kerry Express", "KEX{:011d}"), ("J&T Express", "82{:010d}"), ("Thailand Post", "EB{:09d}TH")]
STATUS_FLOW_TH = {"label_created": "ร้านค้าสร้างรายการจัดส่งแล้ว", "picked_up": "บริษัทขนส่งเข้ารับพัสดุแล้ว", "in_transit": "พัสดุอยู่ระหว่างขนส่ง",
                  "out_for_delivery": "พัสดุกำลังนำจ่าย", "delivered": "จัดส่งสำเร็จ ผู้รับเซ็นรับแล้ว", "failed_attempt": "นำจ่ายไม่สำเร็จ ติดต่อผู้รับไม่ได้"}
orders, items, payments, shipments, events, ltx = [], [], [], [], [], []
seq_by_day = {}


def make_order(cust, when, lines_, channel="line_oa_agent", status=None, method=None, coupon=None, redeem_points=0, session_id=None):
    oid = len(orders) + 1
    day = when.strftime("%y%m%d")
    seq_by_day[day] = seq_by_day.get(day, 0) + 1
    subtotal = round(sum(price(v) * q for v, q in lines_), 2)
    discount = 0.0
    cpn = coupon_by_code.get(coupon) if coupon else None
    if cpn:
        pr = promo_by_id[cpn["promotion_id"]]
        if subtotal >= (pr["min_spend"] or 0):
            discount = round(subtotal * pr["discount_value"] / 100, 2) if pr["discount_type"] == "percent" else (pr["discount_value"] if pr["discount_type"] == "amount" else 0)
            cpn["used_count"] += 1
        else:
            cpn = None
    ship_fee = 0 if subtotal - discount >= SHIP["free_threshold"] or (cpn and promo_by_id[cpn["promotion_id"]]["discount_type"] == "shipping") else SHIP["flat_fee"]
    pts_disc = round(redeem_points * L["baht_per_point_redeemed"], 2)
    total = round(subtotal - discount - pts_disc + ship_fee, 2)
    age_h = (NOW - when).total_seconds() / 3600
    pm = CFG["payment_methods"]["weights"]
    method = method or R.choices(list(pm), list(pm.values()))[0]
    if status is None:
        if R.random() < 0.04:
            status = "cancelled"
        elif age_h < 2:
            status = "paid"
        elif age_h < 20:
            status = "packing"
        elif age_h < 72:
            status = "shipped"
        else:
            status = "delivered" if R.random() > 0.015 else "refunded"
    tier = next(a for a in accounts if a["customer_id"] == cust["id"])
    rate = tiers[tier["tier_id"] - 1]["earn_rate_baht_per_point"]
    earned = int((subtotal - discount - pts_disc) // rate) if status not in ("cancelled", "pending_payment", "refunded") else 0
    orders.append(dict(id=oid, order_number=f"SC-{day}-{seq_by_day[day]:04d}", customer_id=cust["id"], channel=channel, status=status,
                       shipping_address_id=cust["id"], subtotal=subtotal, discount_total=discount, shipping_fee=ship_fee, points_redeemed=redeem_points,
                       points_discount=pts_disc, grand_total=total, coupon_id=cpn["id"] if cpn else None, points_earned=earned,
                       source_session_id=session_id, placed_at=iso(when), updated_at=iso(min(NOW, when + timedelta(hours=min(age_h, 96))))))
    for v, q in lines_:
        items.append(dict(id=len(items) + 1, order_id=oid, variant_id=v["id"], quantity=q, unit_price=price(v), line_total=round(price(v) * q, 2), is_gift=0))
        if status not in ("pending_payment", "cancelled"):      # unpaid orders only hold a reservation (see the end of this script)
            movements.append(dict(id=len(movements) + 1, variant_id=v["id"], warehouse_id=1, movement_type="sale", quantity=-q, reference=orders[-1]["order_number"], created_at=iso(when)))
    gwp = [p for p in promotions if p["promo_type"] == "gift_with_purchase" and p["is_active"] and subtotal - discount >= p["min_spend"]]
    if gwp and status != "cancelled" and when > NOW - timedelta(days=21):
        g = max(gwp, key=lambda p: p["min_spend"])
        items.append(dict(id=len(items) + 1, order_id=oid, variant_id=g["gift_variant_id"], quantity=1, unit_price=0, line_total=0, is_gift=1))
    pstat = {"pending_payment": "pending", "cancelled": "expired" if method != "cod" else "failed", "refunded": "refunded"}.get(status, "succeeded")
    if method == "cod" and status in ("paid", "packing", "shipped"):
        pstat = "pending"
    payments.append(dict(id=len(payments) + 1, order_id=oid, method=method, status=pstat, amount=total,
                         gateway_ref=f"MOCK-{R.randint(10**9, 10**10 - 1)}", qr_payload_ref=(f"mockqr://promptpay/{oid:06d}" if method == "promptpay_qr" else None),
                         expires_at=iso(when + timedelta(minutes=30)) if method in ("promptpay_qr", "mobile_banking") else None,
                         paid_at=iso(when + timedelta(minutes=R.randint(1, 14))) if pstat == "succeeded" else None, created_at=iso(when)))
    if status in ("shipped", "delivered", "refunded"):
        carrier, fmt = R.choice(CARRIERS)
        sid = len(shipments) + 1
        shipped_at = when + timedelta(hours=R.randint(18, 40))
        delivered = status in ("delivered", "refunded")
        bkk = addresses[cust["id"] - 1]["province"] in ("กรุงเทพมหานคร", "นนทบุรี", "สมุทรปราการ")
        transit_days = R.randint(1, 2) if bkk else R.randint(2, 4)
        delivered_at = shipped_at + timedelta(days=transit_days, hours=R.randint(1, 8))
        if delivered and delivered_at > NOW:
            delivered = False
        flow = ["label_created", "picked_up", "in_transit"] + (["out_for_delivery", "delivered"] if delivered else [])
        if not delivered and (NOW - shipped_at).total_seconds() / 3600 > transit_days * 24 - 6:
            flow.append("out_for_delivery")
        shipments.append(dict(id=sid, order_id=oid, warehouse_id=1 if R.random() < 0.7 else 2, carrier=carrier, tracking_number=fmt.format(R.randint(10**8, 10**9 - 1) * 7 + sid),
                              status=flow[-1], shipped_at=iso(shipped_at), estimated_delivery=(shipped_at + timedelta(days=transit_days)).strftime("%Y-%m-%d"),
                              delivered_at=iso(delivered_at) if delivered else None))
        span = (delivered_at if delivered else min(NOW, delivered_at)) - shipped_at
        locs = ["คลังสินค้า บางพลี สมุทรปราการ", "ศูนย์คัดแยก บางนา", "ศูนย์กระจายสินค้า " + addresses[cust["id"] - 1]["province"], "สาขาปลายทาง " + addresses[cust["id"] - 1]["district"], addresses[cust["id"] - 1]["district"]]
        for k, st in enumerate(flow):
            t = shipped_at - timedelta(hours=3) if k == 0 else shipped_at + span * (k - 1) / max(1, len(flow) - 2)
            events.append(dict(id=len(events) + 1, shipment_id=sid, status=st, location=locs[min(k, len(locs) - 1)], description_th=STATUS_FLOW_TH[st], occurred_at=iso(min(t, NOW))))
    if earned:
        ltx.append(dict(id=len(ltx) + 1, customer_id=cust["id"], txn_type="earn", points=earned, order_id=oid, description=f"สะสมแต้มจากคำสั่งซื้อ {orders[-1]['order_number']}",
                        expires_on=(when + timedelta(days=L["points_valid_days"])).strftime("%Y-%m-%d"), created_at=iso(when)))
    if redeem_points:
        ltx.append(dict(id=len(ltx) + 1, customer_id=cust["id"], txn_type="redeem", points=-redeem_points, order_id=oid, description="ใช้แต้มเป็นส่วนลด", expires_on=None, created_at=iso(when)))
    return orders[-1]


accounts = [dict(customer_id=c["id"], member_number=f"SCR{260000 + c['id']:07d}", tier_id=1, points_balance=0, lifetime_points=0, spend_this_period=0,
                 tier_expires_on="2026-12-31", joined_at=c["created_at"]) for c in customers]

# welcome bonus (0 in the official programme: none is published)
for c in customers if L["welcome_bonus_points"] else []:
    ltx.append(dict(id=len(ltx) + 1, customer_id=c["id"], txn_type="bonus", points=L["welcome_bonus_points"], order_id=None, description="แต้มต้อนรับสมาชิกใหม่ (mock)",
                    expires_on=None, created_at=c["created_at"]))

# scripted persona orders first (so their stories are stable), then random history
sessions_for_orders = {}
def add_persona_order(po):
    cust = customers[po["customer"] - 1]
    when = NOW - timedelta(days=po["days_ago"], hours=po.get("hours_ago", 0))
    lines_ = [(variant_of(*ln["variant"]), ln.get("qty", 1)) for ln in po["lines"]]
    o = make_order(cust, when, lines_, status=po.get("status"), method=po.get("method"), coupon=po.get("coupon"), redeem_points=po.get("redeem_points", 0))
    sessions_for_orders[o["id"]] = po.get("from_session")
    return o


for _po in [p for p in CFG["persona_orders"] if p["customer"] <= CFG["customer_count"]]:
    add_persona_order(_po)
while len(orders) < CFG["order_count"]:
    cust = R.choices(customers, weights=[3 if c["id"] <= 12 else 1 for c in customers])[0]
    when = NOW - timedelta(days=R.triangular(0.2, 120, 25), minutes=R.randint(0, 600))
    if when < datetime.fromisoformat(cust["created_at"].replace("Z", "+00:00")):
        continue
    k = R.choices([1, 2, 3, 4], [35, 35, 20, 10])[0]
    chosen = {v["id"]: v for v in R.choices(orderable, weights=weights, k=k)}
    make_order(cust, when, [(v, R.choices([1, 2], [85, 15])[0]) for v in chosen.values()],
               channel=R.choices(["line_oa_agent", "website", "line_shopping"], [55, 35, 10])[0], coupon=R.choice([None, None, "WELCOME50", "FREESHIP", "SEP30", "SEP70", "SEP150"]))

# tiers from 12-month spend; balances from ledger
def settle(a):
    spend = sum(o["grand_total"] for o in orders if o["customer_id"] == a["customer_id"] and o["status"] in ("paid", "packing", "shipped", "delivered"))
    a["spend_this_period"] = round(spend, 2)
    a["tier_id"] = max(t["id"] for t in tiers if spend >= t["min_annual_spend"])
    pts = [t for t in ltx if t["customer_id"] == a["customer_id"]]
    a["points_balance"] = max(0, sum(t["points"] for t in pts))
    a["lifetime_points"] = sum(t["points"] for t in pts if t["points"] > 0)


for _a in accounts:
    settle(_a)
redemptions = []

# ───────────────────────────── consent, skin profiles, analysis sessions, routines, gap events
CONSENT_TXT = CFG["consent_text_th"]
consents, profiles, sessions, findings, recs, routines, routine_items, gap_events = [], [], [], [], [], [], [], []


def consent(cust, ctype, when, minor=False):
    consents.append(dict(id=len(consents) + 1, customer_id=cust["id"], consent_type=ctype, policy_version=CFG["policy_version"],
                         consent_text_th=CONSENT_TXT[ctype], granted_at=iso(when), withdrawn_at=None, channel="line_oa", is_minor_flow=1 if minor else 0))
    return consents[-1]["id"]


def rec(session_id, name, step, rank, reason_en, reason_th, concern, outcome, variant=None):
    p = p_by_name[name]
    recs.append(dict(id=len(recs) + 1, session_id=session_id, product_id=p["id"], variant_id=variant, step_id=steps[step]["id"], rank=rank,
                     reason_en=reason_en, reason_th=reason_th, addresses_concern_id=concerns[concern]["id"], outcome=outcome))


def add_persona_session(ps):
    cust = customers[ps["customer"] - 1]
    when = NOW - timedelta(days=ps["days_ago"], hours=2)
    minor = ps.get("minor", False)
    cid_photo = consent(cust, "face_photo_analysis", when - timedelta(minutes=6), minor)
    cid_prof = consent(cust, "skin_profile_storage", when - timedelta(minutes=6), minor)
    consent(cust, "cross_border_processing", when - timedelta(minutes=6), minor)
    pr = ps["profile"]
    profiles.append(dict(customer_id=cust["id"], consent_id=cid_prof, self_reported_skin_type_id=skin_types[pr["skin_type"]]["id"], sensitivity_level=pr["sensitivity"],
                         known_reactions=pr.get("reactions"), goals=json.dumps(pr["goals"]), current_routine=pr.get("current_routine"), routine_appetite=pr["appetite"],
                         budget_per_product=pr.get("budget"), wears_makeup=pr.get("makeup"), environment=pr.get("environment"), is_pregnant_or_nursing=pr.get("pregnant", 0),
                         updated_at=iso(when)))
    sid = len(sessions) + 1
    expired = ps["days_ago"] > CFG["image_retention_days"]
    sessions.append(dict(id=sid, customer_id=cust["id"], consent_id=cid_photo, image_ref=None if expired else f"s3://srichand-advisor-demo/sessions/{sid:05d}/",
                         image_sha256="".join(R.choice("0123456789abcdef") for _ in range(64)), image_count=(ps["images"] if "images" in ps else 3),
                         image_expires_at=iso(when + timedelta(days=CFG["image_retention_days"])), image_deleted_at=iso(when + timedelta(days=CFG["image_retention_days"])) if expired else None,
                         photo_quality=(ps["quality"] if "quality" in ps else "good"), quality_flags=json.dumps(ps.get("flags", [])), model_version=CFG["model_version"],
                         observed_skin_type_id=skin_types[ps["observed_skin_type"]]["id"], observed_undertone=ps.get("undertone"), observed_depth=ps.get("depth"),
                         summary_th=ps["summary_th"], status="completed", created_at=iso(when)))
    for f in ps["findings"]:
        findings.append(dict(id=len(findings) + 1, session_id=sid, concern_id=concerns[f[0]]["id"], face_zone=f[1], severity=f[2], confidence=f[3], observation_en=f[4]))
    for k, r_ in enumerate(ps["recommendations"]):
        v = variant_of(*r_["variant"])["id"] if r_.get("variant") else None
        rec(sid, r_["product"], r_["step"], k + 1, r_["reason_en"], r_.get("reason_th"), r_["concern"], r_.get("outcome", "shown"), v)
    rid = len(routines) + 1
    routines.append(dict(id=rid, customer_id=cust["id"], session_id=sid, name=ps["routine"]["name"], goal_en=ps["routine"]["goal_en"], is_active=1,
                         review_after=(when + timedelta(days=28)).strftime("%Y-%m-%d"), created_at=iso(when)))
    for it in ps["routine"]["items"]:
        routine_items.append(dict(id=len(routine_items) + 1, routine_id=rid, period=it[0], step_id=steps[it[1]]["id"],
                                  product_id=p_by_name[it[2]]["id"] if it[2] else None, gap_id=gaps[it[3]]["id"] if it[3] else None,
                                  frequency_en=it[4], instruction_en=it[5], instruction_th=None))
    for gslug, cslug in ps.get("gaps", []):
        gap_events.append(dict(id=len(gap_events) + 1, gap_id=gaps[gslug]["id"], customer_id=cust["id"], session_id=sid, concern_id=concerns[cslug]["id"],
                               customer_age_band=f"{(ps_age := NOW.year - int(cust['birth_date'][:4])) // 10 * 10}s", customer_skin_type_id=skin_types[ps["observed_skin_type"]]["id"],
                               generic_option_mentioned=1, created_at=iso(when)))
for _ps in [x for x in CFG["persona_sessions"] if x["customer"] <= CFG["customer_count"]]:
    add_persona_session(_ps)
for oid, snum in sessions_for_orders.items():
    if snum and snum != "own":
        orders[oid - 1]["source_session_id"] = snum

# background sessions + gap events for non-persona customers (the R&D demand signal)
GAP_WEIGHTS = [("dedicated-bha-treatment", 52, ["blackheads-congestion", "excess-sebum-shine", "enlarged-pores", "acne-breakouts"]), ("azelaic-acid", 14, ["sensitivity-redness", "post-acne-marks"]),
               ("medical-acne-care", 12, ["acne-breakouts"]), ("eye-care", 15, ["under-eye-darkness", "fine-lines-wrinkles"]), ("body-sun-care", 7, ["daily-uv-protection"])]
for c in customers[len(PERSONAS):]:
    if R.random() < 0.62:
        when = NOW - timedelta(days=R.triangular(1, 90, 20), minutes=R.randint(0, 900))
        cid_photo = consent(c, "face_photo_analysis", when - timedelta(minutes=5))
        consent(c, "cross_border_processing", when - timedelta(minutes=5))
        obs = R.choices(["oily", "combination", "dehydrated-oily", "normal", "dry", "sensitive", "acne-prone"], [28, 26, 12, 10, 8, 8, 8])[0]
        sid = len(sessions) + 1
        expired = (NOW - when).days > CFG["image_retention_days"]
        sessions.append(dict(id=sid, customer_id=c["id"], consent_id=cid_photo, image_ref=None if expired else f"s3://srichand-advisor-demo/sessions/{sid:05d}/",
                             image_sha256="".join(R.choice("0123456789abcdef") for _ in range(64)), image_count=R.choice([1, 2, 3]),
                             image_expires_at=iso(when + timedelta(days=CFG["image_retention_days"])), image_deleted_at=iso(when + timedelta(days=CFG["image_retention_days"])) if expired else None,
                             photo_quality=R.choices(["good", "usable", "poor"], [55, 38, 7])[0], quality_flags=json.dumps(R.choice([[], [], ["makeup_on"], ["beauty_filter_suspected"], ["low_light"]])),
                             model_version=CFG["model_version"], observed_skin_type_id=skin_types[obs]["id"], observed_undertone=R.choice(["warm_yellow", "neutral", "cool_pink", "warm_golden"]),
                             observed_depth=R.choice(["fair", "light", "light-medium", "medium", "tan"]), summary_th=None, status="completed", created_at=iso(when)))
        pool = {"oily": ["excess-sebum-shine", "enlarged-pores", "blackheads-congestion"], "combination": ["excess-sebum-shine", "dullness-uneven-tone", "enlarged-pores"],
                "dehydrated-oily": ["dehydration", "excess-sebum-shine"], "normal": ["dullness-uneven-tone", "fine-lines-wrinkles"], "dry": ["dryness", "fine-lines-wrinkles"],
                "sensitive": ["sensitivity-redness", "compromised-barrier"], "acne-prone": ["acne-breakouts", "post-acne-marks", "blackheads-congestion"]}[obs]
        for cs in pool[:R.randint(2, 3)]:
            findings.append(dict(id=len(findings) + 1, session_id=sid, concern_id=concerns[cs]["id"], face_zone=R.choice(["t_zone", "cheeks", "forehead", "nose", "chin_jaw", "overall"]),
                                 severity=R.randint(1, 3), confidence=R.choice(["high", "medium", "medium", "low"]), observation_en=None))
        if R.random() < (0.75 if obs in ("oily", "acne-prone", "combination") else 0.35):
            if obs in ("oily", "acne-prone", "combination"):
                g = R.choices(GAP_WEIGHTS, [70, 8, 14, 5, 3])[0]
            else:
                g = R.choices(GAP_WEIGHTS, [w for _, w, _ in GAP_WEIGHTS])[0]
            age = NOW.year - int(c["birth_date"][:4])
            gap_events.append(dict(id=len(gap_events) + 1, gap_id=gaps[g[0]]["id"], customer_id=c["id"], session_id=sid, concern_id=concerns[R.choice(g[2])]["id"],
                                   customer_age_band=f"{age // 10 * 10}s", customer_skin_type_id=skin_types[obs]["id"], generic_option_mentioned=1 if R.random() < 0.8 else 0, created_at=iso(when)))
# advice chats without a registered customer / photo also log gaps (customer_id NULL) — this is the R&D demand signal
for _ in range(CFG["anonymous_gap_events"]):
    g = R.choices(GAP_WEIGHTS, [w for _, w, _ in GAP_WEIGHTS])[0]
    when = NOW - timedelta(days=R.triangular(0, 90, 10), minutes=R.randint(0, 1400))
    st = R.choices(["oily", "combination", "acne-prone", "dehydrated-oily", "sensitive", "dry", "normal"], [30, 24, 16, 10, 8, 6, 6])[0]
    gap_events.append(dict(id=len(gap_events) + 1, gap_id=gaps[g[0]]["id"], customer_id=None, session_id=None, concern_id=concerns[R.choice(g[2])]["id"],
                           customer_age_band=R.choices(["10s", "20s", "30s", "40s", "50s"], [14, 40, 26, 13, 7])[0], customer_skin_type_id=skin_types[st]["id"],
                           generic_option_mentioned=1 if R.random() < 0.85 else 0, created_at=iso(when)))
gap_events.sort(key=lambda e: e["created_at"])
for i, e in enumerate(gap_events):
    e["id"] = i + 1
for c in customers:
    if R.random() < 0.7 or c["is_demo_persona"]:
        consent(c, "marketing", datetime.fromisoformat(c["created_at"].replace("Z", "+00:00")))

# ───────────────────────────── late personas
# Added after the first release. Each gets its own RNG and ids after everyone else, so every existing customer,
# order and session stays byte-identical when a persona is added.
_main_R = R
for _k, _persona in enumerate(CFG.get("late_personas", [])):
    R = random.Random(f"late-persona-{_persona['nick']}")
    _cid = CFG["customer_count"] + _k + 1
    add_customer(_cid, _persona)
    _c = customers[-1]
    accounts.append(dict(customer_id=_cid, member_number=f"SCR{260000 + _cid:07d}", tier_id=1, points_balance=0, lifetime_points=0, spend_this_period=0,
                         tier_expires_on="2026-12-31", joined_at=_c["created_at"]))
    _orders = [add_persona_order(p) for p in CFG["persona_orders"] if p["customer"] == _cid]
    for _ps in [x for x in CFG["persona_sessions"] if x["customer"] == _cid]:
        add_persona_session(_ps)
        for _o in _orders:
            if sessions_for_orders.get(_o["id"]) == "own":
                _o["source_session_id"] = sessions[-1]["id"]
    consent(_c, "marketing", datetime.fromisoformat(_c["created_at"].replace("Z", "+00:00")))
    settle(accounts[-1])
R = _main_R

# ───────────────────────────── carts
carts, cart_items = [], []
for ct in CFG["persona_carts"]:
    cid = len(carts) + 1
    when = NOW - timedelta(hours=ct["hours_ago"])
    carts.append(dict(id=cid, customer_id=ct["customer"], status="open", created_at=iso(when), updated_at=iso(when + timedelta(minutes=9))))
    for ln in ct["lines"]:
        cart_items.append(dict(cart_id=cid, variant_id=variant_of(*ln["variant"])["id"], quantity=ln.get("qty", 1), added_from=ln.get("from", "advisor_recommendation")))

# Stock model (mirrors mcp-server): placing an order RESERVES stock; payment turns the reservation into a sale.
# So only unpaid orders hold a reservation, and each reservation is a movement row the server can later settle or release.
for o in orders:
    if o["status"] == "pending_payment":
        for it in [i for i in items if i["order_id"] == o["id"]]:
            row = inv_idx.get((it["variant_id"], 1))
            if row:
                row["qty_on_hand"] = max(row["qty_on_hand"], row["qty_reserved"] + it["quantity"])
                row["qty_reserved"] += it["quantity"]
                movements.append(dict(id=len(movements) + 1, variant_id=it["variant_id"], warehouse_id=1, movement_type="reservation", quantity=it["quantity"],
                                      reference=o["order_number"], created_at=o["placed_at"]))

print("Mock seed written:")
for name, rows in [("warehouses", warehouses), ("inventory", inventory), ("inventory_movements", movements), ("customers", customers), ("customer_addresses", addresses),
                   ("promotions", promotions), ("promotion_variants", promo_variants), ("coupons", coupons), ("carts", carts), ("cart_items", cart_items),
                   ("orders", orders), ("order_items", items), ("payments", payments), ("shipments", shipments), ("shipment_events", events),
                   ("loyalty_tiers", tiers), ("loyalty_accounts", accounts), ("loyalty_transactions", ltx), ("rewards_catalog", rewards), ("reward_redemptions", redemptions),
                   ("consent_records", consents), ("customer_skin_profiles", profiles), ("face_analysis_sessions", sessions), ("analysis_findings", findings),
                   ("recommendations", recs), ("routines", routines), ("routine_items", routine_items), ("range_gap_events", gap_events)]:
    dump(name, rows)
