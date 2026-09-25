# 02 · Thai FDA cosmetic-claims guardrails

> **Status: draft for legal review.** Built from the Cosmetics Act B.E. 2558, the Thai FDA cosmetic advertising manual (B.E. 2559 edition read in full; B.E. 2567 update via secondary transcriptions) and related Acts. Full analysis, sources and the 19-item "needs lawyer review" list: `research/findings/thai_regulatory.md`. Bricks is not a law firm.

## Why this matters
- Cosmetics Act s.41 prohibits advertising that is false, exaggerated, or implies a therapeutic effect. Breach: up to 1 year imprisonment and/or THB 100,000 (s.84), plus up to THB 10,000 per day for a continuing offence (s.88). It applies to *any person* who advertises — assume a brand-operated chat reply counts.
- A claim to treat, prevent or cure makes the product a **drug** under the Drug Act.
- Presenting as a doctor or diagnosing is an offence under the Medical Profession Act s.26 (up to 3 years).

## Hard rules (put these in the system prompt)
1. Never say a cosmetic **treats, cures, prevents or reduces** acne, melasma, freckles, inflammation, rash, allergy or any disease. Forbidden stems: `รักษา`, `ป้องกันสิว`, `ลดสิว`, `ลดการเกิดสิว`, `ลดปัญหาสิว`, `ลดการอักเสบ`, `ลดฝ้า`, `รักษาฝ้า`, `ฆ่าเชื้อ`, `ยับยั้งแบคทีเรีย`.
2. No **mechanism or structure** claims: collagen/elastin stimulation, melanin or tyrosinase inhibition, cell repair/renewal, DNA, "fights free radicals", lifting/V-shape, fat loss, "penetrates to the dermis".
3. Use **appearance language**: `แลดู…`, `ดู…ขึ้น`, `ช่วยให้ผิวแลดูกระจ่างใส / เรียบเนียน / ชุ่มชื้น`.
4. Add the FDA qualifiers where relevant: **"ผลลัพธ์ขึ้นอยู่กับสภาพผิวของแต่ละบุคคล"**; whitening cannot change natural skin tone; anti-wrinkle effects last only while the product is in use.
5. No superlatives (`ดีที่สุด`, `อันดับ 1` without evidence), no guarantees (`เห็นผล 100%`), no invented time promises (`ขาวใน 7 วัน`). A time-bound claim may be quoted **only** verbatim from `product_claims` together with its official test footnote.
6. No absolutes on safety: not `ปลอดภัย 100%`, `ไม่ระคายเคือง`, `ไม่แพ้`, `ไร้ผลข้างเคียง`. Say what was tested: "ผ่านการทดสอบการระคายเคืองในอาสาสมัคร 32 คน" (quote `products.tested_claims_th`).
7. Never say `อย. รับรอง`. Notification is not approval.
8. No comparison with injections, Botox, laser or clinic procedures. No doctor endorsement. No before/after promises.
9. Sunscreen: quote only the labelled value (e.g. "SPF50+ PA++++") and give correct-use advice (amount, reapply). Never "กันแดด 100%" or "ไม่ต้องทาซ้ำ".
10. **Observe, don't diagnose.** Say "จากภาพ ผิวดูมีความมันบริเวณทีโซน และมีตุ่มแดงบางจุด (เป็นการสังเกตจากภาพ ไม่ใช่การวินิจฉัย)". Never "คุณเป็นสิวอักเสบ / ฝ้า / โรซาเซีย / ผิวหนังอักเสบ".

## Wording table (most used rows)
| Don't say | Say instead | Basis |
|---|---|---|
| รักษาสิว · ลดสิว · ป้องกันสิว | "สูตรสำหรับผิวเป็นสิว" · "เหมาะสำหรับผิวมัน เป็นสิวง่าย" · "Anti-acne" left untranslated | Guideline |
| ลดปัญหาสิว · ลดการอุดตัน | "ช่วยขจัดสิ่งสกปรกและความมันส่วนเกิน" · "ทำความสะอาดรูขุมขน ผิวแลดูเรียบเนียน" | Prohibited side: guideline; alternative: by analogy — **confirm with counsel** |
| ลดการอักเสบ · ลดผื่นแดง · รักษาผิวแพ้ง่าย | "ให้ความชุ่มชื้น ช่วยให้ผิวรู้สึกสบาย" · "สำหรับผิวบอบบาง แพ้ง่าย" | Guideline |
| ขาวถาวร · ขาวใน 7 วัน | "ผิวแลดูกระจ่างใสขึ้นเมื่อใช้อย่างต่อเนื่อง ผลลัพธ์ขึ้นอยู่กับสภาพผิวของแต่ละบุคคล" | Guideline |
| ยับยั้งการสร้างเมลานิน | "ช่วยให้ผิวแลดูกระจ่างใส" · "รอยดำแลดูจางลง" | Guideline |
| รักษาฝ้า · ลดฝ้า กระ | "จุดด่างดำแลดูจางลง" + individual-results qualifier; for sunscreen "ช่วยปกป้องผิวจากแสงแดด" | Guideline |
| ลบริ้วรอย · ป้องกันริ้วรอย | "ช่วยให้ริ้วรอยแลดูลดเลือน" + "เห็นผลเฉพาะช่วงที่ใช้ผลิตภัณฑ์" | Guideline |
| กระตุ้นคอลลาเจน | "ผิวแลดูเต่งตึง เรียบเนียน" | Guideline |
| ต่อต้านอนุมูลอิสระ | "มีสารแอนติออกซิแดนท์" (only if present) | Guideline |
| ซึมลึกถึงชั้นหนังแท้ | "เนื้อบางเบา ซึมซาบไว ไม่เหนียวเหนอะหนะ" | Guideline |
| ยกกระชับ หน้าเรียว V-shape | "ช่วยให้ผิวหน้าดูกระชับอย่างเป็นธรรมชาติ" | Guideline |
| ปลอดภัย 100% · ไม่ระคายเคือง | "ผ่านการทดสอบการระคายเคือง… ทั้งนี้การแพ้เป็นปัจจัยเฉพาะบุคคล" | Guideline |
| อย. รับรอง | "จดแจ้งแล้ว" (+ notification number if known) | Guideline |
| แพทย์ผิวหนังแนะนำ · "หมอผิว AI" | "ผู้ช่วยแนะนำความงาม (ระบบ AI)" | Guideline + Medical Profession Act |
| จบทุกปัญหาผิว | "ช่วยบำรุงผิวให้ดูสุขภาพดี" | Guideline |
| ปรับสมดุลไมโครไบโอม / ค่า pH ผิว | "ช่วยฟื้นสมดุลผิวจากความแห้งกร้าน" | Guideline |

The full 34-row table is in `research/findings/thai_regulatory.md` §1.4.

## Using official Srichand copy
- `product_claims.claim_th` and `products.description_th` are the brand's own published wording. Prefer quoting or lightly shortening them over writing new claims.
- **Caveat for the client:** some live srichand.com copy uses phrasing that the 2567 guideline appears to restrict (e.g. "ลดการสร้างเม็ดสีเมลานิน", "ช่วยลดการเกิดฝ้า กระ", "เติมเต็มคอลลาเจน", "กระตุ้นการสร้างคอลลาเจน"). The advisor should **not** repeat those sentences; rephrase with the table above. This is worth flagging to Srichand's regulatory team as a by-product of the project.
- The `ingredients.what_it_does_en` dictionary is **internal reasoning material** written in plain science language. It must be re-worded through this guideline before anything reaches a customer.

## Output validation (engineering)
Run every outgoing message through a blocklist before sending; on a hit, regenerate once, then fall back to a safe template.
```
รักษา|หายขาด|ป้องกันสิว|ลดสิว|ลดการเกิดสิว|ลดปัญหาสิว|ลดการอักเสบ|ฆ่าเชื้อ|ยับยั้ง|รักษาฝ้า|ลดฝ้า|ขาวถาวร|ขาวใน\s*\d+|กระตุ้น(การสร้าง)?คอลลาเจน|
ซ่อมแซมเซลล์|ระดับเซลล์|ต่อต้านอนุมูลอิสระ|ซึมลึกถึงชั้นหนังแท้|ปลอดภัย\s*100|ไม่ระคายเคือง(?!.*ทดสอบ)|ไม่แพ้|ไร้ผลข้างเคียง|อย\.?\s*รับรอง|ดีที่สุด|อันดับ\s*1|
การันตี|เห็นผล\s*100|เทียบเท่า(ฉีด|เลเซอร์|โบท็อกซ์)|แพทย์แนะนำ|หมอแนะนำ|คุณเป็น(สิวอักเสบ|ฝ้า|โรค)
```

## Needs lawyer review before launch (top items)
1. Whether a 1:1 chat reply is "advertising" under s.41 — we assume yes.
2. Verify all 2567-edition rows against the official PDF (we could not open it; rows are from secondary transcriptions).
3. Acceptable Thai wording for congestion/blackheads and for "blemish-prone" positioning.
4. Whether quoting the brand's existing time-bound test claims ("ใน 7 วัน") in chat is acceptable.
5. The 2024 Ministerial Regulation on penetration claims — Royal Gazette status unconfirmed.
