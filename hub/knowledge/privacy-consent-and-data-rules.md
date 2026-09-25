---
title: ความยินยอม รูปใบหน้า ผู้เยาว์ และการลบข้อมูล (PDPA)
slug: privacy-consent-and-data-rules
use_when: ใช้เมื่อเรื่องเกี่ยวกับรูปใบหน้า การขอความยินยอม ข้อความยินยอมที่ต้องใช้ ลูกค้าอายุต่ำกว่า 20 ปี ระยะเวลาเก็บข้อมูล สิ่งที่เก็บและไม่เก็บ การลบข้อมูล หรือเมื่อลูกค้าถามว่า "เอารูปไปทำอะไร" "เก็บข้อมูลอะไรบ้าง" "ลบให้หรือยัง"
---
# Privacy rules (PDPA)

Status: working draft, pending legal review.

## Position
A face photo used only to look at skin is not clearly "biometric data" under Thai law, but the skin findings may count as health data and enforcement in the cosmetics sector is active. Treat the photo and everything derived from it as sensitive personal data.

## The consents
| Consent | Needed for | Exact Thai text the customer agrees to |
|---|---|---|
| Face photo analysis | Looking at any face photo | ฉันยินยอมโดยชัดแจ้งให้ศรีจันทร์ใช้ภาพถ่ายใบหน้าของฉันเพื่อวิเคราะห์ลักษณะผิวที่มองเห็นได้และแนะนำผลิตภัณฑ์เท่านั้น ไม่ใช้เพื่อระบุตัวตน ภาพจะถูกลบภายใน 24 ชั่วโมงหลังวิเคราะห์เสร็จ ฉันสามารถถอนความยินยอมหรือขอลบข้อมูลได้ทุกเมื่อโดยพิมพ์ "ลบข้อมูลของฉัน" การไม่ให้ความยินยอมไม่กระทบการใช้บริการอื่น (สามารถตอบแบบสอบถามแทนการส่งภาพได้) |
| Cross-border processing | Looking at any face photo (the AI provider may be abroad) | ฉันรับทราบว่าภาพและข้อมูลของฉันจะถูกประมวลผลโดยผู้ให้บริการระบบ AI ซึ่งอาจตั้งอยู่ในประเทศที่มีมาตรฐานการคุ้มครองข้อมูลส่วนบุคคลไม่เทียบเท่าประเทศไทย และฉันยินยอมให้ส่งข้อมูลดังกล่าวภายใต้สัญญาประมวลผลข้อมูลที่ห้ามเก็บรักษาและห้ามนำไปฝึกโมเดล |
| Skin profile storage | Remembering what the customer told us (skin type, goals, reactions) | ฉันยินยอมให้ศรีจันทร์เก็บข้อมูลสภาพผิว เป้าหมาย และประวัติการแพ้ที่ฉันให้ไว้ เพื่อใช้ปรับคำแนะนำให้เหมาะกับฉันในครั้งต่อไป |
| Marketing | Promotions on LINE — never assumed, never pre-ticked | ฉันยินยอมรับข่าวสาร โปรโมชั่น และสิทธิพิเศษจากศรีจันทร์ผ่าน LINE |
| Rewards terms | Becoming a Srichand Rewards member | ฉันยอมรับข้อกำหนดและเงื่อนไขของ Srichand Rewards และนโยบายความเป็นส่วนตัว |

Rules for every consent: explicit yes in the chat; one consent per question; separate from each other; refusing never blocks other services; withdrawing is as easy as giving.

## Minors
- Under 20 is a minor. Default for under-20s: no photo — use the questionnaire.
- Under 10: a parent or guardian must consent to everything.
- 10–19: a guardian must confirm before any photo analysis.
- Srichand Rewards: minimum age 16, and 16–19 needs a guardian to confirm. (Srichand's own documents conflict: the published terms say 20+, the LINE sign-up form says 16+.)
- If age is unknown, ask the customer to confirm they are 20 or older before offering photo analysis.

## What is kept and what is never kept
| Kept | Never kept |
|---|---|
| An opaque reference to the image, its checksum, image count, expiry and deletion time | The image itself in the database, thumbnails, face templates, location or camera data |
| Quality flags, observed skin type, undertone, depth, a short Thai summary | Any diagnosis, identity attribute, age estimate |
| Findings: concern, face zone, severity, confidence | |
| The consent trail: type, version, exact text, time, withdrawal | |
The raw image is deleted within 24 hours of analysis. Photos and findings are never used for marketing, testimonials or model training, and never for identification.

## Deleting data
When a customer asks to delete their data: photo, profile and cross-border consents are withdrawn; image references, findings, recommendations, saved routines and the skin profile are erased; gap statistics are anonymised.
Kept by law: orders, payments and the points ledger.
Access or correction requests are answered within 30 days by the data-protection contact: dpo.srichand@aktivist.co.th.

## Other people's photos
A photo of someone else, of a child, or with other people in frame is not analysed. Explain that only the customer's own face, with their own consent, can be looked at.
