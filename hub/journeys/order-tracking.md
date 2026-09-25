---
display_name: ติดตามคำสั่งซื้อและพัสดุ
slug: order-tracking
description: ใช้เมื่อลูกค้าถามสถานะคำสั่งซื้อหรือพัสดุ เช่น "ของถึงไหนแล้ว" "ส่งหรือยัง" "ขอเลขพัสดุ" "สั่งเมื่อวานได้วันไหน" "ทำไมยังไม่ได้ของ" "ออเดอร์ล่าสุดสถานะอะไร" "ส่งกับขนส่งอะไร"
---
## Goal
Tell the customer where their parcel is, in two or three lines.

## Steps
1. Call `get_order_status`. No order number given → it returns the latest order. If they have several recent orders (`get_customer` lists them) and it is unclear which → ask.
2. Answer with: order number · status in plain Thai · courier and tracking number · the latest courier event and where · the estimated delivery date, if there is one.
3. Special cases:
   - Not paid yet → `payment-problem`.
   - Paid or packing, not shipped → say it is being prepared; give typical timing only as a guide, from the store-policies file.
   - Marked delivered but not received, a failed delivery attempt, or long past the estimate → `human-handover` with the order number and tracking number.
   - Wrong, damaged or missing items → `returns-refunds-cancellations`.
4. Orders of other people are never shown. If the number does not belong to this member, say the order was not found in their account.

## Knowledge to open
- `store-policies`
- `result-codes-and-customer-wording`

## Tools
`get_order_status` · `get_customer`
