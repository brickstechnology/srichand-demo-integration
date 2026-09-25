# 07 · Store policies, Srichand Rewards and live campaigns

Facts read from srichand.com on 18 Sep 2026 (full notes and URLs: `research/findings/rewards_policies_brand.md`). Policies change — re-verify before launch.

## Shipping
- **Free shipping from ฿599.** Below that the live cart charged a **฿50** flat fee (the fee itself is not published on any policy page).
- Carriers and delivery lead times are not published. In the prototype, couriers and ETAs are simulated.
- The site has no order-tracking page; tracking through the LINE advisor is therefore a genuine service improvement.

## Payment
- Offered: **mobile banking, credit/debit card, TrueMoney, PromptPay**.
- **Cash on delivery is not offered**, nor instalments. The prototype contains no COD orders.
- In the demo, PromptPay QR codes are mock references and `confirm_payment_mock` stands in for the gateway webhook.

## Returns, refunds, cancellation
- Report a problem **within 3 days of delivery**; only wrong or defective items. No change-of-mind returns. An unboxing video is requested.
- Goods go back sealed within 14 days; refunds can take up to 30 business days.
- An order can be cancelled only **before it reaches "Ready to Ship"**.
- The advisor does not decide claims — it explains the policy and hands over to customer service.

## Customer service
Phone **02-300-1661**, every day 9:00–18:00 · **support@srichand.co.th** · Facebook "SRICHAND ศรีจันทร์" · LINE **@srichand1948** (SASI: **@sasidiary**). Data-protection contact: dpo.srichand@aktivist.co.th.

## Srichand Rewards (official rules)
- **Single-level points programme — no tiers are published.**
- **Earn: ฿25 = 1 point** on the net amount paid (after discounts, excluding shipping); remainders under ฿25 per receipt earn nothing.
- **Point value: not published** ("at the company's discretion"). Points cannot be exchanged for cash or transferred. ⚠ The prototype's redemption value (1 point = ฿0.50) and reward catalogue are **assumptions for the demo**.
- **Expiry:** one year, "counted from the year received" (exact rule ambiguous). An account inactive for three years may be closed.
- **Join (prototype):** the advisor can sign a new member up in the chat with `register_member` (name, mobile, birth date, explicit terms acceptance, optional marketing consent). It returns the member number; staff link the LINE chat to it in the hub. The prototype sends no SMS OTP — the record is stored with `phone_verified = 0`.
- **Join (official flow today):** add LINE @srichand1948 → register with Thai mobile number + SMS OTP → link the srichand.com account with member ID and latest order number.
- **Channels:** srichand.com, Shopee and Lazada orders post within 17 days once linked; physical-store receipts uploaded in LINE post within 48 hours. TikTok Shop is not mentioned.
- Missing points must be disputed within 30 days.
- ⚠ Age conflict for the client to resolve: T&Cs say members must be 20+, the LINE sign-up form says 16+.
- Birthday or welcome benefits: none found on official pages (so none are simulated).

## Campaigns live on 18 Sep 2026
| Campaign | Mechanics |
|---|---|
| **THE MOONRISE FESTIVAL 2026** | 78th-anniversary fan event, Sun 25 Oct 2026. Buy Srichand + SASI products 7–27 Sep and upload the receipt in LINE to enter a draw for 900 seats. Marketplace, COD and pre-orders excluded. |
| **Website coupons, 1–30 Sep** | ฿30 off at ฿399 · ฿70 off at ฿699 · ฿150 off at ฿1,299 (collectable coupons; no code strings are published — `SEP30/70/150` in the DB are placeholders). |
| **Free gift at ฿499** | Three Skin Moisture Burst sachets + canvas bag, limited to 100. Verified in a live test cart (added at ฿522, not at ฿493). Other gift listings print thresholds (฿699 … ฿3,555) but were not triggered in live carts → stored as inactive. |
| **Buy-1-get-1 sachets** | Barrier Boost and Timeless sachet packs at ฿117 / ฿234. |
| **Sale prices** | Most core skincare is ฿269 against list prices of ฿399–495; stored per SKU as `list_price` / `sale_price`. |

## What the advisor should do with this
- Quote prices and promotions only from `get_promotions`, `cart_view` and `get_product` in the current conversation.
- Use "อีก ฿X ส่งฟรี" nudges from `cart_view.add_for_free_shipping` — honestly, never by padding the routine.
