---
display_name: ใส่ตะกร้า สั่งซื้อ และชำระเงิน
slug: cart-and-checkout
description: ใช้เมื่อลูกค้าจะซื้อสินค้า เช่น "เอาตัวนี้" "ใส่ตะกร้าให้หน่อย" "สั่งเลย" "สรุปยอดให้หน่อย" "จ่ายยังไง" "ใช้โค้ดนี้ได้ไหม" "ใช้แต้มลดได้ไหม" "เอาออกจากตะกร้าตัวนึง" "เปลี่ยนเป็น 2 ชิ้น"
---
## Goal
Take the customer from "I'll take it" to a placed order, with no surprises about the total.

## Before you start
The chat must be linked to a member. If it is not → `membership-signup-and-linking`.

## Steps
1. Make sure you have the exact variant (size, shade) from `get_product` or `match_shade`. Unsure → ask.
2. Call `cart_add_item` ONCE with all the items in one items list, marking where they came from (advisor recommendation, search, reorder, promotion). The result tells you which lines went in and which were refused — explain each refusal using the result-codes file and offer the alternative. Only use the single-item form when there really is one item.
3. Call `cart_view`, then `get_promotions` with the basket total.
4. Ask whether they have a coupon and whether they want to use points. Balance → `get_loyalty`.
5. Ask which payment method they prefer, from the methods in the store-policies file.
6. Read the order back in one message: items and quantities · subtotal · coupon and points · shipping · total to pay · payment method. Ask: "ยืนยันสั่งซื้อไหมคะ"
7. Only after a clear yes → call `create_order` once.
   - Success → give the order number, amount, how long they have to pay, and any free gift included.
   - Refused → explain with the result-codes file, fix the cause, read the new total back, and ask again.
8. After payment is confirmed (in the demo: `confirm_payment_mock`, only when the presenter says the payment was made) → confirm it is paid and how many points were earned.

## Changing the cart
- Change a quantity → `cart_update_item`, then show the cart again.
- Remove items → `clear_cart_item` with every SKU they dropped in one call. Only pass all = true when they clearly asked to start over; that one needs approval.
- Changing a shade or size → `clear_cart_item` for the old variant, `cart_add_item` for the new one.
- An order that is already placed cannot be edited → `human-handover`.

## Avoid
- Calling `create_order` without an explicit yes to the read-back total, or twice for one yes.
- Adding items to reach free shipping unless they asked.
- Quoting a total you calculated yourself — totals come from the tools.

## Knowledge to open
- `store-policies`
- `srichand-rewards-rules`
- `result-codes-and-customer-wording`

## Tools
`get_product` · `cart_add_item` · `cart_update_item` · `clear_cart_item` · `cart_view` · `get_promotions` · `get_loyalty` · `create_order` · `confirm_payment_mock`
