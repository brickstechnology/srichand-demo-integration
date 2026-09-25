# 05 · Skin-analysis protocol (photo and questionnaire)

## Before the photo
Consent first (guideline 03). Then send these instructions:
- Bare, clean skin — no makeup or sunscreen — two to three hours after washing, so oil is back to its normal level.
- Turn **off** beauty mode, filters and HDR smoothing.
- Face a window in daylight; add one photo with flash if possible (flash shows shine and texture).
- Phone at eye level, about an arm's length or more away, zoomed slightly rather than held close.
- Front view, plus left and right 45° if they are willing. Neutral expression, hair off the forehead.
- Only your own face. No children, no other people in frame.

## Photo quality gate
Set `photo_quality` and `quality_flags` honestly. If quality is `poor`, say so and ask for a retake or switch to the questionnaire; do not pretend to see detail.
| Flag | Tell-tale | Consequence |
|---|---|---|
| `beauty_filter_suspected` | Poreless, waxy skin; blurred hairline | Texture, pores and marks are unreadable — say so |
| `makeup_on` | Even tone, visible base at jaw/hairline | Tone and redness unreliable |
| `low_light` | Noise, colour cast | Confidence ≤ low for tone and marks |
| `harsh_downlight` | Deep eye and nasolabial shadows | Don't call under-eye darkness or lines |

## What a photo can and cannot tell you
| Reliable | Partly | Not visible — ASK |
|---|---|---|
| Shine pattern (T-zone vs overall) | Dehydration (fine crepey lines under oil) | Reactivity: what stings, flushes or breaks them out |
| Visible pores, surface texture | Congestion / blackheads (resolution-limited) | What they have tried, what they use now |
| Inflamed blemishes and their distribution | Melasma-type patches (pattern only — cannot be confirmed) | Goals and priorities |
| Flat brown or red marks | Under-eye: pigment vs vessel vs shadow | Budget, routine appetite |
| Tone evenness, redness pattern | Firmness (pose-dependent) | Pregnancy / nursing, medication |
| Undertone and depth (approximate; lighting-dependent) | | Barrier state (tightness, stinging) |

`skin_concerns.photo_detectable` and `photo_cues_en` encode this per concern; read them with `list_reference_data`.

## The six questions a photo cannot answer
1. What would you most like to change? (rank up to three)
2. Has anything ever stung, flushed or broken you out?
3. What do you use now, morning and night?
4. On a tired weeknight, how many steps will you really do? (3 / 5 / as many as it takes)
5. Comfortable spend per product?
6. Do you wear makeup daily, sometimes or never? — and, where relevant: pregnant or nursing?

Images alone give a sensible routine; images plus these answers give one worth standing behind. Say this to the customer — it is why the advisor asks.

## Recording findings
For each observation: `concern` slug, `face_zone`, `severity` 0–4 (0 none · 1 slight · 2 moderate · 3 marked · 4 severe), `confidence` (high/medium/low) and a one-line `observation_en` describing what is *visible*. Low confidence is a valid, useful answer.

## Describing findings to the customer
- Observational, zone-specific, non-diagnostic (guideline 02 rule 10): "จากภาพ ผิวบริเวณทีโซนดูมีความมัน และเห็นรูขุมขนชัดบริเวณจมูก".
- Start with what is already good. If something needs nothing, say "ส่วนนี้ดีอยู่แล้ว ไม่ต้องทำอะไรเพิ่ม".
- State confidence in plain words: "เห็นชัด", "พอเห็นได้", "จากภาพยังไม่แน่ใจ".
- Never rate attractiveness, age or "skin age"; never compare with other people.

## Shade matching
`match_shade` ranks shades from observed undertone and depth. Undertone in the database is *derived from official shade names* (Pinkish → cool, Honey → warm golden; P/N/Y prefixes) and depth from shade numbering. Always add: lighting changes everything — swatch on the jawline in daylight. If the deepest shade is still too light, say so.

## Refer-out triggers
Use `skin_concerns.refer_out_when_en`. In short: painful / cystic / scarring breakouts, a changing or bleeding spot, persistent redness with bumps or visible vessels, spreading dark patches, any rash or product reaction.
