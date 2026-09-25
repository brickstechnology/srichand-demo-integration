---
title: ความหมายของรหัสผลลัพธ์จากระบบ และถ้อยคำที่ใช้บอกลูกค้า
slug: result-codes-and-customer-wording
use_when: ใช้เมื่อระบบตอบกลับว่าไม่สำเร็จ (ok เป็น false หรือมี error) และต้องรู้ว่ารหัสนั้นหมายถึงอะไร และควรอธิบายให้ลูกค้าฟังอย่างไรโดยไม่ใช้ศัพท์เทคนิค
---
# Result codes: meaning and customer-safe wording

Never show a code, an id or an English error to the customer. Explain in plain Thai what happened and what can be done.

## Identity
| Code or message | Meaning | Say |
|---|---|---|
| "No Srichand customer matches…" / not paired | This chat is not linked to a member yet | ตอนนี้แชตนี้ยังไม่ได้เชื่อมกับบัญชีสมาชิกค่ะ เลยยังตรวจสอบข้อมูลส่วนนี้ให้ไม่ได้ |
| "This customer has no order…" | No such order for this member | ไม่พบคำสั่งซื้อหมายเลขนี้ในบัญชีของคุณลูกค้าค่ะ รบกวนตรวจสอบหมายเลขอีกครั้งนะคะ |

## Membership sign-up
| Code | Meaning | Say |
|---|---|---|
| terms_not_accepted | No explicit yes to the terms yet | ขอให้คุณลูกค้ายืนยันยอมรับข้อกำหนดก่อนนะคะ |
| invalid_phone | Not a 10-digit Thai mobile number | รบกวนขอเบอร์มือถือ 10 หลักอีกครั้งค่ะ |
| invalid_birth_date | Wrong format or Buddhist-era year | ขอวันเกิดเป็น วัน/เดือน/ปี อีกครั้งนะคะ |
| under_minimum_age | Younger than the minimum age | ขออภัยค่ะ การสมัครสมาชิกมีอายุขั้นต่ำตามเงื่อนไข |
| minor_requires_guardian | Under 20: a guardian must confirm | เนื่องจากอายุยังไม่ถึง 20 ปี ขอให้ผู้ปกครองช่วยยืนยันในแชตนี้ด้วยนะคะ |
| phone_already_registered · email_already_registered | An account already uses it. Reveal nothing about that account | เบอร์นี้มีบัญชีสมาชิกอยู่แล้วค่ะ เดี๋ยวให้เจ้าหน้าที่ช่วยเชื่อมบัญชีให้นะคะ |

## Consent and analysis
| Code | Meaning | Say |
|---|---|---|
| age_unknown | No birth date on file | ขอยืนยันก่อนนะคะว่าคุณลูกค้าอายุ 20 ปีขึ้นไปหรือไม่ |
| minor_requires_guardian | Under 20 asked for photo analysis | สำหรับอายุต่ำกว่า 20 ปี เราใช้การตอบคำถามแทนการส่งรูปค่ะ |
| no_active_consent (with a list of missing consents) | A required consent is missing or was withdrawn | ก่อนทำขั้นตอนนี้ ขออนุญาตถามความยินยอมเพิ่มอีกข้อนะคะ |
| consent_text_required | Opt-in needs the agreed sentence | (ask for the explicit yes again) |

## Cart, order, payment
| Code | Meaning | Say |
|---|---|---|
| not_for_sale | A gift item, or a size not sold on its own | ตัวนี้ไม่ได้จำหน่ายแยกค่ะ มีแบบแพ็กหรือเซตให้เลือกแทน |
| out_of_stock | None available to ship | ตอนนี้สินค้าหมดค่ะ (add the restock date if one is given) |
| insufficient_stock | Fewer available than requested, counting what is already in the cart | เหลือเพียง … ชิ้นค่ะ รับตามจำนวนนี้ไหมคะ |
| quantity_limit | More units of one item than an online order allows; bulk and reseller orders go to staff | สำหรับการสั่งจำนวนมาก ขอส่งต่อให้เจ้าหน้าที่ดูแลนะคะ |
| cart_empty | Nothing in the cart | ตะกร้ายังว่างอยู่ค่ะ |
| not_in_cart | The item to change is not in the cart | ตัวนี้ไม่ได้อยู่ในตะกร้าค่ะ |
| coupon_not_found | Unknown code, or a code that belongs to someone else | ไม่พบโค้ดนี้ค่ะ รบกวนตรวจสอบตัวสะกดอีกครั้ง |
| coupon_expired · coupon_not_started_yet · coupon_fully_redeemed | Outside its dates, or used up | โค้ดนี้ใช้ไม่ได้แล้ว / ยังไม่ถึงช่วงเวลาใช้ / ถูกใช้ครบจำนวนแล้วค่ะ |
| coupon_min_spend_not_met | Basket below the coupon's minimum | โค้ดนี้ใช้ได้เมื่อซื้อครบ … บาท ตอนนี้ยังขาดอีก … บาทค่ะ |
| not_enough_points | Asked to use more points than the balance | แต้มมีไม่พอค่ะ ตอนนี้มี … คะแนน |
| points_exceed_order_value | More points than the order is worth | ใช้แต้มได้สูงสุด … คะแนนสำหรับออเดอร์นี้ค่ะ |
| payment_expired | Payment window passed: order cancelled, stock released, points and coupon restored, items back in the cart | เลยเวลาชำระเงินแล้วค่ะ ออเดอร์เดิมถูกยกเลิกอัตโนมัติ สินค้ากลับมาอยู่ในตะกร้าแล้ว สั่งใหม่ได้เลยนะคะ |
| order_is_paid · order_is_cancelled · order_is_… | The order is no longer awaiting payment | ออเดอร์นี้ชำระเงินเรียบร้อยแล้ว / ถูกยกเลิกไปแล้วค่ะ |
| "Stock … changed while the order was being placed" | Someone bought the last units first; nothing was ordered or charged | มีลูกค้าท่านอื่นสั่งตัดหน้าไปพอดีค่ะ ยังไม่มีการตัดเงินนะคะ ขอเช็กตะกร้าให้ใหม่ |

## Anything else
An unknown slug, product or shade means a wrong value was sent — check the glossary and try again; do not tell the customer. For any other failure: apologise briefly, do not guess, and offer staff contact.
