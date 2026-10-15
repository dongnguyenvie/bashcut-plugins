---
name: product-ad
description: Recipe for an ad or selling video (paid, commerce, UGC, launch, channel teaser): a truth source, hook and CTA as a pair, an arc from what the product has, disclosure rules, one-change A/B variants. Use after bashcut.vlog:plan picks product-ad. Triggers: "quảng cáo", "video bán hàng", "TVC", "chạy ads", "UGC", "A/B test".
---

# Product ad

Reply in the user's language. An ad sells one thing to one audience; a review (`bashcut.vlog:product-review`) judges
it. Plan with `bashcut.vlog:plan`, edit with `bc:edit-workflow`. A measured reference ad the user points to wins over
every range here (T15 §7).

## 1. Ad brief first

Fill these before writing a word, in the brief (`project set-data brief`, each `{value, status, source}`; T14 §4):

| Field | What | Where it lives |
|---|---|---|
| audience and pain | who, and the problem they feel | `audience` |
| one core benefit | the single thing to remember | `angle` |
| proof that exists | a demo in the footage, a sourced number, a real review the user can share | `ideas`, `notes` |
| CTA | one action: buy, visit, comment, follow | `goal` |
| placement | paid feed, organic commerce or UGC, launch film; the outputs | `outputs`, `notes` |
| truth source | product page, spec sheet or the user, for every claim | `notes` with the link |
| channel name, @handle, logo (channel or brand teaser) | exactly as the user spells them; the logo as a file | `channelName`, `handle`, `logo` |

These are the `askAtIntake` fields (one intake round; name, handle and logo as one question). No answer: decide,
write it `inferred` with its reason. Never invent a handle or a logo: without them, the brand name as plain text.

## 2. Hook and CTA as a pair

Write them together; the CTA pays off what the hook promises (T14 §4). The pair is the plan's `promise` `{hook,
payoff}`, written with `bashcut.vlog:hook-script` (2–3 openings on the real footage compared before locking one). One
message: an ad that argues a second point fails the strategy audit. Hook and offer must read with the sound off.
After the rough cut, read both ends (opening and close words, titles, first shots) and check the close answers the
opening and the product is on screen when the placement needs it.

## 3. Pick an arc from what you have

Choose the arc for something the product or footage has ("a visible before/after → Before/After"); drop a device
with no reason (T14 §4). Examples from published practice, not slots (T14 §7):

| Arc | Best for |
|---|---|
| Problem → agitate → solve (PAS) | a pain the audience already feels |
| Before / after | a visible change (skin, a room, a photo) |
| Demo loop | a product whose use is the proof |
| Feature cascade | several small features, each with its own shot |
| Testimonial | a real customer or the creator's honest use |
| Channel or brand teaser: question → proof → reveal → a new loop for the CTA | a channel, series or brand, not one product: the reveal answers the opening question, and the CTA ("follow @handle for the next one") opens the next |

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`; feed → `feed-4x5`, `square`; landscape promo → `youtube-1080`.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Promise `hookSeconds` | visual + verbal promise in 1–3 s; the full hook 2–8 s (T14 §3) | shorter for paid feed and commerce; longer for a launch film | `transcript words --to F`, `review layout --to F` |
| Product first on screen | commerce with a cart link: within about 3 s; brand or launch film: at the reveal, after the pain (T14 §3, a contradiction) | placement and arc; say which | `review shots --to F` → `described` subjects' `firstSeconds` |
| Total length | 6–15 s paid cut-down; 15–45 s organic commerce or UGC; 30–60 s launch or SaaS promo (T14 §3) | placement, proof needed, speech density; `maxSeconds` is the only hard limit | `platforms get`; brief `lengthSeconds` |
| Beat proportions | hook 10–15 %, problem 15–25 %, solution or demo 30–45 % (the longest), proof 15–25 %, CTA 7–15 % (T14 §3) | the arc; how long the product action takes on the footage | sections vs markers (`review run`) |
| Montage / demo shot | 0.6–1.2 s in a music montage; 2–3 s per demo beat; longer for hero and proof (T14 §3) | music tempo; the action's length | `review shots --summary` per section |
| `maxShotSeconds` | the top of the demo band; one hero hold at 1.5–2.5× the average (T07 §3) | a demo that must be followed holds longer | `review shots --summary` |
| CTA hold | 2–4 s paid social; 5–9 s when the end card carries a URL or logo (T14 §3) | CTA words and reading time | `review layout --from F` → `holdSeconds` |
| Re-hook | one per about 10–20 s; a soft mid-roll CTA only past about 20 s (T14 §3) | sources disagree on closing the loop before the CTA; record which | `review shots --summary` |
| On-screen copy `captionLineChars`, `minTextSize` | about 6 words a frame or fewer; hook text up to about 60 characters in 9:16 (T14 §3) | font, hold, sound-off viewing | `review layout` |
| Speech rate | the speaker's or voice's measured rate; never sped up to fit (T02 §4, T14 §3) | speaker, language, voice | `speech rate`, `narration windows` |
| Music under the voice | 5–18 dB (T11 §3) | the product's own sound leads when it is the point | `audio mix-measure` |

## Truth rules (not taste)

- Every number, price, superlative and comparison has a source in the brief. No source: cut it or show only what the
  footage proves (T14 §7).
- One feature per shot, each shot new information. A claim without its shot is cut or shown as text with its source.
- Never invent capabilities, customers, reviews, numbers, urgency ("chỉ hôm nay") or logos (T14 §4).
- Sponsorship: said in the first seconds, `vlog-disclosure` on screen, the user's wording. AI-generated people,
  voices or shots: no label on the video; the platform's upload toggle (`bashcut.vlog:publish`).
- Price and offer exactly as the merchant states them; ask when unsure.

## Variants: change one thing

Variants are for a real A/B test only; a revision is made in place. Each variant changes **one** field and shares
everything else, including the cut (T14 §3, §4):

1. Finish, review and save the base version first.
2. `variants create <name> --changed "<the one change>"`, open the copy, make only that change, review it.
3. `variants diff <other>`: anything beyond the declared change is a mistake to undo.
4. Check one variant in **every** output shape (`ui frame --phone` at the hook and the CTA) before making the batch.
5. Typical single changes: the hook, the opening shot, the CTA wording, the voice, the music. A wider "angle" spread
   is for exploring, not testing.

Naming a winner is not BashCut's job and needs real numbers: several hundred to about 1,000 impressions per variant
over 3–7 days (T14 §3). Say this when the user asks which won.

## Shots, text, sound, look

- Shots: hero (product alone, clean background), in use, the result, the pain (before), hands, scale against
  something known, the CTA background. Missing: plan rows with `source: stock` or `generated`
  (`bashcut.vlog:scene-prompt`).
- Every number on screen with its source in the brief; the offer readable on mute.
- One music bed under the voice, a sized sound on the reveal; the product's own sound when it is the point.
- Colour: true to life first, mood second; measure first (`bc:color-grade`).
- Transitions: hard cuts as the base; `vlog-zoom-hit` (or `crash-zoom`) on the reveal; one or two special
  transitions a minute at most (T08 §3).

## Review notes

- Blockers: the product missing from the opening (commerce), an offer unreadable on mute, a CTA gone before it is
  read.
- Montage shots under 1 s are the style: short-shot notes stay info.
- `needs_user`: the truth source, the placement, sponsorship wording, the exact price and offer, which variants,
  music.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3).

- `promise`: the hook and CTA pair (§2).
- `stages`: `{"effects": {"required": true, "skill": "bc:motion-graphics", "why": "offer card, CTA card with @handle and logo"}, "colour": {"rules": ["true-to-life product colour first"]}, "visuals": {"skill": "bc:visual-plan", "after": "voiceover", "required": true, "why": "the voiceover or the creator's speech carries it; each line gets the product, a proof or a card"}}`
- `checks` (source: product-ad recipe): `claims-sourced` every number and claim has a source in the brief;
  `product-first` commerce: the product on screen within the plan's `hookSeconds` (about 2–4 s); `offer-on-mute` the
  offer reads with the sound off; `cta-hold` the CTA holds long enough to read (2–4 s, 5–9 s with a handle or URL);
  `cta-handle` @handle and logo visible through the CTA (channel teaser); `new-loop` channel teaser: the reveal answers
  the opening question and the CTA opens a new one; `disclosure` a sponsored ad says so early; nothing else (AI,
  stock, effects) is labelled on the video.
- `askAtIntake`: `["truthSource", "placement", "channelName", "handle", "logo"]` (the last three only for a channel or
  brand teaser).
