---
display_name: สั่งซ้ำของเดิม
slug: reorder
description: ใช้เมื่อลูกค้าอยากสั่งของที่เคยสั่งแล้วอีกครั้ง เช่น "สั่งเหมือนเดิม" "เอาแบบครั้งที่แล้ว" "กันแดดหมดแล้วขออีกหลอด" "ตัวที่เคยซื้อชื่ออะไรนะ" "ขอเซ็ตเดิม"
---
## Goal
Rebuild the basket from a previous order quickly, at today's prices.

## Steps
1. Call `get_customer` and look at their recent orders. More than one → ask which.
2. Call `get_order_status` for that order to list what was in it. Leave out free gifts.
3. Confirm which items and quantities they want again.
4. Call `check_stock` for each. Out of stock or no longer sold → say so and offer the closest alternative via `stock-availability` or `product-question`.
5. Call `cart_add_item` once with all the items in one items list, marked as a reorder. Anything it refuses comes back per line with its reason.
6. Continue with `cart-and-checkout` from the read-back step. Prices and promotions are today's — say so if the total differs from last time.

## Knowledge to open
- `result-codes-and-customer-wording`

## Tools
`get_customer` · `get_order_status` · `check_stock` · `cart_add_item`
