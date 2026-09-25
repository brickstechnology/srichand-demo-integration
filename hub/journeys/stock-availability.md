---
display_name: เช็กของ มีของไหม เข้าเมื่อไหร่
slug: stock-availability
description: ใช้เมื่อลูกค้าถามว่าสินค้ามีของไหม เช่น "มีของไหม" "สีนี้หมดหรือยัง" "ของเข้าเมื่อไหร่" "ขนาดใหญ่ยังมีไหม" "สั่งได้กี่ชิ้น" "ทำไมกดสั่งไม่ได้"
---
## Goal
Tell the customer exactly what can be ordered now, and what to do if it cannot.

## Steps
1. Identify the exact size and shade: `get_product` lists the variants. Ask if it is unclear which one they mean.
2. Call `check_stock` for that variant.
3. Answer:
   - Available → say so. Low stock → give the number left.
   - Out of stock → give the restock date if one is returned; otherwise say there is no date yet.
4. Offer alternatives from the same `get_product` result: another size, a twin pack or sachet box, another shade, or a set that contains it.
5. A size that is not sold on its own → explain it comes only in a pack or set, and show that pack.
6. Wants to buy what is available → `cart-and-checkout`.

## Avoid
- Promising a restock date the tool did not give.
- "Almost sold out" pressure. State the number and stop.

## Knowledge to open
- `result-codes-and-customer-wording`

## Tools
`get_product` · `check_stock`
