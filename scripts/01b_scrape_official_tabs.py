#!/usr/bin/env python3
"""Step 1b — fetch the official 'ingredient' and 'how to use' tabs from each product page on srichand.com.
Output: research/raw/official_tabs_2026-09-18.json  {product_id: {url, ingredient_text, howtouse_text}}
Polite: 1 request/second, single pass, public pages only."""
import html, json, re, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
products = json.load(open(ROOT / "db/seed/products.json"))
listings = json.load(open(ROOT / "db/seed/site_listings.json"))
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
out_path = ROOT / "research/raw/official_tabs_2026-09-18.json"
out = json.load(open(out_path)) if out_path.exists() else {}

def tab(h, tid):
    m = re.search(r'id="%s"\s+role="tabpanel"[^>]*>([\s\S]*?)</div>' % tid, h)
    if not m:
        return None
    t = re.sub(r"<(br|/p|/li)[^>]*>", "\n", m.group(1))
    t = html.unescape(re.sub(r"<[^>]+>", " ", t)).replace("\xa0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\s*\n\s*", "\n", t).strip() or None

for p in products:
    if p["product_type"] != "single" or str(p["id"]) in out:
        continue
    urls = [p["official_url"]] + [l["permalink"] for l in listings if l["product_id"] == p["id"] and l["permalink"] != p["official_url"] and l["listing_type"] in ("regular", "sachet_box")]
    rec = dict(url=None, ingredient_text=None, howtouse_text=None)
    for u in urls[:3]:
        r = subprocess.run(["curl", "-sS", "-m", "40", "-A", UA, u], capture_output=True)
        h = r.stdout.decode("utf-8", "ignore")
        ing, how = tab(h, "ingredient"), tab(h, "howtouse")
        time.sleep(1.0)
        if ing or how:
            rec = dict(url=u, ingredient_text=ing, howtouse_text=how)
            if ing:
                break
    out[str(p["id"])] = rec
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print("pages:", len(out), "with ingredients:", sum(1 for v in out.values() if v["ingredient_text"]), "with how-to:", sum(1 for v in out.values() if v["howtouse_text"]))
