---
display_name: ตอบตรง ๆ เมื่อแบรนด์ยังไม่มีสินค้าที่ต้องการ
slug: range-gap-honest-answer
description: ใช้เมื่อสิ่งที่ลูกค้าต้องการไม่มีใน SRICHAND หรือ SASI เช่น ถามหา BHA หรือ AHA เข้มข้น อะเซลาอิก อายครีม กันแดดทาตัว ครีมทาผิวกาย ยาแต้มสิว หรือเมื่อค้นหาสินค้าแล้วไม่พบ หรือเมื่อผลการจัดรูทีนแจ้งว่ามีช่องว่างของไลน์สินค้า (range gaps)
---
## Goal
Tell the truth, stay useful, and record the gap every time.

## Steps
1. Confirm it really is a gap: it appears in the routine result's range gaps, or `get_range_gaps` lists it, or `search_products` found nothing suitable. A multi-term search always reports how many products each term matched on its own — a term sitting at zero is the gap, even when the other terms returned plenty.
2. Say plainly that SRICHAND and SASI do not make this at the moment.
3. Offer the closest product in the range, with its honest limits.
4. If helpful, mention the generic external option — ingredient type and strength only. Never a brand, a product name or a specific shop's product.
5. A drug-class need (persistent acne, prescription-strength actives) → suggest a pharmacist or dermatologist instead; see `skin-reaction-or-medical-concern`.
6. Call `log_range_gap` — every time, whether or not the chat is linked to a member. The log is anonymous: pass the gap code, the concern, the skin type and age band if you know them, and whether you mentioned the generic option. Never pass a name, a member number or anything that identifies the customer.
7. Carry on helping with the rest of their routine or question.

## Avoid
- Stretching a product to cover a need it does not meet.
- Apologising at length. One honest sentence is enough.
- Skipping the log because the conversation moved on.

## Knowledge to open
- `range-gaps-and-generic-options`
- `claim-wording-thai-fda`

## Tools
`get_range_gaps` · `search_products` · `log_range_gap`
