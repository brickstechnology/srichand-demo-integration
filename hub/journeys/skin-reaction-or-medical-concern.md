---
display_name: อาการแพ้ ปัญหาผิวที่ควรพบแพทย์ และคำถามเชิงการแพทย์
slug: skin-reaction-or-medical-concern
description: ใช้เมื่อลูกค้าเล่าอาการผิดปกติหลังใช้ผลิตภัณฑ์ หรือขอให้วินิจฉัย/รักษา เช่น "ใช้แล้วแพ้" "ผื่นขึ้น" "แสบ แดง คัน" "หน้าบวม" "สิวอักเสบหนักมาก" "เป็นสิวหัวช้าง" "นี่ใช่ฝ้าไหม" "ไฝเปลี่ยนสี" "ท้องอยู่ใช้ได้ไหม" "ให้นมลูกอยู่" "กินยารักษาสิวอยู่ใช้ได้ไหม" "ช่วยดูหน่อยว่าเป็นโรคอะไร"
---
## Goal
Safety first. Never diagnose, never advise treatment; get the customer to the right help and keep the rest of their routine gentle.

## Steps
1. A reaction to a product:
   a. Tell them to stop using it now and rinse with plain water.
   b. Swelling of lips, eyes or face, trouble breathing, blisters, or a spreading rash → advise medical care immediately. Say nothing else first.
   c. Milder stinging, redness or itching → suggest a pharmacist or doctor if it has not settled in a day or two.
   d. Ask which product and when it started. Do not guess the cause or blame an ingredient.
   e. Hand over with `human-handover` so staff can record the case: product, when bought and order number if they have it, what happened.
2. "What is this? Is it melasma, rosacea, an infection?" → explain that you can describe what is visible but cannot say what it is; use the "see a doctor" table in the observation knowledge file.
3. Severe, painful, scarring or long-lasting breakouts → a dermatologist or pharmacist is the right help; cosmetics only support. If they still want a routine, keep it to a gentle cleanser, a light moisturiser and sunscreen via `routine-recommendation`, and record the gap with `range-gap-honest-answer` (medical acne care).
4. Pregnant or nursing → no retinoids; pass that flag when recommending; every other active: "confirm with your doctor".
5. On prescription or acne medication → their doctor or pharmacist decides what can be combined; offer only gentle basics.
6. Return to normal help only when the customer is ready.

## Avoid
- Naming a condition, a medicine or a dose.
- "It's normal, keep using it."
- Recommending a new product in the same breath as a reaction.

## Knowledge to open
- `skin-observation-wording`
- `ingredient-and-layering-facts`
- `advisor-scope-and-limits`
- `store-policies`

## Tools
None required. `get_order_status` only if the customer offers an order number for the hand-over.
