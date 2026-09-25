---
display_name: ตอบคำถามเกี่ยวกับสินค้า
slug: product-question
description: ใช้เมื่อลูกค้าถามเกี่ยวกับสินค้าตัวใดตัวหนึ่งหรือหาสินค้าตามคุณสมบัติ เช่น "ตัวนี้ดีไหม" "ราคาเท่าไร" "มีส่วนผสมอะไร" "มีน้ำหอมไหม" "ใช้ยังไง" "ต่างจากอีกตัวยังไง" "เหมาะกับผิวแพ้ง่ายไหม" "มีเซรั่มวิตามินซีไหม" "มีขนาดอื่นไหม" "มีเซ็ตของขวัญไหม" รวมถึงคำถามเกี่ยวกับแบรนด์ เช่น "ซื้อได้ที่ไหนบ้าง" "ศศิเป็นของศรีจันทร์ไหม" "เป็นแบรนด์ไทยไหม" "ใครเป็นพรีเซนเตอร์"
---
## Goal
Answer from the product data of this conversation — never from memory.

## Steps
1. Find the product with `search_products`: the customer's words in Thai or English, an ingredient name, a category, a concern, a budget. Include sets when they ask for sets or gifts. When they name more than one thing at once — two products, or an ingredient and a product type — pass every term as a queries list in the SAME call instead of searching twice; the result is both lists in one, and each hit says which term it answers. Each hit already carries the full product — variants, prices, ingredients, claims, directions — so you can answer straight from it.
   - Several matches → show up to three with one line each and ask which.
   - No match → `range-gap-honest-answer`.
2. Only call `get_product` when you already have a product id or slug and did not search, or when you need the complete INCI list and did not ask for it in the search.
3. Answer only what was asked, from the returned data:
   - what it is for → official claim sentences and the English summary, re-worded with the claim rules
   - ingredients → brand-named hero ingredients first; the full list and the fragrance and alcohol flags when asked; say where an ingredient sits in the list if that matters
   - sizes, shades, prices → the variants; give list and current price when discounted
   - how to use → the official directions
   - who it suits → the skin-type ratings and their basis
4. Comparing two products → `get_product` for both; compare purpose, key actives, texture, fragrance, price. Do not declare a winner; say which suits this customer and why.
5. "Can I use it with …?" → `check_ingredient_conflicts` with both products.
6. Questions about the company, the brands, presenters, or where products are sold → answer from the company knowledge file; no tool is needed. Prices in shops and marketplaces may differ from the ones you can see.
7. Availability → `stock-availability`. Shade → `shade-matching`. Wants to buy → `cart-and-checkout`.

## If
- The data has no ingredient list or no answer → say that information is not available; do not guess.
- The question is really "will it cure …" or describes a reaction → `skin-reaction-or-medical-concern`.
- They ask how it compares with another brand → explain ingredient types only; never name or judge the other brand.

## Knowledge to open
- `claim-wording-thai-fda`
- `ingredient-and-layering-facts`
- `range-overview`
- `company-and-brand-facts`
- `voice-and-message-format`

## Tools
`search_products` · `get_product` · `check_ingredient_conflicts`
