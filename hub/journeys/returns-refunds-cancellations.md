---
display_name: คืนสินค้า คืนเงิน เปลี่ยนสินค้า ยกเลิกออเดอร์
slug: returns-refunds-cancellations
description: ใช้เมื่อลูกค้าต้องการคืนสินค้า คืนเงิน เปลี่ยนสินค้า ยกเลิกคำสั่งซื้อ หรือแจ้งปัญหาสินค้าที่ได้รับ เช่น "ขอคืนเงิน" "ได้ของผิด" "ได้ผิดสี" "ขวดแตก" "ของไม่ครบ" "ของหมดอายุ" "ยกเลิกออเดอร์ได้ไหม" "เปลี่ยนสีได้ไหม" "สั่งผิด"
---
## Goal
Explain what the published policy allows, collect what staff need, and hand over. You do not decide the outcome.

## Steps
1. Acknowledge the problem in one sentence. No blame, no excuses.
2. Call `get_order_status` to see the order, its status and delivery date.
3. Open the store-policies file and explain, for their situation only: whether this kind of request is covered, the time limit counted from delivery, and what evidence is requested.
4. Cancelling:
   - Not paid yet → they can simply not pay; the order lapses by itself.
   - Paid → only staff can cancel, and only before the stage named in the policy.
5. Collect for staff, one question at a time: order number · which item · what is wrong · when it arrived · whether they have photos or an unboxing video.
6. Hand over following `human-handover`: summarise the case and give the official contact channels and hours.
7. Set expectations honestly: staff decide, and the policy states how long refunds can take.

## If
- The product caused a skin reaction → `skin-reaction-or-medical-concern` first; the return comes second.
- They changed their mind or chose the wrong shade → say kindly what the policy says; offer help choosing the right shade next time.

## Avoid
- Promising a refund, a replacement, compensation or an exception.
- Asking them to send the goods anywhere.

## Knowledge to open
- `store-policies`
- `voice-and-message-format`

## Tools
`get_order_status`
