---
name: product-ad
description: Recipe for a product ad or selling video in BashCut (paid feed cut-down, organic commerce or UGC, launch or SaaS promo) — an ad brief with a truth source (and channel name, @handle and logo for a channel teaser), the hook and CTA written as a pair (plan.promise) and checked over the opening and the close, an arc chosen from a menu (including a channel or brand teaser) by what the product and footage have, beat proportions instead of fixed seconds, truth and disclosure rules for every claim, and variants that change one thing each (variants create, variants diff); ranges with sources for the review profile. Use after bashcut.vlog:plan or bc:edit-workflow picked product-ad, or when the user wants an ad, a channel or brand teaser, a product video that sells, a TVC or several ad versions to test. Triggers: "quảng cáo", "video quảng cáo", "video bán hàng", "TVC", "ads", "chạy ads", "UGC", "video ra mắt sản phẩm", "nhiều phiên bản", "A/B test".
---

# Product ad

Reply in the user's language. An ad sells one thing to one audience; a review (`bashcut.vlog:product-review`) judges
it. Plan with `bashcut.vlog:plan` (sections, shot rows, ranges into the plan, the review profile), then edit with
`bc:edit-workflow`. A measured reference ad the user points to wins over every range here (T15 §7).

## 1. Ad brief first

Fill these before writing a word, and write them into the brief (`bashcut project set-data brief`, each `{value, status,
source}`; T14 §4):

| Field | What | Where it lives |
|---|---|---|
| audience and pain | who, and the problem they feel | `audience` |
| one core benefit | the single thing the viewer should remember | `angle` |
| proof that exists | a demo in the footage, a number with a source, a real review the user can share | `ideas`, `notes` |
| CTA | one action: buy, visit, comment, follow | `goal` |
| placement | paid feed, organic commerce or UGC, launch film; and the outputs | `outputs`, `notes` |
| truth source | the product page, spec sheet or the user, for every claim | `notes` with the link |
| channel name, @handle, logo (a channel or brand teaser) | exactly as the user spells them; the logo as a file | `channelName`, `handle`, `logo` |

These are the recipe's `askAtIntake` fields: they join the one round of intake questions (`bc:edit-workflow`; the
channel's name, handle and logo as one question). No answer: decide, write the field `inferred` with its reason, and
the strategy audit checks it. Never invent a handle or a logo: without them, the brand name as plain text.

## 2. Hook and CTA as a pair

Write the hook and the CTA together; the CTA pays off what the hook promises (T14 §4). The pair is the plan's
`promise`: `{"hook": "<the opening's question or claim>", "payoff": "<the CTA line that closes it>"}`, written with
`bashcut.vlog:hook-script`. One message: an ad that also argues a second point fails the strategy audit. Write 2–3 openings on the real
footage and compare them (`bashcut.vlog:hook-script` §3) before locking one. The hook and the offer must read with the
sound off.

After the rough cut, read both ends: the opening (`transcript words --to F` first words, `review layout --to F`
first title, `review shots --to F` first cut and described subjects) and the close (`transcript words --from F`,
`review layout --from F` last title and its hold). Check the pair: does
the close answer the opening's promise, and is the product on screen when the placement needs it?

## 3. Pick an arc from what you have

Choose the arc because of something the product or footage has ("the product has a visible before/after → Before/
After"); drop a device that has no reason (T14 §4). Worked examples from published practice, not slots (T14 §7):

| Arc | Best for |
|---|---|
| Problem → agitate → solve (PAS) | a pain the audience already feels |
| Before / after | a visible change (skin, a room, a photo) |
| Demo loop | a product whose use is the proof (a gadget, an app) |
| Feature cascade | several small features, each with its own shot |
| Testimonial | a real customer or the creator's own honest use |
| Channel or brand teaser: question → proof → reveal → open a new loop for the CTA | promoting a channel, a series or a brand, not one product: the reveal answers the opening question, and the CTA ("follow @handle for the next one") opens the next |

## Ranges

Outputs: vertical → `tiktok`, `reels`, `shorts`; feed → `feed-4x5`, `square`; landscape promo → `youtube-1080`. Write
each chosen value and its reason in the plan.

| Check (review key) | Sample range | Why it varies | Measure with |
|---|---|---|---|
| Promise `hookSeconds` | visual + verbal promise in 1–3 s; the full hook 2–8 s (T14 §3) | shorter for paid feed and commerce; longer for a launch film the viewer chose to watch | `bashcut transcript words --to F`, `review layout --to F`, `firstCut` |
| Product first on screen | commerce with a cart link: within about 3 s; a brand or launch film: at the reveal, after the pain (T14 §3, a contradiction) | placement and arc; say which you chose | `bashcut review shots --to F` → `described` subjects' `firstSeconds` (after `media describe`) |
| Total length | 6–15 s paid cut-down; 15–45 s organic commerce or UGC; 30–60 s launch or SaaS promo (T14 §3) | placement, how much proof the product needs, speech density; the platform's `maxSeconds` is the only hard limit | `bashcut platforms get <id>`; the brief's `lengthSeconds` |
| Beat proportions | hook about 10–15 %, problem or context 15–25 %, solution or demo 30–45 % (the longest), proof 15–25 %, CTA 7–15 % (T14 §3) | the arc, and how long the product action really takes on the footage | plan sections against their markers (`bashcut review run`, section off plan) |
| Montage / demo shot | 0.6–1.2 s in a music montage; 2–3 s per demo beat; longer holds for the hero and the proof (T14 §3) | music tempo; how long the action takes | `bashcut review shots --summary` per section |
| Longest shot `maxShotSeconds` | the top of your demo band; one hero hold at 1.5–2.5× the average (T07 §3) | a demo that must be followed holds longer | `review shots --summary` max |
| CTA hold | 2–4 s for paid social; 5–9 s when the end card carries a URL or logo to read (T14 §3) | CTA words and reading time | `bashcut review layout --from F` → the last title's `holdSeconds` |
| Re-hook | one re-hook or open loop per about 10–20 s of runtime; a soft mid-roll CTA only past about 20 s (T14 §3) | sources disagree on closing the loop before the CTA or keeping one into it; record which | `review shots --summary` per section |
| On-screen copy `captionLineChars`, `minTextSize` | about 6 words per frame or fewer; hook text up to about 60 characters in 9:16 (T14 §3) | font, hold, sound-off viewing | `bashcut review layout` → `longestLineChars`, `holdSeconds`, `fontShare` |
| Speech rate | the speaker's or voice's own measured rate; never sped up to fit (T02 §4, T14 §3) | speaker, language, voice | `bashcut speech rate`, `bashcut narration windows --rate <r>` |
| Music under the voice | 5–18 dB under (T11 §3) | the product's own sound leads when it is the point | `bashcut audio mix-measure` → `musicUnderSpeech` |

## Truth rules (not taste)

- Every number, price, superlative and comparison has a source in the brief (product page, spec sheet, the user). No
  source: cut it or show only what the footage proves (T14 §7).
- One feature per shot, and every shot adds new information. A claim without its shot is cut or shown as text with its
  source (T14 §4).
- Never invent capabilities, customers, reviews, numbers, urgency ("chỉ hôm nay") or logos. Use the brand name as
  plain text when no verified logo file is given (T14 §4).
- Sponsorship: said in the first seconds and `vlog-disclosure` on screen; ask the user for the wording. AI-generated
  people, voices or shots: the platform's label (`bashcut platforms get <id>` → `disclosure`).
- Price and offer exactly as the merchant states them; ask when unsure.

## Variants: change one thing

Variants are for a real A/B test only; a revision of the ad is made in place (`bc:edit-workflow`, revision). When the
user wants versions to test, each variant changes **one** field and shares everything else, including the cut
(T14 §3, §4):

1. Finish, review and save the base version first.
2. `bashcut variants create hook-b --changed "hook: price question instead of the before/after"` writes a copy next to
   the project. Open it (`bashcut project open <folder>`), make only that change, review it.
3. `bashcut variants diff <other>` shows what really differs; anything beyond the declared change is a mistake to undo.
   `bashcut variants list` shows all of them with what each changes.
4. Check one variant in **every** output shape (`bashcut ui frame <frame> --phone` at the hook and the CTA, per output)
   before making the batch (T14 §4).
5. Typical single changes: the hook, the opening shot, the CTA wording, the voice, the music. A wider "angle" spread is
   for exploring, not testing.

Naming a winner is not BashCut's job and needs real numbers: sources ask for several hundred to about 1,000
impressions per variant over 3–7 days before calling it (T14 §3). Say this when the user asks which one won.

## Shots

Hero (product alone, clean background), the product in use, the result, the pain (before), hands, scale against
something known, the CTA background. Commerce: the product clearly in the first seconds. Missing shots: plan rows with
`source: stock` or `generated` (`bashcut.vlog:scene-prompt`), labelled when not the user's own.

## Text, sound, look

- Every number on screen with its source in the brief; the offer readable on mute.
- Sound: one music bed under the voice, a sized sound on the reveal; the product's own sound when it is the point.
  Loudness is each output's own target (`bashcut platforms get`).
- Look intent: true-to-life product colour first; mood second. Measure first (`bc:color-grade`).
- Transitions: hard cuts as the base; `vlog-zoom-hit` on the reveal; one or two special transitions per minute at most
  (T08 §3).

## Review notes

- A viewer notices first: the product missing from the opening (commerce), an offer they cannot read on mute, a CTA
  that is gone before it is read. Treat these as blockers.
- Fast montage shots under 1 s are the style here: short-shot notes stay info.
- `needs_user`: the truth source, the placement, sponsorship wording, the exact price and offer, which variants to
  make, music choice.

## Plan data

What this recipe adds to the plan (`bashcut.vlog:plan` §3); `bc:edit-workflow` and the critic read it.

- `promise`: the hook and CTA pair (§2).
- `stages`: `{"effects": {"required": true, "skill": "bc:motion-graphics", "why": "offer card, CTA card with @handle and logo"}, "colour": {"rules": ["true-to-life product colour first"]}}`
- `checks` (source: product-ad recipe): `claims-sourced` every number and claim has a source in the brief;
  `product-first` commerce: the product on screen within about 3 s; `offer-on-mute` the offer reads with the sound
  off; `cta-hold` the CTA holds long enough to read (2–4 s, 5–9 s with a handle or URL); `cta-handle` @handle and
  logo visible in the last 3 s (channel teaser); `new-loop` channel teaser: the reveal answers the opening question
  and the CTA opens a new one; `disclosure` sponsorship or AI shots labelled.
- `askAtIntake`: `["truthSource", "placement", "channelName", "handle", "logo"]` (the last three only for a channel or
  brand teaser).
