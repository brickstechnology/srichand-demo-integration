#!/usr/bin/env python3
"""Step 7 — Excel export for non-developers: exports/srichand-catalogue.xlsx
Sheets: README · Products · SKUs & prices · Ingredients (INCI) · Hero ingredients · Advisor mapping · Sets · Range gaps · Site listings · Provenance"""
import sqlite3
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
con = sqlite3.connect(ROOT / "db/srichand.db")
wb = Workbook()
HEAD = PatternFill("solid", fgColor="2E1A47")
BAND = PatternFill("solid", fgColor="F6F2FA")

def sheet(title, sql, widths=None, wrap=()):
    ws = wb.create_sheet(title)
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    ws.append(cols)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = HEAD; c.alignment = Alignment(vertical="center", wrap_text=True)
    for i, row in enumerate(cur.fetchall()):
        ws.append(list(row))
        if i % 2:
            for c in ws[ws.max_row]:
                c.fill = BAND
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions
    for i, col in enumerate(cols, 1):
        w = (widths or {}).get(col) or min(46, max(10, len(col) + 2, *(len(str(r[0].value or "")) + 2 for r in ws.iter_rows(min_row=2, max_row=min(ws.max_row, 60), min_col=i, max_col=i))))
        ws.column_dimensions[get_column_letter(i)].width = w
        if col in wrap:
            for r in ws.iter_rows(min_row=2, min_col=i, max_col=i):
                r[0].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[1].height = 30
    return ws

ws = wb.active; ws.title = "README"
rows = [("Srichand catalogue — review workbook", ""), ("Snapshot", "srichand.com, 18 Sep 2026 (prices change often — most core skincare was on sale)"),
        ("Purpose", "Lets non-developers eyeball and correct product facts. Generated from db/srichand.db by scripts/07_export_xlsx.py — edit the source data, not this file."),
        ("What is real", "Names, SKUs, list/sale prices, web stock flag, Thai copy, INCI lists, hero ingredients, official claims — all from srichand.com (3 INCI lists from retailers, flagged)."),
        ("What is derived", "English names, category/line assignment, finish/coverage/oil-control hours (parsed from Thai copy), shade undertone/depth (from shade names), set contents (text-matched)."),
        ("What is curated", "Advisor mapping (concerns, skin types, routine step), ingredient dictionary, range gaps — Bricks' reading of official copy + cosmetic science."),
        ("What is NOT here", "Mock operational data (stock quantities, customers, orders, points). See the database and docs/data-dictionary.md."),
        ("Blank cells", "Mean 'not published / not verified'. Nothing about a product was invented."), ("", ""), ("Sheet", "Rows")]
for r in rows: ws.append(r)
ws["A1"].font = Font(bold=True, size=14)
for r in ws.iter_rows(min_row=2, max_col=1):
    r[0].font = Font(bold=True)
ws.column_dimensions["A"].width = 22; ws.column_dimensions["B"].width = 120
for r in ws.iter_rows(min_col=2, max_col=2):
    r[0].alignment = Alignment(wrap_text=True, vertical="top")

sheets = [
 ("Products", """SELECT p.id AS product_id, b.name_en AS brand, l.name_en AS line, pc.name_en AS category_group, c.name_en AS category, p.name_en, p.name_th, p.product_type, p.lifecycle_status,
      (SELECT MIN(COALESCE(v.sale_price, v.list_price)) FROM product_variants v WHERE v.product_id = p.id) AS price_from_thb,
      (SELECT COUNT(*) FROM product_variants v WHERE v.product_id = p.id) AS skus, (SELECT SUM(v.web_in_stock) FROM product_variants v WHERE v.product_id = p.id) AS skus_in_stock,
      p.spf_value, p.pa_rating, p.finish, p.coverage, p.oil_control_hours_claimed, p.is_water_resistant_claimed,
      CASE p.is_fragrance_free WHEN 1 THEN 'yes' WHEN 0 THEN 'NO - contains fragrance' END AS fragrance_free, CASE p.is_alcohol_free WHEN 1 THEN 'yes' WHEN 0 THEN 'NO - lists alcohol' END AS alcohol_free,
      p.free_from, (SELECT COUNT(*) FROM product_ingredients x WHERE x.product_id = p.id) AS inci_count, p.tagline_th, p.summary_en, p.tested_claims_th, p.how_to_use, p.description_th, p.curation_notes, p.official_url
    FROM products p JOIN brands b ON b.id = p.brand_id LEFT JOIN product_lines l ON l.id = p.line_id JOIN categories c ON c.id = p.category_id LEFT JOIN categories pc ON pc.id = c.parent_id
    ORDER BY b.id, pc.sort_order, c.sort_order, p.name_en""", {"name_en": 42, "name_th": 46, "summary_en": 70, "description_th": 70, "how_to_use": 50, "tested_claims_th": 50, "tagline_th": 40, "curation_notes": 50, "official_url": 40}, ("summary_en",)),
 ("SKUs & prices", """SELECT v.sku, b.name_en AS brand, p.name_en AS product, v.variant_label, v.pack_format, v.units_per_pack, v.size_value, v.size_unit, v.shade_code, v.shade_name, v.shade_undertone AS undertone_derived, v.shade_depth_rank AS depth_rank_derived,
      v.shade_guidance_th AS official_shade_guidance, v.list_price, v.sale_price, COALESCE(v.sale_price, v.list_price) AS current_price,
      CASE WHEN v.sale_price IS NOT NULL THEN ROUND(100.0 * (v.list_price - v.sale_price) / v.list_price) END AS discount_pct, v.web_in_stock, v.is_listed_on_site, v.barcode, v.price_checked_at
    FROM product_variants v JOIN products p ON p.id = v.product_id JOIN brands b ON b.id = p.brand_id ORDER BY b.id, p.name_en, v.size_value, v.shade_code""", {"product": 44, "variant_label": 34, "official_shade_guidance": 44}, ()),
 ("Ingredients (INCI)", """SELECT p.name_en AS product, pi.position, pi.inci_as_listed, CASE pi.is_key_active WHEN 1 THEN 'key' END AS key_active, i.common_name, i.ingredient_class, i.what_it_does_en AS what_it_does_internal_note, i.caution_en,
      pi.shade_scope, s.name AS source, pi.source_url FROM product_ingredients pi JOIN products p ON p.id = pi.product_id LEFT JOIN ingredients i ON i.id = pi.ingredient_id JOIN data_sources s ON s.id = pi.source_id ORDER BY p.name_en, pi.position""",
      {"product": 42, "inci_as_listed": 44, "what_it_does_internal_note": 60, "source": 36, "source_url": 40}, ()),
 ("Hero ingredients", """SELECT p.name_en AS product, h.hero_name AS hero_as_named_by_brand, i.inci_name AS dictionary_inci, h.official_benefit_th FROM product_hero_ingredients h JOIN products p ON p.id = h.product_id LEFT JOIN ingredients i ON i.id = h.ingredient_id ORDER BY p.name_en""",
      {"product": 42, "hero_as_named_by_brand": 40, "official_benefit_th": 90}, ()),
 ("Advisor mapping", """SELECT p.name_en AS product, 'concern' AS mapping, s.name_en AS value, x.relevance AS strength, x.basis, x.rationale_en AS rationale FROM product_concerns x JOIN products p ON p.id = x.product_id JOIN skin_concerns s ON s.id = x.concern_id
    UNION ALL SELECT p.name_en, 'skin type', s.name_en, x.suitability, x.basis, NULL FROM product_skin_types x JOIN products p ON p.id = x.product_id JOIN skin_types s ON s.id = x.skin_type_id
    UNION ALL SELECT p.name_en, 'routine step', r.name_en, CASE WHEN x.use_am AND x.use_pm THEN 'AM+PM' WHEN x.use_am THEN 'AM' ELSE 'PM' END, NULL, COALESCE(x.frequency_en,'') || CASE WHEN x.usage_note_en IS NOT NULL THEN ' — ' || x.usage_note_en ELSE '' END FROM product_routine_steps x JOIN products p ON p.id = x.product_id JOIN routine_steps r ON r.id = x.step_id
    ORDER BY 1, 2, 4 DESC""", {"product": 42, "value": 34, "rationale": 80}, ()),
 ("Sets", """SELECT bp.name_th AS set_name, bv.sku AS set_sku, bv.list_price, bv.sale_price, bv.web_in_stock, bc.component_label, bc.quantity, bc.is_free_gift FROM bundle_components bc JOIN product_variants bv ON bv.id = bc.bundle_variant_id JOIN products bp ON bp.id = bv.product_id ORDER BY bp.name_th""", {"set_name": 70, "component_label": 50}, ()),
 ("Range gaps", """SELECT g.title_en AS gap, g.severity, g.missing_category, g.why_it_matters_en, p.name_en AS closest_in_range, g.closest_in_range_limits_en, g.generic_external_option_en, g.generic_external_option_th, g.commercial_read_en,
      (SELECT COUNT(*) FROM range_gap_events e WHERE e.gap_id = g.id) AS simulated_demand_events FROM range_gaps g LEFT JOIN products p ON p.id = g.closest_in_range_product_id""",
      {"gap": 40, "why_it_matters_en": 80, "closest_in_range_limits_en": 50, "generic_external_option_en": 50, "generic_external_option_th": 50, "commercial_read_en": 60}, ("why_it_matters_en", "commercial_read_en", "generic_external_option_en", "generic_external_option_th", "closest_in_range_limits_en")),
 ("Site listings (345)", """SELECT s.site_listing_id, s.listing_type, s.listing_name, p.name_en AS mapped_to_product, s.regular_price, s.current_price, s.on_sale, s.in_stock, s.variation_count, s.permalink FROM site_listings s LEFT JOIN products p ON p.id = s.product_id ORDER BY s.listing_type, s.listing_name""",
      {"listing_name": 80, "mapped_to_product": 44, "permalink": 50}, ()),
 ("Provenance", "SELECT table_name, origin, description, production_source, (SELECT 1) AS _ FROM data_provenance ORDER BY origin, table_name", {"description": 110, "production_source": 40}, ()),
]
for title, sql, widths, wrap in sheets:
    s = sheet(title, sql, widths, wrap)
    ws.append((title, s.max_row - 1))
wb["Provenance"].delete_cols(5)
out = ROOT / "exports" / "srichand-catalogue.xlsx"
wb.save(out)
print("written", out, {s.title: s.max_row - 1 for s in wb.worksheets[1:]})
