# Team guidelines (long-form, for people)

> **The agent does not read this folder.** What the agent reads lives in `hub/` — `hub/journeys` (procedures) and `hub/knowledge` (reference), in the Integration Hub's own format. These files are the fuller versions for the Bricks team, Srichand's brand team and legal: they keep the reasoning, the engineering notes (output blocklist, vendor terms) and the "needs lawyer review" lists that do not belong in an agent prompt.

# Original knowledge base notes

These Markdown files are the **RAG layer**: guidance the agent retrieves as text. Product facts are *not* here — they live in the SQL database and are read through tools, so they can never drift or be paraphrased wrongly.

| File | Use it when… | Status |
|---|---|---|
| `01-advisor-persona-and-flow.md` | deciding what to say or which tool to call next | Bricks draft |
| `02-thai-fda-claims-guardrails.md` | wording ANY benefit, skin observation or product claim | Draft — **legal review required** before launch |
| `03-pdpa-face-photo-handling.md` | a photo, consent, a minor, or a deletion request is involved | Draft — **legal review required** |
| `04-range-gap-policy.md` | Srichand has no product for the need | Agreed with client lead (Bricks) |
| `05-skin-analysis-protocol.md` | asking for, reading, or describing a face photo | Bricks draft |
| `06-ingredient-and-routine-rules.md` | combining actives, pregnancy, sensitivity, routine order | Bricks draft (cosmetic science) |
| `07-store-policies-and-rewards.md` | shipping, payment, returns, contact, Srichand Rewards, campaigns | Sourced from srichand.com, 18 Sep 2026 |
| `08-brand-and-range-overview.md` | the customer (or an executive) asks about the company, brands or lines | Sourced |

## Loading notes for the engine
- Chunk on `##` headings; every section is written to stand alone.
- Keep the file name and heading as chunk metadata so the agent can cite "per guideline 02 §3".
- Files 02 and 03 are **guardrails**: load their "Hard rules" sections into the system prompt rather than relying on retrieval.
- Underlying research with full source lists: `research/findings/thai_regulatory.md` and `research/findings/rewards_policies_brand.md`.

## Division of labour
| Question | Answered by |
|---|---|
| What products exist, price, shade, stock, ingredients, official claims? | SQL via tools (`search_products`, `get_product`, `check_stock`, …) |
| Which products for this person? | `recommend_routine` (deterministic) — the LLM explains, it does not choose |
| How may I phrase it? What must I never say? | This knowledge base |
| Order, payment, tracking, points | SQL via tools |
