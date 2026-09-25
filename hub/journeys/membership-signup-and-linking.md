---
display_name: สมัครสมาชิก / เชื่อมบัญชีสมาชิกกับแชต
slug: membership-signup-and-linking
description: ใช้เมื่อลูกค้าอยากสมัครสมาชิก Srichand Rewards หรือเป็นสมาชิกอยู่แล้วแต่แชตนี้ยังไม่เชื่อมบัญชี เช่น "สมัครสมาชิกยังไง" "อยากสะสมแต้ม" "สมัครให้หน่อย" "เป็นสมาชิกแล้วทำไมดูแต้มไม่ได้" "เชื่อมบัญชีให้หน่อย" หรือเมื่อระบบแจ้งว่าแชตนี้ยังไม่ได้จับคู่กับบัญชีสมาชิกระหว่างที่ลูกค้าขอดูแต้ม ออเดอร์ หรือจะสั่งซื้อ
---
## Goal
A new person leaves with a member number; an existing member is passed to staff to be linked. Never expose someone else's account.

## Steps
1. Ask first: "เคยสมัครสมาชิก Srichand Rewards ไว้แล้วหรือยังคะ"

### Already a member
2. Do not look anyone up by phone number or name, and do not confirm whether a number is registered.
3. Explain that staff link the chat to their membership after a quick check, and hand over with `human-handover`. If they know their member number, include it in the hand-over summary.
4. Meanwhile, product advice, stock and promotions still work.

### Not a member yet
2. Collect, one question at a time: first name (last name optional) · Thai mobile number · birth date (convert a Buddhist-era year to the Gregorian year) · email (optional).
3. Age: below the minimum → explain kindly that they cannot join yet. Aged 16–19 → a parent or guardian must confirm in the chat.
4. Show the summary of the terms from the rewards knowledge file and ask for an explicit yes.
5. Ask separately, with no default: "ต้องการรับข่าวสารและโปรโมชั่นทาง LINE ไหมคะ"
6. Call `register_member` once, passing the exact Thai sentence they agreed to.
7. Success → give them their member number and say that staff will link this chat to it shortly; after that, points, orders and the cart work here. Use the customer message the tool returns as a base.
8. Refused → explain with the result-codes file. "Number already registered" → treat as "Already a member" above, and reveal nothing about that account.

## Avoid
- Signing up someone who is already linked (if `get_customer` works in this chat, they are a member).
- Calling `register_member` twice for the same person.
- Saying the phone number is verified — the prototype sends no SMS code.

## Knowledge to open
- `srichand-rewards-rules`
- `privacy-consent-and-data-rules`
- `result-codes-and-customer-wording`

## Tools
`get_customer` · `register_member`
