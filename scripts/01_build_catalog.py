#!/usr/bin/env python3
"""Step 1 — build the REAL catalogue seed files from the srichand.com Store API snapshot.

Input : research/raw/srichand_store_api_{products,variations}_2026-09-18.json.gz
Output: db/seed/{data_sources,brands,product_lines,categories,products,product_variants,
                 site_listings,product_images}.json  +  db/seed/_catalog_index.json (helper for later steps)

Nothing in here is invented: names, SKUs, prices, shades, stock flags, descriptions and images
are copied from the official API. Derived fields (English names from URL slugs, category/line
assignment, shade undertone) are rule-based and documented in docs/data-dictionary.md.
"""
import collections
import difflib
import gzip
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib_normalize import (canonical_key, classify_listing, clean, name_en_from_slug, parse_size,
                           parse_spf, strip_html)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "research" / "raw"
SEED = ROOT / "db" / "seed"
SNAPSHOT_AT = "2026-09-18T11:12:00Z"

P = json.load(gzip.open(RAW / "srichand_store_api_products_2026-09-18.json.gz"))
V = json.load(gzip.open(RAW / "srichand_store_api_variations_2026-09-18.json.gz"))
VAR_BY_PARENT = collections.defaultdict(list)
for v in V:
    VAR_BY_PARENT[v["parent"]].append(v)

# ------------------------------------------------------------------ manual overrides (reviewed by hand)
FORCE_TYPE = {  # listing id -> listing_type
    39481: "set", 39477: "set", 39143: "set", 40231: "set", 40228: "set", 40234: "set",
    31776: "set", 23079: "set", 11579: "set", 27674: "set",
    39989: "duplicate", 39961: "duplicate",          # "(GWP)" twins of Sugar Rush cream blush / lip tint
    17430: "duplicate",                               # "1-free-1" twin of Sunlution Whitening 15 ml
    37563: "duplicate",                               # "[ใหม่]" twin of sasi Jolly Sweet Lip Tint
}
FORCE_KEY = {  # listing id -> canonical key of another listing group
    31932: "ศรีจันทร์เอ็นชานเท็ดคัฟเวอร์เพอร์เฟคท์ฟาวน์เดชั่น",
    26921: "ศรีจันทร์แบร์ทูเพอร์เฟคท์คอร์เรคติ้งคอมแพคพาวเดอร์",
    26915: "ศรีจันทร์แบร์ทูเพอร์เฟคท์คอร์เรคติ้งคอมแพคพาวเดอร์",
    40306: "ศศิโทเมโท่โทนอัพลูสพาวเดอร์",
    39989: "ศศิชูการ์รัชครีมบลัช", 39961: "ศศิชูการ์รัชลิปทินท์", 17430: "ศรีจันทร์ซันลูชั่นสกินไวท์เทนนิ่งซันสกรีน",
    37563: "ศศิจอลลี่สวีทลิปทินท์",
    # 2026 renewal of Skin Essential Fine Smooth is a different formula/label from the legacy SPF versions
    4406: "LEGACY:ศรีจันทร์สกินเอสเซ็นเชียลไฟน์สมูทฟาวน์เดชั่น", 10988: "LEGACY:ศรีจันทร์สกินเอสเซ็นเชียลไฟน์สมูทฟาวน์เดชั่น",
    4404: "LEGACY:ศรีจันทร์สกินเอสเซ็นเชียลไฟน์สมูทฟาวน์เดชั่นพาวเดอร์", 4405: "LEGACY:ศรีจันทร์สกินเอสเซ็นเชียลไฟน์สมูทฟาวน์เดชั่นพาวเดอร์",
}
NAME_EN_OVERRIDE = {  # canonical key -> English name (where the URL slug is unhelpful)
    "LEGACY:ศรีจันทร์สกินเอสเซ็นเชียลไฟน์สมูทฟาวน์เดชั่น": "Skin Essential Fine Smooth Foundation SPF50+ PA++++ (legacy version)",
    "LEGACY:ศรีจันทร์สกินเอสเซ็นเชียลไฟน์สมูทฟาวน์เดชั่นพาวเดอร์": "Skin Essential Fine Smooth Foundation Powder SPF35 PA+++ (legacy version)",
    "ศรีจันทร์แบร์ทูเพอร์เฟคท์คอร์เรคติ้งคอมแพคพาวเดอร์": "Bare to Perfect Correcting Compact Powder",
}
NAME_EN_BY_LISTING = {  # any listing id in the group -> clean English product name
    40513: "Skin Essential Fine Smooth Foundation", 40297: "Girls Can 3-in-1 Tone Up & Primer Sunscreen",
    40292: "Acne Sol Comfort Matte Concealer", 39934: "Sugar Rush Lip Tint", 39566: "Whitening Moisture Toner Pad",
    39563: "Acne Sol Calming Toner Pad", 39139: "Super C Brightening 15X Ampoule Mask", 39136: "Skin Moisture Burst 15X Ampoule Mask",
    38339: "Magic Matte Foundation Powder", 37535: "Snowy Dreams Cheek Palette",
    36228: "Phyto Camellia PDRN Bright Glowing Cleansing Gel Foam", 34867: "All Day Fix Fixing Spray",
    34802: "All Day Fix Translucent Setting Compact Powder", 5696: "All Day Fix Translucent Setting Powder",
    33609: "Masterpiece Me Color Symphony Multi Palette", 33570: "Masterpiece Me Watercolor Liquid Blush",
    29212: "Good Day Color & Care SPF30 PA+++ Lip Serum", 5678: "Good Day Color & Care SPF30 PA+++ Lip Balm",
    27645: "BamBam x SRICHAND Pure Kiss Brightening Lip Balm", 27669: "BamBam x SRICHAND First Kiss Plumping Lip Balm",
    27469: "Perfect Personal Color Gloss Stick", 27508: "Perfect Personal Color Eyeshadow Palette", 25008: "Wonder Glow Lip Oil",
    21867: "Kiss & Contour Stick", 21861: "Kiss & Highlighter Stick", 5685: "Kiss & Blush Stick",
    12339: "Super Fix 18H Oil Control Foundation Powder", 4376: "Super C Brightening Intense Serum",
    10596: "Rise & Shine Plumping Lipstick", 10595: "Rise & Shine Moji Blush", 10594: "Rise & Shine Semi Matte Cushion",
    10593: "Rise & Shine Perfect Eyebrow Auto Pencil", 9331: "Peace & Love Watery Lip Tint", 5687: "Sugar Rush Lip Tint Vol.2",
    5684: "Girls Can Be Unique Eyeshadow Palette", 5675: "Baby Powder", 5674: "Baby Newborn Powder",
    4411: "Gel Blush pH Cheek & Lip", 4410: "Translucent Finish Powder", 4364: "Timeless Anti-Aging Facial Serum",
    24058: "Resurface Pro-Retinol Intense Serum", 29242: "Advanced Anti-Melasma Serum", 9302: "Skin Moisture Burst Bi-Phase Cleansing Water",
    25092: "Acne Sol 2-in-1 Double Cleansing Gel", 5691: "Pretty Easy Perfect Eyebrow Pencil", 8270: "Brow To Be Auto Pencil",
    4412: "Feelin' Me Matte Liquid Lip – Summer Garden Collection", 4396: "Feelin' Me Matte Liquid Lip", 30192: "Floral Hya Lip Gel",
    4413: "Hya Colla Lip Tint", 5688: "Sun Cool Loose Powder", 5689: "Super Oil Control Powder", 5690: "BB Perfect Powder", 5692: "Pearly Glow Powder",
    # clearance-only products
    36824: "Roses All Around Deep Matte Lipstick", 36810: "Sunlution Perfect UV Protection Milk", 33914: "Luminescence Fabulous UV Shield",
    33910: "Black Edition Oil Control Powder", 17821: "Roses All Around Hot Cheek Blush Palette",
    18300: "Skin Refining Micellar Cleansing Water (Japan series)", 18244: "Skin Essential Compact Powder",
    18203: "Skinlution Hydrating", 18202: "Skinlution Anti-Aging", 18201: "Skinlution Acne Care",
    18075: "Roses All Around Endless Lash Mascara", 17904: "Mojo Bar Liquid Contour",
}
CAT_BY_LISTING = {33570: "blush", 5698: "compact-powder", 5689: "loose-powder", 4394: "brush-accessory", 36824: "lipstick",
                  32132: "lipstick", 10596: "lipstick", 33609: "eyeshadow", 4411: "blush"}
CLR_KEY_OVERRIDE = {33914: "CLR:luminescence", 17860: "CLR:luminescence", 17859: "CLR:luminescence", 17742: "CLR:luminescence"}
# clearance lots the fuzzy matcher cannot place: clearance listing id -> a regular listing id of the same product
CLEARANCE_TO = {36825: 10599, 17907: 31907, 17875: 5685, 18067: 4376, 17978: 5684, 33900: 29212, 17965: 5678,
                36823: 4378, 36816: 27508, 36814: 27469, 17873: 40297, 18080: 4404}
# hidden-but-real single units worth keeping (parent listing is unpublished but the SKU is live in the API)
HIDDEN_VARIANT_PARENTS = {4373: "ศรีจันทร์ซันลูชั่นแอคเน่แคร์ซันสกรีน"}   # Sunlution Acne Care 40 ml single

# ------------------------------------------------------------------ brand / line / category rules
BRANDS = [
    dict(id=1, slug="srichand", name_en="SRICHAND", name_th="ศรีจันทร์", price_tier="mass",
         site_url="https://srichand.com/brand/srichand/"),
    dict(id=2, slug="sasi", name_en="SASI", name_th="ศศิ", price_tier="value",
         site_url="https://srichand.com/brand/sasi/"),
    dict(id=3, slug="srichand-baby", name_en="SRICHAND Baby", name_th="ศรีจันทร์ เบบี้", price_tier="value",
         site_url="https://srichand.com/product-category/srichand-baby/"),
]

# (slug, brand, name_en, name_th, domain, [keywords th/en — matched against "name_th || name_en" lower-cased])
LINES = [
    ("sunlution", 1, "Sunlution", "ซันลูชั่น", "sunscreen", ["ซันลูชั่น", "sunlution", "perfect uv protection"]),
    ("luminescence-uv", 1, "Luminescence Fabulous UV Shield", "ลูมิเนสเซนส์", "sunscreen", ["luminescence", "ลูมิเนสเซนส์"]),
    ("skin-moisture-burst", 1, "Skin Moisture Burst", "สกิน มอยส์เจอร์ เบิร์ส", "skincare", ["สกิน มอยส์เจอร์ เบิร์ส", "สกินมอยส์เจอร์", "skin moisture burst"]),
    ("barrier-boost", 1, "Barrier Boost", "แบริเออร์ บูสต์", "skincare", ["แบริเออร์ บูส", "barrier boost"]),
    ("phyto-camellia-pdrn", 1, "Phyto Camellia PDRN Bright Glowing", "ไฟโต คามิลเลีย พีดีอาร์เอ็น", "skincare", ["ไฟโต คามิลเลีย", "phyto camellia"]),
    ("super-c", 1, "Super C Brightening", "ซุปเปอร์ ซี ไบร์ทเทนนิ่ง", "skincare", ["ซุปเปอร์ ซี", "super c "]),
    ("resurface", 1, "Resurface Pro-Retinol", "รีเซอร์เฟส", "skincare", ["รีเซอร์เฟส", "resurface"]),
    ("timeless", 1, "Timeless Anti-Aging", "ไทม์เลส", "skincare", ["ไทม์เลส", "timeless"]),
    ("advanced-anti-melasma", 1, "Advanced Anti-Melasma", "แอดวานซ์ แอนตี้ เมลาสม่า", "skincare", ["เมลาสม่า", "melasma"]),
    ("skinlution", 1, "Skinlution", "สกินลูชั่น", "skincare", ["สกินลูชั่น", "skinlution"]),
    ("skin-refining", 1, "Skin Refining (Japan series)", None, "skincare", ["skin refining"]),
    ("bare-to-perfect", 1, "Bare to Perfect", "แบร์ ทู เพอร์เฟคท์", "powder", ["แบร์ ทู เพอร์เฟค", "แบร์ทูเพอเฟค", "bare to perfect"]),
    ("translucent-powder", 1, "Translucent Powder (heritage)", "ทรานส์ลูเซนท์ พาวเดอร์", "powder", ["ทรานส์ลูเซนท์", "translucent"]),
    ("skin-essential", 1, "Skin Essential", "สกิน เอสเซ็นเชียล", "base_makeup", ["สกิน เอสเซ็นเชียล", "skin essential"]),
    ("super-coverage", 1, "Super Coverage Always Matte", "ซูเปอร์ คัฟเวอเรจ", "base_makeup", ["ซูเปอร์ คัฟเวอเรจ", "super coverage"]),
    ("skin-booster", 1, "Skin Booster Flawless", "สกิน บูสเตอร์", "base_makeup", ["สกิน บูสเตอร์", "skin booster"]),
    ("enchanted", 1, "Enchanted", "เอ็นชานเท็ด", "base_makeup", ["เอ็นชานเท็ด", "เอนชานท์เท็ด", "enchanted"]),
    ("super-fix", 1, "Super Fix 18H", "ซูเปอร์ ฟิกซ์", "powder", ["ซูเปอร์ ฟิกซ์", "super fix"]),
    ("porefect", 1, "Porefect Skin Primer", "พอร์เฟกต์ สกิน", "base_makeup", ["พอร์เฟกต์ สกิน", "porefect"]),
    ("rise-and-shine", 1, "Rise & Shine", "ไรซ์ แอนด์ ไชน์", "colour_makeup", ["ไรซ์ แอนด์ ไชน์", "rise & shine", "rise &amp; shine"]),
    ("masterpiece-me", 1, "Masterpiece Me", "มาสเตอร์พีซ มี", "colour_makeup", ["มาสเตอร์พีซ", "masterpiece"]),
    ("snowy-dreams", 1, "Snowy Dreams", "สโนวี ดรีม", "colour_makeup", ["สโนวี ดรีม", "snowy dream"]),
    ("roses-all-around", 1, "Roses All Around", None, "colour_makeup", ["roses all around"]),
    ("bambam", 1, "SRICHAND x BamBam", "แบมแบม x ศรีจันทร์", "lip", ["แบมแบม", "bambam"]),
    ("day-to-glow", 1, "Day to Glow", "เดย์ ทู โกลว์", "lip", ["เดย์ ทู โกลว์", "day to glow"]),
    ("feelin-me", 1, "Feelin' Me", "ฟีลลิน มี", "lip", ["ฟิลลิน มี", "ฟีลลิน มี", "feelin"]),
    ("srichand-lips", 1, "Srichand Lip Colour & Care", None, "lip", ["จูซซี่ ไซรัป", "juicy syrup", "ไฮยา ลิป", "hya lip", "ไฮยา คอลลา", "hya colla", "ลิป บาล์ม เอ็มยู", "lip balm mu"]),
    ("srichand-classics", 1, "Srichand Classics", None, "powder", ["ออริจินัล พาวเดอร์", "black edition", "แบล็ค อิดิชั่น", "bright & bloom", "bright &amp; bloom", "ไบรท์ แอนด์ บลูม", "แฮร์ พาวเดอร์", "gel blush", "เจล บลัช"]),
    ("srichand-tools", 1, "Tools & Accessories", None, "tools", ["บรัช", "brush", "กระเป๋า", "bag"]),
    ("baby", 3, "Srichand Baby", "ศรีจันทร์ เบบี้", "baby", ["เบบี้ พาวเดอร์", "เบบี้ นิวบอร์น", "baby powder", "baby baby"]),
    ("acne-sol", 2, "Acne Sol", "แอคเน่ โซล", "mixed", ["แอคเน่ โซล", "acne sol"]),
    ("girls-can", 2, "Girls Can", "เกิร์ล แคน", "mixed", ["เกิร์ล แคน", "girls can"]),
    ("magic-matte", 2, "Magic Matte", "เมจิก แมท", "base_makeup", ["เมจิก แมท", "magic matte"]),
    ("sugar-rush", 2, "Sugar Rush", "ชูการ์ รัช", "colour_makeup", ["ชูการ์ รัช", "sugar rush"]),
    ("perfect-personal-color", 2, "Perfect Personal Color", "เพอร์เฟกต์ เพอร์ซันนอล คัลเลอร์", "colour_makeup", ["เพอร์ซันนอล คัลเลอร์", "personal color"]),
    ("mojo-bar", 2, "Mojo Bar", "โมโจ บาร์", "colour_makeup", ["โมโจ บาร์", "mojo bar"]),
    ("all-day-fix", 2, "All Day Fix", "ออล เดย์ ฟิกซ์", "powder", ["ออล เดย์ ฟิกซ์", "all day fix"]),
    ("tomato-tone-up", 2, "Tomato Tone Up", "โทเมโท่ โทน อัพ", "powder", ["โทเมโท่", "tomato"]),
    ("kiss-and", 2, "Kiss & Stick", "คิส แอนด์", "colour_makeup", ["คิส แอนด์", "kiss &", "kiss &amp;"]),
    ("good-day-good-night", 2, "Good Day / Good Night Lip Care", None, "lip", ["กู๊ด เดย์", "กู๊ด ไนท์", "good day", "good night"]),
    ("sasi-toner-pads", 2, "Toner Pads", None, "skincare", ["โทนเนอร์ แพด", "โทเนอร์ แพด", "toner pad"]),
    ("sasi-loose-powder", 2, "SASI Loose & Compact Powders", None, "powder", ["ซัน คูล", "ซูเปอร์ ออยล์ คอนโทรล", "บีบี เพอร์เฟค", "เพิร์ลลี่ โกลว์", "ชายนิ่ง สตาร์", "shining star"]),
    ("sasi-brows", 2, "SASI Brows", None, "colour_makeup", ["บราวทูบี", "พริตตี้ อีซี่"]),
    ("sasi-lips", 2, "SASI Lip Colour", None, "lip", ["คลิกกี้", "clicky", "คัดเดิ้ล", "cuddle", "จอลลี่", "jolly", "ซุปเปอร์สตาร์", "superstar", "อะโฮลิค", "aholic", "วันเดอร์ โกลว์", "wonder glow", "พีซ แอนด์ เลิฟ", "peace", "ฟรุ้ตตี้", "เดลี่ ทินท์เต็ด"]),
]

# (slug, parent_slug, name_en, name_th, [keywords], sort) — ordered most-specific first for matching
CATS = [
    ("skincare", None, "Skincare", "ผลิตภัณฑ์ดูแลผิวหน้า", [], 10),
    ("sunscreen", None, "Sunscreen", "ครีมกันแดด", [], 20),
    ("powder", None, "Powder", "แป้ง", [], 30),
    ("base-makeup", None, "Base Makeup", "ผลิตภัณฑ์รองพื้น", [], 40),
    ("colour-makeup", None, "Colour Makeup", "ตกแต่งผิวหน้า", [], 50),
    ("lip", None, "Lip", "ผลิตภัณฑ์ตกแต่งริมฝีปาก", [], 60),
    ("baby-care", None, "Baby Care", "ผลิตภัณฑ์สำหรับเด็ก", [], 70),
    ("hair", None, "Hair", "ผลิตภัณฑ์สำหรับผม", [], 80),
    ("tools", None, "Tools & Accessories", "อุปกรณ์", [], 90),
    ("sets", None, "Sets & Bundles", "เซต", [], 100),
    ("gifts", None, "Gifts with Purchase", "ของแถม", [], 110),
    # children — matched in this order
    ("face-sunscreen", "sunscreen", "Face Sunscreen", "กันแดดสำหรับผิวหน้า", ["ซันสกรีน", "sunscreen", "กันแดด", "uv shield", "uv protection", "uv มิลค์"], 21),
    ("makeup-remover", "skincare", "Makeup Remover", "ลบเครื่องสำอาง", ["คลีนซิ่ง วอเตอร์", "cleansing water", "micellar"], 12),
    ("cleanser", "skincare", "Cleanser", "ทำความสะอาดผิวหน้า", ["คลีนซิ่ง เจล", "cleansing gel", "เจล โฟม", "gel foam"], 11),
    ("sheet-mask", "skincare", "Sheet Mask", "ชีทมาส์ก", ["แอมพูล มาส์ก", "ampoule mask"], 16),
    ("powder-mask", "skincare", "Powder Mask", "ผงมาส์กหน้า", ["พาวเดอร์ มาส์ก", "powder mask"], 17),
    ("toner-pad", "skincare", "Toner Pad", "โทนเนอร์แพด", ["โทนเนอร์ แพด", "toner pad"], 18),
    ("lip-scrub", "lip", "Lip Scrub", "ลิปสครับ", ["ลิป สครับ", "lip scrub"], 68),
    ("lip-balm", "lip", "Lip Balm & Care", "ลิปมัน / บำรุง", ["ลิป บาล์ม", "ลิปบาล์ม", "lip balm", "ลิป เซรั่ม", "lip serum", "ไฮเดรติ้ง ลิป", "hydrating lip", "ลิป เจล", "lip gel", "ทินท์ บาล์ม", "tint balm", "color & care", "คัลเลอร์ แอนด์ แคร์"], 66),
    ("lip-oil", "lip", "Lip Oil", "ลิปออยล์", ["ลิป ออย", "lip oil"], 65),
    ("lip-liner", "lip", "Lip Liner", "ลิปไลเนอร์", ["ลิป ไลเนอร์", "lip liner", "สเกตช์ลิป"], 67),
    ("lip-tint", "lip", "Lip Tint", "ลิปทินท์", ["ลิป ทินท์", "lip tint", "ลาสติ้ง ลิป", "lasting lip", "วอเทอร์คัลเลอร์"], 63),
    ("liquid-lip", "lip", "Liquid / Matte Lip", "ลิปจิ้มจุ่ม", ["ลิควิด ลิป", "liquid lip", "แมท ลิป", "matte lip", "พุดดิ้ง ลิป", "pudding lip"], 62),
    ("lip-gloss", "lip", "Lip Gloss", "ลิปกลอส", ["กลอส", "gloss"], 64),
    ("lipstick", "lip", "Lipstick", "ลิปสติกแท่ง", ["ลิปสติก", "lipstick"], 61),
    ("serum", "skincare", "Serum", "เซรั่ม", ["เซรั่ม", "serum", "skinlution", "สกินลูชั่น"], 14),
    ("essence", "skincare", "Essence", "เอสเซนส์ / น้ำตบ", ["เอสเซนส์", "essence"], 13),
    ("moisturizer", "skincare", "Moisturiser / Gel Cream", "มอยเจอร์ไรเซอร์ / เจลครีม", ["เจล ครีม", "gel cream"], 15),
    ("setting-spray", "base-makeup", "Setting Spray", "สเปรย์ล็อกเมคอัพ", ["ฟิกซิ่ง สเปรย์", "fixing spray"], 46),
    ("cushion", "base-makeup", "Cushion", "คุชชั่น", ["คุชชั่น", "cushion"], 43),
    ("concealer", "base-makeup", "Concealer", "คอนซีลเลอร์", ["คอนซีลเลอร์", "concealer"], 44),
    ("primer", "base-makeup", "Primer", "ไพรเมอร์", ["ไพร์เมอร์", "primer"], 41),
    ("baby-powder", "baby-care", "Baby Powder", "แป้งเด็ก", ["เบบี้ พาวเดอร์", "เบบี้ นิวบอร์น", "baby powder", "baby baby"], 71),
    ("hair-powder", "hair", "Hair Powder", "แป้งสำหรับผม", ["แฮร์ พาวเดอร์", "hair powder"], 81),
    ("foundation-powder", "powder", "Foundation Powder (compact)", "แป้งผสมรองพื้น", ["ฟาวน์เดชั่น พาวเดอร์", "ฟาวน์เดชั่น ลูส พาวเดอร์", "foundation powder", "foundation loose powder"], 33),
    ("compact-powder", "powder", "Compact / Pressed Powder", "แป้งอัดแข็ง", ["คอมแพค", "compact", "ฟินนิช พาวเดอร์", "finish powder", "skincare powder", "สกินแคร์ พาวเดอร์", "oil control powder", "ออย คอนโท พาวเดอร์"], 32),
    ("loose-powder", "powder", "Loose Powder", "แป้งฝุ่น", ["ลูส พาวเดอร์", "loose powder", "ทรานส์ลูเซนท์ พาวเดอร์", "translucent powder", "พาวเดอร์ (50", "เซ็ตติ้ง พาวเดอร์", "คอมฟอร์ท พาวเดอร์"], 31),
    ("foundation", "base-makeup", "Foundation", "รองพื้น", ["ฟาวน์เดชั่น", "foundation"], 42),
    ("blush", "colour-makeup", "Blush", "บลัชออน", ["บลัช", "blush", "ชีค พาเลต", "cheek"], 51),
    ("highlighter", "colour-makeup", "Highlighter", "ไฮไลท์เตอร์", ["ไฮไลท์", "highlighter"], 52),
    ("contour", "colour-makeup", "Contour", "คอนทัวร์", ["คอนทัวร์", "contour"], 53),
    ("eyebrow", "colour-makeup", "Eyebrow", "ดินสอเขียนคิ้ว", ["อายโบรว์", "eyebrow", "เขียนคิ้ว"], 55),
    ("mascara", "colour-makeup", "Mascara", "มาสคาร่า", ["mascara", "มาสคาร่า"], 56),
    ("eyeshadow", "colour-makeup", "Eyeshadow", "อายแชโดว์", ["อายแชโดว์", "eyeshadow", "มัลติพาเลท"], 54),
    ("brush-accessory", "tools", "Brushes & Accessories", "แปรงและอุปกรณ์", ["บรัช", "brush"], 91),
    ("product-set", "sets", "Product Set", "เซตผลิตภัณฑ์", [], 101),
    ("gwp", "gifts", "Gift with Purchase", "ของแถม", [], 111),
    ("gift-card", "gifts", "Gift Card", "บัตรของขวัญ", ["gift card"], 112),
]


def match_first(text, table, kw_index):
    t = text.lower()
    for row in table:
        for kw in row[kw_index]:
            if kw.lower() in t:
                return row[0]
    return None


# ------------------------------------------------------------------ pass 1: classify + group
listings = []
for x in P:
    c = classify_listing(x["name"])
    ltype = FORCE_TYPE.get(x["id"], c["listing_type"])
    key = FORCE_KEY.get(x["id"]) or canonical_key(x["name"])
    listings.append(dict(raw=x, ltype=ltype, qty=c["pack_qty"], is_bogo=c["is_bogo"], key=key))

groups = collections.OrderedDict()   # canonical key -> product dict


def brand_of(x):
    slugs = [b["slug"] for b in x["brands"]]
    n = clean(x["name"]).lower()
    if any(k in n for k in ["เบบี้ พาวเดอร์", "เบบี้ นิวบอร์น", "baby baby", "srichand baby"]):
        return 3
    if "sasi" in slugs or "ศศิ" in n or re.search(r"\bsasi\b", n):
        return 2
    return 1


def primary_rank(l):  # which listing supplies the product's descriptive copy
    return ({"regular": 0, "sachet_box": 1, "multipack": 2, "duplicate": 3}.get(l["ltype"], 9), -len(l["raw"]["description"]))


for l in listings:
    if l["ltype"] in ("regular", "sachet_box", "multipack", "duplicate"):
        groups.setdefault(l["key"], dict(key=l["key"], listings=[], kind="single"))["listings"].append(l)
    elif l["ltype"] == "set":
        groups[f"SET:{l['raw']['id']}"] = dict(key=f"SET:{l['raw']['id']}", listings=[l], kind="set")
    elif l["ltype"] == "gift":
        groups[f"GIFT:{l['raw']['id']}"] = dict(key=f"GIFT:{l['raw']['id']}", listings=[l], kind="gift")

# ------------------------------------------------------------------ pass 2: clearance -> canonical (fuzzy on English names)
def en_tokens(s):
    s = clean(s).lower()
    s = re.sub(r"\[clearance\]|case\s*\d+|\(c\d+\)|c\d{2,3}\b|\bth\b|re-aw|re-pkg|sachet|watsons?|7-11|nationwide|exclusive barcode|japan series|bogo on pack|\(.*?\)|–|-", " ", s)
    s = re.sub(r"\d+(\.\d+)?\s*(ml|g)\b\.?", " ", s)
    s = re.sub(r"spf\s*\d+\+?|pa\+*", " ", s)
    s = re.sub(r"[^a-z0-9& ]", " ", s)
    return [w for w in s.split() if w not in ("srichand", "sasi", "the", "with", "x")]


for g in groups.values():
    prim = sorted(g["listings"], key=primary_rank)[0]
    g["primary"] = prim
    g["name_en_auto"] = NAME_EN_OVERRIDE.get(g["key"]) or name_en_from_slug(prim["raw"]["slug"])

single_groups = [g for g in groups.values() if g["kind"] == "single"]
clearance_report = []
for l in listings:
    if l["ltype"] != "clearance":
        continue
    toks = en_tokens(l["raw"]["name"])
    best, best_score = None, 0.0
    if l["raw"]["id"] in CLEARANCE_TO:
        tgt = next(t for t in listings if t["raw"]["id"] == CLEARANCE_TO[l["raw"]["id"]])
        best, best_score = groups[tgt["key"]], 1.0
    for g in ([] if best else single_groups):
        if g.get("clearance_only"):
            continue
        if brand_of(g["primary"]["raw"]) != brand_of(l["raw"]) and brand_of(l["raw"]) != 3:
            continue
        gt = en_tokens(g["name_en_auto"])
        score = difflib.SequenceMatcher(None, " ".join(sorted(toks)), " ".join(sorted(gt))).ratio()
        inter = len(set(toks) & set(gt)) / max(1, len(set(toks) | set(gt)))
        score = 0.5 * score + 0.5 * inter
        if score > best_score:
            best, best_score = g, score
    if best is not None and best_score >= 0.80:
        best["listings"].append(l)
        l["key"] = best["key"]
        clearance_report.append((round(best_score, 2), clean(l["raw"]["name"]), "→", best["name_en_auto"]))
    else:
        # clearance-only product: group clearance lots of the same product together
        ck = CLR_KEY_OVERRIDE.get(l["raw"]["id"]) or "CLR:" + " ".join(toks)
        if ck not in groups:
            groups[ck] = dict(key=ck, listings=[], kind="single", clearance_only=True,
                              name_en_auto=" ".join(w.capitalize() if not w.isupper() else w for w in
                                                    re.sub(r"\s+", " ", re.sub(r"\[Clearance\]|Case\s*\d+.*$|\(C\d+\).*$|\bTH\b.*$|\(Re-.*$", "", clean(l["raw"]["name"]))).strip().split(" ")))
            single_groups.append(groups[ck])
        groups[ck]["listings"].append(l)
        groups[ck]["primary"] = groups[ck]["listings"][0]
        l["key"] = ck
        clearance_report.append((round(best_score, 2), clean(l["raw"]["name"]), "✗ clearance-only", best["name_en_auto"] if best else ""))

# ------------------------------------------------------------------ pass 3: emit rows
line_id = {row[0]: i + 1 for i, row in enumerate(LINES)}
cat_id = {row[0]: i + 1 for i, row in enumerate(CATS)}
SRC_API = 1

products, variants, site_rows, images = [], [], [], []
seen_sku = set()
pid_counter = 0
vid_counter = 0


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s


def parse_variation(v):
    """'Color: 130 Honey' -> shade; 'Size: 30ml' -> ignored (size comes from the listing name)."""
    shade_code = shade_name = None
    for part in clean(v.get("variation") or "").split(", "):
        if ":" not in part:
            continue
        k, val = [t.strip() for t in part.split(":", 1)]
        if k in ("Color", "Model") and not re.search(r"ชิ้น|กล่อง|ซอง|^\d+\s*(ml|g)", val):
            m = re.match(r"^([A-Za-z]{0,2}\d{1,3}[A-Za-z]?)\s+(.+)$", val)
            if m:
                shade_code, shade_name = m.group(1), m.group(2)
            else:
                shade_name = val
    return shade_code, shade_name


def undertone(code, name):
    n = (name or "").lower()
    c = (code or "").upper()
    if re.match(r"^P\d", c) or "pink" in n or "พิงก์" in n or "ชมพู" in n or "rose" in n:
        return "cool_pink"
    if re.match(r"^Y\d", c):
        return "warm_yellow"
    if re.match(r"^N\d", c):
        return "neutral"
    if "honey" in n or "ฮันนี่" in n or "golden" in n or "โกลเด้น" in n:
        return "warm_golden"
    if "peach" in n or "พีช" in n:
        return "peach"
    return None


SHADE_CATS = {"foundation", "cushion", "concealer", "foundation-powder", "compact-powder", "loose-powder"}

for g in groups.values():
    prim = g["primary"]
    x = prim["raw"]
    pid_counter += 1
    pid = pid_counter
    g["product_id"] = pid
    name_th = clean(x["name"])
    name_th_clean = re.sub(r"^(\[[^\]]+\]\s*)+", "", name_th)
    name_th_clean = re.sub(r"\s*SRICHAND Phyto.*$", "", name_th_clean)
    if g["kind"] == "single" and not g.get("clearance_only"):
        name_th_clean = re.sub(r"\s*\((?:\s*\d+(\.\d+)?\s*(มล|ก|g|ml)\.?\s*)\)\s*(New)?$", "", name_th_clean).strip()
        name_th_clean = re.sub(r"\s*\d+(\.\d+)?\s*(มล|ก)\.?$", "", name_th_clean).strip()
    name_en = g["name_en_auto"]
    gl_ids = [l["raw"]["id"] for l in g["listings"]]
    for lid in gl_ids:
        if lid in NAME_EN_BY_LISTING:
            name_en = NAME_EN_BY_LISTING[lid]
    hay = f"{name_th} || {name_en}"
    brand = brand_of(x)
    if g["kind"] == "set":
        cslug, ptype = "product-set", "set"
        name_en = "Set: " + (name_en_from_slug(x["slug"]) or name_th_clean)
    elif g["kind"] == "gift":
        cslug = "gift-card" if "gift card" in hay.lower() else "gwp"
        ptype = "gift_card" if cslug == "gift-card" else "gift_with_purchase"
        name_en = "GWP: " + re.sub(r"^ฟรี\s*", "", name_th_clean)
    else:
        cslug = match_first(hay, [r for r in CATS if r[1]], 4) or "loose-powder"
        for lid in gl_ids:
            cslug = CAT_BY_LISTING.get(lid, cslug)
        ptype = "accessory" if cslug == "brush-accessory" else "single"
    lslug = match_first(hay, [r for r in LINES if r[1] == brand], 5)
    spf, pa = parse_spf(name_th)
    regular_listings = [l for l in g["listings"] if l["ltype"] in ("regular", "sachet_box", "multipack", "duplicate", "set", "gift")]
    if g.get("clearance_only"):
        lifecycle = "clearance_only"
    elif g["key"].startswith("LEGACY:") or not any(l["raw"]["is_in_stock"] for l in regular_listings):
        lifecycle = "legacy" if g["key"].startswith("LEGACY:") else "active"
    else:
        lifecycle = "active"
    desc = strip_html(x["description"])
    free_from = []
    dl = desc.lower()
    for token, tag in [("พาราเบน", "paraben"), ("paraben", "paraben"), ("มิเนอรัล ออยล์", "mineral_oil"), ("mineral oil", "mineral_oil"),
                       ("ซิลิโคน", "silicone"), ("สารแต่งสี", "colourant"), ("สารแต่สี", "colourant"), ("น้ำหอม", "fragrance"),
                       ("fragrance free", "fragrance"), ("แอลกอฮอล์", "alcohol"), ("alcohol free", "alcohol"), ("ซัลเฟต", "sulfate"), ("talc free", "talc")]:
        if token in dl and re.search(r"(ปราศจาก|free)", dl):
            seg = re.search(r"(ปราศจาก[^\n]*|[^\n]*\bfree\b[^\n]*)", dl)
            if seg and token in seg.group(0) and tag not in free_from:
                free_from.append(tag)
    products.append(dict(
        id=pid, brand_id=brand, line_id=line_id.get(lslug), category_id=cat_id[cslug],
        slug=slugify(f"{BRANDS[brand-1]['slug']}-{name_en}")[:90] or f"product-{pid}",
        name_en=name_en, name_th=name_th_clean, product_type=ptype, lifecycle_status=lifecycle,
        tagline_th=strip_html(x["short_description"]) or None, description_th=desc or None, summary_en=None,
        texture=None, finish=None, coverage=None, spf_value=spf, pa_rating=pa,
        free_from=json.dumps(free_from) if free_from else None,
        is_fragrance_free=(1 if "fragrance" in free_from else None), is_alcohol_free=(1 if "alcohol" in free_from else None),
        tested_claims_th=None, official_url=x["permalink"], image_url=(x["images"][0]["src"] if x["images"] else None),
        review_count_site=x.get("review_count") or 0,
        average_rating_site=(float(x["average_rating"]) if x.get("average_rating") and float(x["average_rating"]) > 0 else None),
        source_id=SRC_API, confidence="official", verified_at=SNAPSHOT_AT, curation_notes=None))
    for i, im in enumerate(x["images"][:6]):
        images.append(dict(id=len(images) + 1, product_id=pid, url=im["src"], alt_text=clean(im.get("alt") or "") or None, sort_order=i))

    # shade guidance lines from the official description, e.g. "110 SAND ผิวสีเนื้อโทนชมพู"
    guidance = {}
    for line in desc.split("\n"):
        m = re.match(r"^\s*([A-Z]{0,2}\d{2,3})\s+[A-Za-z][A-Za-z ]+.*?((?:เหมาะ|ผิว).+)$", line.strip())
        if m:
            guidance[m.group(1)] = line.strip()

    for l in g["listings"]:
        lx = l["raw"]
        if l["ltype"] in ("clearance", "duplicate") and not g.get("clearance_only"):
            continue                                    # duplicates of an existing canonical product: keep only in site_listings
        size_v, size_u = parse_size(lx["name"])
        for v in VAR_BY_PARENT.get(lx["id"], []):
            sku = v["sku"] or f"SITE-{v['id']}"
            if sku in seen_sku:
                continue
            seen_sku.add(sku)
            vid_counter += 1
            code, sname = parse_variation(v)
            reg = int(v["prices"]["regular_price"]) / 100
            cur = int(v["prices"]["price"]) / 100
            if l["ltype"] == "sachet_box":
                fmt, units = "sachet_box", 6
            elif l["ltype"] == "multipack":
                fmt, units = "multipack", l["qty"]
                mt = re.search(r"รวม\s*(\d+)\s*ซอง", clean(lx["name"]))
                if mt:
                    units = int(mt.group(1))
            elif g["kind"] == "set":
                fmt, units = "set", 1
            elif g["kind"] == "gift":
                fmt, units = "gift", 1
            else:
                fmt, units = "full_size", 1
            label_bits = []
            if units > 1:
                label_bits.append(("BOGO " if l["is_bogo"] else "") + (f"Box of {units}" if fmt == "sachet_box" else f"Pack of {units}"))
            if size_v:
                label_bits.append(f"{size_v:g} {size_u}")
            if code or sname:
                label_bits.append(" ".join(t for t in [code, sname] if t))
            variants.append(dict(
                id=vid_counter, product_id=pid, sku=sku, variant_label=" · ".join(label_bits) or "Standard",
                pack_format=fmt, units_per_pack=units, size_value=size_v, size_unit=size_u,
                shade_code=code, shade_name=sname,
                shade_undertone=(undertone(code, sname) if cslug in SHADE_CATS else None), shade_depth_rank=None,
                shade_guidance_th=guidance.get(code), list_price=reg, sale_price=(cur if cur < reg else None), currency="THB",
                web_in_stock=1 if v["is_in_stock"] else 0, is_listed_on_site=1,
                site_listing_id=lx["id"], site_variation_id=v["id"], barcode=None, price_checked_at=SNAPSHOT_AT,
                _cslug=cslug, _bogo=l["is_bogo"]))

# hidden single units (real SKUs whose parent listing is unpublished)
for parent, key in HIDDEN_VARIANT_PARENTS.items():
    g = groups[key]
    for v in VAR_BY_PARENT.get(parent, []):
        if v["sku"] in seen_sku:
            continue
        seen_sku.add(v["sku"])
        vid_counter += 1
        size_v, size_u = parse_size(v["name"])
        reg = int(v["prices"]["regular_price"]) / 100
        cur = int(v["prices"]["price"]) / 100
        variants.append(dict(id=vid_counter, product_id=g["product_id"], sku=v["sku"], variant_label=f"{size_v:g} {size_u}",
                             pack_format="full_size", units_per_pack=1, size_value=size_v, size_unit=size_u, shade_code=None,
                             shade_name=None, shade_undertone=None, shade_depth_rank=None, shade_guidance_th=None,
                             list_price=reg, sale_price=(cur if cur < reg else None), currency="THB",
                             web_in_stock=1 if v["is_in_stock"] else 0, is_listed_on_site=0, site_listing_id=parent,
                             site_variation_id=v["id"], barcode=None, price_checked_at=SNAPSHOT_AT, _cslug="face-sunscreen", _bogo=False))

# mini vs full size, and shade depth rank (derived from official numbering)
by_product = collections.defaultdict(list)
for v in variants:
    by_product[v["product_id"]].append(v)
for pid, vs in by_product.items():
    sizes = [v["size_value"] for v in vs if v["pack_format"] == "full_size" and v["size_value"]]
    if sizes:
        mx = max(sizes)
        for v in vs:
            if v["pack_format"] == "full_size" and v["size_value"] and v["size_value"] * 2 <= mx and v["size_value"] <= 20:
                v["pack_format"] = "mini"
    if vs[0]["_cslug"] in SHADE_CATS:
        codes = sorted({v["shade_code"] for v in vs if v["shade_code"] and re.search(r"\d", v["shade_code"])},
                       key=lambda c: int(re.sub(r"\D", "", c)))
        if len(codes) > 1 and all(re.match(r"^\d+$", c) for c in codes):
            rank = {c: i + 1 for i, c in enumerate(codes)}
            for v in vs:
                v["shade_depth_rank"] = rank.get(v["shade_code"])

# a product is 'legacy' if nothing in it is in stock AND it was not already flagged
for p in products:
    vs = by_product.get(p["id"], [])
    if p["lifecycle_status"] == "active" and vs and not any(v["web_in_stock"] for v in vs):
        p["curation_notes"] = "All variants out of stock on srichand.com at snapshot time."

for l in listings:
    x = l["raw"]
    g = groups.get(l["key"]) if l["ltype"] not in ("set", "gift") else groups.get(f"{'SET' if l['ltype']=='set' else 'GIFT'}:{x['id']}")
    site_rows.append(dict(site_listing_id=x["id"], product_id=g["product_id"] if g else None, listing_name=clean(x["name"]),
                          listing_type=l["ltype"], permalink=x["permalink"],
                          regular_price=int(x["prices"]["regular_price"]) / 100, current_price=int(x["prices"]["price"]) / 100,
                          on_sale=1 if x["on_sale"] else 0, in_stock=1 if x["is_in_stock"] else 0,
                          variation_count=len(x["variations"]), image_url=(x["images"][0]["src"] if x["images"] else None),
                          site_categories=json.dumps([c["slug"] for c in x["categories"]]),
                          snapshot_at=SNAPSHOT_AT))

bogo_variant_ids = [v["id"] for v in variants if v["_bogo"]]
for v in variants:
    v.pop("_cslug"), v.pop("_bogo")

SEED.mkdir(parents=True, exist_ok=True)


def dump(name, rows):
    (SEED / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1))
    print(f"  {name}: {len(rows)} rows")


print("Catalogue seed written:")
dump("brands", [dict(b, positioning=None, target_audience=None, source_id=SRC_API) for b in BRANDS])
dump("product_lines", [dict(id=line_id[r[0]], brand_id=r[1], slug=r[0], name_en=r[2], name_th=r[3], domain=r[4],
                            positioning_en=None, hero_ingredients=None, source_id=SRC_API) for r in LINES])
dump("categories", [dict(id=cat_id[r[0]], parent_id=cat_id.get(r[1]), slug=r[0], name_en=r[2], name_th=r[3], sort_order=r[5]) for r in CATS])
dump("products", products)
dump("product_variants", variants)
dump("site_listings", site_rows)
dump("product_images", images)
(SEED / "_catalog_index.json").write_text(json.dumps(dict(
    bogo_variant_ids=bogo_variant_ids,
    groups={g["key"]: dict(product_id=g["product_id"], kind=g["kind"], listing_ids=[l["raw"]["id"] for l in g["listings"]]) for g in groups.values()},
), ensure_ascii=False, indent=1))

if "--report" in sys.argv:
    print("\nClearance mapping report:")
    for r in sorted(clearance_report, key=lambda r: -r[0]):
        print("  ", *r)
    print("\nProducts without a line:")
    for p in products:
        if p["line_id"] is None and p["product_type"] == "single":
            print("  ", p["id"], p["name_en"], "|", p["name_th"][:50])
