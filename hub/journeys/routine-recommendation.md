---
display_name: แนะนำผลิตภัณฑ์และจัดรูทีน
slug: routine-recommendation
description: ใช้เมื่อลูกค้าขอให้แนะนำสกินแคร์ เมคอัพ หรือจัดรูทีนให้ เช่น "ผิวมันใช้อะไรดี" "เป็นสิวง่ายควรใช้ตัวไหน" "จัดเซ็ตให้หน่อย" "เช้า-เย็นต้องทาอะไรบ้าง" "งบ 300 ได้อะไรบ้าง" "อยากหน้าใส" "แนะนำกันแดดหน่อย" หรือหลังจากวิเคราะห์ผิวเสร็จแล้ว
---
## Goal
Give a routine the customer will actually follow. The selection tool chooses the products; you explain them.

## Steps
1. Collect the inputs. Use what `get_customer` already holds (skin profile, latest analysis); ask only for what is missing, one question at a time:
   - concerns in order of priority (up to three) · skin type · sensitivity
   - budget per product · how many steps they will do · makeup wanted or not
   - reacts to fragrance? · outdoor sport or swimming? · pregnant or nursing?
2. Call `recommend_routine` with those inputs. Never pick or swap products yourself.
3. Present the result: morning steps, then evening steps, one line each — product, why it fits (from the tool's reasons, re-worded with the claim rules), price as returned.
4. A pick marked as needing a shade match → say the shade still has to be chosen and offer `shade-matching`.
5. Steps the tool left unfilled → if it is an essential step, say honestly that nothing fits their filters and ask whether to relax the budget or the fragrance filter.
6. Layering cautions from the tool → explain them simply: which nights, what not to combine, sunscreen.
7. `range_gaps` in the result → follow `range-gap-honest-answer` for each one.
8. Refer-out rules in the result → mention when the customer's description matches.
9. Ask what they would change. To change anything, call `recommend_routine` again with new inputs.
10. Questions about one product → `get_product`. Questions about combining products → `check_ingredient_conflicts`.
11. When they accept and the chat is linked to a member → `save_routine` (include gap slots), and tell them you will check in after about four weeks.
12. Offer to put the products in the cart → `cart-and-checkout`.

## Avoid
- More steps or a higher spend than they asked for.
- Promising results or timelines.
- Recommending from memory when the tool returned nothing.

## Knowledge to open
- `claim-wording-thai-fda`
- `ingredient-and-layering-facts`
- `concern-and-skin-type-glossary`
- `range-overview`

## Tools
`get_customer` · `list_reference_data` · `recommend_routine` · `get_product` · `check_ingredient_conflicts` · `save_routine`
