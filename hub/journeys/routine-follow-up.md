---
display_name: ติดตามผลและปรับรูทีน
slug: routine-follow-up
description: ใช้เมื่อลูกค้ากลับมาเล่าผลหลังใช้ผลิตภัณฑ์หรืออยากปรับรูทีน เช่น "ใช้มาเดือนนึงแล้ว" "ยังไม่เห็นผลเลย" "ใช้แล้วผิวแห้ง ลอกนิดหน่อย" "อยากเพิ่มเรตินอล" "ตัวนี้หมดแล้วเปลี่ยนเป็นอะไรดี" "ลดขั้นตอนได้ไหม"
---
## Goal
Adjust the saved routine to what really happened, one change at a time.

## Steps
1. Call `get_customer` and read the active routine and skin profile. No saved routine → use `routine-recommendation` instead.
2. Ask what they actually use, how often, and how their skin feels now.
3. Decide which case this is:
   - Discomfort — dryness, mild peeling, slight stinging: pause the newest active, keep cleanser, a barrier moisturiser and sunscreen, reintroduce slowly later. Rash, swelling, burning or anything severe → `skin-reaction-or-medical-concern`.
   - No visible change yet: check how long and how consistently; set honest expectations; keep the routine steady rather than adding more.
   - Wants more: add one active only, with the introduction schedule from the ingredient knowledge file.
   - Wants less or cheaper: reduce steps or budget.
4. Call `recommend_routine` with the updated inputs. Check combinations with `check_ingredient_conflicts` when an active is added.
5. If what they told you changes their profile (a new reaction, pregnancy, a new goal) and profile storage is consented → `save_skin_profile`.
6. When they accept → `save_routine`.
7. Products they need to buy → `cart-and-checkout`. Products they are re-buying → `reorder`.

## Knowledge to open
- `ingredient-and-layering-facts`
- `claim-wording-thai-fda`
- `skin-observation-wording`

## Tools
`get_customer` · `recommend_routine` · `check_ingredient_conflicts` · `save_skin_profile` · `save_routine`
