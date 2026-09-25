#!/usr/bin/env python3
"""Step 2 — derive set contents (bundle_components) by matching official set names/descriptions
against canonical product names. Output: db/seed/bundle_components.json
Basis: text-matching of official copy (DERIVED). Anything that cannot be matched is left out rather than guessed."""
import gzip, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lib_normalize import clean, strip_html

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "db" / "seed"
P = {x["id"]: x for x in json.load(gzip.open(ROOT / "research/raw/srichand_store_api_products_2026-09-18.json.gz"))}
products = json.load(open(SEED / "products.json"))
variants = json.load(open(SEED / "product_variants.json"))
index = json.load(open(SEED / "_catalog_index.json"))

def norm(s):
    s = clean(s)
    s = re.sub(r"เอสพีเอฟ\s*\d+\+?|พีเอ\s*\+*|SPF\s*\d+\+?|PA\s*\+*", " ", s, flags=re.I)
    for a, b in [("แบร์ทูเพอเฟค", "แบร์ทูเพอร์เฟคท์"), ("บูสต์", "บูส"), ("เอสเซ็นส์", "เอสเซนส์"), ("คลีนซิ่ง", "คลีนซิ่ง")]:
        s = s.replace(a, b)
    return re.sub(r"[^\wก-๙]+", "", s).lower()

singles = []
for p in products:
    if p["product_type"] != "single":
        continue
    th = re.sub(r"^(ศรีจันทร์|ศศิ)\s*", "", p["name_th"])
    singles.append((p, norm(th), norm(p["name_en"])))
singles.sort(key=lambda t: -len(t[1]))          # longest names first so 'Gel Cream' beats 'Cream'

rows, report = [], []
for key, g in index["groups"].items():
    if g["kind"] not in ("set", "gift"):
        continue
    x = P[g["listing_ids"][0]]
    name = clean(x["name"])
    text_name = norm(name)
    text_all = norm(name + " " + strip_html(x["description"]))
    bundle_variants = [v for v in variants if v["product_id"] == g["product_id"]]
    found = []
    consumed = text_all
    for p, th, en in singles:
        hit = None
        if len(th) >= 8 and th in consumed:
            hit = th
        elif len(en) >= 10 and en in consumed:
            hit = en
        if hit:
            consumed = consumed.replace(hit, "§")
            found.append(p)
    for p in found:
        th = re.sub(r"^(ศรีจันทร์|ศศิ)\s*", "", p["name_th"])
        # quantity + size + free-gift hints from the listing NAME only (most reliable part)
        m = re.search(re.escape(th[:25]) + r"[^\[\]+]*?\((\d+(?:\.\d+)?)\s*(มล|ก)\.?\)\s*(\d+)?\s*(ชิ้น|ซอง)?", name)
        size = float(m.group(1)) if m else None
        qty = int(m.group(3)) if m and m.group(3) else 1
        is_gift = bool(re.search(r"แถมฟรี[^\]]*" + re.escape(th[:20]), name))
        comp_variant = None
        cands = [v for v in variants if v["product_id"] == p["id"] and v["pack_format"] in ("full_size", "mini") and not v["shade_code"]]
        if size:
            cands = [v for v in cands if v["size_value"] == size]
        if len(cands) == 1:
            comp_variant = cands[0]["id"]
        for bv in bundle_variants:
            rows.append(dict(bundle_variant_id=bv["id"], component_variant_id=comp_variant, component_product_id=p["id"],
                             component_label=p["name_en"] + (f" {size:g}" + ("ml" if m.group(2) == "มล" else "g") if size else ""),
                             quantity=qty, is_free_gift=1 if is_gift else 0))
    report.append((g["product_id"], name[:80], [p["name_en"] for p in found]))

# de-duplicate on PK
seen, out = set(), []
for r in rows:
    k = (r["bundle_variant_id"], r["component_label"])
    if k not in seen:
        seen.add(k); out.append(r)
(SEED / "bundle_components.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"bundle_components: {len(out)} rows")
if "--report" in sys.argv:
    for r in report:
        print(r[0], "|", r[1], "\n      →", r[2])
