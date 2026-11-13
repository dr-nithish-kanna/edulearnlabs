# pair-match: kit design for Quilt Picnic (kit v0.4.0 to v0.5.0)

Status: DESIGN and BUILT, 2026-11-13. Opus design pass for the mechanic asked for in `planning/memory-match-design.md` section 8.
The owner was asleep and asked for an unattended build, so every open point is decided below with a recommendation,
a reason and the default used. Built on the kit branch `ccr-4d0bb17c-4dbh4d` (continues from kit v0.4.0 at
`fc6a32b`). Section 12 records where the build differs from this doc.

Files read for this design: main repo `CLAUDE.md`, `planning/memory-match-design.md` (the spec, sections 1 to 8 and
the defaults of section 10), `planning/slot-build-design.md` (the model), `planning/framework-spec.md`,
`planning/game-playbook.md`, `templates/game-repo/GAME_RULES.md`; kit `CLAUDE.md`, `README.md`, `src/types.ts`,
`src/session.ts`, `src/content.ts`, `src/slot.ts`, `src/fill.ts`, `src/pitch.ts`, `src/audio.ts`, `src/strings.ts`,
`src/game.ts`, `src/host.ts`, `src/juice.ts`, `src/ui/*`, `src/styles/*`, `src/mechanics/*`, `build/validate.mjs`,
`tests/slot.test.ts`, `tests/word-e2e.cjs`, `dev/word*`.

## 0. The big idea in five lines

1. **A board is one question.** The session engine already counts questions, adapts and ends at 5 boards or
   180 seconds; a pair-match "question" is one quilt board, resolved with `Session.resolve()` like slot-build.
2. **Rules are a pure reducer** (`src/pair.ts`): taps and keys send the same `lift` action, misses close with a
   `close` action, the hint ladder climbs on misses in a row. Every rule is tested without a browser.
3. **Boards are planned, not random**: an anchor picture chosen by the session, plus pictures picked by the level's
   rules (all different, two from one group, colour variants), laid out with a seeded shuffle.
4. **Misses are counted, never shown.** They decide "clean board" (counts for stars, mastery, moving up), and the
   ladder, and they are sent to the website as a fact. The child sees only flaps that close softly.
5. **The quilt is the website's.** The game reports one `{ id, kind: "patch", patch, at }` per finished board and
   gets `HostInit.quilt = { patches }` to draw the mini quilt. The kit stores nothing.

## 1. Decisions (owner away; recommendation and default for each)

1. **One board is one question.** `session.maxQuestions` 5 and `maxSeconds` 180 give the spec's "5 boards or about
   180 seconds". *Why:* the adapt, timing, practice and record code already works per question; no new loop.
2. **Pictures live once, in a game-level `pictures` list.** Levels say how to build a board (`pair` block) and may
   narrow the pool (`pair.pool`). *Why not items per level like slot-build:* 16 pictures times 5 levels is 80 copies
   of the same entries; one list cannot drift. The session expands each pair-match level's items from the list at
   start (a small, additive change in `Session`), so `pickItem`, practice and `itemFitsLevel` work unchanged.
3. **The session picks an anchor picture per board** (the usual `pickItem`, fresh pictures first). The anchor is
   always on the board; the planner adds the rest. The anchor's id is the question's item id, so `missed` lists
   anchors of boards that were not clean. *Honest note:* for memory, "missed" is a weak signal (it names a board,
   not a weakness). It stays because the record shape is shared; practice mixes an anchor back in now and then,
   which is harmless.
4. **Board sizes are fixed by the pair count:** 2 pairs 2x2, 3 pairs 2x3, 4 pairs 2x4, 6 pairs 3x4, 8 pairs 4x4. No
   other counts (5 pairs would need a 2x5 row too narrow for 64 px cards on a phone). Validator enforces it.
5. **Planned distractor pictures per level** (the memory version of planned wrong answers). Each picture may carry
   `pair.group` (category, for example "animal") and `pair.family` (the same thing in another colour, for example
   red ball and blue ball are family "ball"). The level says how many pairs on the board are look-alikes:
   - `near`: pairs that share a group with another pair on the board (two animals). 0 or at least 2.
   - `variants`: pairs that share a family with another pair on the board (red and blue ball). 0 or at least 2.
   - every other pair has a group and family of its own ("very different").
   Defaults per level (the spec's table):

   | Level | Board | `pair` block | Content rule |
   |---|---|---|---|
   | 1 | 2x2 | `{ "pairs": 2 }` | very different pictures |
   | 2 | 2x3 | `{ "pairs": 3 }` | very different pictures |
   | 3 | 2x4 | `{ "pairs": 4, "near": 2 }` | two share a category |
   | 4 | 3x4 | `{ "pairs": 6, "near": 4 }` | similar pairs |
   | 5 | 4x4 | `{ "pairs": 8, "near": 2, "variants": 2 }` | colour variants as distractors |

   A picture with no group or family is its own group and family.
6. **Planner algorithm (pure, `planBoard`).** Anchor first. Then a variant cluster (prefer the anchor's family),
   then a near cluster (prefer the anchor's group, never two of one family), then fill with pictures whose group and
   family are new on the board. If the pool cannot meet a rule, the planner relaxes it (takes any unused picture)
   and marks the board `relaxed`; the kit tests prove the playground content never relaxes, and the validator
   checks the counts a level needs (decision 20). Cards are shuffled with the seeded random; a layout where more
   than half the pairs sit side by side (an easy giveaway) is reshuffled, up to 6 times.
7. **Seed: the session id plus the board index.** *Why not fixed per anchor like slot-build trays:* a memory game
   that repeats a layout rewards remembering yesterday's board, not finding pairs. Tests pass a fixed seed.
8. **Lift rule.** Tap a closed flap: it lifts and plays its pair's note. A second flap: if it shows the same picture,
   both stay up (a match). If not, both stay up for about 1 second, then close softly. A tap on a third flap while a
   miss is still showing closes the miss at once and lifts the new flap (fast tappers are never blocked). A tap on an
   open or found flap does nothing. Never auto-match.
9. **Misses are counted, never shown.** No counter, no red, no buzzer, no "wrong" sound; the voice stays silent on a
   miss. Hazel tilts her head (the `nudge` pose) as the visual cue.
10. **Hint ladder (hints only, never the answer).**

    | Rung | Name | What happens | Trigger | Cost |
    |---|---|---|---|---|
    | 0 | Nudge | Hazel hops and says "Find two that match" again | 8 s idle, at most 2 in a row | free |
    | 1 | Peek | every closed flap lifts for 1.5 s, then closes; bubble "Take a peek!" | 3rd miss in a row, once per board | hint |
    | 2 | Sparkle | one closed flap of an unfound pair twinkles until it is lifted; bubble "Try this one!" | every 3 more misses in a row (6, 9, ...) | hint |

    A match resets the miss streak but not the rungs already used. Tapping Hazel gives the next rung at once (Peek if
    unused, else Sparkle) and resets the streak; while a sparkle is still showing, a tap repeats it for free.
    *Which flap sparkles:* the lowest-numbered closed flap of an unfound pair whose twin the child has already seen,
    else the lowest-numbered closed unfound flap. So the sparkle invites a memory success, it does not solve it: the
    child still has to remember (or find) the twin.
11. **Clean board (first try).** `firstTry` is true when no Peek or Sparkle was shown and misses are at most the
    board's allowance, `pair.allow`, default `max(1, floor(pairs * 3 / 4))`: 1, 2, 3, 4, 6 for 2, 3, 4, 6, 8 pairs.
    *Why this number:* a simulation of 20 000 boards per size: a child who remembers every flap stays within it
    every time (99 to 100 percent); one who remembers 60 percent of flaps does on 76 to 82 percent of small boards
    and about half of the 3x4 and 4x4 boards; a pure guesser almost never on 2x4 and up. So "clean" means memory,
    not luck (except on 2x2, where luck is unavoidable and harmless).
12. **Adapt rule.** Up after `upAfterCorrect` clean boards in a row, down after `downAfterWrong` boards that needed 2
    or more Sparkles ("struggled"). Any other board is "steady": it ends an up streak, counts as not first try, but
    does not count toward moving down. Defaults: `upAfterCorrect` 1 and `downAfterWrong` 1. *Why 1:* a board is 20
    to 60 seconds of play, worth more evidence than one quiz answer, and a session has only 5 boards. The validator
    allows `upAfterCorrect` 1 for pair-match only. Shared change: `ResolveOutcome.steady` (additive, decision 21).
13. **Board complete beat.** (1) the last match plays its chord at once; (2) wait for any voice line still playing
    (at most 4.5 s); (3) the pairs light one after another in note order, each with its note (a rising tune);
    (4) a soft chord, the quilt glows, a patch glides from the board to the mini quilt, confetti, Hazel happy.
14. **Reward: the quilt.** `"reward": { "type": "quilt", "patches": ["gingham-red", "dots-blue", ...] }` (at least 2
    patch slugs). One patch per finished board, clean or not (effort is rewarded, like the garden). The patch is the
    next one in the fixed cycle after the last patch on the child's quilt (`HostInit.quilt.patches`, last entry), so
    the pattern never repeats a patch twice in a row and never depends on a random number. Fact sent:
    `{ id: "<session id>-<board index>", kind: "patch", patch, at }`.
15. **The mini quilt.** A 3 x 3 board at the left of the scene shows the newest 9 patches from HostInit (the quilt
    at the start of the session) and grows as boards finish. The end screen shows up to 16 newest patches with
    this session's marked new. The parent "My quilt" page is website work, later.
16. **Matching pairs share a note.** Pair k on the board (0 based, in plan order) plays `pitchFor(k + 1)` from
    `src/pitch.ts` (C4, D4, E4, G4, A4, C5, D5, E5). Both flaps of a pair play the same note, so a child can match by
    ear; a match plays `chordFor(k + 1)` rolled. Notes are per board, so they never teach "fox is always C".
17. **Voice.** Only "Find two that match" (first board, and on an idle nudge) and the hint lines. Pictures are not
    named (spec default 10.2). Voice first: the completion tune waits for speech to finish. Lift notes do not wait:
    feedback within 0.3 s wins over a talking Hazel. `skin.say(text)` may return a promise to play a recording.
18. **Visual twin for every sound.** Lift note: a soft ring glows on the card. Match chord: both cards hop and
    glow. Completion tune: each pair lights as its note plays. Peek and Sparkle have no sound beyond the voice line.
    A miss has no sound at all; the visual is the flaps closing and Hazel's head tilt.
19. **Layout (960 x 600 scene, one transform, bottom anchored, same as slot-build).**
    - Board area x 240 to 760, y 124 to 590 (520 x 466). Cell size: the largest that fits, at most 180, gap 14.
    - Mini quilt x 24 to 216, y 124 to 330. Hazel at x 790, y 380 (150 wide), her bubble opens upward inside the right
      column, so it never covers a card.
    - At 667 x 375 (landscape phone, scale 0.625), the back button covers the scene down to about y 112, so the board
      starts at y 124. Resulting cards: 2x2 180 scene px (112 px real), 2x3 164 (102 px), 2x4 119 (74 px),
      3x4 119 (74 px), 4x4 106 (66 px). So small boards (2x2, 2x3) are at least 96 px and every board at least 64 px.
    - Upright phones get the existing "Turn your phone sideways" prompt (class `ell-pair-rotate`).
20. **Validator rules** (`build/validate.mjs`, build time only):
    - game level: `pictures` is a list of 4 or more items; each has a unique slug id, `prompt.text`, `prompt.image`
      (a slug), `answer` equal to `prompt.text`; `pair.group` and `pair.family` are slugs when given; `pair.twin`
      (optional, the second card's image for later "mother and baby" levels) is a slug.
    - every image id is unique (two pictures that look the same would be two different pairs);
    - levels: no `items` or `generator`, a `pair` block with `pairs` in 2, 3, 4, 6, 8; `near` and `variants` 0 or 2 to
      `pairs`; `near + variants <= pairs`; `allow` 0 to 20; `pool` lists known picture ids;
    - capacity: the level's pool has at least `pairs + 1` pictures (so two boards in a row can differ), at least
      `pairs - near - variants + 1` different groups, a group with two or more families when `near` is set, and
      families with two or more members holding at least `variants` pictures when `variants` is set;
    - `reward` must be `{ "type": "quilt", "patches": [2 or more slugs] }`, `upAfterCorrect` may be 1;
    - `pictures`, `pair` and the quilt reward are refused for every other mechanic.
21. **Shared code touched (all additive).** `types.ts` (new optional types and fields), `session.ts` (expand
    pair-match levels from `pictures`, no choices for pair-match, `ResolveOutcome.steady` and `misses`, patch
    rewards), `host.ts` (`HostInit.quilt`), `validate.mjs`. Proof: every existing test and the golden files pass
    unchanged.
22. **Lean registry, no drag code.** New runner `pairMatch` in `src/mechanics/pair-match.ts`, styles in
    `@edulearnlabs/kit/pair.css`. It imports neither `src/drag.ts` nor the slot or fill screens (only the shared
    helpers `bump` and `stripUndefined`). The playground build is checked for the drag module's code.
23. **Keyboard.** The board is a grid of buttons with a roving tab stop: Tab enters the board, arrow keys move (they
    stop at the edges), Enter or Space lifts, Tab moves on to Hazel (help). Focus is visible (teal ring). Found cards
    stay focusable so the arrows keep the grid shape; Enter on them does nothing.
24. **Screen reader.** Each card is "Card 3 of 8, closed" or "Card 3: fox" when up; a polite live region says
    "A match!" or "Not a match." and nothing else. Picture names come from `prompt.text`.
25. **Reduced motion.** No lift transform, no bounce, no hop, no glide, no confetti. A flap fades out (opacity) and
    back in, a match glows, the sparkle is a steady glow, the patch fades into the quilt. Everything is transform and
    opacity (no 3D, no layout properties).

## 2. Data shape

### 2.1 game.json

```json
{
  "mechanic": "pair-match",
  "session": { "maxQuestions": 5, "maxSeconds": 180 },
  "adapt": { "upAfterCorrect": 1, "downAfterWrong": 1 },
  "reward": { "type": "quilt", "patches": ["gingham-red", "dots-blue", "stripe-green", "flower-yellow"] },
  "strings": { "find": "Find two that match", "peek": "Take a peek!", "sparkle": "Try this one!",
               "match": "A match!", "quilt": "Your quilt is growing!", "quiltTitle": "My quilt" },
  "pictures": [
    { "id": "p-fox", "prompt": { "text": "fox", "image": "fox" }, "answer": "fox", "pair": { "group": "animal" } },
    { "id": "p-ball-red", "prompt": { "text": "red ball", "image": "ball-red" }, "answer": "red ball",
      "pair": { "group": "toy", "family": "ball" } }
  ],
  "levels": [
    { "id": "two", "difficulty": 1, "pair": { "pairs": 2 } },
    { "id": "three", "difficulty": 2, "pair": { "pairs": 3 } },
    { "id": "four", "difficulty": 3, "pair": { "pairs": 4, "near": 2 } },
    { "id": "six", "difficulty": 4, "pair": { "pairs": 6, "near": 4 } },
    { "id": "eight", "difficulty": 5, "pair": { "pairs": 8, "near": 2, "variants": 2 } }
  ]
}
```

### 2.2 types.ts (additive)

```ts
export type Mechanic = ... | 'pair-match';
export interface PairTags { group?: string; family?: string; twin?: string }
Item.pair?: PairTags;
export interface PairLevel { pairs: 2 | 3 | 4 | 6 | 8; near?: number; variants?: number; allow?: number; pool?: string[] }
Level.pair?: PairLevel;
export interface QuiltRewardDef { type: 'quilt'; patches: string[] }
export interface PairGameDef extends Omit<GameDef, 'reward'> { reward?: QuiltRewardDef; pictures: Item[] }
GameDef.pictures?: Item[];
export interface PatchReward { id: string; kind: 'patch'; patch: string; at: string; species?: never }
export interface QuiltView { patches: string[] }          // HostInit.quilt
SessionRecord.misses?: number;                           // pair-match only
SessionRecord.rewards?: (Reward | WordReward | PatchReward)[];
GameStrings: find?, peek?, sparkle?, match?, quilt?, quiltTitle?
```

### 2.3 Planned board (what the screen receives)

```ts
interface PairBoard {
  rows: number; cols: number;
  pairs: { item: string; image: string; twin: string; name: string }[];   // plan order; note = pitchFor(k + 1)
  cards: { id: number; pair: number; image: string }[];                    // reading order, ids 0..n-1
  allow: number;                                                           // misses still "clean"
  relaxed: boolean;                                                        // a content rule could not be met
}
```

### 2.4 Message contract (protocol stays 1)

- `HostInit.quilt?: { patches: string[] }`: patch ids on the child's quilt for this game, oldest first. Sent only to
  games whose catalog entry has a quilt reward. Website recommendation: send at most the newest 64.
- `GameCompleted.session.rewards`: one `{ id, kind: "patch", patch, at }` per finished board. Repeats of a patch id
  are normal (a quilt has many squares of one pattern): the website keeps every entry, deduped by `id`.
- `GameCompleted.session.misses`: total misses this session (a fact for the parent page; never shown to the child).
  `hints` counts Peeks and Sparkles. `mistakes` stays `{}` (a memory miss has no kind).
- Website store recommendation: `quilts[profile][game] = { "v": 1, "patches": [{ "patch", "at", "session" }] }`,
  at most 200 per child per game, same newer-`v` guard as `walls`.

## 3. Reducer (`src/pair.ts`)

State: `board`, `found` (per pair), `open` (0 to 2 card ids), `seen` (per card), `phase` play or complete, `misses`,
`streak`, `peeks`, `sparkles`, `sparkle` (card id or -1), `idleMs`, `idleHints`.

| Action | Rule | Effects |
|---|---|---|
| `lift { card }` | ignored if complete, found, or open. With a miss showing: close it first. 1st flap: open. 2nd: match or miss | `closed`?, `lifted`, then `match` (+ `complete`) or `miss` (+ `peek` or `sparkle` on every 3rd miss in a row) |
| `close` | closes a showing miss | `closed` |
| `tick { ms }` | 8 s idle gives a nudge, at most 2 in a row | `nudge` |
| `help` | next rung (Peek once, then Sparkle), streak to 0 | `peek` or `sparkle` |

`outcome = { firstTry, steady, hints, misses }` with `firstTry = hints === 0 && misses <= allow` and
`steady = !firstTry && sparkles < 2`.

## 4. Screen (`src/mechanics/pair-match.ts`, `src/styles/pair.css`)

Hooks for tests and tools: `.ell-pair-view[data-phase]` (`play`, `lighting`, `reward`), `[data-hint]`,
`[data-board]` (`2x2` etc.), `.ell-pair-card[data-pair][data-card]` (never shown or spoken), `.is-open`, `.is-found`,
`.is-sparkle`, `.is-peek`, `.is-lit`, `.ell-pair-patch`. A miss closes after 1000 ms; a peek lasts 1500 ms and blocks
taps while it shows (the child is looking).

## 5. Skin contract (`PairSkin`, exported from the kit)

| Field | What it is |
|---|---|
| `symbols` | `<symbol>` markup injected once |
| `backdrop` | SVG markup on 960 x 600 (may extend past the edges for wide screens) |
| `picture(image)` | full `<svg>` markup for an image id, drawn in a square card face; `''` for unknown ids |
| `flap(index)` | SVG markup for the closed flap of card `index` (a fabric patch); one string for all is fine |
| `patch(id)` | SVG markup for a quilt patch id (mini quilt and end screen), square |
| `quilt` | board art behind the mini quilt, SVG on 192 x 206 |
| `hazel` | Hazel's spot `{ x, y }` in scene px (default 790, 380) |
| `say(text)` | voice hook: return a promise to play the game's recording of a line, or nothing for the kit voice |

Every field is optional: without a skin the kit draws coloured fabric flaps, a neutral picture frame and plain
patch squares, so the playground and the tests always work. The kit ships no per-game art.

## 6. Size

Estimate: reducer and planner about 1.3 KB brotli, screen about 3 KB, CSS about 1 KB (separate file). Quiz, fill
and word pages unchanged within 0.1 KB. Measured numbers: section 12 and the kit README.

## 7. Tests

Unit (`tests/pair.test.ts`): lift, match, miss, close, third-tap close, ignored taps, found pairs, complete, miss
streak, Peek once, Sparkle every 3, sparkle choice (seen twin first), Hazel help, idle nudge, outcome (clean, steady,
struggled, allowance), planner (grid sizes, card counts, every pair twice, near, variants, very different, anchor
always on, determinism, relaxed flag, side-by-side rule, twin images), session (steady adapt, patch rewards and
cycle, misses in the record, pictures expanded into levels), validator rules, the playground game.
Browser (`tests/pair-e2e.cjs`): hit targets per board size, mini quilt from HostInit, tap and keyboard play, miss
close, third-tap close, no counter or red mark, Peek after 3 misses, Sparkle after 6, completion beat order with a
fake voice (tune after voice, one note per pair, the same note for both flaps of a pair), session end with patch
rewards and the record, reduced motion, 667 x 375 phone on the 4x4 board, rotate prompt, no drag code in the build.

## 8. Implementation steps (in order)

1. Types, spec mirror. 2. `src/pair.ts` reducer and planner with tests first. 3. Session edits (golden green).
4. Validator. 5. Screen and CSS. 6. Dev fixture `dev/pair.html`, `pair.ts`, `pair-game.json`, `pair-skin.ts`.
7. Browser checks. 8. Size, README, version 0.5.0, commit and push.

## 9. Risks

1. Real touch on tablets still untested (same as every kit mechanic so far).
2. 2x2 boards are partly luck. Harmless (they are the warm-up level), but stars on level 1 say little.
3. The website must add `quilt` to HostInit, accept `kind: "patch"` rewards and keep `misses`. Until then a v0.5.0
   game works but its patches are dropped by `validRewards`.
4. Level 5 colour variants need art where red and blue differ by more than colour alone (colour-blind children):
   give each variant a second cue (a stripe, a dot pattern). Art preview task, not kit work.

## 10. What a game must implement

```ts
import '@edulearnlabs/kit/styles.css';
import '@edulearnlabs/kit/pair.css';
import { pairMatch, startGame, type GameDef } from '@edulearnlabs/kit';
import def from '../game.json';
import { skin } from './skin';          // a PairSkin: picture per image id, flap, patches, backdrop, optional voice
void startGame(def as unknown as GameDef, { mechanics: { 'pair-match': pairMatch }, skin });
```

## 11. Owner questions left open (defaults used)

1. Allowance formula (decision 11). Default: `floor(pairs * 3 / 4)`, at least 1. A game can set `pair.allow`.
2. `upAfterCorrect` 1 (decision 12). Default: 1 for Quilt Picnic. Raise to 2 if children climb too fast.
3. Board layout changes every session (decision 7). Default: yes.

## 12. Implementation notes (kit v0.5.0, 2026-11-13)

Built on the kit branch `ccr-4d0bb17c-4dbh4d` in two commits (logic, then screen, playground, browser checks and
docs). Nothing from the design was cut. The `v0.5.0` tag is not on GitHub (tag pushes are blocked); the owner creates it.

**Where the build differs from sections 1 to 11, and why**
1. **4x4 cards are 106 scene px, not 109** (the board area is 466 px tall: 4 cards and 3 gaps of 14). On a 667 x 375
   phone that is 66 px, measured in the browser check. Still at least 64.
2. **The planner never leaves a need of exactly 1 that no picture can meet.** The first version tried to make 4 near
   pairs on a 3x4 board from an anchor in a group of 3 (ladybug, bee, snail) and got stuck at 3. It now looks one step
   ahead and starts a second near group instead (for example 2 bugs and 2 animals). Found by the "every anchor, every
   level, 12 seeds, never relaxed" test.
3. **The side-by-side rule starts at 3 pairs.** On a 2x2 board the two pairs are either both side by side or both
   diagonal; forcing "diagonal" every time would itself be a giveaway, so 2x2 takes any layout.
4. **`hashSeed` moved from `slot.ts` to `random.ts`** (still exported from `slot.ts`), so pair-match does not import the
   slot module.
5. **Skill id:** the validator wants a skill that starts with the subject, so the playground uses
   `logic-memory.memory.matching-pairs`. `planning/memory-match-design.md` says `logic.memory.matching-pairs`; the game
   repo must use the `logic-memory.` form (and add it to the skills list).
6. **Clicks, not pointer events.** With no drag there is no reason for Pointer Events: one `click` listener per card
   covers tap, mouse, Enter and Space, and `touch-action: manipulation` (base CSS) removes the tap delay.

**Checks.** Unit: 211 tests (172 before plus 39 in `tests/pair.test.ts`), typecheck clean, golden files unchanged.
Browser (`tests/pair-e2e.cjs`): 68 checks, all ok: no drag or other mechanic code in the pair bundle; a throttled full
session that climbs 2x2, 2x3, 2x4, 3x4, 4x4 with one miss, keyboard play (Tab, arrows, Enter and Space), card sizes per
board, the mini quilt from HostInit, notes (two flaps of a pair share a note, then a 3 note chord), the record (5 clean,
1 miss, 0 hints, levels 1 to 5, 5 patches continuing the cycle after the last HostInit patch), the end-screen quilt;
third-tap close, Peek after 3 misses (all 8 flaps, taps wait), Sparkle after 6 (exactly one flap, never a match), the
completion tune after a 2.5 s fake voice line, in note order, Hazel help, Back mid-session (record not completed, then
GameExit); reduced motion (flaps fade, no transform animation); 667 x 375 and 960 x 600 on the 4x4 board (cards, back
button, quilt and Hazel's bubble never overlap a card); the rotate prompt on an upright phone. On the new code the
word checks pass 66 of 66 and the fill and pond checks 327 of 327.

**Size.** Pair page 15.75 KB JS with the playground skin, 14.89 KB with no skin, CSS 3.23 KB, Before Play 54.0 KB.
About 5.5 KB more than a quiz-only game. Every other page grew about 0.15 KB (shared session changes).

**Still open:** website support (HostInit `quilt`, `kind: "patch"` rewards and a `quilts` store in `progress.ts`, keep
`misses`), the art preview and the game repo, real touch devices, the owner's `v0.5.0` tag.
