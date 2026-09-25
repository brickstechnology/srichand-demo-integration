---
display_name: เลือกเฉดสีรองพื้น คุชชั่น คอนซีลเลอร์ แป้ง
slug: shade-matching
description: ใช้เมื่อลูกค้าถามเรื่องเฉดสีของรองพื้น คุชชั่น คอนซีลเลอร์ หรือแป้ง เช่น "ผิวขาวเหลืองใช้เบอร์ไหน" "ช่วยเลือกสีให้หน่อย" "110 กับ 115 ต่างกันยังไง" "ผิวสองสีมีเบอร์ที่เข้มพอไหม" "คอนซีลเลอร์ปิดใต้ตาใช้สีไหน"
---
## Goal
Suggest the closest shade and an alternative, honestly labelled as approximate.

## Steps
1. Identify the product: `search_products`, then `get_product` to see its shades and any official "suits which skin tone" line.
2. Get undertone and depth:
   - From `get_customer` if a recent analysis recorded them.
   - Otherwise ask: which shade they wear in another base product, whether skin leans pink, neutral or yellow, how they tan, how deep their skin is compared with people around them.
3. Call `match_shade` with the product, undertone and depth.
4. Present the best shade and one alternative; quote the official guidance line if there is one. Always add that a match from a photo or description is approximate and that a swatch on the jawline in daylight is the real test.
5. Call `check_stock` for the best shade. Low → say how many are left. Out → offer the alternative shade or the restock date.
6. If the tool warns that the deepest shade may still be too light → say so plainly; do not talk the customer into a wrong shade.
7. Under-eye concealing: one step lighter or pinker than the face shade; blemishes: the face shade.
8. Wants to buy → `cart-and-checkout` with that exact shade.

## Knowledge to open
- `concern-and-skin-type-glossary`
- `voice-and-message-format`

## Tools
`search_products` · `get_product` · `get_customer` · `match_shade` · `check_stock`
