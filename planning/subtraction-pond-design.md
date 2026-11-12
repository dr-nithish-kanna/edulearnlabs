# Pond Hop (Subtraction for Grade 1): creative design plan (draft for review)

Status: DRAFT, 2026-11-12. Nothing is built from this. Written following section 7 of `planning/game-playbook.md`.
Every open question has a default in section 10, so you can critique the whole thing without answering first.
Working title is "Pond Hop". Keyword title and URL: "Subtraction for Grade 1", `/math-games/subtraction-for-grade-1`.

## 1. The game in one sentence

Frogs sit on a lily pad. A friend says "3 frogs are going for a swim!" The child sends 3 frogs hopping into the
water, then taps how many are still on the pad. Later levels use a lantern of fireflies on a ten-frame.

Skill: `math.subtraction.within-20` (Grade 1, "take away", numbers up to 10 first, then up to 20).
Game id `subtraction-grade-1`, repo `dr-nithish-kanna/subtraction-grade-1` (you create it from the template).

## 2. Why this game next (short version)

- It is the natural pair of Addition Garden. A parent who sees one will look for the other (good for the site).
- It is the best test of whether `fill-container` is really reusable. If the second game needs a lot of kit surgery,
  the mechanic was too specific, and we want to learn that now.
- Lowest risk of the three candidates: no new art pipeline, no new audio pipeline, no layout rewrite.
- The risk is the opposite one: it can feel like Addition Garden with the arrows reversed (your "AI slip" worry).
  Section 3 lists the four things that make it feel different.

## 3. Creative direction (the recommended combination)

| Group | Pick | Reuses fill-container? |
|---|---|---|
| How the child does it | **Hop away**: drag or tap frogs off the pad into the water, then "How many are left?" | Needs the reserved `direction: "remove"` (kit change, Opus) |
| How the child does it | **Lantern** (levels 4 and 5): fireflies in a ten-frame jar fly out into the night; break ten to take away 5 from 13 | Same extension, ten-frame variant |
| How the child does it | **Keep N** (level 3): "Leave 5 on the pad. How many hopped away?" The unknown is the part that left | Needs one new goal rule (Opus) |
| What the child gets | **Fireflies fill the evening**: each solved order lights one firefly in the sky, the sky ends the session full of light. Nothing stored, nothing to lose | Skin and a small kit hook, no website change |
| How it feels | **Notes that go down, and a glow chord for what is left** | Reuses `pitch.ts` as is |
| How it feels | **Each thing leaves in its own way**: frogs leap with a ripple ring, fireflies drift up and blink | Skin plus a small exit-animation hook |
| How it feels | **Dusk pond**: deep blue and teal, warm lantern light. A different mood from the sunny garden | Skin only (art) |

Four differences from Addition Garden, so it does not feel like a copy:
1. Things leave instead of arriving (opposite motion, opposite sound).
2. The mood is evening, not sunshine. Different palette and backdrop.
3. Level 3 asks "how many hopped away?" which is a different question, not a reversed one.
4. The reward is the sky filling with light, not a garden you own.

Not recommended now (kept as options, section 9): number-line hops, fact-family house, frog life cycle pond,
sticker pick.

## 4. A round, step by step (levels 1 and 2, "Hop away")

1. A friend arrives at the pond (duckling, turtle, dragonfly or fish). Hazel is the lantern keeper.
2. A big lily pad holds N frogs. The friend says it aloud and shows it in a bubble: "3 frogs are going for a swim!"
   The numeral 3 is shown beside three small frog icons.
3. The child drags 3 frogs into the water. Tap-to-pick then tap-the-water and keys `1` also work (same three
   input paths as the garden).
4. Each frog that leaves plays the next note down the scale and leaves a ripple ring (visual twin for sound).
5. When 3 have left, the pad is calm. The question appears: "How many frogs are still on the pad?" Three big
   choices, planned distractors (off by one, and the wrong operation, which here is the sum).
6. Right answer: the remaining frogs bounce once, a warm chord of that number plays, a firefly lights in the sky.
7. Taking too many: the extra frog hops back onto the pad with a soft wobble. No buzzer, no red mark.
8. Hints (same ladder as the garden, hints only, never the answer): Look (Hazel points at the pad and the order is
   spoken again), Count (number badges 1, 2, 3 light on the frogs that should leave), Slots (ghost ripples in the
   water for the frogs still to send). A wrong "How many left?" tap dims that choice and the remaining frogs light
   up one by one with their notes, so the child can count the answer for themselves.

## 5. Levels (data sketch, not final)

All levels use the existing `arithmetic` generator with `op: "-"`. Item ids stay the arithmetic ids (`q-8m3` is
always 8 - 3), as GAME_RULES rule 17 requires.

| Level | Id | Numbers | Layout | Question |
|---|---|---|---|---|
| 1 | `within-5` | `a` 2 to 5, `b` 1 to 4, result 1 to 4 | Pad, frogs | Hop away, then how many left |
| 2 | `within-10` | `a` 4 to 10, `b` 1 to 7, result 1 to 9 | Pad, frogs | Hop away, then how many left |
| 3 | `keep` | `a` 5 to 10, `b` 2 to 8, result 1 to 8 | Pad, frogs | Keep N on the pad, then how many hopped away |
| 4 | `teen-minus-small` | `a` 11 to 15, `b` 1 to 4, no crossing ten (result 10 to 14) | Lantern ten-frames | Fireflies out, then how many left |
| 5 | `cross-ten` | `a` 11 to 18, `b` 3 to 9, result 3 to 9, crossing ten | Lantern ten-frames | Break ten, then how many left |

Level 5 teaches the strategy "13 - 5 = 13 - 3 - 2": the child removes 3 fireflies so the second frame empties, the
frame folds into the "10" token, and the last 2 come out of the full ten. This mirrors the garden's make-ten flip
and is the same idea run backwards.

Zero: results of 0 are left out for now. "No frogs left" is a real concept, but an empty pad on a first-grade
quiz is confusing without teaching. A later level can add it on purpose.

Game-level settings follow the garden: 3 choices, distractors `off-by-one`, `wrong-operation`, `off-by-two`; adapt up
after 3 first-try right, down after 2 misses; session ends at 10 questions or 180 seconds.

## 6. What changes in the code (and what needs Opus)

| Where | Change | Size | Model |
|---|---|---|---|
| Kit: `fill.ts` reducer | `direction: "remove"`: the container starts full, drops go the other way, overtake hops back, goal is "removed == b" | Medium | **Opus** |
| Kit: `fill.ts` | New goal `keep`: goal met when what is left equals N, naming step asks the removed count | Small to medium | **Opus** |
| Kit: ten-frame variant | Remove from a ten-frame, "break ten" fold (inverse of make-ten) | Medium | **Opus** |
| Kit: `validate.mjs` and schema | Accept `direction: "remove"` and `goal: "keep"`, new rules (for example removed cannot exceed on-pad) | Small | **Opus** |
| Kit: `content.ts` | `buildFill` for `op: "-"` (the generator and distractors already handle subtraction) | Small | Opus with the rest |
| Kit: audio and skin contract | Countdown note sequence (reuses `pitch.ts`), skin hook for how an item leaves | Small | Opus with the rest |
| Kit: release | New minor tag, README note, quiz and addition games must still pass unchanged (additive release) | Small | You make the tag on GitHub |
| Game repo | `game.json`, `skin.ts` (pond, frogs, lantern, fireflies, 4 friends), start from the garden skin | Medium | Sonnet |
| Website | Catalog entry, game page (300 to 600 words of text), category list, sync, smoke test. No new store | Small | Sonnet |
| Art | Dusk pond backdrop, lily pad, frog (2 poses), 4 friends, lantern and fireflies, ripple, sky | Medium | Sonnet |

Recommendation: do the kit work as one Opus pass that starts with a short design doc
(`planning/fill-container-remove-design.md`), like we did for the garden, because the reducer is the heart of every
fill game and live Addition Garden depends on it staying unchanged.

Not touched: session record, message contract, the website progress store, Hazel, drag layer.

## 7. Reward and feel details

- **Fireflies fill the evening.** One firefly per solved order, each with a different gentle blink rhythm. They stay
  in the sky for the rest of the session. On the end screen they drift together and light the lantern, then the
  screen says something kind like "The pond is glowing!" Nothing is saved to the website and nothing is lost if the
  child stops. Stars still go to the website as today.
- **Sound.** Every frog that leaves plays the note of the count still on the pad (so 8 frogs, 3 leave: notes for 7,
  6, 5). The right answer plays the chord of the remaining number. Sound has a visual twin (ripples, glow). Voice
  finishes before tones start (playbook lesson).
- **Motion.** Transform and opacity only. A reduced-motion version of every animation: frogs fade out and the
  ripple becomes a soft glow.
- **Reading load.** The friend's line is spoken and shown with icons. Words of five letters or fewer where possible.
- **Orientation.** Landscape, like the garden. The playbook lists a real portrait layout as future work for all fill
  games, not part of this game.

## 8. Safety and rules check

No login, no ads, no prices, no external links, no data collected from the child, no storage in the game. No timers
shown, no streaks, nothing wilts, no failure screen. Hit targets 64 px or more. Tap, drag and keyboard all work.
Before Play stays under 100 KB.

## 9. Ideas we are not doing now (and why)

- **Number-line hops back** (Hazel hops left on a number line): a different mechanic (`number-line` is reserved in the
  framework spec), big Opus work, and counting back by ones is a weaker strategy. Better as a later "Subtraction
  number line" game, as the MVP list already hints for addition.
- **Fact-family house** (3 numbers, 2 add and 2 subtract facts): lovely for Grade 2, needs its own mechanic.
- **Frog life cycle pond** (egg, tadpole, frog, grown by sessions): cheapest, because the garden store and growth
  rule already exist. But it is the garden in a frog costume, and it would repeat the exact reward feel. If you like it,
  it is a swap of reward only.
- **Sticker pick** (choose 1 of 3 at the end): allowed by GAME_RULES and a good different feel, but it needs a store
  on the website. Better built once as a website-wide sticker book that every game can use, not per game.

## 10. Owner decisions (defaults if you say nothing)

1. Theme: frogs on a lily pad at dusk, lantern with fireflies for levels 4 and 5. [Default: yes.]
2. Cast of friends: duckling, turtle, dragonfly, fish, anonymous like the garden's cast. Frogs are the items, not
   the cast. [Default: these four.]
3. Level 3 "Keep N" (how many hopped away?). [Default: in, because it is what stops the game being a mirror. If the
   Opus pass says it widens the kit too much, we cut it and release without it.]
4. Reward: fireflies in the session only. [Default: yes. Swap to the frog life cycle pond if you want something to
   come back to.]
5. Zero left: not in this version. [Default: no.]
6. Order wording: "3 frogs are going for a swim!" for pad levels, "3 fireflies are flying home!" for the lantern.
   [Default: these lines.]

## 11. Next steps

1. You critique this doc and answer or ignore section 10.
2. Opus pass: `planning/fill-container-remove-design.md` (reducer, schema, validator, ten-frame remove, skin hook).
   I will tell you when to switch models.
3. Static art preview in `brand/subtraction-pond/` (one pad scene, one lantern scene, the cast, the glowing sky).
   You approve it.
4. Build bottom-up with tests after each step: kit change and release note, game repo, sync into the website,
   website tests, browser check on the throttled profile.
5. Ship order as in the playbook. Kit tag by you, PR and deploy only when you say so.
