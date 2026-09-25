# Srichand — Rewards, Store Policies, Brand Facts, Current Campaigns

Research date: 2026-09-18 (B.E. 2569). Researcher: Claude (agent), for the Srichand DB + AI customer-service prototype.

**Method / reliability legend**

- **[SITE-TEXT]** = read verbatim from HTML text on srichand.com / srichand.co.th (raw HTML fetched, not an AI summary). Highest reliability.
- **[SITE-IMAGE]** = read by eye from an image published on srichand.com (T&C posters, banners, how-to cards). High reliability; small print could be mis-read, so quote with care.
- **[SITE-API]** = observed from srichand.com's public WooCommerce Store API (`/wp-json/wc/store/v1/...`) using an anonymous test cart on 2026-09-18 (cart was emptied afterwards). Reflects live behaviour today; not a published policy statement.
- **[PRESS]** = third-party press / PR release. Reliable for what the company announced; figures are company claims.
- **[3RD-PARTY-UNVERIFIED]** = user-generated or secondary content; do not present as fact.
- **INFERENCE** = my deduction, explicitly labelled. Not stated by Srichand.

Thai Buddhist-era years: B.E. 2569 = 2026 CE; B.E. 2567 = 2024; B.E. 2560 = 2017; B.E. 2531 = 1988; B.E. 2491 = 1948.

---

## 1. SRICHAND REWARDS (ศรีจันทร์ รีวอร์ด) — membership / loyalty programme

### 1.1 What it is

- "ศรีจันทร์ รีวอร์ด (SRICHAND REWARDS)" is the membership programme of บริษัท ศรีจันทร์สหโอสถ จำกัด, giving benefits to customers who buy the company's brands "อาทิเช่น ศรีจันทร์ ศรีจันทร์เบบี้ และศศิ" (e.g. Srichand, Srichand Baby and sasi). Customers earn points on purchases "ผ่านช่องทางออนไลน์ ออฟไลน์ และร้านค้าต่างๆ ที่เข้าร่วมรายการ" (online, offline and participating stores) and redeem points for rewards. [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
- Member-benefit page headline: "SRICHAND REWARDS อภิสิทธิ์พิเศษสำหรับลูกค้า ศรีจันทร์และศศิ" (exclusive privileges for Srichand and sasi customers). [SITE-TEXT] (https://srichand.com/member-benefit/)
- The nav item "MEMBER BENEFITS" points to https://srichand.com/member-benefit/ (note: singular; `/member-benefits/` and `/srichand-rewards/` return 404). [SITE-TEXT] (https://srichand.com/)

### 1.2 Tiers

- **No tier names or spend thresholds are published.** Neither the member-benefit page nor the member T&C mentions any tier/level (no Silver/Gold/etc.). It is a single-level points programme as far as public documents show. [SITE-TEXT] (https://srichand.com/member-benefit/ ; https://srichand.com/member-terms-and-conditions/)
- The T&C does say benefits may differ per member: clause 2.12 "สิทธิประโยชน์ที่ทางบริษัทเสนอให้แก่สมาชิกแต่ละรายอาจมีความแตกต่างกัน ขึ้นอยู่กับประวัติการซื้อผลิตภัณฑ์ รายการโปรโมชั่นสินค้าแต่ละประเภท และ/หรือนโยบายทางการตลาดของบริษัท" (benefits may vary by purchase history, promotions and marketing policy). [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
- => For the prototype DB: **do not invent tiers.** If a tier field is needed, mark it as hypothetical/demo data.

### 1.3 Earn rate

- **25 baht = 1 point.** Clause 3.2: "ทุกการซื้อผลิตภัณฑ์ของบริษัท ครบ 25 บาท จะได้รับคะแนนสะสม 1 คะแนน โดยคะแนนที่ได้รับจะถูกคำนวณจากยอดชำระสุทธิเท่านั้น (หลังหักค่าขนส่ง ส่วนลด และค่าใช้จ่ายอื่น ๆ ถ้ามี) ทั้งนี้ เศษของยอดการซื้อสินค้าที่ไม่ครบ 25 บาท ในแต่ละใบเสร็จจะไม่สามารถนำมาคำนวณเป็นคะแนนสะสมได้" — points are calculated on the **net paid amount** (after shipping, discounts, other charges); remainders under 25 baht per receipt earn nothing. [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
- Member page wording: "ช้อปสินค้าทุก 25 บาท รับ 1 คะแนนสะสมทันที" (every 25 baht = 1 point) for purchases on www.srichand.com once the website account is linked. [SITE-TEXT] (https://srichand.com/member-benefit/)
- Bonus points may be granted occasionally for qualifying purchases (clause 3.14). [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)

### 1.4 Point value on redemption

- **No fixed baht value per point is published.** Clause 3.3: "มูลค่าของคะแนนจะเป็นไปตามดุลยพินิจของบริษัท" (the value of points is at the company's discretion). [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
- Points are redeemed for rewards/privileges ("แลกเป็นของรางวัลต่างๆ"); points **cannot be exchanged for cash** (clause 3.11), **cannot be transferred or pooled** with another member (clause 3.9), and a confirmed redemption **cannot be edited or cancelled** (clause 3.10). [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
- The website coupon widget on the brand pages has a points hook: it shows "ยืนยันการใช้ 0 คะแนน" (confirm use of 0 points) and "กรุณาล็อกอินเพื่อใช้พอยท์แลกรางวัล" (please log in to use points to redeem rewards); redeemed coupons go to "คูปองของฉัน" (https://srichand.com/my-account/coupons). The current September coupons cost 0 points. [SITE-TEXT] (https://srichand.com/srichand/)

### 1.5 Point expiry / account inactivity

- Clause 3.5: "คะแนนสะสมมีอายุ 1 ปี นับจากปีที่ท่านได้รับคะแนน ... ในกรณีที่ท่านไม่ได้แลก/ใช้คะแนนสะสมก่อนวันหมดอายุ คะแนนสะสมคงเหลือทั้งหมดของท่าน จะถูกยกเลิกทันที" — points are valid **1 year "counted from the year you received the points"**; unused points are cancelled at expiry. [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
  - INFERENCE / ambiguity: the wording "นับจากปีที่ได้รับ" does not say whether expiry is a rolling 12 months or end of the following calendar year. The exact expiry date rule is **not stated**.
- Clause 2.5: membership may be cancelled, and all outstanding points forfeited, if the account has **no activity for 3 consecutive years**. [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)

### 1.6 Which channels earn points, and when points post

- Clause 3.4.1 — **Online: "ช้อปปี้ ลาซาด้า และ www.srichand.com"** (Shopee, Lazada and srichand.com): points post **within 17 days** after a successful order, provided there is no return. The member must **link** the member account to the online-store account; after linking, points are awarded automatically for every order from that linked store. [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
- Clause 3.4.2 — An order number older than **14 days** can still be used to link accounts but earns no points for that order; points start from the next order. [SITE-TEXT] (same URL)
- Clause 3.4.3 — **Participating physical stores:** points post **within 48 hours** after the member successfully uploads the receipt via the member LINE account. [SITE-TEXT] (same URL)
- Clause 3.4.4 — other activities: as the company specifies. [SITE-TEXT] (same URL)
- TikTok Shop is **not** named in clause 3.4.1 (only Shopee, Lazada, srichand.com are named, prefixed by "เช่น" = "such as"). Whether TikTok Shop orders earn points: **not found**.
- Clause 3.6: members check, collect and redeem points via LINE Official **@Srichand1948**. [SITE-TEXT] (same URL)
- Clause 3.7–3.8: missing/incorrect points must be reported **within 30 days** of purchase, with proof of order and payment; acceptance is at the company's sole discretion. [SITE-TEXT] (same URL)
- Clause 3.16: if goods are returned and refunded, the points (and any rewards redeemed with them) must be returned; the company may deduct points without notice. [SITE-TEXT] (same URL)

### 1.7 How to join

- "เพียง Add Line เพื่อสมัครสมาชิก SRICHAND REWARDS ที่ @srichand1948 และทำการเชื่อมต่อบัญชีเว็บไซต์เข้ากับ SRICHAND REWARDS" — add LINE **@srichand1948** to register, then link the website account. Link used on the page: https://line.me/ti/p/~@srichand1948. [SITE-TEXT] (https://srichand.com/member-benefit/)
- A second LINE OA for the sasi brand, **@sasidiary**, can also be used to register for Srichand Rewards and upload receipts (campaign T&Cs: "เพิ่มเพื่อนทาง LINE Official @srichand1948 หรือ @sasidiary และสมัครสมาชิกศรีจันทร์ รีวอร์ด"). [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/ ; https://srichand.com/srichand-x-cj-more-event/)
- Registration steps shown on the how-to cards [SITE-IMAGE] (https://srichand.com/member-benefit/):
  1. Add friend on LINE OFFICIAL @SRICHAND1948 (or scan QR).
  2. In the LINE OA "SRICHAND ศรีจันทร์", tap "สมัครสมาชิก / เข้าสู่ระบบ" on the rich menu (bottom-right), fill the form, then "รอรับ SMS เพื่อยืนยันรหัส OTP" (confirm via SMS OTP).
  - Form fields visible: ชื่อ (first name)*, นามสกุล (last name)*, วันเกิด (birth date)* "(ต้องมีอายุ 16 ปีขึ้นไป)" (must be 16+), หมายเลขโทรศัพท์ (phone)*, อีเมล (email)*, เพศ (gender: ชาย/หญิง/ไม่ระบุ), อาชีพ (occupation), รหัสอ้างอิง (referral code), plus consent checkboxes for T&C/privacy policy and marketing consent.
- Linking the srichand.com account to Srichand Rewards (6 steps) [SITE-IMAGE] (https://srichand.com/member-benefit/):
  1. In LINE: menu "โปรไฟล์" (Profile) > "รับคะแนนเพิ่มเติม" (Get more points).
  2. At "Srichand Website" tap "เชื่อมต่อทันที" (Connect now).
  3. Enter the srichand.com member ID — "กรอกเฉพาะหมายเลขหลัง SRM" (digits after the "SRM" prefix; found on srichand.com > My account > ข้อมูลส่วนตัว).
  4. Enter the latest website order number — "กรอกเฉพาะหมายเลขหลัง #" (digits after #; from My account > ประวัติการสั่งซื้อ), tap "เชื่อมต่อกับ website".
  5. System shows "กำลังเชื่อมต่อ" then "เชื่อมต่อแล้ว!".
  6. Verify under "รับคะแนนเพิ่มเติม" — Srichand Website shows "เชื่อมต่อแล้ว".
  - INFERENCE: because step 4 requires an existing website order number, a customer needs at least one srichand.com order before linking; combined with clause 3.4.2, link within 14 days of that order for it to earn points.
- The **website account** itself (separate from the LINE rewards membership) can be created via mobile number/email, Google or Facebook login. Page sections: "วิธีการสมัครสมาชิกผ่าน Desktop / Mobile / ทาง Google / ทาง Facebook / ทาง E-mail" (steps are images). [SITE-TEXT] (https://srichand.com/how-to-register-srichand-rewards/)
- Foreign phone numbers cannot be used to register for Srichand Rewards: "ไม่สามารถใช้เบอร์โทรศัพท์ต่างประเทศในการสมัครสมาชิกได้". [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/)

### 1.8 Eligibility and other T&C highlights

- One account per customer; duplicates may be merged into the most recent account (clause 1.2). [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
- Age: clause 1.4 "สมาชิกต้องมีอายุตั้งแต่ 20 ปีขึ้นไป" — members must be **20+**; under-20s need consent of a legal guardian. [SITE-TEXT] (same URL)
  - **Discrepancy to flag:** the LINE registration form image says "(ต้องมีอายุ 16 ปีขึ้นไป)" (must be 16+). [SITE-IMAGE] (https://srichand.com/member-benefit/)
- Benefits are for end consumers only — excludes dealers/resellers, the company's product sales staff, and non-genuine users (clauses 2.8, 3.12.1). Commercial use of points is prohibited (clause 3.13). [SITE-TEXT] (same URL)
- Membership is non-transferable (clause 2.9). Members can edit personal data themselves on the platform (clause 2.10) or via Customer Relations **02-300-1661, every day 9:00–18:00**, with identity documents (clause 2.11). [SITE-TEXT] (same URL)
- The company may change/cancel the programme or conditions at any time without notice (clauses 2.7, 2.14, 3.15); the company's decision is final in disputes (clause 2.13). Thai text prevails over any English translation. [SITE-TEXT] (same URL)

### 1.9 Birthday, welcome, free-shipping perks

- **Birthday benefit: not found** in any official page (birth date is collected at registration, but no birthday perk is stated).
- **Welcome benefit: not found on official pages.** A Lemon8 user post (dated 2025-12-27) describes a time-limited (1–31 Oct 2568/2025) "Welcome Gift Set" redeemable for 0 points by new members (Rosia sunscreen + sasi BB powder, ~15 days delivery). [3RD-PARTY-UNVERIFIED] (https://www.lemon8-app.com/@kittiya2609/7588456807102988801) — treat as a past promotion, not a standing benefit.
- Past referral promo: "#SRICHANDREWARDS #FriendsGetFriends" on Srichand's X account (Nov 2024), bonus points for inviting friends — details not verifiable (X blocked fetch). [3RD-PARTY-UNVERIFIED / search snippet] (https://x.com/srichand1948/status/1852244181479231932)
- **Free shipping is NOT a member-only perk** — it is a site-wide threshold (599 baht; see §2.1). The site footer lists three generic benefits: "จัดส่งฟรี เมื่อช้อปครบ 599.-", "สิทธิพิเศษ สำหรับสมาชิก", "รับของขวัญเพิ่ม เมื่อช้อปครบตามเงื่อนไข". [SITE-TEXT] (https://srichand.com/)
- Members get access to member-only campaigns/lucky draws (see §4), which all require Srichand Rewards membership. [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/)

---

## 2. Store policies on srichand.com

Note: srichand.com has **no** dedicated /shipping, /faq or /contact page (checked the public WordPress page list; `/contact/`, `/faq/`, `/about-us/` return 404). Policy pages that exist: /how-to-buy, /refund-and-returns-policy, /privacy-policy, /cookie-policy, /terms-and-conditions, /member-terms-and-conditions. [SITE-API] (https://srichand.com/wp-json/wp/v2/pages?per_page=100)

### 2.1 Shipping fee and free-shipping threshold

- Free shipping threshold: "จัดส่งฟรี เมื่อช้อปครบ 599.-" (free delivery when you shop 599 baht or more) — shown in the footer of every page. [SITE-TEXT] (https://srichand.com/)
- **Shipping fee below the threshold: 50 baht flat rate** (rate label "ค่าจัดส่ง", method `flat_rate`). Observed live: cart of ฿580 → shipping ฿50; cart of ฿609 → rate "จัดส่งฟรี" ฿0 (method `advanced_free_shipping`). Default destination was Bangkok (TH-10). [SITE-API] (https://srichand.com/wp-json/wc/store/v1/cart — anonymous test cart, 2026-09-18)
  - Caveats: the ฿50 fee is **not published in text** on any policy page; it was only observed in the cart. Whether it varies by province/remote area was **not tested**. The threshold appears to apply to the item subtotal (INFERENCE from the two test carts; interaction with coupons not tested).
- **Carriers used: not found.** The return policy only says returns go back "ทางไปรษณีย์" (by post) and references the carrier's delivery record ("บันทึกการจัดส่งของบริษัทขนส่ง") without naming a carrier. [SITE-TEXT] (https://srichand.com/refund-and-returns-policy/)
- **Delivery lead time: not found** on any srichand.com page.

### 2.2 Payment methods

- How-to-buy page, step 2.5: "เลือกช่องทางการชำระเงิน ซึ่งจะมีให้เลือก 3 ช่องทาง" — 3 channels: **2.5.1 Mobile Banking, 2.5.2 บัตรเครดิต/เดบิต (credit/debit card), 2.5.3 ทรูมันนี่ (TrueMoney)**. [SITE-TEXT] (https://srichand.com/how-to-buy/)
- The live Store API exposes four payment gateway IDs: `omise`, `omise_mobilebanking`, `omise_promptpay`, `omise_truemoney`. [SITE-API] (https://srichand.com/wp-json/wc/store/v1/cart)
  - INFERENCE: payments are processed through the Omise (Opn Payments) gateway, and **PromptPay QR** appears to be enabled as a fourth method even though the how-to-buy page (last modified 2024-06-30) lists only three. Confirm with Srichand before telling customers PromptPay is available.
- **COD (เก็บเงินปลายทาง): not offered on srichand.com** as far as observable — no COD gateway is exposed and it is not listed on the how-to-buy page. (INFERENCE from absence.) Note the Moonrise campaign excludes COD orders from online channels, which is relevant to marketplaces. [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/)
- **Instalments: not found.**
- Older bank-transfer wording still on the page: step 2.6 says for Mobile Banking "ลูกค้าจะต้องแนบหลักฐานการชำระเงินในระบบ (ขนาดไฟล์ไม่เกิน 1 MB)" (attach payment slip ≤ 1 MB) then click "แจ้งชำระเงิน". The refund policy likewise refers to customers who paid "ผ่านการโอนเงินเข้าบัญชีธนาคารของบริษัท" (by transfer to the company's bank account). [SITE-TEXT] (https://srichand.com/how-to-buy/ ; https://srichand.com/refund-and-returns-policy/)
- Checkout also collects shipping address and **tax-invoice details** ("รายละเอียดการออกใบกำกับภาษี"), and has a discount-code field ("กรอกโค้ดส่วนลด"). [SITE-TEXT] (https://srichand.com/how-to-buy/)
- After payment the customer receives an order-confirmation email; if no contact within 24 hours, call 02-3001661 to confirm the order. [SITE-TEXT] (https://srichand.com/how-to-buy/)
- Using someone else's credit card without permission makes the user liable for the charges/damages. [SITE-TEXT] (https://srichand.com/terms-and-conditions/)

### 2.3 Cancellation, return, exchange, refund

Source for all of §2.3: [SITE-TEXT] (https://srichand.com/refund-and-returns-policy/) — "นโยบายการยกเลิก เปลี่ยน คืนสินค้า หรือการคืนเงิน".

- **Cancel an order:** possible only while status is "อยู่ในระหว่างการจัดเตรียมสินค้า" (being prepared) — in My Account > "คำสั่งซื้อ" > button "ยกเลิกออเดอร์". **Cannot cancel once status is "Ready to Ship".**
- **On receipt:** customer should film a **continuous unboxing video** ("ถ่าย Clip VDO แบบต่อเนื่อง ตั้งแต่ตอนเริ่มแกะกล่อง"). Problems must be reported **within 3 days** of the successful-delivery date (per the carrier's record) via phone 02-3001661, Facebook "SRICHAND ศรีจันทร์", or email Support@srichand.co.th.
- **Exchange/return request window: 3 days** from successful delivery. Accepted reasons only:
  - wrong item received (wrong size, colour, product, etc.);
  - item defective, broken, damaged or unusable on receipt.
  - "ลูกค้าที่ต้องการเปลี่ยนสี รุ่น จำนวน หรือเปลี่ยนใจไม่รับสินค้า จะไม่สามารถเปลี่ยนหรือคืนสินค้าได้ในทุกกรณี" — **no change-of-mind returns**, no swapping colour/model/quantity.
- Customer must show proof of inspection (the unboxing evidence) (3.2).
- **Physical return deadline: 14 days** from successful delivery, in original condition — "ปิดสนิท และยังไม่ได้เปิดใช้งาน" (sealed and unused), with all items/accessories in the box (3.3).
- Return address (by post): บริษัท ศรีจันทร์สหโอสถ จำกัด (ฝ่ายลูกค้าสัมพันธ์), เลขที่ 50 ซอยพระรามเก้า 53 ถนนพระราม 9 แขวงพัฒนาการ เขตสวนหลวง กรุงเทพมหานคร 10250 (3.4). Keep and show the receipt (3.5).
- Return postage: the company reimburses return shipping based on postal rates / actual receipt, except where damage was caused by the customer (3.6).
- **Refunds: within 30 business days ("30 วันทำการ") from approval** — to the same credit card (after the transaction is voided / goods inspected), or by bank transfer to an account **in the customer's own name only** (4.1–4.2).
- Related: the member T&C (2.6) confirms the company accepts returns where goods don't match the order or have manufacturing/shipping problems. (https://srichand.com/member-terms-and-conditions/)

### 2.4 Order tracking

- **No tracking page or carrier-tracking instructions found.** Order status is visible in My Account > "คำสั่งซื้อ / ประวัติการสั่งซื้อ" (statuses mentioned: being prepared; "Ready to Ship"), and an order-confirmation email is sent. [SITE-TEXT] (https://srichand.com/refund-and-returns-policy/ ; https://srichand.com/how-to-buy/)
- Whether a tracking number is emailed/SMSed: **not found**.

### 2.5 Customer-service contacts

- Phone: **02-300-1661** ("ฝ่ายลูกค้าสัมพันธ์" / Customer Relations). Hours stated in the member T&C: **"ทุกวัน เวลา 9:00–18:00 น."** (every day 09:00–18:00). [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/)
- Email: **support@srichand.co.th**. [SITE-TEXT] (https://srichand.com/ footer)
- Facebook: "SRICHAND ศรีจันทร์" — https://www.facebook.com/srichand1948/. [SITE-TEXT] (https://srichand.com/refund-and-returns-policy/)
- LINE OA: **@srichand1948** (Srichand; membership, points, receipt upload); **@sasidiary** (sasi). [SITE-TEXT / SITE-IMAGE] (https://srichand.com/member-benefit/ ; https://srichand.com/srichand-x-cj-more-event/)
  - Note: the LINE OA is documented for membership/points. It is **not explicitly listed** as a complaints/returns channel in the return policy (which lists phone, Facebook, email).
- Other official social handles: TikTok @srichand_official (https://www.tiktok.com/@srichand_official); X https://x.com/SRICHAND1948; sasi Facebook https://www.facebook.com/sasidiary and X https://x.com/sasidiary. [SITE-TEXT / SITE-IMAGE] (https://srichand.com/ ; https://srichand.com/srichand-the-moonrise-festival-2026/)
- Official marketplace stores linked from the footer: Shopee https://shopee.co.th/srichandofficial ; Lazada https://www.lazada.co.th/shop/srichand-official/. [SITE-TEXT] (https://srichand.com/)
- Campaign-specific contact (Moonrise reserve winners): customer_relations@srichand.co.th and phone 096-351-2555. [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/)
- Head office / return address: 50 Soi Rama 9 Soi 53, Rama 9 Rd, Phatthanakan, Suan Luang, Bangkok 10250. [SITE-TEXT] (https://srichand.co.th/who-we-are/)
- The site displays a "DBD registered" badge in the footer. [SITE-TEXT] (https://srichand.com/)

### 2.6 Privacy policy / PDPA

Source: [SITE-TEXT] (https://srichand.com/privacy-policy/) — "ประกาศเกี่ยวกับความเป็นส่วนตัว สำหรับลูกค้า คู่ค้า และผู้มาติดต่อ (Privacy Notice for Customers, Business Partners and Visitors)", "ประกาศ ณ วันที่ 1 กรกฏาคม 2567" (dated 1 July 2024).

- Issued by บริษัท ศรีจันทร์สหโอสถ จำกัด and affiliates "เพื่อให้เป็นไปตามพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562" (to comply with the Personal Data Protection Act B.E. 2562 / PDPA).
- Personal data examples: name, username, phone, address, email, personal preferences, **purchase behaviour**, **health and beauty information**, IP address, device ID, cookies. Health data is "ข้อมูลส่วนบุคคลที่มีความอ่อนไหว" (sensitive personal data) — the company "จะมีการขอความยินยอมจากท่านก่อนเก็บรวบรวมและประมวลผล" (will ask consent before collecting/processing).
  - Relevance to an AI agent: skin-condition/health details a customer volunteers may count as sensitive data → needs explicit consent handling. (INFERENCE about applicability; the consent rule itself is stated.)
- Purposes (customers): managing orders; competitions/promotions/prize delivery; answering enquiries; operating the **loyalty/points programme**; personalised marketing **based on consent**; analytics; fraud prevention; abandoned-cart/back-in-stock notices. Legal bases named: contract, legitimate interest, consent.
- Payment and delivery data are passed to the payment provider and delivery provider to fulfil orders.
- Sources: directly from the customer (website, forms, apps, POS, events, social media) and third parties (agents, stores, partners, affiliates, Facebook/Google login).
- **Minors:** the company does not knowingly collect data from persons **under 20** without parent/guardian consent; inadvertently collected data will be deleted.
- Disclosure: not disclosed externally without explicit consent except to necessary service providers (IT, payment, post/parcel, marketing, research, etc.) under data-processing agreements, to affiliates for the stated purposes, or where required by law.
- Cross-border transfer possible, ensuring adequate protection standards. Security: encryption in transit, access control.
- Retention: as long as necessary for the stated purposes (no fixed period given), longer if required by law/disputes.
- Data-subject rights listed: access & copy, rectification, data portability, erasure, restriction, withdraw consent, object; right to complain to the Personal Data Protection Committee (คณะกรรมการคุ้มครองข้อมูลส่วนบุคคล).
- DPO / contact (outsourced): บริษัท เอปซีลอง ลีกัล จำกัด, 253 อาคาร 253 อโศก ถนนอโศก-มนตรี แขวงคลองเตยเหนือ เขตวัฒนา 10110; โทร 064-6916161; email **dpo.srichand@aktivist.co.th**.
- Policy changes are posted on www.srichand.co.th and www.srichand.com. Campaign T&Cs add their own PDPA section and point to https://srichand.co.th/th/privacy-policy/privacy-notice-for-customers-business-partners-and-visitors. [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/)

### 2.7 Website terms of use (selected)

Source: [SITE-TEXT] (https://srichand.com/terms-and-conditions/)

- Operator: "บริษัท ศรีจันทร์สหโอสถ จำกัด และบริษัทในเครือ". One user account per person; duplicate/false registrations forfeit rewards.
- The company does not warrant that product information and prices on the site are always accurate/current.
- Governing law: Thailand; Thai courts.

---

## 3. Company and brand facts

### 3.1 Legal entity, founding, origin story

- Thai legal name: **บริษัท ศรีจันทร์สหโอสถ จำกัด**. [SITE-TEXT] (https://srichand.co.th/who-we-are/)
- English name used by the company: **Srichand United Dispensary Co., Ltd.** (company LinkedIn page; also used in press). [PRESS] (https://th.linkedin.com/company/srichand ; https://www.thestorythailand.com/en/srichand-surpasses-thb-1-6-billion-in-revenue-rising-to-no-1-in-thai-skincare-market/)
- Founded **พ.ศ. 2491 (1948)** by **คุณพงษ์ หาญอุตสาหะ (Phong Hanutsaha)**, who ran a pharmacy, bought the scented-powder ("ผงหอม") formula from **หมอเหล็ง ศรีจันทร์ (Mor Leng Srichand)** and renamed the shop "ห้างขายยาศรีจันทร์สหโอสถ". Businesses: pharmaceuticals, chemicals, cosmetics. [SITE-TEXT] (https://srichand.co.th/who-we-are/)
- **พ.ศ. 2531 (1988):** became "บริษัท ศรีจันทร์สหโอสถ จำกัด"; the hero product was ผงหอมศรีจันทร์, an oil-control face powder/mask. [SITE-TEXT] (same URL)
- **พ.ศ. 2549 (2006):** **คุณรวิศ หาญอุตสาหะ (Rawit Hanutsaha)**, 3rd-generation heir, took over management and began the turnaround. [SITE-TEXT] (same URL)
- **พ.ศ. 2557 (2014):** rebrand from "ผงหอมศรีจันทร์" (60+ years old) to the modern "แบรนด์ศรีจันทร์"; the Translucent Powder launched in 2014 drove mass awareness. [SITE-TEXT] (https://srichand.co.th/who-we-are/) [PRESS] (https://marketeeronline.co/archives/175398)
- The corporate site describes "78 ปี" of history (1948→2026) and positions the company in "Health, Wellness, and Beauty (HWB)". Brand logo line: "SRICHAND BANGKOK 1948". [SITE-TEXT / SITE-IMAGE] (https://srichand.co.th/who-we-are/ ; https://srichand.com/)
- Head office: เลขที่ 50 ซอยพระรามเก้า 53 ถนนพระราม 9 แขวงพัฒนาการ เขตสวนหลวง กรุงเทพฯ 10250. [SITE-TEXT] (https://srichand.co.th/who-we-are/)

### 3.2 Executives

- **CEO: คุณรวิศ หาญอุตสาหะ — ประธานเจ้าหน้าที่บริหาร (CEO)**, 3rd generation. [SITE-TEXT] (https://srichand.co.th/who-we-are/); quoted with this title in 2026 releases. [PRESS] (https://www.ryt9.com/s/prg/12809909)
- CMO (as of June 2022 only): **ระบิล สิริมนกุล — ประธานเจ้าหน้าที่ฝ่ายการตลาด**. [PRESS] (https://positioningmag.com/1390589) — current status **not verified**.
- Other current executives: **not found**.

### 3.3 Financials and market position (company claims via press)

- Revenue: 2021 ฿520m → 2022 ฿717m → 2023 ฿1,019m → 2024 ฿1,600m. [PRESS, 26 Jun 2025] (https://www.thestorythailand.com/en/srichand-surpasses-thb-1-6-billion-in-revenue-rising-to-no-1-in-thai-skincare-market/)
- Latest reported: total revenue **฿2,055.50m**, net profit **฿274.78m (+34%)**; ~500 SKUs (SRICHAND ~300, sasi ~200); 2026 growth target 15%; target ฿3,000m within 2 years; **IPO planned "next year"**; domestic ~90% / international ~10% of revenue, international growing 135% (Laos +162%). [PRESS, 25 Jun 2026] (https://www.thumbsup.in.th/srichan-t-beauty)
- NielsenIQ-based claims: No.1 loose powder (Jan 2023–Apr 2025); No.1 face moisturiser segment (Jan 2024–Apr 2025). [PRESS] (https://www.thestorythailand.com/en/srichand-surpasses-thb-1-6-billion-in-revenue-rising-to-no-1-in-thai-skincare-market/) — "SRICHAND Skin Moisture Burst Gel Cream Sachet" No.1 face moisturiser for the 2nd consecutive year (NielsenIQ). [PRESS] (https://www.thumbsup.in.th/srichan-t-beauty)
- "มอยส์ศรีจันทร์ แมสแล้ว 50 ล้านชิ้น*" — footnote: cumulative sales of SRICHAND Skin Moisture Burst Gel Cream in 10, 15, 50 and 120 ml sizes across all channels. [SITE-TEXT] (https://srichand.com/articles/srichand-moisturizer-hits-50-million-units-sold/)
- Channel mix: ~90% offline / 10% online (2025). [PRESS] (https://www.thestorythailand.com/en/srichand-surpasses-thb-1-6-billion-in-revenue-rising-to-no-1-in-thai-skincare-market/)
- April 2026: new corporate logo built on the Thai letter **"ศ"**; positioning as "T-Beauty Leader" / "องค์กรไทยที่คนไทยภูมิใจ". [PRESS] (https://www.brandbuffet.in.th/2026/04/srichan-thai-beauty-leader/ ; https://www.thumbsup.in.th/srichan-t-beauty)

### 3.4 Brand positioning — SRICHAND vs sasi vs Srichand Baby

- **SRICHAND (ศรีจันทร์):** heritage master brand — "SRICHAND แบรนด์ที่เข้าใจผิวคนไทยอย่างแท้จริง" (the brand that truly understands Thai skin); tagline **"SRICHAND BE UNSTOPPABLE"**; pillars on the corporate site: MAKE UP (flagship "Bare to Perfect Translucent Powder", billed "NO.1 TRANSLUCENT POWDER"), SKINCARE, SUNSCREEN. [SITE-TEXT] (https://srichand.co.th/who-we-are/ ; https://srichand.co.th/srichand/)
  - 2026 strategy language: **T-Beauty** and **T-SKIN** ("บทพิสูจน์จากทุกผิวไทย" — proven on all Thai skin; products designed for hot-humid climate, strong sun, pollution). [PRESS] (https://mileday365.com/srichand-x-bambam/ ; https://www.thumbsup.in.th/srichan-t-beauty)
- **sasi (ศศิ):** sub-brand launched **พ.ศ. 2560 (2017)** to extend to a younger audience — "กลุ่มลูกค้าของ sasi คืออายุตั้งแต่ 16-35 ปี" (ages 16–35), good quality at value prices; repositioned in June 2022 as a "Beauty and Lifestyle Brand" under "Because girls can". In 2022 the revenue split was Srichand 60% / sasi 35% / other 5%. [PRESS] (https://positioningmag.com/1390589 ; https://marketeeronline.co/archives/268476)
  - srichand.com hosted a "sasi 9th Anniversary Event" in May 2026 (consistent with a 2017 launch). [SITE-API/SITE-TEXT] (https://srichand.com/proxie-event/)
  - sasi hero products: tinned powder, lip tint, blush stick. [PRESS] (https://www.thumbsup.in.th/srichan-t-beauty)
  - sasi faces: **เก้า สุภัสสรา ธนชาต (Kao Supassara)** — "FACE OF sasi (Lipstick & Color Cosmetics)" [SITE-IMAGE] (https://srichand.com/ Moonrise banner); boy band **PROXIE**. [PRESS] (https://www.thestorythailand.com/en/srichand-surpasses-thb-1-6-billion-in-revenue-rising-to-no-1-in-thai-skincare-market/)
  - Price tier: described as "tens to hundreds of baht"; site shows sasi items from ฿29. [PRESS] (https://positioningmag.com/1390589) [SITE-API] (srichand.com product catalogue)
  - sasi has its own LINE OA **@sasidiary**, Facebook/X "sasidiary". [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/)
- **Srichand Baby (ศรีจันทร์ เบบี้):** baby-care line named in the member T&C as one of the company's brands; on srichand.com it is a section of the SRICHAND shop page (#srichand-baby) and an article category. Products include Srichand Baby Powder (50 g) and Newborn Powder (150 g). [SITE-TEXT] (https://srichand.com/member-terms-and-conditions/ ; https://srichand.com/srichand/ ; https://srichand.com/product/srichand-baby-newborn-powder-150-g/)
  - Launch year of Srichand Baby: **not found**.

### 3.5 SRICHANDxBamBam

- **Who:** **แบมแบม กันต์พิมุกต์ ภูวกุล (BamBam, Kunpimook Bhuwakul)** — Thai-born global K-pop artist; press releases call him "ศิลปินระดับโกลบอล". (He is widely known as a member of GOT7 — general knowledge; the Srichand releases themselves do not mention GOT7.) [PRESS] (https://kazz-magazine.com/165849-2/)
- **When:** announced as presenter of **SRICHAND IN-SKIN** at a launch event at Parc Paragon, Bangkok — release dated **11 ธันวาคม 2567 (11 Dec 2024)**. [PRESS] (https://kazz-magazine.com/165849-2/ ; https://positioningmag.com/1502932). The corporate site says: "ปลายปี 2024 แบมแบม กันต์พิมุกต์ ในฐานะ GLOBAL ARTIST ... ภายใต้แคมเปญ SRICHAND IN-SKIN เข้าใจทุกผิวคนไทย". [SITE-TEXT] (https://srichand.co.th/who-we-are/)
- **Products at launch (3 lines):** Skin Moisture Burst (Essence, Serum, Gel Cream — 72-hour hydration claim), Super C Brightening Intense Serum, Timeless Anti-Aging Facial Serum; plus a "SRICHAND IN-SKIN x BamBam Skin Moisture Burst Boxset". [PRESS] (https://positioningmag.com/1502932 ; https://www.brandbuffet.in.th/2024/12/srichand-the-power-of-bambam-to-boost-sales/)
- **Year 2 (2026):** BamBam continues for a 2nd consecutive year under the **T-SKIN** concept [PRESS, 2 Feb 2026] (https://mileday365.com/srichand-x-bambam/); launch event "**The Symphony of GLOWolution**" at Parc Paragon (release dated 11 Mar 2026) for the **SRICHAND IN-SKIN Phyto Camellia PDRN Series** — 4 steps: Bright Glowing Cleansing Gel Foam, Essence, Serum, Gel Cream (vegan PDRN). [PRESS] (https://www.thaipr.net/business/3701537)
- **On srichand.com:** /srichandxbambam/ is a shop landing page listing the In-Skin skincare ranges: Skin Moisture Burst, 15X Ampoule Masks, Phyto Camellia PDRN, Super C Brightening, Barrier Boost, Timeless Anti-Aging, Advanced Anti Melasma, Resurface Pro-Retinol, plus sets. Homepage quote attributed to BamBam: "ผิว ก็คือ ผิว ผิวซุปเปอร์สตาร์หรือผิวคนธรรมดา ทุกผิวอ่อนแอได้เหมือนกัน ทุกผิวก็ข้ามสแตนดาร์ดของตัวเองได้เหมือนกัน". [SITE-TEXT] (https://srichand.com/srichandxbambam/ ; https://srichand.com/)
- Homepage banner (Aug 2026): BamBam with "มอยส์ศรีจันทร์ แมสแล้ว 50 ล้านชิ้น — 'พิสูจน์แล้วจากทุกผิวไทย'". [SITE-IMAGE] (https://srichand.com/)

### 3.6 Current presenters / ambassadors (as shown on srichand.com today)

From THE MOONRISE FESTIVAL key visual on the homepage/shop page [SITE-IMAGE] (https://srichand.com/srichand/):

| Person | Role label on the banner |
|---|---|
| **BAMBAM** — แบมแบม กันต์พิมุกต์ ภูวกุล | SRICHAND IN-SKIN (skincare) |
| **BAIFERN** — ใบเฟิร์น พิมพ์ชนก ลือวิเศษไพบูลย์ | SRICHAND BASE MAKEUP |
| **ZEE** — ซี พฤกษ์ พานิช | SRICHAND SUNLUTION (sunscreen) |
| **NUNEW** — นุนิว ชวรินทร์ เพริศพิริยะวงศ์ | SRICHAND SUNLUTION (sunscreen) |
| **KAO** — เก้า สุภัสสรา ธนชาต | FACE OF sasi (Lipstick & Color Cosmetics) |

- Homepage quotes: Zee — "First Step ในทุกวันของซี คือ การทากันแดด" (Zee's first step every day is applying sunscreen); NuNew — "เต็ม 10 ของกันแดด ให้ 100 ไปเลย" (out of 10 for the sunscreen, I give 100); Baifern — "แค่ไม่หยุดรักตัวเอง ก็ไม่มีอะไรมาหยุดคุณได้ ... SRICHAND BE UNSTOPPABLE". [SITE-TEXT] (https://srichand.com/)
- **Zee–NuNew** were announced on **27 April 2026** as duo presenters of **SRICHAND SUNLUTION** "ทั้งในประเทศไทย และสาธารณรัฐประชาธิปไตยประชาชนลาว" (Thailand and Lao PDR), campaign "ดันบาร์กันแดดให้สุด ปกป้องผิวครบทุกมิติ", launch event "Escape the Sun Island Party", with two new hybrid sunscreens: **Sunlution Moisture Burst Watery Sunscreen SPF50+ PA++++** and **Sunlution Tone Up Serum Sunscreen SPF50+ PA++++**. Sunlution grew 52%+ the previous year (company claim). [PRESS] (https://www.ryt9.com/s/prg/12809909)
- **Baifern Pimchanok** was officially unveiled as Srichand presenter in **July 2020** (with the "แป้งม่วง Gen2" Translucent Powder relaunch of 25 May 2020). [PRESS] (https://marketeeronline.co/archives/175398)
- Press (June 2026) says the company now uses a record **13 presenters**, "เช่น แบมแบม, ใบเฟิร์น, ซี, นุนิว, เก้า, และวง PROXIE". [PRESS] (https://www.thumbsup.in.th/srichan-t-beauty). The Momentum additionally names "เก่ง" and "น้ำปิง" for Srichand and lists PROXIE members for sasi — full names/roles of those two **not verified**. [PRESS] (https://themomentum.co/business-srichand-sasi/)

### 3.7 Retail distribution in Thailand

- Official list of participating "ร้านค้าชั้นนำทั่วประเทศ" in the Moonrise Festival T&C (i.e., where Srichand/sasi are sold): **7-Eleven Thailand และ All Online, Watsons, CJ MORE & NINE BEAUTY, Lotus's, Big C, Konvy, EVEANDBOY, BEAUTRIUM, Tops, Multy, Gourmet Market, Found&Found, Matsumoto** (Matsumoto Kiyoshi — INFERENCE on full name), plus other leading stores; official online channel: **www.srichand.com**. [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/)
- **Boots** is also named as a retailer in the March 2026 PDRN press release: "Website SRICHAND Official, Lazada, Shopee และ TikTok Shop (SRICHAND Official) หรือช้อปได้ที่ Watsons, EVEANDBOY, Beautrium, Boots, Multy และร้านค้าชั้นนำทั่วประเทศ". [PRESS] (https://www.thaipr.net/business/3701537)
- Marketplaces: Shopee (shopee.co.th/srichandofficial), Lazada (srichand-official), TikTok Shop "SRICHAND Official". [SITE-TEXT] (https://srichand.com/) [PRESS] (https://www.thaipr.net/business/3701537)
- CJ MORE / CJX (NINE BEAUTY zone) is an active co-promotion partner (see §4.3). [SITE-IMAGE] (https://srichand.com/srichand-x-cj-more-event/)

### 3.8 Export markets

- Japan, Philippines, Laos, China — ~5% of sales; customer base 85% Thai / 15% foreign. [PRESS, 6 Mar 2026] (https://en.thairath.co.th/money/business_marketing/marketing_trends/2918375)
- Japan: 2,000+ retail doors; Laos: strong growth. [PRESS] (https://www.thestorythailand.com/en/srichand-surpasses-thb-1-6-billion-in-revenue-rising-to-no-1-in-thai-skincare-market/)
- 2026 plans: new Myanmar partner signed; sasi sells well in the Philippines (expanding offline); Vietnam targeted for ~10% of sales; further ASEAN roll-out (Vietnam, Singapore, Malaysia, Indonesia by 2027). [PRESS] (https://www.thumbsup.in.th/srichan-t-beauty ; https://themomentum.co/business-srichand-sasi/)

### 3.9 Notable awards / recognitions

- **Brand Footprint 2025 — "Outstanding Brand ในหมวด Facial Care"** (Worldpanel) and a **YouGov 2025** "Top Improver" personal-care ranking. [PRESS] (https://mileday365.com/srichand-x-bambam/); Brand Footprint growth ranking also cited on srichand.com. [SITE-TEXT] (https://srichand.com/articles/srichand-moisturizer-hits-50-million-units-sold/)
- **QMAC 2026** (most-wanted employer) and **GEN Z TOP BRAND 2026**. [PRESS] (https://www.thumbsup.in.th/srichan-t-beauty)
- Product test claims: Moisture Burst Gel Cream — 72-hour moisture retention tested by **DERMSCAN ASIA**; irritation test by **SPINCONTROL ASIA**. [SITE-TEXT] (https://srichand.com/articles/srichand-moisturizer-hits-50-million-units-sold/)

### 3.10 Product-line architecture (as organised on srichand.com)

Top-level shop navigation: **SRICHANDxBamBam** | **SHOP → SRICHAND / sasi / All Shop** | ARTICLES (Skincare, Sunscreen, Make up, Srichand Baby) | MEMBER BENEFITS. [SITE-TEXT] (https://srichand.com/)

SRICHAND shop page section anchors (exact labels) [SITE-TEXT] (https://srichand.com/srichand/): THE MOONRISE FESTIVAL · SPECIAL PROMOTION · SKIN ESSENTIAL SERIES · AMPOULE MASK SHEET · SUNSCREEN · PHYTO CAMELLIA PDRN · SUPER C BRIGTENING SERIES [sic] · แป้งสูตรลับในตำนาน (the legendary secret-formula powder = Srichand Original Powder Mask) · ENCHANTED SERIES · BARRIER BOOST SERIES · POWDER · SKINCARE · FOUNDATION · LIPS · EYES & CHEEK · BUNDLE · SRICHAND BABY · SRICHAND MUSE LIMITED SET · HAIR.

Sub-brands / families used in campaign documents [SITE-IMAGE] (https://srichand.com/srichand-the-moonrise-festival-2026/):

- **FACE BASE MAKE UP** — Enchanted Cover Perfect, Super Coverage Always Matte, Skin Essential Fine Smooth (each as foundation / cushion / foundation powder; full and sachet/small sizes).
- **SRICHAND IN-SKIN** (skincare) — Skin Moisture Burst (Serum 50 ml, Essence 150 ml, Gel Cream 50 ml; sachets), Phyto Camellia PDRN Bright Glowing (Serum 30 ml, Gel Cream 50 ml, Essence 150 ml; sachets), 15X Ampoule Masks (Skin Moisture Burst; Super C Brightening). Website also lists under In-Skin: Super C Brightening, Barrier Boost, Timeless Anti-Aging, Advanced Anti Melasma, Resurface Pro-Retinol. (https://srichand.com/srichand/)
- **SRICHAND SUNLUTION** (sunscreen = "SUNSCREEN + SOLUTION" per corporate site) — Rosia Ultra Protection Serum Sunscreen, Tone Up Serum Sunscreen, Moisture Burst Watery Sunscreen (all SPF50+ PA++++, 40 ml & 7 ml); also Acne Care and Skin Whitening sunscreens on the shop page. (https://srichand.co.th/who-we-are/ ; https://srichand.com/srichand/)
- **sasi** — e.g. Jolly Sweet Lip Tint, Sugar Rush Lip Tint, Kiss & Blush Stick, Brow-To-Be Auto Pencil, Pretty Easy Perfect Eyebrow Pencil.
- Newer colour line seen on the homepage: **SRICHAND "Day to Glow" Plumping Lip Balm** ("#ลิปโกลว์ปากแกลม"). [SITE-IMAGE] (https://srichand.com/)

Pack formats matter for customer service: many items exist as full size, **sachet (ซอง)** and boxes of sachets ("[6pcs/Box]"), "[Bogo]" packs, and "Set" bundles. [SITE-TEXT] (https://srichand.com/srichand/)

---

## 4. Current campaigns visible on srichand.com (as of 2026-09-18)

### 4.1 THE MOONRISE FESTIVAL 2026 — "A Mythical Night Under The Full Moon"

Source: [SITE-IMAGE] T&C poster and key visual (https://srichand.com/srichand-the-moonrise-festival-2026/ ; receipt examples: https://srichand.com/srichand-receipt-example-the-moonrise-festival-2026/).

- **What:** "กิจกรรม Lucky Fan ลุ้นเป็นผู้โชคดีเข้าร่วมกิจกรรม THE MOONRISE FESTIVAL 2026" by the Srichand and sasi brands — a lucky draw for seats at a fan event celebrating the company's **78th anniversary** ("เฉลิมฉลองครบรอบ 78 ปีครั้งยิ่งใหญ่ของ บริษัท ศรีจันทร์สหโอสถ จำกัด" — image alt text on https://srichand.com/srichand/). Prize value ฿999 each. Lottery permit no. **2094/2569**.
- **Event date:** **Sunday 25 October 2026** (วันอาทิตย์ที่ 25 ตุลาคม 2569). Line-up on key visual: ZEE, NUNEW, BAIFERN, BAMBAM, KAO. Venue: **not stated** on the page. (The poster's announcement section also contains the words "SPORTDAY 2026", and winners are split into a purple team and a pink team.)
- **Qualifying purchase (per single receipt = 1 entry):** Srichand products — at least **1 regular-size** item *or* at least **6 sachet/small-size** items (formulas can be mixed) — **together with** sasi products — at least **1 regular-size** item *or* at least **2 small-size** items. Only listed participating products count. Bundle packs / "1 แถม 1" packs count as 1 item; Shelf Ready Boxes count as 3 or 6 by actual pieces.
- **Purchase + receipt-upload window:** **7 Sep 2026 00:01 – 27 Sep 2026 23:59.** Re-upload deadline if rejected: 29 Sep 2026 23:59. All entries visible by 30 Sep 2026 23:59.
- **Draw:** 5 Oct 2026 10:00, run by the organiser's agent "บริษัท ลัคกี้วันกรุ๊ป จำกัด" at เลขที่ 332 ห้อง A11–A12 ชั้น 2 อาคาร A ศูนย์การค้าเออร์เบิน สแควร์ ถนนประชาชื่น แขวงทุ่งสองห้อง เขตหลักสี่ กรุงเทพฯ 10210. **Winners announced: Tue 6 Oct 2026 18:00** on Srichand Facebook/X (SRICHAND1948) and sasi Facebook/X (sasidiary). **900 winners** (+ reserves): ranks 1–450 = purple team, 451–900 = pink team. One right per person.
- **Winner confirmation:** via LINE @srichand1948 or @sasidiary, menu "รางวัล" → "ยืนยันสิทธิ์เข้าร่วมกิจกรรม THE MOONRISE FESTIVAL 2026", **7 Oct 2026 18:00 – 11 Oct 2026 23:59**, with national ID or passport number + photo. Reserves contacted 12–13 Oct 2026 (email from customer_relations@srichand.co.th; phone 096-351-2555). Rights are non-transferable; winners must attend in person with the matching receipt/order proof and ID.
- **How to enter:** be a Srichand Rewards member (LINE @srichand1948 or @sasidiary; Thai phone number; name and phone must match membership data) → upload the receipt/order proof in LINE menu "สะสมคะแนน" or rich menu, entering purchase date, store name, receipt/order number and amount → status becomes "อนุมัติ" within 24 hours → check under "โปรไฟล์" > "รางวัลของฉัน". If a receipt is rejected for not meeting the campaign conditions, the customer still gets normal points. No limit on number of receipts (each receipt number once).
- **Eligible channels:** official online = www.srichand.com; leading retailers (7-Eleven & All Online, Watsons, CJ MORE & NINE BEAUTY, Lotus's, Big C, Konvy, EVEANDBOY, BEAUTRIUM, Tops, Multy, Gourmet Market, Found&Found, Matsumoto) — for retailers' online channels **only the retailer's own app/website**; "**ไม่รวมการสั่งซื้อผ่าน Marketplace หรือแพลตฟอร์มบุคคลที่สาม เช่น Lazada, Shopee, Tiktok, Grab**" (marketplace orders excluded). Other Thai stores count if they issue a proper POS/electronic receipt. Handwritten/back-dated receipts are rejected. **COD orders and pre-orders are excluded**; cancelled orders are void.
- Other: employees of Srichand and of บริษัท บัซซี่บีส์ จำกัด (Buzzebees — INFERENCE: likely the loyalty-platform vendor) are ineligible; prizes ≥ ฿1,000 are subject to 5% withholding tax; alcohol prohibited at the event; PDPA notice included.
- On srichand.com, the SRICHAND shop page has a dedicated "THE MOONRISE FESTIVAL" product section listing the participating SKUs. (https://srichand.com/srichand/#moonrise-festival)

### 4.2 September 2026 website discount coupons

Source: [SITE-TEXT] (https://srichand.com/srichand/ and https://srichand.com/sasi/) — "คูปองส่วนลด — เก็บโค้ดเตรียมช้อป รับส่วนลดสุดคุ้ม ลดเลยทั้งเว็บไซต์" (site-wide coupons; login required to collect).

| Discount | Minimum spend | Coupon period |
|---|---|---|
| ฿30 | ซื้อครบ 399 บาท | 1–30 ก.ย. 2026 |
| ฿70 | ซื้อครบ 699 บาท | 1–30 ก.ย. 2026 |
| ฿150 | ซื้อครบ 1,299 บาท | 1–30 ก.ย. 2026 |

### 4.3 Gift with purchase (GWP) — ฿499 threshold, active today

- Active GWP: "**ฟรี Skin Moisture Burst Gel Cream 10ml + Serum 5 ml. + Essence 10 ml. อย่างละ 1 ซอง + SRICHAND CANVAS BAG 1 ใบ**" — description "**ของแถมเมื่อซื้อครบ 499.- จำกัด 100 ใบ**" (free gift when spending ฿499; limited to 100). Listed value ฿367. [SITE-TEXT] (https://srichand.com/product/free_mois_sachet_bag/)
- Verified live: the gift line (฿0) was auto-added to a test cart at ฿522 and was absent at ฿493. No additional gift was added at ฿1,015, ฿1,218 or ฿1,305, so **only the ฿499 GWP appears active today**. [SITE-API] (anonymous test cart, 2026-09-18)
- Older GWP placeholder products still exist in the catalogue (likely expired; do **not** quote as current): 699 → Kabuki Brush (100 pcs); 999 → Skin Moisture Burst 15X Ampoule Mask ×4 (50); 1,177 → PowerBank 10000 mAh (50); 1,199 → cosmetic bag (50); 1,199 → Sunlution Skin Whitening 15 ml + Super C sachets (50); 2,199 → Lotus's gift card ฿300 (10); 3,555 → Big C gift card ฿300 (20). [SITE-API] (srichand.com product catalogue; e.g. https://srichand.com/product/free_supercsunlution/)

### 4.4 "1 แถม 1" / BOGO and bundle offers

- **[Bogo] packs** (buy-one-get-one sachet packs) currently listed: Barrier Boost Soothing Gel Cream 10 ml, Barrier Boost Essence 10 ml, Barrier Boost Serum 7 ml, Timeless Anti-Aging Facial Serum Sachet 7 ml — each as "[Bogo][3ชิ้น] … รวม 6 ซอง" (฿117) and "[Bogo][6ชิ้น/กล่อง] … รวม 12 ซอง" (฿234). [SITE-TEXT] (https://srichand.com/srichandxbambam/)
- **SPECIAL PROMOTION** section: e.g. "SRICHAND Skin Moisture Burst Gel Cream 120ml 2 Pcs **Free** Skin Moisture Burst 15X Ampoule Mask 18ml 2 Pcs" (฿790); "Barrier Boost Serum 30 ml + Soothing Gel Cream 50 ml **Free** Cleansing Gel Foam 50 ml" (currently out of stock); ampoule-mask bundles "StrengthSkin, Boost Dewy Hydration" and "Revive Dull Skin, Boost Bright Radiance". [SITE-TEXT] (https://srichand.com/srichand/#special-promo)
- Flash-sale style markdowns on the homepage today (examples): Skin Moisture Burst Gel Cream 120 ml ฿790→฿395 (-50%); Essence 150 ml ฿435→฿269; Gel Cream 50 ml ฿455→฿269; Super C Essence 150 ml ฿435→฿269; Super C Intense Serum 30 ml ฿399→฿269; Resurface Pro-Retinol Serum 30 ml ฿559→฿329; 3-piece Moisture Burst set ฿1,385→฿807. Prices change frequently — read live prices from the catalogue, not from this note. [SITE-TEXT] (https://srichand.com/)

### 4.5 "สวยสะบัด ลุ้นทองจัดหนัก กับ SRICHAND X CJ MORE" (gold lucky draw) — final round ending

Source: [SITE-IMAGE] (https://srichand.com/srichand-x-cj-more-event/)

- Buy Srichand and sasi products worth **every ฿149 per receipt** (net of discounts, Srichand/sasi items only; remainders don't count; receipts can't be combined) at **CJ MORE and CJX (NINE BEAUTY zone), all branches** → upload the receipt via LINE @srichand1948 or @sasidiary → get **1 token = 1 draw entry**; **CJ สบายการ์ด (CJ Sabai Card) members get 2 tokens**. Tokens must be exchanged for entries under LINE menu "รางวัล".
- Prizes: gold bars totalling 6 baht-weight, total value ฿433,200; **per month:** 1 × gold 1 baht-weight (฿72,200) + 4 × gold 1 salueng (฿18,050 each). (Gold price reference date 3 Apr 2026.)
- Campaign period: **25 Jun 2026 00:00 – 24 Sep 2026 23:59**, in 3 rounds. **Round 3 (current):** purchases 25 Aug – 24 Sep 2026; upload by 24 Sep; exchange tokens by 26 Sep; draw Thu 1 Oct 2026; winners announced **Tue 6 Oct 2026 18:00** on Facebook (Srichand ศรีจันทร์ / sasi ศศิ) and the two LINE OAs. One prize max per person; winners must contact the company via LINE within 15 days.
- Receipt check: status "อนุมัติ"/"ปฏิเสธ" within 24 hours; re-upload within 24 hours if rejected.

### 4.6 Other / recently ended items (for context; not current)

- Homepage CSS still references a banner "**Big Deals Begin — ดีลใหญ่ ได้เวลาช้อป**": up to 65% off; coupons ฿70 off at ฿799 and ฿150 off at ฿1,399; spend ฿1,199 get free Sunlution Skin Whitening 15 ml + Super C sachets (value ฿315, first 50 orders); dated **16–31 ส.ค. 69 (16–31 Aug 2026)** → **expired**. [SITE-IMAGE] (https://srichand.com/wp-content/uploads/2026/08/26DS1722-SC-Web-16-31-Aug26_Desktop-Banner-scaled.webp)
- Past member events still in the MEMBER BENEFITS section/page list: "sasi 9th Anniversary Event Fan Zone with Face of sasi" (page modified May 2026) and a "PROXIE" event (Apr 2026). [SITE-API/SITE-TEXT] (https://srichand.com/proxie-event/)
- Homepage brand banners (not promotions): Sunlution "ดันบาร์กันแดดให้สุด ปกป้องผิวครบทุกมิติ"; In-Skin "สกินแคร์กู้ผิว 3 Steps … ยาวนานถึง 72 ชั่วโมง*"; "Day to Glow Plumping Lip Balm"; BamBam "มอยส์ศรีจันทร์ แมสแล้ว 50 ล้านชิ้น". [SITE-IMAGE] (https://srichand.com/)

---

## 5. Not found / uncertain

**Srichand Rewards**
- Tier names and qualification thresholds — **not found; no tiers are published** (programme appears single-level).
- Baht value of a point / redemption catalogue — **not found** (T&C: value is at the company's discretion). The actual rewards catalogue lives inside the LINE OA and was not accessible.
- Exact expiry mechanics ("1 year counted from the year received" — rolling vs calendar-year) — **ambiguous in source**.
- Birthday benefit — **not found**. Standing welcome benefit — **not found** (only an unverified third-party post about an Oct 2025 welcome gift).
- Whether TikTok Shop orders earn points — **not found** (T&C names Shopee, Lazada, srichand.com "for example").
- List of "participating" physical stores for everyday point earning — **not found** (only campaign-specific lists).
- Minimum age conflict: T&C says 20+ (or guardian consent); LINE sign-up form says 16+ — **unresolved**.

**Store policies**
- Shipping fee: ฿50 flat was **observed in a live cart only**, not published; remote-area surcharges and whether the ฿599 threshold is calculated before/after coupons — **not verified**.
- Carriers and delivery lead time — **not found**.
- Order-tracking method (tracking numbers, notifications) — **not found** beyond My Account order status and confirmation email.
- PromptPay availability — inferred from a gateway ID in the public API; **not listed on the how-to-buy page**. COD and instalments — **not found / apparently not offered**.
- Customer-service hours (every day 9:00–18:00) come from the member T&C for the phone line; hours for LINE/Facebook/email — **not found**.
- International shipping from srichand.com — **not found**.

**Company / brand**
- Current executives other than the CEO — **not found** (CMO name is from 2022 only).
- Srichand Baby launch year and positioning statement — **not found**.
- Full verified list of all 13 presenters and their assigned lines — only BamBam, Baifern, Zee, NuNew, Kao (from the official banner) and PROXIE (press) are confirmed.
- BamBam's GOT7 membership is general knowledge, not stated in Srichand's own materials reviewed.
- THE MOONRISE FESTIVAL venue — **not stated** on the campaign page.
- Financial figures, market-share ranks and export-market percentages are **company claims reported by press**, not audited data; sources differ slightly (e.g. international share quoted as ~5% in Mar 2026 vs ~10% in Jun 2026).
- English renderings of executive names vary across outlets; Thai spellings (รวิศ หาญอุตสาหะ; พงษ์ หาญอุตสาหะ) are authoritative. "Rawit Hanutsaha" is the romanisation used by LinkedIn/English press.

**Campaigns**
- Campaign details were read from images; small print (e.g. exact permit number, phone numbers) should be re-checked against the live poster before being quoted to customers.
- Which homepage slider banners are actually displayed today vs merely left in the page CSS could not be fully determined; the "Big Deals Begin" banner is dated Aug 2026 and treated as expired.
- Prices/discounts change frequently; treat §4.4 price examples as a snapshot of 2026-09-18.
