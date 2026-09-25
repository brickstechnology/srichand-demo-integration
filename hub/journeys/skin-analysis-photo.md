---
display_name: วิเคราะห์ผิวจากรูปถ่าย
slug: skin-analysis-photo
description: ใช้เมื่อลูกค้าอยากให้ดูหรือวิเคราะห์ผิวจากรูป หรือส่งรูปหน้าตัวเองเข้ามา เช่น "ช่วยดูผิวให้หน่อย" "ผิวเราเป็นแบบไหน" "วิเคราะห์หน้าให้หน่อย" "ส่งรูปให้ดูได้ไหม" "ดูจากรูปนี้ควรใช้อะไร"
---
## Goal
With explicit consent, describe what is visible on the customer's skin, record it, and hand over to the routine journey. Never diagnose.

## Steps
1. Call `get_customer`.
   - Chat not linked to a member → the analysis cannot be saved. Offer two choices: sign up first (journey `membership-signup-and-linking`), or get advice from a few questions without saving (journey `skin-analysis-questionnaire`).
   - Under 20 → do not ask for a photo. Go to `skin-analysis-questionnaire`.
   - Age unknown → ask them to confirm they are 20 or older before going on.
2. A photo arrived before consent → do not look at it or describe it. Say so kindly and continue with step 3.
3. Consent. Explain in one short message what the photo is used for. Then ask for each consent separately and call `record_consent` after each explicit yes, using the exact Thai texts from the privacy knowledge file:
   a. `face_photo_analysis`
   b. `cross_border_processing`
   c. `skin_profile_storage`
   If (a) or (b) is refused → go to `skin-analysis-questionnaire`. If only (c) is refused → continue, but save nothing about what they tell you.
4. Send the photo instructions from the photo knowledge file.
5. When photos arrive, judge quality and flags. Poor → ask for one retake; still poor → questionnaire.
6. Ask the questions a photo cannot answer, one at a time. If (c) was given, save the answers with `save_skin_profile`.
7. Call `list_reference_data` once for the concern and skin-type codes.
8. Observe. For each finding: concern code, face zone, severity, confidence, one line on what is visible.
9. Tell the customer, using the observation wording: what is already good, the main observations by zone with how sure you are, what could not be judged. Add the "observation, not a diagnosis" sentence.
10. Call `save_skin_analysis` with the image count, quality, flags, observed skin type, undertone, depth, a short Thai summary and the findings. Keep the returned session id.
11. Continue with `routine-recommendation`, passing the session id.

## If
- The photo shows someone else, a child, or several people → do not analyse; explain why.
- Something matches a "see a doctor" sign → switch to `skin-reaction-or-medical-concern`.
- A tool answers that a consent is missing → ask for that consent, then retry once.

## Knowledge to open
- `privacy-consent-and-data-rules`
- `photo-guidelines`
- `skin-observation-wording`
- `concern-and-skin-type-glossary`
- `result-codes-and-customer-wording`

## Tools
`get_customer` · `record_consent` · `list_reference_data` · `save_skin_profile` · `save_skin_analysis`
