#!/usr/bin/env python3
"""Step 5 — provenance registry, source list, and the Postgres flavour of the schema."""
import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "db" / "seed"
AT = "2026-09-18T11:12:00Z"
sources = [
    (1, "srichand_store_api", "srichand.com public WooCommerce Store API", "https://srichand.com/wp-json/wc/store/v1/products", "official", "All 345 listings and 1,339 variations: names, SKUs, list/sale prices, stock flags, descriptions, images. Raw snapshot in research/raw/."),
    (2, "srichand_product_pages", "srichand.com product pages (ingredient + how-to-use tabs)", "https://srichand.com/shop/", "official", "Full INCI lists and usage directions published by the brand on each product page."),
    (3, "third_party_inci_db", "INCIDecoder / SkinSort (third-party ingredient databases)", "https://incidecoder.com/brands/srichand", "third_party_db", "Used only to cross-check official INCI lists."),
    (4, "srichand_policies", "srichand.com policy, membership and campaign pages", "https://srichand.com/", "official", "Srichand Rewards T&C, shipping threshold, payment methods, returns, campaigns. Details in research/findings/rewards_policies_brand.md."),
    (5, "retailer_listings", "Thai retailer listings (Watsons TH, Konvy, Beautrium, Lotus's)", "https://www.watsons.co.th/", "retailer", "Cross-checks and fallback where an official tab is empty."),
    (6, "thai_regulators", "Thai FDA cosmetic advertising manual; Cosmetics Act B.E. 2558; PDPA B.E. 2562; PDPC notifications", "https://www.fda.moph.go.th/", "regulator", "Basis for knowledge/ guideline documents. Details in research/findings/thai_regulatory.md."),
    (7, "bricks_curation", "Bricks curation (cosmetic-science knowledge + reading of official copy)", None, "curated", "Ingredient dictionary, concern taxonomy, routine steps, product↔concern mappings, range gaps."),
    (8, "mock_generator", "scripts/04_generate_mock.py (seed 20260918)", None, "internal_mock", "All operational data. Fictional people; real SKUs and prices."),
]
json.dump([dict(id=s[0], code=s[1], name=s[2], url=s[3], source_type=s[4], accessed_at=AT, notes=s[5]) for s in sources], open(SEED / "data_sources.json", "w"), ensure_ascii=False, indent=1)

REAL, DER, CUR, MOCK = "real_sourced", "derived", "curated_knowledge", "mock"
prov = [
    ("data_sources", CUR, "Where every fact came from.", None), ("data_provenance", CUR, "This registry.", None),
    ("brands", REAL, "Brands sold on srichand.com.", "Product master data (PIM/ERP)"),
    ("product_lines", DER, "Collections inferred from official product names; positioning text is a curated reading of official copy.", "PIM"),
    ("categories", DER, "Advisor-friendly category tree mapped from the site's own categories.", "PIM"),
    ("products", REAL, "Canonical products de-duplicated from 345 site listings. Official Thai copy verbatim; English name/summary, finish, coverage, oil-control hours are DERIVED from that copy.", "PIM"),
    ("product_variants", REAL, "Every purchasable SKU with official SKU code, list price, sale price and web stock flag at snapshot time. Shade undertone/depth are DERIVED from official shade names.", "PIM + pricing engine"),
    ("bundle_components", DER, "Set contents matched from official set names/descriptions by text. Verify against client BOM.", "PIM / BOM"),
    ("site_listings", REAL, "Raw snapshot of all 345 public listings and how each maps to a canonical product.", "E-commerce platform"),
    ("product_images", REAL, "Official image URLs (hot-linked, not copied).", "DAM"),
    ("product_claims", REAL, "Official claim sentences, verbatim Thai.", "Regulatory-approved claims library"),
    ("ingredients", CUR, "Cosmetic-science dictionary written by Bricks.", "R&D ingredient master"),
    ("product_ingredients", REAL, "Full INCI lists in label order from official product pages (retailer fallback is flagged per row).", "R&D formula master"),
    ("product_hero_ingredients", REAL, "Hero ingredients exactly as the brand names them in official copy, linked to the dictionary.", "PIM"),
    ("ingredient_interactions", CUR, "Layering rules.", "R&D / advisor guideline"),
    ("skin_types", CUR, "Advisor taxonomy.", None), ("skin_concerns", CUR, "Advisor taxonomy with photo cues, Thai-FDA-safe wording and refer-out rules.", None),
    ("product_concerns", CUR, "Which product serves which concern; every row states its basis (official positioning / site category / ingredient inference).", "Advisor guideline owned by brand + R&D"),
    ("product_skin_types", CUR, "Suitability by skin type, with basis.", "Advisor guideline"),
    ("routine_steps", CUR, "AM/PM step order.", None), ("product_routine_steps", CUR, "Where each product sits in a routine.", "Advisor guideline"),
    ("range_gaps", CUR, "Needs the range cannot meet + the generic external option the advisor may mention.", "Brand strategy"),
    ("range_gap_concerns", CUR, "Concerns that trigger each gap.", None),
    ("warehouses", MOCK, "Fictional warehouses.", "WMS"), ("inventory", MOCK, "Simulated quantities, consistent with the real web stock flag.", "WMS / ERP"),
    ("inventory_movements", MOCK, "Simulated stock ledger.", "WMS"), ("customers", MOCK, "Fictional people; 6 scripted demo personas.", "CRM / LINE OA"),
    ("customer_addresses", MOCK, "Fictional addresses (real district/postcode pairs).", "CRM"),
    ("promotions", DER, "Rows with origin='observed_on_site' are real mechanics seen on srichand.com; origin='mock' rows are invented for the demo.", "Promotion engine"),
    ("promotion_variants", DER, "Variants in each promotion.", "Promotion engine"), ("coupons", MOCK, "Coupon code strings are placeholders.", "Promotion engine"),
    ("carts", MOCK, "Simulated.", "E-commerce platform"), ("cart_items", MOCK, "Simulated.", "E-commerce platform"),
    ("orders", MOCK, "Simulated orders using real SKUs, prices and the real free-shipping rule.", "OMS"), ("order_items", MOCK, "Simulated.", "OMS"),
    ("payments", MOCK, "Simulated; methods limited to those srichand.com really offers.", "Payment gateway"),
    ("shipments", MOCK, "Simulated; carrier names real, tracking numbers fake.", "Carrier APIs"), ("shipment_events", MOCK, "Simulated.", "Carrier APIs"),
    ("loyalty_tiers", REAL, "Srichand Rewards is a single-level programme: ฿25 = 1 point (official).", "Loyalty platform"),
    ("loyalty_accounts", MOCK, "Simulated balances.", "Loyalty platform"), ("loyalty_transactions", MOCK, "Simulated ledger using the official earn rate.", "Loyalty platform"),
    ("rewards_catalog", MOCK, "ASSUMED: Srichand publishes no redemption catalogue or point value.", "Loyalty platform"), ("reward_redemptions", MOCK, "Empty.", "Loyalty platform"),
    ("consent_records", MOCK, "Simulated PDPA consent trail; consent wording is a draft for legal review.", "Consent management"),
    ("customer_skin_profiles", MOCK, "Simulated self-reported profiles.", "Advisor service"), ("face_analysis_sessions", MOCK, "Simulated; images are never stored in the DB.", "Advisor service"),
    ("analysis_findings", MOCK, "Simulated.", "Advisor service"), ("recommendations", MOCK, "Simulated; product references are real.", "Advisor service"),
    ("routines", MOCK, "Simulated.", "Advisor service"), ("routine_items", MOCK, "Simulated.", "Advisor service"),
    ("range_gap_events", MOCK, "Simulated demand signal.", "Advisor service → BI"),
]
json.dump([dict(table_name=p[0], origin=p[1], description=p[2], production_source=p[3]) for p in prov], open(SEED / "data_provenance.json", "w"), ensure_ascii=False, indent=1)

# ---- Postgres flavour
s = (ROOT / "db" / "schema.sql").read_text()
s = s.replace("PRAGMA foreign_keys = ON;", "-- PostgreSQL 14+ flavour, generated by scripts/05_meta.py from db/schema.sql — do not edit by hand.")
s = re.sub(r"\bINTEGER PRIMARY KEY\b", "BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY", s)
s = re.sub(r"\bTIMESTAMP\b", "TIMESTAMPTZ", s)
s = re.sub(r"(\s)JSON(\s*,|\s*--|\s*\n)", r"\1JSONB\2", s)
s = re.sub(r"(\w+_id\s+)INTEGER\b", r"\1BIGINT", s)
s = s.replace("Dialect-neutral SQL: runs as-is on SQLite (bun:sqlite).", "PostgreSQL flavour.")
(ROOT / "db" / "schema.postgres.sql").write_text(s)
print("data_sources:", len(sources), "| data_provenance:", len(prov), "| schema.postgres.sql written")
