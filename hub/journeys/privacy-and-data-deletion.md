---
display_name: ข้อมูลส่วนตัว การลบข้อมูล และการรับข่าวสาร
slug: privacy-and-data-deletion
description: ใช้เมื่อลูกค้าถามหรือขอเกี่ยวกับข้อมูลส่วนตัวของตัวเอง เช่น "ลบข้อมูลของฉัน" "ลบรูปให้หรือยัง" "เอารูปไปทำอะไร" "เก็บข้อมูลอะไรของฉันบ้าง" "ขอถอนความยินยอม" "ไม่อยากรับข่าวสารแล้ว" "เลิกส่งโปรมาได้ไหม" "อยากรับโปรโมชั่น"
---
## Goal
Answer privacy questions plainly and carry out deletion or opt-out requests straight away.

## Steps
1. "What do you keep? What happens to my photo?" → answer from the privacy knowledge file. For their own record, `get_customer` shows which consents are active and since when.
2. "Delete my data" / "withdraw my consent":
   a. Tell them in one message what will be erased and what is kept by law (from the privacy knowledge file), and that it cannot be undone.
   b. Ask once: "ยืนยันให้ลบเลยไหมคะ"
   c. On yes → call `withdraw_consent_and_erase`.
   d. Confirm what was erased. Their orders and points remain, and they can still shop and ask questions.
3. "Stop sending promotions" → call `set_marketing_preference` with opt-in false immediately. No questions, no persuasion. Confirm that order and service messages continue.
4. "I want promotions" → ask for an explicit yes to the marketing consent sentence, then `set_marketing_preference` with opt-in true and that sentence.
5. A copy of their data, a correction, or a complaint about data handling → give the data-protection contact from the privacy knowledge file and the response time; hand over with `human-handover`.

## Avoid
- Trying to talk them out of deleting or opting out.
- Deleting without the single confirmation in step 2.
- Saying everything is deleted — orders and points are kept, and you must say so.

## Knowledge to open
- `privacy-consent-and-data-rules`

## Tools
`get_customer` · `withdraw_consent_and_erase` · `set_marketing_preference`
