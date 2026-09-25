# Entity-relationship diagram

Generated from `db/schema.sql`. Rendered by GitHub, VS Code (Mermaid preview) or https://mermaid.live.

## 1. Catalogue (real, sourced)

```mermaid
erDiagram
  data_sources ||--o{ brands : "source_id"
  brands ||--o{ product_lines : "brand_id"
  data_sources ||--o{ product_lines : "source_id"
  categories ||--o{ categories : "parent_id"
  brands ||--o{ products : "brand_id"
  product_lines ||--o{ products : "line_id"
  categories ||--o{ products : "category_id"
  data_sources ||--o{ products : "source_id"
  products ||--o{ product_variants : "product_id"
  product_variants ||--o{ bundle_components : "bundle_variant_id"
  product_variants ||--o{ bundle_components : "component_variant_id"
  products ||--o{ bundle_components : "component_product_id"
  products ||--o{ site_listings : "product_id"
  products ||--o{ product_images : "product_id"
  products ||--o{ product_claims : "product_id"
  data_sources ||--o{ product_claims : "source_id"
  brands {
    integer id PK
    text slug
    text name_en
    text name_th
    text positioning
    text target_audience
    text price_tier
  }
  bundle_components {
    integer bundle_variant_id FK
    integer component_variant_id FK
    integer component_product_id FK
    text component_label
    integer quantity
    boolean is_free_gift
  }
  categories {
    integer id PK
    integer parent_id FK
    text slug
    text name_en
    text name_th
    integer sort_order
  }
  data_sources {
    integer id PK
    text code
    text name
    text url
    text source_type
    timestamp accessed_at
    text notes
  }
  product_claims {
    integer id PK
    integer product_id FK
    text claim_th
    text claim_en
    text claim_type
    integer source_id FK
  }
  product_images {
    integer id PK
    integer product_id FK
    text url
    text alt_text
    integer sort_order
  }
  product_lines {
    integer id PK
    integer brand_id FK
    text slug
    text name_en
    text name_th
    text domain
    text positioning_en
  }
  product_variants {
    integer id PK
    integer product_id FK
    text sku
    text variant_label
    text pack_format
    integer units_per_pack
    numeric size_value
  }
  products {
    integer id PK
    integer brand_id FK
    integer line_id FK
    integer category_id FK
    text slug
    text name_en
    text name_th
  }
  site_listings {
    integer site_listing_id PK
    integer product_id FK
    text listing_name
    text listing_type
    text permalink
    numeric regular_price
    numeric current_price
  }
```

## 2. Ingredients

```mermaid
erDiagram
  products ||--o{ product_ingredients : "product_id"
  ingredients ||--o{ product_ingredients : "ingredient_id"
  data_sources ||--o{ product_ingredients : "source_id"
  products ||--o{ product_hero_ingredients : "product_id"
  ingredients ||--o{ product_hero_ingredients : "ingredient_id"
  data_sources {
    integer id PK
    text code
    text name
    text url
    text source_type
    timestamp accessed_at
    text notes
  }
  ingredient_interactions {
    integer id PK
    text class_a
    text class_b
    text interaction
    text advice_en
    text advice_th
  }
  ingredients {
    integer id PK
    text inci_name
    text common_name
    text name_th
    text ingredient_class
    text what_it_does_en
    text what_it_does_th
  }
  product_hero_ingredients {
    integer product_id FK
    text hero_name
    integer ingredient_id FK
    text official_benefit_th
  }
  product_ingredients {
    integer product_id FK
    integer position
    integer ingredient_id FK
    text inci_as_listed
    boolean is_key_active
    integer source_id FK
    text source_url
  }
  products {
    integer id PK
    integer brand_id FK
    integer line_id FK
    integer category_id FK
    text slug
    text name_en
    text name_th
  }
```

## 3. Advisor knowledge (curated)

```mermaid
erDiagram
  products ||--o{ product_concerns : "product_id"
  skin_concerns ||--o{ product_concerns : "concern_id"
  products ||--o{ product_skin_types : "product_id"
  skin_types ||--o{ product_skin_types : "skin_type_id"
  products ||--o{ product_routine_steps : "product_id"
  routine_steps ||--o{ product_routine_steps : "step_id"
  products ||--o{ range_gaps : "closest_in_range_product_id"
  range_gaps ||--o{ range_gap_concerns : "gap_id"
  skin_concerns ||--o{ range_gap_concerns : "concern_id"
  product_concerns {
    integer product_id FK
    integer concern_id FK
    integer relevance
    text basis
    text rationale_en
  }
  product_routine_steps {
    integer product_id FK
    integer step_id FK
    boolean use_am
    boolean use_pm
    text frequency_en
    text usage_note_en
  }
  product_skin_types {
    integer product_id FK
    integer skin_type_id FK
    text suitability
    text basis
  }
  products {
    integer id PK
    integer brand_id FK
    integer line_id FK
    integer category_id FK
    text slug
    text name_en
    text name_th
  }
  range_gap_concerns {
    integer gap_id FK
    integer concern_id FK
  }
  range_gaps {
    integer id PK
    text slug
    text title_en
    text missing_category
    text severity
    text why_it_matters_en
    integer closest_in_range_product_id FK
  }
  routine_steps {
    integer id PK
    text slug
    text name_en
    text name_th
    integer step_order
    boolean applies_am
    boolean applies_pm
  }
  skin_concerns {
    integer id PK
    text slug
    text name_en
    text name_th
    text concern_group
    text photo_detectable
    text photo_cues_en
  }
  skin_types {
    integer id PK
    text slug
    text name_en
    text name_th
    text description_en
  }
```

## 4. Commerce (mock)

```mermaid
erDiagram
  product_variants ||--o{ inventory : "variant_id"
  warehouses ||--o{ inventory : "warehouse_id"
  product_variants ||--o{ inventory_movements : "variant_id"
  warehouses ||--o{ inventory_movements : "warehouse_id"
  customers ||--o{ customer_addresses : "customer_id"
  product_variants ||--o{ promotions : "gift_variant_id"
  promotions ||--o{ promotion_variants : "promotion_id"
  product_variants ||--o{ promotion_variants : "variant_id"
  promotions ||--o{ coupons : "promotion_id"
  customers ||--o{ coupons : "customer_id"
  customers ||--o{ carts : "customer_id"
  carts ||--o{ cart_items : "cart_id"
  product_variants ||--o{ cart_items : "variant_id"
  customers ||--o{ orders : "customer_id"
  customer_addresses ||--o{ orders : "shipping_address_id"
  coupons ||--o{ orders : "coupon_id"
  orders ||--o{ order_items : "order_id"
  product_variants ||--o{ order_items : "variant_id"
  orders ||--o{ payments : "order_id"
  orders ||--o{ shipments : "order_id"
  warehouses ||--o{ shipments : "warehouse_id"
  shipments ||--o{ shipment_events : "shipment_id"
  cart_items {
    integer cart_id FK
    integer variant_id FK
    integer quantity
    text added_from
  }
  carts {
    integer id PK
    integer customer_id FK
    text status
    timestamp created_at
    timestamp updated_at
  }
  coupons {
    integer id PK
    integer promotion_id FK
    text code
    integer customer_id FK
    integer max_uses
    integer used_count
    timestamp expires_at
  }
  customer_addresses {
    integer id PK
    integer customer_id FK
    text label
    text recipient
    text phone
    text address_line
    text subdistrict
  }
  customers {
    integer id PK
    text line_user_id
    text line_display_name
    text first_name
    text last_name
    text phone
    text email
  }
  inventory {
    integer variant_id FK
    integer warehouse_id FK
    integer qty_on_hand
    integer qty_reserved
    integer reorder_point
    text next_restock_date
    timestamp updated_at
  }
  inventory_movements {
    integer id PK
    integer variant_id FK
    integer warehouse_id FK
    text movement_type
    integer quantity
    text reference
    timestamp created_at
  }
  order_items {
    integer id PK
    integer order_id FK
    integer variant_id FK
    integer quantity
    numeric unit_price
    numeric line_total
    boolean is_gift
  }
  orders {
    integer id PK
    text order_number
    integer customer_id FK
    text channel
    text status
    integer shipping_address_id FK
    numeric subtotal
  }
  payments {
    integer id PK
    integer order_id FK
    text method
    text status
    numeric amount
    text gateway_ref
    text qr_payload_ref
  }
  product_variants {
    integer id PK
    integer product_id FK
    text sku
    text variant_label
    text pack_format
    integer units_per_pack
    numeric size_value
  }
  promotion_variants {
    integer promotion_id FK
    integer variant_id FK
  }
  promotions {
    integer id PK
    text code
    text name_th
    text name_en
    text promo_type
    text mechanics_en
    numeric min_spend
  }
  shipment_events {
    integer id PK
    integer shipment_id FK
    text status
    text location
    text description_th
    timestamp occurred_at
  }
  shipments {
    integer id PK
    integer order_id FK
    integer warehouse_id FK
    text carrier
    text tracking_number
    text status
    timestamp shipped_at
  }
  warehouses {
    integer id PK
    text code
    text name
    text province
    text serves
  }
```

## 5. Loyalty — Srichand Rewards

```mermaid
erDiagram
  customers ||--o{ loyalty_accounts : "customer_id"
  loyalty_tiers ||--o{ loyalty_accounts : "tier_id"
  customers ||--o{ loyalty_transactions : "customer_id"
  orders ||--o{ loyalty_transactions : "order_id"
  product_variants ||--o{ rewards_catalog : "variant_id"
  loyalty_tiers ||--o{ rewards_catalog : "min_tier_id"
  customers ||--o{ reward_redemptions : "customer_id"
  rewards_catalog ||--o{ reward_redemptions : "reward_id"
  coupons ||--o{ reward_redemptions : "coupon_id"
  coupons {
    integer id PK
    integer promotion_id FK
    text code
    integer customer_id FK
    integer max_uses
    integer used_count
    timestamp expires_at
  }
  customers {
    integer id PK
    text line_user_id
    text line_display_name
    text first_name
    text last_name
    text phone
    text email
  }
  loyalty_accounts {
    integer customer_id PK
    text member_number
    integer tier_id FK
    integer points_balance
    integer lifetime_points
    numeric spend_this_period
    text tier_expires_on
  }
  loyalty_tiers {
    integer id PK
    text code
    text name
    numeric min_annual_spend
    numeric earn_rate_baht_per_point
    text benefits_en
    text benefits_th
  }
  loyalty_transactions {
    integer id PK
    integer customer_id FK
    text txn_type
    integer points
    integer order_id FK
    text description
    text expires_on
  }
  orders {
    integer id PK
    text order_number
    integer customer_id FK
    text channel
    text status
    integer shipping_address_id FK
    numeric subtotal
  }
  product_variants {
    integer id PK
    integer product_id FK
    text sku
    text variant_label
    text pack_format
    integer units_per_pack
    numeric size_value
  }
  reward_redemptions {
    integer id PK
    integer customer_id FK
    integer reward_id FK
    integer points_spent
    integer coupon_id FK
    timestamp redeemed_at
  }
  rewards_catalog {
    integer id PK
    text name_th
    text name_en
    text reward_type
    integer points_cost
    integer variant_id FK
    numeric discount_value
  }
```

## 6. Advisor sessions (mock, PDPA-aware)

```mermaid
erDiagram
  customers ||--o{ consent_records : "customer_id"
  customers ||--o{ customer_skin_profiles : "customer_id"
  consent_records ||--o{ customer_skin_profiles : "consent_id"
  skin_types ||--o{ customer_skin_profiles : "self_reported_skin_type_id"
  customers ||--o{ face_analysis_sessions : "customer_id"
  consent_records ||--o{ face_analysis_sessions : "consent_id"
  skin_types ||--o{ face_analysis_sessions : "observed_skin_type_id"
  face_analysis_sessions ||--o{ analysis_findings : "session_id"
  skin_concerns ||--o{ analysis_findings : "concern_id"
  face_analysis_sessions ||--o{ recommendations : "session_id"
  products ||--o{ recommendations : "product_id"
  product_variants ||--o{ recommendations : "variant_id"
  routine_steps ||--o{ recommendations : "step_id"
  skin_concerns ||--o{ recommendations : "addresses_concern_id"
  customers ||--o{ routines : "customer_id"
  face_analysis_sessions ||--o{ routines : "session_id"
  routines ||--o{ routine_items : "routine_id"
  routine_steps ||--o{ routine_items : "step_id"
  products ||--o{ routine_items : "product_id"
  range_gaps ||--o{ routine_items : "gap_id"
  range_gaps ||--o{ range_gap_events : "gap_id"
  customers ||--o{ range_gap_events : "customer_id"
  face_analysis_sessions ||--o{ range_gap_events : "session_id"
  skin_concerns ||--o{ range_gap_events : "concern_id"
  skin_types ||--o{ range_gap_events : "customer_skin_type_id"
  analysis_findings {
    integer id PK
    integer session_id FK
    integer concern_id FK
    text face_zone
    integer severity
    text confidence
    text observation_en
  }
  consent_records {
    integer id PK
    integer customer_id FK
    text consent_type
    text policy_version
    text consent_text_th
    timestamp granted_at
    timestamp withdrawn_at
  }
  customer_skin_profiles {
    integer customer_id PK
    integer consent_id FK
    integer self_reported_skin_type_id FK
    text sensitivity_level
    text known_reactions
    json goals
    text current_routine
  }
  customers {
    integer id PK
    text line_user_id
    text line_display_name
    text first_name
    text last_name
    text phone
    text email
  }
  face_analysis_sessions {
    integer id PK
    integer customer_id FK
    integer consent_id FK
    text image_ref
    text image_sha256
    integer image_count
    timestamp image_expires_at
  }
  product_variants {
    integer id PK
    integer product_id FK
    text sku
    text variant_label
    text pack_format
    integer units_per_pack
    numeric size_value
  }
  products {
    integer id PK
    integer brand_id FK
    integer line_id FK
    integer category_id FK
    text slug
    text name_en
    text name_th
  }
  range_gap_events {
    integer id PK
    integer gap_id FK
    integer customer_id FK
    integer session_id FK
    integer concern_id FK
    text customer_age_band
    integer customer_skin_type_id FK
  }
  range_gaps {
    integer id PK
    text slug
    text title_en
    text missing_category
    text severity
    text why_it_matters_en
    integer closest_in_range_product_id FK
  }
  recommendations {
    integer id PK
    integer session_id FK
    integer product_id FK
    integer variant_id FK
    integer step_id FK
    integer rank
    text reason_en
  }
  routine_items {
    integer id PK
    integer routine_id FK
    text period
    integer step_id FK
    integer product_id FK
    integer gap_id FK
    text frequency_en
  }
  routine_steps {
    integer id PK
    text slug
    text name_en
    text name_th
    integer step_order
    boolean applies_am
    boolean applies_pm
  }
  routines {
    integer id PK
    integer customer_id FK
    integer session_id FK
    text name
    text goal_en
    boolean is_active
    text review_after
  }
  skin_concerns {
    integer id PK
    text slug
    text name_en
    text name_th
    text concern_group
    text photo_detectable
    text photo_cues_en
  }
  skin_types {
    integer id PK
    text slug
    text name_en
    text name_th
    text description_en
  }
```
