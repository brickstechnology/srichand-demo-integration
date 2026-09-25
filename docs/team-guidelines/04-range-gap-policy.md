# 04 · Range-gap policy: what to do when Srichand has no product for the need

## The policy (agreed)
1. **Be honest.** Say plainly that Srichand / SASI does not currently make a product for this.
2. **Be useful.** You MAY describe a **generic** external option — an ingredient class, a strength, where to find it ("a 2% salicylic acid leave-on from a pharmacy").
3. **Never name a competitor** brand, product line or retailer-exclusive product. Never disparage one.
4. **Offer the closest in-range option** with its honest limits.
5. **Log it every time** with `log_range_gap`. The log is a second deliverable: a continuous, structured read on what Srichand's own customers need that Srichand doesn't sell.
6. Drug-class needs (persistent acne, azelaic acid above 10%, prescription retinoids) → "ask a pharmacist or dermatologist", not a product tip.

`recommend_routine` returns `range_gaps[]` whenever a customer's concerns touch a gap, including `generic_external_option_th` — use that text, adapted to the conversation.

## Example (Thai)
> ตรงนี้ขอบอกตามตรงนะคะ สำหรับสิวเสี้ยนบริเวณจมูก ส่วนผสมที่นิยมใช้ดูแลคือ BHA (ซาลิไซลิก แอซิด) แบบไม่ต้องล้างออก ซึ่งตอนนี้ศรีจันทร์ยังไม่มีผลิตภัณฑ์ลักษณะนี้โดยตรงค่ะ ที่ใกล้เคียงที่สุดในเครือคือ โทนเนอร์แพด Acne Sol ของศศิ ซึ่งมีซาลิไซลิก แอซิด แต่ไม่ได้ระบุความเข้มข้น เหมาะกับการดูแลต่อเนื่อง ถ้าใช้ครบ 6 สัปดาห์แล้วยังไม่พอใจ ลองมองหาผลิตภัณฑ์ BHA 2% จากร้านขายยาหรือร้านเครื่องสำอางทั่วไป ใช้สัปดาห์ละ 2–3 คืนได้ค่ะ

## Current gap list (from `range_gaps`; verified against the full official catalogue and INCI lists on 18 Sep 2026)
| Gap | Severity | What is true | Closest in range | Generic option |
|---|---|---|---|---|
| Dedicated leave-on **BHA** treatment under the SRICHAND brand | High | Salicylic acid *does* exist in the portfolio — it is on the official INCI of 13 products: Sunlution Acne Care (#32 of 54) and 12 SASI products (the Acne Sol line, Magic Matte concealers, Whitening toner pad) — but never as a SRICHAND leave-on treatment and never with a stated % | SASI Acne Sol Calming Toner Pad | 2% salicylic acid leave-on, 2–3 nights/week |
| **Azelaic acid** | Medium | None in any INCI list | Advanced Anti-Melasma Serum (marks only) | Azelaic acid 10% from a pharmacy; higher is a medicine |
| **Medical acne care** | Medium | Out of scope for any cosmetic range | Gentle routine + Sunlution Acne Care | Pharmacist / dermatologist |
| **Eye care** | Low | No eye cream or serum in the catalogue | Concealer (cosmetic cover only) | Fragrance-free eye cream with caffeine/peptides, or the face moisturiser |
| **Body sun care** | Low | Sunlution is face-size only (7–40 ml) | Sunlution Rosia (water-resistant) | Body sunscreen SPF50+ PA++++ 100 ml+ |

> Correction to earlier pitch notes: "no BHA anywhere in the range" and "the range's AHA is inside Super C" were both inaccurate. Salicylic acid (BHA) is on the INCI of 13 products; glycolic acid sits at INCI positions #24 of 29 (Super C gel cream) and #26 of 36 (Super C serum) — a low level, not an exfoliating dose. **A true exfoliating-acid step (AHA or BHA at a stated strength) is the real white space.**

## Reporting
`get_range_gaps` (or the `v_gap_demand` view) gives events per gap, distinct customers and a split by skin type — ready for a monthly R&D / range-planning dashboard. In the prototype these events are simulated.
