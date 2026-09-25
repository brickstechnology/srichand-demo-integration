#!/usr/bin/env python3
"""Step 3 — advisor knowledge layer.

Reads db/seed/products.json (+ research/findings/inci_*.json when present) and writes:
  skin_types, skin_concerns, routine_steps, ingredients, ingredient_interactions,
  product_hero_ingredients, product_ingredients, product_concerns, product_skin_types,
  product_routine_steps, product_claims, range_gaps, range_gap_concerns
and enriches products.json / product_lines.json in place.

Provenance: official copy is parsed by regex (coverage, finish, oil-control hours, water resistance,
claims); the per-product mappings in curation.py are hand-curated readings of that copy;
makeup categories get rule-based mappings. Full INCI lists come only from cited sources."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import curation as C

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "db" / "seed"
FIND = ROOT / "research" / "findings"


def load(name):
    return json.load(open(SEED / f"{name}.json"))


def dump(name, rows):
    (SEED / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    print(f"  {name}: {len(rows)} rows")


products = load("products")
lines = load("product_lines")
cats = {c["id"]: c for c in load("categories")}
by_name = {p["name_en"]: p for p in products}

# ------------------------------------------------------------------ dictionaries
skin_types = [dict(id=i + 1, slug=s[0], name_en=s[1], name_th=s[2], description_en=s[3]) for i, s in enumerate(C.SKIN_TYPES)]
concerns = [dict(id=i + 1, slug=c[0], name_en=c[1], name_th=c[2], concern_group=c[3], photo_detectable=c[4], photo_cues_en=c[5],
                 cosmetic_wording_th=c[6], refer_out_when_en=c[7]) for i, c in enumerate(C.CONCERNS)]
steps = [dict(id=i + 1, slug=s[0], name_en=s[1], name_th=s[2], step_order=s[3], applies_am=s[4], applies_pm=s[5], is_makeup=s[6])
         for i, s in enumerate(C.ROUTINE_STEPS)]
ingredients = [dict(id=i + 1, inci_name=g[0], common_name=g[1], name_th=g[2], ingredient_class=g[3], what_it_does_en=g[4],
                    what_it_does_th=None, evidence_level=g[5], caution_en=g[6], is_uv_filter=g[7], uv_coverage=g[8],
                    is_potential_irritant=g[9], is_fragrance=g[10]) for i, g in enumerate(C.INGREDIENTS)]
interactions = [dict(id=i + 1, class_a=x[0], class_b=x[1], interaction=x[2], advice_en=x[3], advice_th=x[4]) for i, x in enumerate(C.INTERACTIONS)]
st_id = {s["slug"]: s["id"] for s in skin_types}
cn_id = {c["slug"]: c["id"] for c in concerns}
sp_id = {s["slug"]: s["id"] for s in steps}
ing_id = {g["inci_name"].lower(): g["id"] for g in ingredients}


def find_ingredient(label):
    k = re.sub(r"\s+", " ", label.strip().lower()).rstrip(".")
    k = C.INGREDIENT_ALIASES.get(k, k).lower()
    return ing_id.get(k)


# ------------------------------------------------------------------ regex enrichment from official Thai copy
def enrich_from_copy(p):
    d = (p.get("description_th") or "") + " " + (p.get("tagline_th") or "")
    slug = cats[p["category_id"]]["slug"]
    m = re.search(r"(?:คุมมัน|ควบคุมความมัน)[^0-9\n]{0,25}?(\d{1,2})\s*(?:ชั่วโมง|ชม)", d)
    if m:
        p["oil_control_hours_claimed"] = int(m.group(1))
    else:
        p.setdefault("oil_control_hours_claimed", None)
    p["is_water_resistant_claimed"] = 1 if re.search(r"กันน้ำ|waterproof|water[- ]resist", d, re.I) else None
    if slug in ("foundation", "cushion", "concealer", "foundation-powder", "compact-powder", "loose-powder", "primer"):
        if re.search(r"ปกปิด(?:ระดับ)?ปานกลางถึงสูง", d):
            p["coverage"] = "medium_to_full"
        elif re.search(r"ปกปิด(?:ระดับ)?ปานกลาง", d):
            p["coverage"] = "medium"
        elif re.search(r"ปกปิดเนียนขั้นสุด|กลบมิด|ปกปิดสูง|ฟูลคัฟเวอร์|full coverage", d, re.I):
            p["coverage"] = "full"
        elif re.search(r"โปร่งแสง|translucent", d + p["name_en"], re.I):
            p["coverage"] = "sheer"
        n = p["name_en"].lower() + " " + p["name_th"]
        if re.search(r"semi[- ]?matte|เซมิ|กึ่งแมท|ซอฟต์แมตต์", n + d, re.I):
            p["finish"] = "semi_matte"
        elif re.search(r"matte|แมตต์|แมทต์|แมท|oil control|คุมมัน", n, re.I) or re.search(r"เนื้อแมตต์|ลุคแมตต์", d):
            p["finish"] = "matte"
        elif re.search(r"glow|โกลว์|ฉ่ำ", n, re.I):
            p["finish"] = "glowy"
        elif re.search(r"tone ?up|โทน ?อัพ", n, re.I):
            p["finish"] = "tone_up"
    tests = [ln.strip() for ln in (p.get("description_th") or "").split("\n") if re.search(r"จากการทดสอบ|ผ่านการทดสอบ|Dermatologically|tested", ln)]
    if tests:
        p["tested_claims_th"] = " | ".join(dict.fromkeys(tests))[:900]


for p in products:
    p.setdefault("oil_control_hours_claimed", None)
    p.setdefault("is_water_resistant_claimed", None)
    if p["product_type"] == "single":
        enrich_from_copy(p)

# ------------------------------------------------------------------ curated per-product knowledge
heroes, p_concerns, p_skin, p_steps = [], [], [], []
missing = []
for name, cur in C.PRODUCT_CURATION.items():
    p = by_name.get(name)
    if not p:
        missing.append(name)
        continue
    p["summary_en"] = cur["summary"]
    p["texture"] = cur.get("texture")
    if cur.get("finish"):
        p["finish"] = cur["finish"]
    for hero, inci in cur["heroes"]:
        heroes.append(dict(product_id=p["id"], hero_name=hero, ingredient_id=find_ingredient(inci) if inci else None, official_benefit_th=None))
    for slug, rel, basis, why in cur["concerns"]:
        p_concerns.append(dict(product_id=p["id"], concern_id=cn_id[slug], relevance=rel, basis=basis, rationale_en=why))
    for slug, suit, basis in cur["skin"]:
        p_skin.append(dict(product_id=p["id"], skin_type_id=st_id[slug], suitability=suit, basis=basis))
    s = cur["step"]
    p_steps.append(dict(product_id=p["id"], step_id=sp_id[s[0]], use_am=s[1], use_pm=s[2], frequency_en=s[3], usage_note_en=s[4]))
if missing:
    print("!! curation keys without a product:", missing)

# fill official benefit sentence for each hero from the description bullets
for h in heroes:
    p = next(x for x in products if x["id"] == h["product_id"])
    key = re.split(r"[ (]", h["hero_name"])[0].lower()
    for ln in (p.get("description_th") or "").split("\n"):
        if key and key in ln.lower() and len(ln) < 420 and re.search(r"[ก-๙]", ln):
            h["official_benefit_th"] = ln.strip(" •–-")
            break

# ------------------------------------------------------------------ rule-based mappings for makeup & everything not hand-curated
CAT_STEP = {
    "primer": ("primer", 1, 0), "foundation": ("base", 1, 0), "cushion": ("base", 1, 0), "concealer": ("conceal", 1, 0),
    "foundation-powder": ("powder", 1, 0), "compact-powder": ("powder", 1, 0), "loose-powder": ("powder", 1, 0),
    "setting-spray": ("setting-spray", 1, 0), "blush": ("colour", 1, 0), "highlighter": ("colour", 1, 0), "contour": ("colour", 1, 0),
    "eyeshadow": ("colour", 1, 0), "eyebrow": ("colour", 1, 0), "mascara": ("colour", 1, 0),
    "lipstick": ("lips", 1, 0), "liquid-lip": ("lips", 1, 0), "lip-tint": ("lips", 1, 0), "lip-gloss": ("lips", 1, 0), "lip-oil": ("lips", 1, 0),
    "lip-liner": ("lips", 1, 0), "lip-balm": ("lip-care", 1, 1), "lip-scrub": ("lip-care", 0, 1),
    "cleanser": ("cleanse", 1, 1), "makeup-remover": ("makeup-removal", 0, 1), "essence": ("essence", 1, 1), "serum": ("treatment-serum", 1, 1),
    "moisturizer": ("moisturise", 1, 1), "sheet-mask": ("mask", 0, 1), "powder-mask": ("mask", 0, 1), "toner-pad": ("toner-pad", 0, 1),
    "face-sunscreen": ("sunscreen", 1, 0),
}
curated_ids = {x["product_id"] for x in p_steps}
for p in products:
    if p["product_type"] != "single" or p["id"] in curated_ids:
        continue
    slug = cats[p["category_id"]]["slug"]
    if slug in CAT_STEP:
        s = CAT_STEP[slug]
        p_steps.append(dict(product_id=p["id"], step_id=sp_id[s[0]], use_am=s[1], use_pm=s[2], frequency_en=None, usage_note_en=None))
    def add(cslug, rel, basis, why):
        p_concerns.append(dict(product_id=p["id"], concern_id=cn_id[cslug], relevance=rel, basis=basis, rationale_en=why))
    hrs = p.get("oil_control_hours_claimed")
    if slug in ("foundation", "cushion", "foundation-powder", "compact-powder", "loose-powder", "primer"):
        if hrs or p.get("finish") == "matte":
            add("makeup-longevity-oil-control", 3 if hrs and hrs >= 12 else 2, "official_positioning",
                f"Official copy claims {hrs}-hour oil control." if hrs else "Matte-finish positioning.")
            add("excess-sebum-shine", 2, "official_positioning", "Oil-control base/powder.")
            p_skin.append(dict(product_id=p["id"], skin_type_id=st_id["oily"], suitability="ideal", basis="official_positioning"))
            p_skin.append(dict(product_id=p["id"], skin_type_id=st_id["combination"], suitability="ideal", basis="official_positioning"))
        if p.get("coverage") in ("medium_to_full", "full"):
            add("coverage-blemishes", 3, "official_positioning", f"Official copy: {p['coverage'].replace('_', ' ')} coverage.")
        elif p.get("coverage") in ("medium", "sheer"):
            add("natural-everyday-base", 3 if p["coverage"] == "medium" else 2, "official_positioning", f"Official copy: {p['coverage']} coverage.")
        if p.get("spf_value"):
            add("daily-uv-protection", 1, "official_positioning", f"SPF{p['spf_value']} {p.get('pa_rating') or ''} — a top-up, not a replacement for sunscreen.")
    if slug == "concealer":
        add("coverage-blemishes", 3, "site_category", "Concealer.")
        add("under-eye-darkness", 2, "site_category", "Covers under-eye darkness cosmetically.")
    if slug in ("lip-balm", "lip-oil", "lip-scrub"):
        add("lip-dryness", 3, "site_category", "Lip care.")
    if slug == "face-sunscreen":
        add("daily-uv-protection", 3, "site_category", "Sunscreen.")
    n = (p["name_en"] + " " + p["name_th"]).lower()
    if "acne sol" in n or "แอคเน่ โซล" in n:
        add("acne-breakouts", 2, "official_positioning", "SASI Acne Sol line is positioned for blemish-prone skin.")
        p_skin.append(dict(product_id=p["id"], skin_type_id=st_id["acne-prone"], suitability="ideal", basis="official_positioning"))

# de-duplicate composite keys
def dedupe(rows, keys):
    seen, out = set(), []
    for r in rows:
        k = tuple(r[x] for x in keys)
        if k not in seen:
            seen.add(k); out.append(r)
    return out


p_concerns = dedupe(p_concerns, ["product_id", "concern_id"])
p_skin = dedupe(p_skin, ["product_id", "skin_type_id"])
p_steps = dedupe(p_steps, ["product_id", "step_id"])
heroes = dedupe(heroes, ["product_id", "hero_name"])

# ------------------------------------------------------------------ official claims (verbatim bullet lines)
claims = []
for p in products:
    if p["product_type"] != "single":
        continue
    for ln in (p.get("description_th") or "").split("\n"):
        t = ln.strip()
        if not re.match(r"^[•\-–]", t) and not t.startswith("ปราศจาก"):
            continue
        t = t.strip("•–- ").strip()
        if len(t) < 12 or len(t) > 400:
            continue
        if re.search(r"ปราศจาก|free\b", t, re.I):
            ctype = "free_from"
        elif re.search(r"ทดสอบ|tested", t, re.I):
            ctype = "test_result"
        elif re.search(r"technology|เทคโนโลยี|tech\b", t, re.I):
            ctype = "technology"
        elif re.match(r"^[A-Za-z0-9][A-Za-z0-9 &\-\.%/()]{2,60}\s*[:：]?\s*[ก-๙]", t):
            ctype = "ingredient_story"
        else:
            ctype = "benefit"
        claims.append(dict(id=len(claims) + 1, product_id=p["id"], claim_th=t, claim_en=None, claim_type=ctype, source_id=1))

# ------------------------------------------------------------------ full INCI from cited research
product_ingredients = []
inci_report = []
NAME_MAP = {  # research label -> products.name_en
    "Skin Moisture Burst Bi-Phase Cleansing Water": "Skin Moisture Burst Bi-Phase Cleansing Water",
}
SRC_TYPE_ID = {"official": 2, "retailer": 5, "third_party_db": 3}


def resolve_product(label):
    lab = re.sub(r"(?i)\b(srichand|sasi)\b", "", label)
    lab = re.sub(r"\(.*?\)|\d+(\.\d+)?\s*(ml|g)\b|SPF\s*\d+\+?|PA\+*|/", " ", lab, flags=re.I)
    lab = re.sub(r"\s+", " ", lab).strip().lower()
    best, score = None, 0
    import difflib
    for p in products:
        if p["product_type"] != "single":
            continue
        s = difflib.SequenceMatcher(None, lab, p["name_en"].lower()).ratio()
        if s > score:
            best, score = p, s
    return (best, score) if score >= 0.72 else (None, score)


official_inci_done = set()
TABS = json.load(open(ROOT / "research" / "raw" / "official_tabs_2026-09-18.json")) if (ROOT / "research" / "raw" / "official_tabs_2026-09-18.json").exists() else {}


def parse_inci_blocks(text):
    """Official ingredient tabs come in several layouts (wrapped lines, one block per shade group, marketing
    text before the list). Return [(label_or_None, [ingredients...]), ...] for blocks that look like INCI lists."""
    blocks, label, cur = [], None, ""
    def flush():
        nonlocal cur, label
        if cur.strip():
            blocks.append((label, cur.strip()))
        cur = ""
    for ln in [l.strip() for l in text.split("\n") if l.strip()]:
        if ln.count(",") == 0 and len(ln) < 60 and (not cur or cur.rstrip().endswith(".")):
            flush(); label = ln.rstrip(":"); continue
        if ln.count(",") <= 1 and len(ln) < 60 and re.match(r"^[A-Z]?\d{1,3}\b|^(Matte|Shimmer|Glitter)\b", ln) and cur.rstrip().endswith("."):
            flush(); label = ln; continue
        cur += (" " if cur else "") + ln
    flush()
    out = []
    for lab, body in blocks:
        body = re.split(r"(?i)\bmay contain\b|\[\s*\+/-|\(\+/-\)", body)[0]
        body = re.sub(r"(?i)^ingredients?\s*:\s*", "", body).strip().rstrip(".")
        body = re.sub(r"\s*\(and\)\s*", ", ", body)          # raw-material blends written as "A (and) B"
        body = re.sub(r"\s*\((?:Defensil|trade name)[^)]*\)", "", body)
        toks = [x.strip() for x in re.split(r"\s*,\s+|\s*,(?=[A-Za-z(])", body) if x.strip()]
        if len(toks) >= 8 and sum(len(x.split()) > 7 for x in toks) / len(toks) < 0.1 and not re.search(r"[ก-๙]", body[:200]):
            out.append((lab, toks))
    return out


# official pages whose ingredient tab is known to show the WRONG product's list (site data errors found during verification)
INCI_SITE_ERRORS = {"Skin Essential Fine Smooth Foundation SPF50+ PA++++ (legacy version)": "srichand.com shows a POWDER ingredient list on this liquid foundation's page (site data error) — INCI withheld."}
for p in products:
    tab = TABS.get(str(p["id"]))
    if not tab:
        continue
    if p["name_en"] in INCI_SITE_ERRORS:
        p["curation_notes"] = ((p.get("curation_notes") or "") + " " + INCI_SITE_ERRORS[p["name_en"]]).strip()
        if tab.get("howtouse_text"):
            p["how_to_use"] = tab["howtouse_text"][:1500]
        continue
    if tab.get("howtouse_text"):
        p["how_to_use"] = tab["howtouse_text"][:1500]
    else:
        p.setdefault("how_to_use", None)
    if not tab.get("ingredient_text"):
        continue
    blocks = parse_inci_blocks(tab["ingredient_text"])
    if not blocks:
        inci_report.append((p["name_en"], "official tab present but not parseable", 0))
        continue
    lab, toks = blocks[0]
    scope = None
    if len(blocks) > 1 or lab:
        scope = (lab or "first block") + (f" (+{len(blocks) - 1} more shade group(s) on the official page)" if len(blocks) > 1 else "")
    for i, label in enumerate(toks):
        product_ingredients.append(dict(product_id=p["id"], position=i + 1, ingredient_id=find_ingredient(label), inci_as_listed=label,
                                        is_key_active=0, source_id=2, source_url=tab["url"], shade_scope=scope))
    official_inci_done.add(p["id"])
    inci_report.append((p["name_en"], "official tab" + (f" [{scope}]" if scope else ""), len(toks)))
for p in products:
    p.setdefault("how_to_use", None)

for f in sorted(FIND.glob("inci_*.json")):
    data = json.load(open(f))
    for item in data.get("products", []):
        if not item.get("inci_full"):
            inci_report.append((item.get("product_name_en"), "NOT FOUND", 0))
            continue
        p, score = resolve_product(item["product_name_en"])
        if not p:
            inci_report.append((item["product_name_en"], f"unmatched ({score:.2f})", len(item["inci_full"])))
            continue
        if p["id"] in official_inci_done or any(r["product_id"] == p["id"] for r in product_ingredients):
            continue
        sid = SRC_TYPE_ID.get(item.get("inci_source_type"), 3)
        for i, label in enumerate(item["inci_full"]):
            product_ingredients.append(dict(product_id=p["id"], position=i + 1, ingredient_id=find_ingredient(label), inci_as_listed=label.strip(),
                                            is_key_active=0, source_id=sid, source_url=item.get("inci_source_url"), shade_scope=None))
        note = []
        if item.get("sources_agree") is False:
            note.append("INCI sources disagree — see research/findings.")
        if item.get("notes"):
            note.append("INCI note: " + item["notes"][:400])
        if note:
            p["curation_notes"] = ((p.get("curation_notes") or "") + " " + " ".join(note)).strip()
        if item.get("contains_fragrance") is True and p.get("is_fragrance_free") is None:
            p["is_fragrance_free"] = 0
        inci_report.append((item["product_name_en"], f"→ {p['name_en']} ({item.get('inci_source_type')})", len(item["inci_full"])))

frag_ids = {g["id"] for g in ingredients if g["is_fragrance"]}
alc_id = ing_id["alcohol denat."]
by_pid = {}
for r in product_ingredients:
    by_pid.setdefault(r["product_id"], []).append(r)
for p in products:
    rows = by_pid.get(p["id"])
    if not rows:
        continue
    has_frag = any(r["ingredient_id"] in frag_ids or re.search(r"(?i)\b(parfum|fragrance|perfume)\b", r["inci_as_listed"]) for r in rows)
    claimed_free = p.get("is_fragrance_free") == 1
    p["is_fragrance_free"] = 0 if has_frag else 1
    if has_frag and claimed_free:
        p["curation_notes"] = ((p.get("curation_notes") or "") + " CHECK: official copy says fragrance-free but the official INCI lists fragrance.").strip()
    has_alc = any(re.match(r"(?i)^alcohol( denat\.?)?$", r["inci_as_listed"].strip()) for r in rows)
    if has_alc:
        if p.get("is_alcohol_free") == 1:
            p["curation_notes"] = ((p.get("curation_notes") or "") + " CHECK: official copy says alcohol-free but the official INCI lists Alcohol.").strip()
        p["is_alcohol_free"] = 0

KEY_CLASSES = {"bha", "aha", "retinoid", "retinoid_alternative", "vitamin_c", "brightener", "uv_filter", "ceramide", "peptide", "soothing"}
cls = {g["id"]: g["ingredient_class"] for g in ingredients}
for r in product_ingredients:
    if r["ingredient_id"] and cls[r["ingredient_id"]] in KEY_CLASSES:
        r["is_key_active"] = 1

# ------------------------------------------------------------------ range gaps
gaps, gap_concerns = [], []
for i, g in enumerate(C.RANGE_GAPS):
    closest = by_name.get(g["closest"])
    gaps.append(dict(id=i + 1, slug=g["slug"], title_en=g["title"], missing_category=g["missing"], severity=g["severity"],
                     why_it_matters_en=g["why"], closest_in_range_product_id=closest["id"] if closest else None,
                     closest_in_range_limits_en=g["closest_limits"], generic_external_option_en=g["generic_en"],
                     generic_external_option_th=g["generic_th"], commercial_read_en=g["commercial"]))
    for c in g["concerns"]:
        gap_concerns.append(dict(gap_id=i + 1, concern_id=cn_id[c]))

for ln in lines:
    if ln["slug"] in C.LINE_POSITIONING:
        pos, hero = C.LINE_POSITIONING[ln["slug"]]
        ln["positioning_en"] = pos
        ln["hero_ingredients"] = json.dumps(hero, ensure_ascii=False) if hero else None

brands = load("brands")
for b in brands:
    info = C.BRAND_INFO.get(b["slug"])
    if info:
        b.update(info); b["source_id"] = 4
dump("brands", brands)
print("Knowledge seed written:")
dump("products", products)
dump("product_lines", lines)
dump("skin_types", skin_types)
dump("skin_concerns", concerns)
dump("routine_steps", steps)
dump("ingredients", ingredients)
dump("ingredient_interactions", interactions)
dump("product_hero_ingredients", heroes)
dump("product_ingredients", product_ingredients)
dump("product_concerns", p_concerns)
dump("product_skin_types", p_skin)
dump("product_routine_steps", p_steps)
dump("product_claims", claims)
dump("range_gaps", gaps)
dump("range_gap_concerns", gap_concerns)
if "--report" in sys.argv:
    print("\nINCI report:")
    for r in inci_report:
        print("  ", r)
