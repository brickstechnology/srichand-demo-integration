// Seed load order (respects foreign keys). Shared by build.ts and sync.ts.
export const TABLES = [
  "data_sources", "data_provenance",
  "brands", "product_lines", "categories", "products", "product_variants", "bundle_components", "site_listings",
  "product_images", "product_claims",
  "ingredients", "product_ingredients", "product_hero_ingredients", "ingredient_interactions",
  "skin_types", "skin_concerns", "product_concerns", "product_skin_types", "routine_steps", "product_routine_steps",
  "range_gaps", "range_gap_concerns",
  "warehouses", "inventory", "inventory_movements", "customers", "customer_addresses",
  "promotions", "promotion_variants", "coupons", "carts", "cart_items",
  "orders", "order_items", "payments", "shipments", "shipment_events",
  "loyalty_tiers", "loyalty_accounts", "loyalty_transactions", "rewards_catalog", "reward_redemptions",
  "consent_records", "customer_skin_profiles", "face_analysis_sessions", "analysis_findings",
  "recommendations", "routines", "routine_items", "range_gap_events",
];
