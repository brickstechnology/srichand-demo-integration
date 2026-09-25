# 06 · Ingredient and routine rules

Internal reasoning guide. Anything said to a customer must be re-worded through guideline 02.

## Routine order
AM: cleanse → essence → treatment serum → moisturise → **sunscreen** → (primer → base → conceal → powder → colour → lips)
PM: remove makeup/sunscreen → cleanse → (toner pad, some nights) → essence → treatment serum → moisturise → (mask 1–3×/week)
Thin to thick; one new active at a time; two weeks between introductions.

## Layering rules (mirrors `ingredient_interactions`)
| Combination | Rule |
|---|---|
| Retinoid + exfoliating acid (AHA/BHA) | Different nights until skin is fully accustomed |
| AHA + BHA | One exfoliant per session |
| Retinoid (HPR) + bakuchiol | Fine to alternate; start one, add the other after 4 weeks |
| Any retinoid or exfoliant | Daily SPF50+ PA++++ is non-negotiable |
| Vitamin C derivatives under sunscreen | Pairs well — morning use |
| Retinoid + ceramides / ectoin / panthenol / cica | Pairs well — buffer with Barrier Boost on retinoid nights |
| Niacinamide + tranexamic acid + vitamin C derivatives | Combine freely |

## Retinoid ramp-up (Resurface Pro-Retinol Intense Serum)
Weeks 1–2: two nights a week · weeks 3–6: every other night · then nightly if comfortable. Pea-sized amount on dry skin, avoid eye corners and lips, moisturiser on top. Expect mild dryness early on; stop and switch to Barrier Boost if there is stinging or peeling. **Not in pregnancy or nursing** — the tool excludes retinoids when `pregnant_or_nursing` is true; Timeless (bakuchiol) is the alternative, still "check with your doctor".

## Range-specific facts from the official INCI lists (verified 18 Sep 2026)
| Product | Fact worth knowing |
|---|---|
| Sunlution Acne Care | Filters: avobenzone, octisalate, ethylhexyl triazone (Uvinul T150), DHHB (Uvinul A Plus), bemotrizinol (Tinosorb S), titanium dioxide. Salicylic acid is #32 of 54 — a low, undisclosed level. No niacinamide (a widely copied third-party listing confuses it with Skin Whitening). |
| Sunlution Moisture Burst Watery | Official ingredient tab carries marketing copy, so INCI is from a retailer (single source). Filters include iscotrizinol + Tinosorb S. |
| Super C Intense Serum | Contains **fragrance** (#25 of 36). Glycolic acid (#26) and all three vitamin-C forms (#29–31) sit after it → low levels. The work is done by niacinamide, tranexamic acid, arbutin. Not an exfoliant. |
| Super C Gel Cream | Marketed with glycolic acid as an exfoliating hero, but it is #24 of 29 → very mild. 5% niacinamide and 0.1% alpha-arbutin are disclosed. |
| Resurface | HPR #17, retinyl palmitate #30, ceramides NP/AP/EOP, phytosphingosine, cholesterol, bisabolol, Acetyl Hexapeptide-1, 13 hyaluronate forms; no fragrance; **contains Alcohol (#23)** and BHT. |
| Timeless | Bakuchiol-based; fragrance-free per official copy. |
| Barrier Boost Cleansing Gel Foam | Contains **Parfum (#15)** and two colourants — the serum and gel cream in the same line are fragrance-free. For fragrance-reactive customers use the Phyto Camellia cleanser. |
| Barrier Boost Soothing Gel Cream | Fragrance-free; contains two colourants. |
| Phyto Camellia PDRN | Disclosed strengths: PDRN 0.5%, niacinamide 5% (serum, gel cream) / 1.5% (essence), alpha-arbutin 0.1%. |
| Translucent Powder (classic) | INCI published as raw-material blends; no fragrance listed; includes methylisothiazolinone (restricted in EU leave-on products — flag for the client's regulatory team; label not physically checked). |
| Porefect Matte Primer | Alcohol Denat. at #7 (the Glow version is the alcohol-free one). |
| Original Powder Mask | Calamine-based 1948 recipe; contains fragrance and boric acid — rinse-off use, not for sensitive skin. |
| SASI Acne Sol products | Salicylic acid throughout; cleanser, micellar water and loose powder contain tea tree oil (a potential sensitiser). |

The database flags `products.is_fragrance_free` and `is_alcohol_free` **from the INCI list**, not from marketing copy. `recommend_routine` applies `fragrance_free_only` and penalises fragrance when sensitivity is high.

## Sensitive or reactive skin
Default to Barrier Boost serum + gel cream, Phyto Camellia cleanser, Sunlution Rosia or Moisture Burst Watery. Introduce nothing else for two weeks. Avoid: Super C Intense Serum (fragrance), Original Powder Mask, tea-tree products, toner pads.

## Oily skin in a humid climate
Light layers (essence + gel cream), matte sunscreen (Sunlution Acne Care), Translucent Powder for the 2 pm touch-up. Oily skin still needs water — skipping moisturiser often increases shine. For congestion, see the BHA gap in guideline 04.

## Teens (SASI)
Three steps at most: gentle cleanser, light moisturiser if needed, sunscreen. Toner pad 2 nights a week only if tolerated. Persistent acne → parent + pharmacist/dermatologist.
