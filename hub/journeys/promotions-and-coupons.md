---
display_name: โปรโมชั่น คูปอง ของแถม ส่งฟรี
slug: promotions-and-coupons
description: ใช้เมื่อลูกค้าถามเรื่องโปรโมชั่นหรือส่วนลด เช่น "มีโปรอะไรบ้าง" "มีโค้ดลดไหม" "ซื้อเท่าไหร่ส่งฟรี" "ได้ของแถมไหม" "ซื้อ 1 แถม 1 ยังมีไหม" "โค้ดนี้ใช้ได้ไหม" "ทำยังไงให้คุ้มสุด"
---
## Goal
Tell the customer which offers really apply to them now — nothing invented.

## Steps
1. If they have a cart, call `cart_view` to get the basket total; then call `get_promotions` with that total. No cart → `get_promotions` without a total.
2. Tell them, in this order: what already applies to their basket · the nearest threshold they have not reached and how much more it takes · shipping cost and the distance to free shipping, as returned.
3. A specific code → check it is in the promotions returned; its conditions come from there. It is only truly validated when the order is placed.
4. Background on a named campaign (event, draw, dates) → the campaigns knowledge file. If that file and the live promotions disagree, the live data wins.
5. "How do I get the best deal?" → compare honestly: single items, twin packs and sets from `search_products` (include sets), plus the offers above. Do not pad the basket to reach a threshold unless they ask.
6. Ready to buy → `cart-and-checkout`.

## Avoid
- Making up a code, a gift, an extra discount or an end date.
- Promising a gift: gifts depend on stock at the moment of ordering.

## Knowledge to open
- `current-campaigns`
- `store-policies`

## Tools
`cart_view` · `get_promotions` · `search_products`
