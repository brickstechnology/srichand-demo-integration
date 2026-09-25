# 03 · PDPA handling for face photos and skin data

> **Status: draft for legal review.** Based on the Personal Data Protection Act B.E. 2562 and PDPC notifications. Sources and open questions: `research/findings/thai_regulatory.md` §2 and §5.

## Position we recommend (conservative)
- The Act defines biometric data as data from technical processing used to **identify** a person (e.g. face-recognition templates). Commentators say an ordinary photo used for skin analysis is not automatically s.26 sensitive data, and there is no PDPC ruling on skin-analysis photos.
- **Treat it as sensitive anyway**: the *inferences* (skin conditions) may be health data; the PDPC treats biometrics as high-risk; s.26 breaches carry fines up to THB 5 million (s.84) and misuse/unlawful transfer can be criminal (s.79). A cosmetics company was fined THB 2.5 million in August 2025 over a data breach — this sector is being enforced.
- Never run identification, face matching, age/emotion estimation or any processing beyond visible skin characteristics.

## Hard rules (put these in the system prompt)
1. **No photo before explicit consent.** Consent is electronic, specific, separate from T&Cs, not bundled with the service, and as easy to withdraw as to give (s.19). Record the exact text with `record_consent`.
2. Three separate consents: `face_photo_analysis`, `skin_profile_storage`, `cross_border_processing`. Marketing is a fourth, never pre-ticked.
3. **Refusing is fine.** Offer the questionnaire path; the service must still work.
4. **Under 20 = minor.** Default to the questionnaire path with no photo. Under 10: guardian consent always. 10–19: guardian consent too, unless counsel confirms otherwise. The tool enforces this (`minor_requires_guardian`).
5. **Minimise and delete.** The image is processed and the raw file deleted within 24 hours; the database stores only an opaque reference, a hash and derived attributes. Images are never written to the SQL database, logs, analytics or the LLM conversation history.
6. "ลบข้อมูลของฉัน" → confirm once → `withdraw_consent_and_erase`. Tell the customer what was erased and what is kept by law (orders, payments, loyalty ledger). Access/erasure requests must be answered within 30 days.
7. Never use a customer's photo or findings for marketing, training or testimonials.
8. If the customer sends a photo of **someone else** or of a child, do not analyse it; explain why.

## Consent wording (draft, Thai)
Stored verbatim in `consent_records.consent_text_th`; current demo versions are in `scripts/mock_config.json`.
- **Photo:** purpose = analyse visible skin characteristics and recommend products only; not used to identify you; deleted within 24 hours; withdraw any time by typing "ลบข้อมูลของฉัน"; declining does not affect other services.
- **Cross-border:** the AI provider may process data in a country whose protection standard is not equivalent to Thailand's; transfer is under a processing agreement that forbids retention and model training (s.28(2) warning).
- **Profile storage:** we keep what you told us (skin type, goals, reactions) to personalise future advice.

The privacy notice must also state recipients, retention and the DPO contact (s.23). Srichand's site already names `dpo.srichand@aktivist.co.th`.

## Cross-border and vendors
- Sending a photo to a model API hosted abroad is a transfer under ss.28–29. No PDPC adequacy list exists; use Thai-prescribed clauses, ASEAN Model Contractual Clauses or EU SCCs **plus** a data-processing agreement (s.40) **plus** explicit consent with the s.28(2) warning.
- Vendor terms to require: zero data retention, no training on customer data, sub-processor list, breach notice fast enough for Srichand to meet the **72-hour** PDPC notification duty.
- A DPO is probably required for Srichand given sensitive data at scale (s.41) — they already have one.

## What the database stores (and doesn't)
| Stored | Not stored |
|---|---|
| `face_analysis_sessions`: opaque `image_ref`, SHA-256, count, expiry, deletion time, quality flags, model version, observed skin type / undertone / depth, Thai summary | Image bytes, thumbnails, face embeddings, EXIF, location |
| `analysis_findings`: concern, face zone, severity 0–4, confidence, observation | Any diagnosis, any identity attribute |
| `consent_records`: type, policy version, exact text, timestamps, withdrawal, minor flow | — |

After erasure: findings, recommendations and the skin profile are deleted; session rows are blanked (`status = consent_withdrawn`); gap events are anonymised.

## Emerging AI rules
No binding Thai AI law yet. ETDA's draft AI Act (consultation closed 14 Aug 2026) would add chatbot-transparency and deployer duties — the advisor already discloses that it is an AI.
