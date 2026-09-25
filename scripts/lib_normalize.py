"""Shared helpers for turning srichand.com Store API listings into a canonical catalogue.

The site exposes 345 *listings* (each a WooCommerce "variable" product). Many listings are the
same physical product sold in a different pack (single, sachet box, multipack, BOGO, clearance
lot, gift-with-purchase). These helpers classify a listing and derive a canonical product key.
"""
import html
import re

THAI_DIGITS = str.maketrans("๐๑๒๓๔๕๖๗๘๙", "0123456789")


def clean(s: str) -> str:
    s = html.unescape(s or "").translate(THAI_DIGITS)
    s = s.replace("​", "").replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def strip_html(h: str) -> str:
    h = re.sub(r"<(br|/p|/li|/h\d|/div|/tr)[^>]*>", "\n", h or "")
    h = html.unescape(re.sub(r"<[^>]+>", " ", h))
    h = h.replace("​", "").replace("\xa0", " ")
    h = re.sub(r"[ \t]+", " ", h)
    h = re.sub(r"\s*\n\s*", "\n", h)
    return h.strip()


# ---------------------------------------------------------------- listing type
def classify_listing(name: str) -> dict:
    """Return listing_type + pack quantity parsed from the listing name."""
    n = clean(name)
    out = {"listing_type": "regular", "pack_qty": 1, "is_bogo": False}
    if n.startswith("ฟรี") or n.lower().startswith("free"):
        out["listing_type"] = "gift"
        return out
    if n.startswith("[Clearance]"):
        out["listing_type"] = "clearance"
        return out
    if "[Bogo]" in n:
        out["is_bogo"] = True
    m = re.match(r"^(\[[^\]]+\]\s*)+", n)
    prefix = m.group(0) if m else ""
    qty = None
    mq = re.search(r"\[\s*(\d+)\s*(ชิ้น|ซอง)", prefix) or re.search(r"\[ชิ้น(\d+)", prefix)
    if mq:
        qty = int(mq.group(1))
    if "แพ็คคู่" in prefix:
        qty = 2
    body = n[len(prefix):]
    is_set_word = bool(re.search(r"(^|\s)(Set|SET|เซต|เซ็ท|เซท|เชต)(\s|$)|บ็อกเซ็ต|บ็อก เซ็ต|บ็อกเซต", body))
    is_combo = bool(re.search(r"\)\s*(และ|&|\+)\s*", body)) or " และ " in body or "แถมฟรี" in body
    if is_set_word or is_combo:
        out["listing_type"] = "set"
        out["pack_qty"] = qty or 1
        return out
    if re.search(r"1\s*กล่อง\)?\s*$", body) or re.search(r"\(1\s*กล่อง\)", body):
        out["listing_type"] = "sachet_box"
        out["pack_qty"] = 6
        return out
    if qty:
        out["listing_type"] = "multipack"
        out["pack_qty"] = qty
        return out
    return out


# ---------------------------------------------------------------- attribute parsing
SIZE_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:x\s*\d+\s*)?(มล\.?|ml\.?|ML|ก\.?(?![ก-๙])|g\.?(?![a-z])|กรัม)", re.I
)


def parse_size(name: str):
    n = clean(name)
    # prefer the size inside parentheses
    cands = re.findall(r"\(([^)]*)\)", n) + [n]
    for c in cands:
        m = SIZE_RE.search(c)
        if m:
            val = float(m.group(1))
            unit = m.group(2).lower().rstrip(".")
            unit = "ml" if unit in ("มล", "ml") else "g"
            return (int(val) if val.is_integer() else val), unit
    return None, None


def parse_spf(name: str):
    n = clean(name)
    m = re.search(r"(?:SPF|เอสพีเอฟ)\s*(\d+\+?)", n, re.I)
    spf = m.group(1) if m else None
    m2 = re.search(r"(?:PA|พีเอ)\s*(\+{2,4})", n, re.I)
    pa = "PA" + m2.group(1) if m2 else None
    return spf, pa


NOISE = [
    r"\[[^\]]*\]", r"\([^)]*\)", r"แบบซอง\s*ศรีจันทร์", r"แบบซอง", r"1\s*กล่อง", r"\bNew\b", r"ใหม่",
    r"\d+(\.\d+)?\s*(มล\.?|ml\.?|ก\.|g\.?)", r"รวม\s*\d+\s*ซอง", r"SRICHAND.*$",
]


def canonical_key(name: str) -> str:
    n = clean(name)
    for pat in NOISE:
        n = re.sub(pat, " ", n, flags=re.I)
    n = re.sub(r"(เอสพีเอฟ|SPF)\s*\d+\+?", " ", n, flags=re.I)
    n = re.sub(r"(พีเอ|PA)\s*\+*", " ", n, flags=re.I)
    n = n.replace("วิช", " ")
    n = re.sub(r"[^\wก-๙]+", "", n)
    # spelling variants seen on the site
    for a, b in [("แบร์ทูเพอเฟค", "แบร์ทูเพอร์เฟคท์"), ("ทรานซ์ลูเซนท์", "ทรานส์ลูเซนท์"), ("ฟิลลินมี", "ฟีลลินมี"),
                 ("เอนชานท์เท็ด", "เอ็นชานเท็ด"), ("คัพเวอร์", "คัฟเวอร์"), ("ออเวส์", "ออลเวย์ส")]:
        n = n.replace(a, b)
    return n


def name_en_from_slug(slug: str) -> str:
    s = re.sub(r"^(clearance-|1-free-1-)", "", slug)
    s = re.sub(r"-\d+(-\d+)?-?(ml|g|มล|ก)\b.*$", "", s)
    s = re.sub(r"-(spf|pa)-?\d*.*$", "", s)
    words = [w for w in s.split("-") if w]
    small = {"and", "of", "to", "with", "in"}
    out = []
    for w in words:
        if w in ("srichand", "sasi"):
            continue
        out.append(w if w in small else (w.upper() if w in ("uv", "pdrn", "bb", "cc", "hya", "ph", "mu") else w.capitalize()))
    return " ".join(out)
