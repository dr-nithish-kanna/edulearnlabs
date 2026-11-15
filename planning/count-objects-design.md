# Design: Count objects 1 to 10 (game 5, MVP number 1)

Draft 2026-11-15. Status: owner picks made, defaults below, waiting for the owner's critique. Nothing built.

## 1. The skill

- Grade: Pre-K. Subject: math. Topic: counting. Taxonomy id: `math.counting.count-objects`.
- One micro-skill: **count a group one object at a time, and know the last number said is the total** (cardinality).
- Common Pre-K errors this game must prevent: skipping an object, counting one twice, and saying the numbers
  correctly but not knowing the last one is "how many".

## 2. Owner decisions (2026-11-15)

| # | Decision | Pick |
|---|---|---|
| 1 | Cast and story | Hungry hedgehog and friends (hedgehog, duck, mouse), each asks for things to count |
| 2 | Reward (website-owned) | Parade of animals, one new animal per solved round |
| 3 | Mechanic | New kit mechanic `tap-count`, plus the existing `fill-container` for "give me N" |

## 3. Level ladder

| Level | Numbers | Layout | What the child does | Mechanic |
|---|---|---|---|---|
| 1 | 1 to 5 | Neat row | Tap each object once, then answer "How many?" | `tap-count` |
| 2 | 1 to 10 | Neat rows (5 + 5) | Same, more objects | `tap-count` |
| 3 | 1 to 10 | Messy pile | Same, objects scattered so skipping is easy | `tap-count` |
| 4 | 1 to 10 | Bins | "Give the duck N acorns": drag N into a basket | `fill-container` |

Defaults: advance after 2 correct rounds in a row (matches the session adapt rules), never drop below the current
level on a miss, a miss only repeats the hint.

## 4. The `tap-count` mechanic (needs an Opus design pass)

- Each object can be tapped once. A tapped object hops, shows a number badge, and plays a note. Tapping a counted object
  does nothing (no error, no sound). Order is free, because the child may count left to right or any way.
- Numbers are assigned in tap order (1st tap is 1, 2nd tap is 2), so the child's own order is always honoured.
- When all objects are counted, a "How many?" step appears with number choices. The correct answer equals the last
  number said. The child must tap objects before the choices show, so a child cannot win by guessing.
- One badge at a time in a top layer (playbook lesson: labels on crowded objects get hidden).
- Hints only: a wrong choice dims, then the objects recount themselves slowly with voice, ending on the total. Never a
  red X or buzzer. The answer is shown only as a recount, never as the first reaction.
- Hit targets at least 64 px. Tap, keyboard (Tab and Enter), and a reduced-motion version of every animation.
- Pure logic lives in a kit module with unit tests (tap order, double-tap guard, planned distractors for the choices).
- Flag: this changes shared kit shape, so write `planning/tap-count-design.md` with Opus before any code, and
  ship it as a new kit minor version (v0.6.0). Games pin a tag or full SHA.

## 5. Story and cast

- Hedgehog asks for apples, duck for pebbles, mouse for acorns. Three requests per session of about 3 minutes.
- Voice line first, then tones. Each number maps to the pentatonic scale already in the kit (1 to 10 on C4).
- Every sound has a visual twin (the badge pop), because many children play muted.
- Reading load: words are short (for example "Count the apples"), pictures and voice carry the meaning.

## 6. Reward: Parade of animals (website-owned)

- The game only reports `rewards`. The website stores them as facts, same pattern as garden, word wall and quilt.
- One animal per solved round, fixed cycle of species, growth by rounds solved and never by time. No streaks.
- Defaults: 200 cap that folds the oldest into a count, own schema version, newer-schema guard.
- A parent "My parade" page is a later item, like the other reward pages.

## 7. Website and SEO

- Game id: `count-objects-prek`. Page: `/math-games/counting-for-preschool/` (title with keyword, age, benefit).
- 300 to 600 words of real text: what it is, what kids learn, who it is for, how to play, why it helps.
- Catalog entry in `src/data/games.json`, skill `math.counting.count-objects`, home card.
- No ads, prices or external links in the game.

## 8. Open questions with my defaults

1. Title: **Hedgehog Picnic**. Alternative: Count with Hedgehog.
2. Level 4 (give me N) in the first release or later? Default: in the first release, since the mechanic already exists.
3. Voice: browser speech synthesis now, recorded voice later (same as the other games).
4. Portrait layout: still the "turn your phone sideways" prompt, as with the other games.

## 9. Next steps

1. Owner critiques this doc.
2. Opus design pass: `planning/tap-count-design.md` (kit mechanic and data shape).
3. Static art preview in `brand/count-objects/` (hedgehog, duck, mouse, apples, pebbles, acorns). Owner approves.
4. Build bottom-up: kit mechanic with tests, content generator, game screens, browser tests, website support, sync.
