---
display_name: ประเมินผิวจากการตอบคำถาม (ไม่ใช้รูป)
slug: skin-analysis-questionnaire
description: ใช้เมื่อลูกค้าไม่สะดวกหรือไม่ยินยอมส่งรูป อายุต่ำกว่า 20 ปี รูปที่ส่งมาใช้ไม่ได้ หรือพูดว่า "ไม่อยากส่งรูป" "ถามเอาได้ไหม" "เล่าให้ฟังแล้วช่วยแนะนำได้ไหม" "ไม่มีรูปหน้าสด"
---
## Goal
Understand the customer's skin from their own answers, record it when allowed, and hand over to the routine journey.

## Steps
1. Reassure: answering a few questions works well and no photo is needed.
2. If the chat is linked to a member and they want it remembered, ask for the `skin_profile_storage` consent and call `record_consent` after an explicit yes. No consent, or chat not linked → carry on, but save nothing.
3. Ask one question at a time, in plain words:
   a. A few hours after washing: shiny all over, shiny only on the T-zone, comfortable, or tight and flaky?
   b. Does skin often sting, flush or itch with new products?
   c. Breakouts: never, sometimes, often? Where?
   d. Marks left behind, dark spots or patches?
   e. What would they most like to change — up to three, in order.
   f. Current morning and evening products.
   g. How many steps will they really do on a tired night?
   h. Comfortable spend per product.
   i. Makeup: daily, sometimes, never. Outdoor sport or swimming?
   j. Where relevant: pregnant or nursing?
4. Map the answers to a skin type and concern codes using the glossary; call `list_reference_data` if unsure of a code.
5. Play back a two-line summary and let them correct it.
6. If consent was given: `save_skin_profile`, then `save_skin_analysis` with image count 0, every finding at low confidence and marked as self-reported.
7. Continue with `routine-recommendation`.

## If the customer is under 20
- Never ask for a photo.
- Keep the routine to three steps.
- Frequent or painful breakouts → suggest a parent and a pharmacist or dermatologist, via `skin-reaction-or-medical-concern`.

## Knowledge to open
- `concern-and-skin-type-glossary`
- `privacy-consent-and-data-rules`
- `skin-observation-wording`

## Tools
`record_consent` · `list_reference_data` · `save_skin_profile` · `save_skin_analysis`
