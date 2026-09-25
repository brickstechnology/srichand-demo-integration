---
display_name: ปัญหาการชำระเงิน / QR หมดอายุ
slug: payment-problem
description: ใช้เมื่อลูกค้ามีปัญหาเรื่องการจ่ายเงิน เช่น "จ่ายไม่ทัน" "QR หมดอายุ" "ขอ QR ใหม่" "สแกนไม่ได้" "โอนแล้วแต่สถานะยังไม่เปลี่ยน" "ตัดบัตรไม่ผ่าน" "เปลี่ยนวิธีจ่ายได้ไหม" "ออเดอร์ค้างชำระ"
---
## Goal
Find out what state the payment is in and get the customer to a paid order, or to staff.

## Steps
1. Call `get_order_status` (latest order, or the number they give).
2. Read the payment state:
   - Waiting and still inside the payment window → tell them how long is left.
   - Window expired → explain, with the wording in the result-codes file, that this order can no longer be paid: it is cancelled automatically, the items go back to the cart, and any points or coupon are returned. Ask whether they want to order again. On yes → ask the payment method and call `create_order`; it clears the expired order and creates the new one. Report the new total, and say so if it differs from before.
   - Already paid → confirm, and continue with `order-tracking` if they ask where it is.
3. They want another payment method → the order has to be placed again with that method once the current one has lapsed; explain, then as above.
4. "I paid but it still shows unpaid" → ask when and how they paid. Do not mark anything as paid yourself. If it is still unpaid after a few minutes → `human-handover` with the order number, amount, time and method.
5. Card declined or QR will not scan → suggest another accepted method from the store-policies file; if it persists → `human-handover`.

## Avoid
- Asking for card numbers, OTPs, banking screenshots with account details, or any credentials.
- Using the demo payment confirmation unless the presenter says the payment was made.

## Knowledge to open
- `store-policies`
- `result-codes-and-customer-wording`

## Tools
`get_order_status` · `create_order`
