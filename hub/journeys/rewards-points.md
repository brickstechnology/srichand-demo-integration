---
display_name: แต้มสะสมและสิทธิ์สมาชิก Srichand Rewards
slug: rewards-points
description: ใช้เมื่อลูกค้าถามเรื่องแต้มหรือสิทธิ์สมาชิกของตัวเอง เช่น "มีแต้มเท่าไร" "แต้มหมดอายุเมื่อไหร่" "แลกอะไรได้บ้าง" "ซื้อเท่านี้ได้กี่แต้ม" "ทำไมแต้มยังไม่เข้า" "เลขสมาชิกของฉันคืออะไร" "ใช้แต้มลดได้เท่าไหร่"
---
## Goal
Show the customer their own points clearly, and explain the rules without inventing any.

## Steps
1. Call `get_loyalty`.
   - Chat not linked to a member → `membership-signup-and-linking`.
2. Answer what they asked: balance · member number · recent points activity · which entries expire when, as returned.
3. "How many points will I get?" → explain the earning rule from the rewards knowledge file and work it out from their basket total (`cart_view`) — points are earned on the net amount, not on shipping.
4. "What can I exchange?" → only the rewards the tool returns, marked affordable or not. Using points as a discount happens during `cart-and-checkout`.
5. "My points are missing" → explain the posting times from the rewards knowledge file. Past that time → `human-handover` with the order number or receipt date.
6. Rules questions (expiry, transfer, cash, levels, minimum age) → the rewards knowledge file. If the file says something is not published, say exactly that.

## Avoid
- Presenting the prototype's point value or reward list as official Srichand terms.
- Promising birthday or welcome benefits.

## Knowledge to open
- `srichand-rewards-rules`
- `result-codes-and-customer-wording`

## Tools
`get_loyalty` · `cart_view`
