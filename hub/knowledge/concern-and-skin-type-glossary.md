---
title: อภิธานศัพท์ — คำที่ลูกค้าพูด → รหัสปัญหาผิว ประเภทผิว และค่าที่ระบบใช้
slug: concern-and-skin-type-glossary
use_when: ใช้เมื่อต้องแปลงคำพูดของลูกค้า เช่น "หน้ามัน" "สิวอุดตัน" "รอยสิว" "ฝ้า" "หมองคล้ำ" "ผิวแห้งลอก" "แพ้ง่าย" ให้เป็นรหัสปัญหาผิว ประเภทผิว โทนสี ระดับความเข้มของผิว หรือจำนวนขั้นตอนรูทีนที่ระบบรองรับ
---
# Glossary of values the system understands

## Skin concerns
| What customers say | Code | Notes |
|---|---|---|
| หน้ามัน หน้าเยิ้ม มันเงา มันตอนบ่าย | excess-sebum-shine | |
| รูขุมขนกว้าง | enlarged-pores | |
| สิวเสี้ยน สิวอุดตัน สิวหัวดำ หัวขาว ผิวไม่เรียบเป็นตุ่มเล็ก ๆ | blackheads-congestion | |
| สิว สิวอักเสบ สิวขึ้นบ่อย | acne-breakouts | Never "treat"; persistent or painful → doctor |
| รอยสิว รอยดำ รอยแดง | post-acne-marks | |
| จุดด่างดำ กระแดด | dark-spots-sun | |
| ฝ้า ปื้นสีน้ำตาลที่แก้ม | melasma | A pattern, never a diagnosis |
| หมองคล้ำ หน้าไม่ใส สีผิวไม่สม่ำเสมอ | dullness-uneven-tone | |
| ใต้ตาคล้ำ ขอบตาดำ | under-eye-darkness | |
| ริ้วรอย ตีนกา ร่องหน้าผาก | fine-lines-wrinkles | |
| หย่อนคล้อย ไม่กระชับ | loss-of-firmness | |
| ผิวไม่เรียบ ผิวหยาบ | rough-texture | |
| ขาดน้ำ หน้ามันแต่ตึง | dehydration | |
| ผิวแห้ง ลอก เป็นขุย | dryness | |
| ผิวบาง ผิวอ่อนแอ แสบง่ายหลังใช้กรดหรือเรตินอล | compromised-barrier | Not visible in a photo — ask |
| แพ้ง่าย แดงง่าย | sensitivity-redness | |
| อยากได้กันแดด กันแดดตัวไหนดี | daily-uv-protection | |
| เมคอัพไม่ติดทน เยิ้มระหว่างวัน | makeup-longevity-oil-control | |
| อยากปกปิดรอยสิว จุดด่างดำ | coverage-blemishes | |
| อยากได้งานผิวบาง ๆ ธรรมชาติ | natural-everyday-base | |
| ปากแห้ง ปากลอก | lip-dryness | |
Pick at most three, in the customer's order of priority.

## Skin types
| Code | Thai | Tell-tale |
|---|---|---|
| oily | ผิวมัน | Shine all over within a few hours of washing |
| combination | ผิวผสม | Oily T-zone, normal or dry cheeks |
| normal | ผิวธรรมดา | Little shine, no tightness |
| dry | ผิวแห้ง | Tight, flaky, little oil |
| sensitive | ผิวแพ้ง่าย | Stings or flushes easily |
| acne-prone | ผิวเป็นสิวง่าย | Clogs and breaks out easily |
| dehydrated-oily | ผิวมันแต่ขาดน้ำ | Shiny but feels tight; common in air-conditioning |

## Other values
| Field | Allowed values |
|---|---|
| Sensitivity | low · medium · high |
| Routine appetite | minimal_3_steps · standard_5_steps · full_layering |
| Wears makeup | never · sometimes · daily |
| Undertone | cool_pink · neutral · warm_yellow · warm_golden · peach |
| Depth | fair · light · light-medium · medium · tan · deep |
| Face zone | forehead · nose · t_zone · cheeks · under_eye · chin_jaw · lips · overall |
| Photo quality | good · usable · poor |

## Routine steps, in order
Remove makeup → cleanse → toner pad (some nights) → essence → treatment serum → moisturise → mask (1–3 times a week) → sunscreen (morning) → primer → base → conceal → powder → cheeks, eyes, brows → lips → setting spray. Lip care any time.
