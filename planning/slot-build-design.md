# slot-build: kit design for Letter Workshop (kit v0.3.0 to v0.4.0)

Status: DESIGN and BUILT, 2026-11-13. Opus design pass, then implementation on the kit branch `ccr-d63a6d4f-g77ft0`.
Follows the style of `planning/fill-container-remove-design.md`. The owner accepted every default of
`planning/word-building-design.md` and asked for an unattended build, so every open point is decided in section 1
with a recommendation and a reason. Section 11 records where the build differs from this doc.

Files read for this design: main repo `CLAUDE.md`, `planning/game-playbook.md`, `planning/framework-spec.md`,
`planning/style-guide.md`, `planning/fill-container-design.md`, `planning/fill-container-remove-design.md`,
`planning/word-building-design.md`, `planning/word-building-decisions-log.md`, `src/scripts/progress.ts`; kit
`CLAUDE.md`, `README.md`, `src/types.ts`, `src/session.ts`, `src/content.ts`, `src/fill.ts`, `src/drag.ts`,
`src/pitch.ts`, `src/audio.ts`, `src/game.ts`, `src/index.ts`, `src/mechanics/*.ts`, `build/validate.mjs`,
`tests/fill-golden.test.ts`, `tests/fill-e2e.cjs`, `dev/*`; Pond Hop `src/main.ts`, `src/skin.ts`.

## 0. The big idea in five lines

1. **A tile is judged against the slot it lands in.** A right letter clicks in with its own note and stays (it is
   never taken out again). A wrong letter wobbles and hops back to the tray. No red, no buzzer.
2. **Trial and error is allowed but never rewarded.** Any wrong tile makes the word "not first try" (so it does not
   count for stars, mastery or moving up), and each wrong tile climbs the hint ladder, so guessing quickly turns into
   being taught. The child always finishes the word and always gets the card.
3. **Rules are a pure reducer** (`src/slot.ts`), like `fill.ts`: drag, tap-tap and letter keys all send the same
   actions, so they cannot drift apart, and every rule is tested without a browser.
4. **The tray is planned, not random**: needed letters plus distractors chosen by rules (wrong-vowel trap,
   no sound-alikes, no look-alikes unless a level asks), shuffled with the kit's seeded random from the word id, so
   the same word at the same level always shows the same tray.
5. **The word wall is the website's**: the game reports `{ id, kind: "word", wordId, at }` per solved word in
   `GameCompleted.session.rewards`, and gets `HostInit.wall = { words }` to draw the shelf. The kit stores nothing.

## 1. Owner decisions (owner away; recommendation and reason for each)

1. **Placement rule: per-slot check, immediate.** A tile dropped on an empty slot is accepted only if it is the
   letter that slot wants; otherwise it wobbles back.
   *Why not free placement with a check when full:* a 5 year old needs the feedback at the letter, not after five
   letters (they cannot tell which one was wrong), the design doc promises "each tile clicks in with its own note",
   and a full-word check needs a "take it out again" gesture that doubles the input surface.
   *The trial-and-error hole:* a child can brute force a 3 letter word in at most about 9 drops. Closed by decision 3
   (any wrong tile costs first try) and decision 6 (each wrong tile climbs the ladder). Guessing still ends in a
   finished word (no failure screen), but it never earns stars or a level up, and the parent sees `missed`.
2. **Letter keys type into the "cursor": the first empty slot, left to right.** A key whose letter is on a free tray
   tile is placed there and judged like a drop. A key whose letter is not in the tray wobbles the tray and costs
   nothing (a stray key is not a spelling mistake).
   *Why not "the first empty slot that wants it" (the brief's wording):* that makes letter order free for keyboard
   players only. With the cursor, typing is spelling left to right, the same rule as drag, and the H2 "Letter" hint
   (the cursor slot glows) means one thing for every input.
3. **Session record.** `firstTry` is true only with no wrong tile and no H2 or H3 hint. `hints` counts H2 and H3
   steps reached (same as fill). `missed` gets the word id when not first try. `mistakes` gets each letter mistake
   kind **at most once per word** (a guessing child would otherwise flood the parent tip with one word's noise).
4. **Mistake kinds (new, letter games only).** `letter-order` (a letter of this word, but another slot wants it),
   `wrong-vowel` (a vowel on a vowel slot), `look-alike` (b for d, p for q, m for w, n for u), `wrong-letter`
   (anything else). Typed as `LetterMistake`; `SessionRecord.mistakes` widens to `DistractorKind | LetterMistake`.
   `DistractorKind` itself is unchanged, so `choices.distractors` and `buildChoices` are untouched. The website keeps
   unknown kinds as they are (`progress.ts` stores the object) and shows no tip for them until it adds one.
5. **Hint ladder (hints only, never the answer).**

   | Level | Name | What happens | Trigger | Cost |
   |---|---|---|---|---|
   | H1 | Look | Hazel points at the picture, the picture pulses, the word is spoken again; bubble `look` ("Listen!") | 7 s idle (at most 2 replays, then quiet) or the 1st wrong tile | free |
   | H2 | Letter | The cursor slot (first empty) glows; bubble `letter` ("Start here!") | 2nd wrong tile or a Hazel tap | first try |
   | H3 | Tiles | The tiles still needed glow softly; bubble `tiles` ("These letters help!") | 3rd wrong tile or a 2nd Hazel tap | first try |

   *Why none is the answer:* H2 only says where to put the next letter, H3 only which letters are in the word (the
   child still has to order them). The word is never shown as text during play.
   *Tapping the picture* replays the word at any time and is not a hint (hearing the word is the task prompt, like
   re-reading an order). It resets the idle clock.
6. **Ladder climbs with wrong tiles** (`min(3, wrongs)`), exactly as overfill does in fill-container, and never goes
   down within a word. A Hazel tap jumps to at least H2 (same as fill: asking is fine, but it is help).
7. **Pre-filled slots ("given").** Drawn as tiles already in place in a calmer color (`is-given`), never draggable,
   skipped by the cursor, included in the completion beat (they light and play their note too). The tray has no
   tile for them. Positions come from the item (`slot.given: [0, 2]`) or from the level (`given: 1` or `[1, 2]`),
   picked with the seeded random so they repeat. At least one slot is always left empty.
8. **Duplicate letters.** Tiles are individual (puppy has three p tiles), and any tile with the right letter fits any
   slot that wants that letter. Distractors are never letters of the word, so an extra p can never sit in the tray.
9. **Tap-tile then tap-slot.** Tap a tile: it lifts and glows (picked). Tap a slot: the picked tile goes there and is
   judged. Tap the same tile again or press Escape: it settles back. Tap another tile: the pick moves. A tap on a slot
   with nothing picked does nothing. Keyboard: Enter or Space on a focused tile picks it, Enter on a focused slot
   places it; Tab moves between them.
10. **Drag.** Pointer Events through `src/drag.ts` (one pointer, capture, tap fallback). Released over the slot row
    (24 px margin): the empty slot nearest the tile is the target. Released over a filled slot or anywhere else:
    springs back, no cost. No magnetic snap (it would pull every tile to one slot, which reads as a hint), so
    `drag.ts` gains one additive option: `snap()` may return `false` to turn snapping off.
11. **Tray planning (pure, `planSlots`).** Needed letters (word minus given) plus `distractors` extra tiles:
    - never a letter of the word, never two of the same;
    - **wrong-vowel trap** when the level says `vowelTrap: true`: the first distractor is a vowel not in the word,
      from a confusion table (a: e, u, o; e: i, a; i: e, a; o: u, a; u: o, a);
    - **no sound-alikes**, ever: c and k, c and s, s and z, g and j, q and k ("kat" sounds right, so a k tile for
      "cat" would be unfair);
    - **no look-alikes** (b d, p q, m w, n u) unless the level says `lookAlikes: true`, which then makes the first
      free distractor a look-alike of a word letter (a planned reversal trap, for a later level);
    - other distractors come from a consonant pool in a seeded order; `x`, `q` and `y` are left out of the pool;
    - item `slot.tray` lists exact distractor letters and wins over all of the above;
    - the tray is shuffled with `seeded(hash(itemId + levelId))` and is **never the needed letters in word order**
      (that would let a child copy the row); if a shuffle does, it is rotated by one.
    A row of at most 8 tiles keeps every tile at least 64 px on a landscape phone (decision 15).
12. **Completion beat.** The last right tile plays its note at once (instant feedback). Then, in order:
    (1) wait for any voice line still playing (at most 4.5 s), (2) the letters light left to right, about 280 ms
    apart, each with its letter note, (3) the word is spoken through the game's hook (`skin.say`) or the kit voice,
    (4) the reward: a soft chord, the friend's happy pose, the picture card flies to the word wall, confetti.
    *Letter notes:* `letterPitch(ch)` in `src/pitch.ts` maps a to z onto the 15 pentatonic notes (3 octaves from C4),
    so every word is a tune that never sounds wrong and the same word always plays the same tune.
13. **Reward: the word wall.** `GameDef.reward = { "type": "wall" }`. One reward per solved word, first try or not
    (effort is rewarded, as in the garden). A word already on the wall is still played, still counts in the record,
    and still sends a reward; the website dedupes by `wordId`. During play a small board ("My words") shows picture
    thumbnails of the newest 6 words, **without the spelling** (a repeated word would otherwise be copied off the
    wall). The end screen shows this session's cards with picture and word, new ones marked. Word ids are item ids,
    so a word reused at the missing-letter level is the same card.
14. **Adapt rule.** Unchanged: `Session.resolve()` with the outcome. Up after `upAfterCorrect` first-try words, down
    after `downAfterWrong` words that were not first try.
15. **Hit targets.** Tiles and slots are 100 x 100 scene px. On the 960 x 600 scene a 667 x 375 landscape phone
    scales by 0.625, so a tile is 62.5 px. Too small: tiles are **104** scene px (65 px there), slots 104 too.
    Upright phones get the existing "turn your phone sideways" prompt.
16. **Reduced motion.** Dragging still follows the finger. Removed: lift scale, wobble, hop arcs, entrance walks,
    the card flight, bumps, confetti. Replaced by: fades (150 ms), a glow (opacity only) for lit letters and hints.
    Everything is transform and opacity.
17. **Lean registry.** New runner `slotBuild` in `src/mechanics/slot-build.ts`, styles in
    `@edulearnlabs/kit/slot.css`. A game opts in with `mechanics: { 'slot-build': slotBuild }`. Quiz and fill games do
    not import it, so they ship none of it. Shared code changes are additive and tiny (decision 18).
18. **Shared code touched (all additive).** `types.ts` (new optional types and fields), `session.ts` (no choices for
    slot-build; word rewards), `content.ts` (garden checks use `reward.type === 'garden'`), `audio.ts` (`tone(freq)`),
    `pitch.ts` (`letterPitch`), `drag.ts` (`snap` may return `false`), `host.ts` (`HostInit.wall`), `validate.mjs`.
    Proof: the golden files `tests/golden/*.json` and every existing test pass unchanged.
19. **Voice hook.** `skin.say(word, item)` may return a promise (the game plays its own recording, the planned
    build-time voice files); returning nothing uses the kit's speech. The kit never speaks single letters (browser
    speech says "see" for c).

## 2. Data shape

### 2.1 game.json

```json
{
  "mechanic": "slot-build",
  "reward": { "type": "wall" },
  "strings": { "look": "Listen!", "letter": "Start here!", "tiles": "These letters help!", "spell": "Drag the letters!",
               "wall": "Your word wall is growing!", "wallTitle": "My words", "hear": "Hear the word" },
  "levels": [
    { "id": "cvc", "difficulty": 1, "slot": { "distractors": 1 },
      "items": [ { "id": "w-cat", "prompt": { "text": "cat", "say": "cat", "image": "cat" }, "answer": "cat" } ] },
    { "id": "vowel-trap", "difficulty": 2, "slot": { "distractors": 2, "vowelTrap": true }, "items": [] },
    { "id": "missing", "difficulty": 3, "slot": { "distractors": 2, "given": [1, 2] }, "items": [] },
    { "id": "blends", "difficulty": 4, "slot": { "distractors": 2 }, "items": [] },
    { "id": "five", "difficulty": 5, "slot": { "distractors": 3 }, "items": [] }
  ]
}
```
No `choices` block and no `generator`: words are hand-written items. An item may add `"slot": { "given": [0],
"tray": ["e", "h"] }` to fix the given positions or the exact distractors.

### 2.2 types.ts (additive)

```ts
export type Mechanic = ... | 'slot-build';
export type LetterMistake = 'letter-order' | 'wrong-vowel' | 'look-alike' | 'wrong-letter';
export type MistakeKind = DistractorKind | LetterMistake;
export interface SlotLevel { distractors?: number; vowelTrap?: boolean; lookAlikes?: boolean; given?: number | [number, number] }
export interface SlotItemSpec { given?: number[]; tray?: string[] }
Item.slot?: SlotItemSpec;   Level.slot?: SlotLevel;
export interface WallRewardDef { type: 'wall' }
export interface GardenRewardDef { type: 'garden'; species: string[] }
GameDef.reward?: GardenRewardDef;                      // unchanged type, see section 11 note 1
export interface SlotGameDef extends Omit<GameDef, 'reward'> { reward?: WallRewardDef }
export interface WordReward { id: string; kind: 'word'; wordId: string; at: string; species?: never }
export interface WallView { words: string[] }          // HostInit.wall
SessionRecord.mistakes: Partial<Record<MistakeKind, number>>;
SessionRecord.rewards?: (Reward | WordReward)[];
GameStrings: letter?, tiles?, spell?, wall?, wallTitle?, hear?   (look is shared with fill)
```
`Reward` keeps its name and garden shape, so fill code and the website's `validRewards` are untouched.

### 2.3 Message contract (protocol stays 1)

- `HostInit.wall?: { words: string[] }`: word ids the child already has for this game, oldest first. Sent only to
  games whose catalog entry has a wall reward. No profile id, no timestamps.
- `GameCompleted.session.rewards`: one `{ id, kind: "word", wordId, at }` per solved word. `id` is session id plus
  question index (unique, no random number), `at` is a UTC ISO time (a fact, like garden rewards). Repeats allowed;
  the website keeps the first per `wordId`.
- `GameCompleted.session.mistakes` may carry the four letter kinds.

### 2.4 Planned word (what the screen receives)

```ts
interface SlotSpec {
  word: string;              // "puppy"
  given: number[];           // slot indexes already filled
  tray: { id: number; letter: string; trap?: LetterMistake }[];   // shuffled, ids 0..n-1
}
```

## 3. Reducer (`src/slot.ts`)

State: `filled` (tile id per slot, -1 for a given letter, null empty), `phase` build or complete, `hint`, `idleMs`,
`idleHints`, `wrongs`, `helpTaps`, `hintsShown`, `mistakes` (deduped per word).

| Action | Rule | Effects |
|---|---|---|
| `place { tile, slot? }` | slot missing means the cursor. Ignored if the tile is used or the slot is not empty. Right letter: fill. Wrong: wrongs + 1, classify, ladder to `min(3, wrongs)` | `placed` (+ `complete`) or `wrong` + `hint` |
| `type { letter }` | first free tray tile with that letter onto the cursor | as `place`, or `no-tile` (free) |
| `tick { ms }` | 7 s idle gives H1, at most 2 times in a row | `hint` level 1 (replay flag) |
| `help` | ladder to `max(2, hint + 1)`, capped at 3 | `hint` |

`outcome = { firstTry: wrongs === 0 && hintsShown === 0, hints, mistakes }`. Nothing waits for animation: a fast
typist cannot slip a tile in while another flies.

## 4. Screen (`src/mechanics/slot-build.ts`, `src/styles/slot.css`)

Scene 960 x 600, scaled by one transform, bottom-anchored (same approach as fill). Starting layout in scene px:
word wall board 24 to 224 x 116 to 300, picture card 300 to 540 x 88 to 280 (a button: tap to hear), the friend
beside it 552 to 722, Hazel at `skin.hazel` (default 790, 112), slots centered at y 318 (104 px, 14 px gaps),
tray centered at y 470 (104 px, 8 px gaps). Hooks for tests and tools: `.ell-slot-view[data-phase]`
(`build`, `lighting`, `word`, `reward`), `[data-hint]`, `.ell-slot-cell[data-want]` (never shown or spoken),
`.ell-tile[data-letter]`, `.is-given`, `.is-filled`, `.is-lit`, `.is-picked`, `.is-cursor`, `.is-help`.
The polite live region says what was placed and how many letters are left, never the word's spelling.

## 5. Skin contract (`SlotSkin`, exported from the kit)

| Field | What it is |
|---|---|
| `symbols` | `<symbol>` markup injected once |
| `backdrop` | SVG markup on 960 x 600 (may extend past the edges for wide screens) |
| `picture(image)` | full `<svg>` markup for an image id, drawn in a 220 x 172 box; `''` for unknown ids. Never put the word in it |
| `tile`, `given`, `slot` | SVG markup on 104 x 104 behind a tile letter, a given letter, an empty slot |
| `cast` | friends who bring the words, one per word in turn: `{ symbol, viewBox, happy?, enter? }` |
| `hazel` | Hazel's spot `{ x, y }` in scene px |
| `wall` | board art behind the wall thumbnails, SVG on 200 x 184 |
| `say(word, item)` | voice hook: return a promise to play the game's recording, or nothing for the kit voice |

Every field is optional: without a skin the kit draws plain blocks, dashed slots and a neutral picture frame, so the
playground and the tests always work.

## 6. Size

Estimate: reducer and planner about 1.2 KB brotli, screen about 3 KB, CSS about 1.3 KB (separate file). Target about
+4 KB of JS for a slot game over a quiz game; quiz and fill pages unchanged within 0.1 KB (the shared edits are a
few lines). Measured numbers are in the kit README, section v0.4.0.

## 7. Tests

Unit (`tests/slot.test.ts`): placement (right, wrong, filled slot, used tile, cursor), keys (`type`, no-tile),
duplicates, given slots, mistake kinds and per-word dedupe, ladder (wrong tiles, help, idle replays, no climb after
complete), outcome, completion, planner rules (counts, vowel trap, sound-alikes, look-alikes on and off, item tray,
never in word order, determinism, given ranges), `letterPitch`, session record with word rewards and letter mistakes,
validator rules, and the dev word game. Existing 138 tests and the golden files unchanged.
Browser (`tests/word-e2e.cjs`, throttled): drag, tap-tap, keys, wobble-back, given slots, H1 to H3, completion beat
order with a stubbed voice, session end with rewards and record, wall shelf from HostInit, reduced motion, hit targets.

## 8. Implementation steps (in order)

1. Types, spec doc mirror. 2. `letterPitch`, `audio.tone`. 3. `src/slot.ts` reducer and planner with tests first.
4. Session and content edits (golden green). 5. Validator rules. 6. `drag.ts` snap option. 7. Screen and CSS.
8. Dev fixture `dev/word.html`, `word.ts`, `word-game.json`, `word-skin.ts`. 9. Browser checks. 10. Size, README,
version 0.4.0, commit and push.

## 9. Risks

1. Real touch on iPad Safari and cheap Android still untested (same as fill).
2. Browser speech quality for single short words varies a lot ("cat" can sound like "cut" on some voices). The
   `skin.say` hook is there for recorded words; Letter Workshop should ship recordings when the voice pipeline lands.
3. The website must add `wall` to HostInit and accept `kind: "word"` rewards (today `validRewards` drops anything
   that is not a garden reward, so a v0.4.0 game on today's website loses its cards silently but works).
4. The parent tips need lines for the four letter mistake kinds.

## 10. What a game must implement

`src/main.ts`:
```ts
import '@edulearnlabs/kit/styles.css';
import '@edulearnlabs/kit/slot.css';
import { slotBuild, startGame, type GameDef } from '@edulearnlabs/kit';
import def from '../game.json';
import { skin } from './skin';          // a SlotSkin: pictures per image id, cast, backdrop, optional voice
void startGame(def as unknown as GameDef, { mechanics: { 'slot-build': slotBuild }, skin });
```

## 11. Implementation notes (kit v0.4.0, 2026-11-13)

Built on the kit branch `ccr-d63a6d4f-g77ft0` in two commits (logic, then screen, fixture, browser checks and docs).
Nothing from the design was cut.

**Where the build differs from sections 1 to 10, and why**
1. **`GameDef.reward` keeps its garden type.** Widening it to a union broke the type check of existing tests and of any
   game code that reads `def.reward.species`. So the TypeScript type is unchanged, the JSON still says
   `"reward": { "type": "wall" }`, and slot games are typed `SlotGameDef` (`reward?: WallRewardDef`). Fill code now
   checks `reward.type === 'garden'` (same truth value for every valid fill game). `WordReward` declares
   `species?: never` so code that maps `rewards` to `r.species` still compiles.
2. **The word wall board starts at y 116, not 92.** On a 667 x 375 phone the shell's back button covers the scene down
   to about y 112 and hid the board title (seen in a screenshot).
3. **Tile letters use Andika 400**, the only weight the kit ships (a synthetic bold looked smudgy).
4. **The tray is shuffled from `seeded(hash(wordId + "|" + levelId))`**, so a word reused at the missing-letter level
   gets a different (but still fixed) tray and given slots there.
5. **A wrong tile from the tray is classified against the slot it landed on**, not against the planner's intent
   (`SlotTile.trap` is kept for tools and tests only).

**Checks.** Unit: 172 tests (138 before plus 34 in `tests/slot.test.ts`), typecheck clean, golden files unchanged.
Browser (`tests/word-e2e.cjs`, the session and hint runs on the throttled profile): 66 checks covering hit targets,
the wall from HostInit, drag, tap-tap, letter keys, Enter on a tile then a slot, wobble-back, given slots, H1 to H3,
the completion beat order with a 900 ms fake voice (letters light after the voice ends, left to right, each with its
note, then the word is spoken), session end with word rewards and the record, Back mid-session, reduced motion and
muted, a 667 x 375 phone with 8 tiles (smallest 65 px), and the rotate prompt.
Fill suites on the new code: garden 137 checks (one run hit the known "H2: exactly one count badge" timing flake),
pond 190 of 190. The `pond-extra` check also failed once on the untouched v0.3.0 code on this machine, so it is a
timing flake that predates this release.

**Size.** Quiz page +0.06 KB, fill page +0.09 KB, pond page +0.06 KB. Word page 16.9 KB JS (16.0 KB with no skin):
about 6.8 KB more than a quiz-only game, of which about 5.5 KB is slot-build itself. Over the +4 KB aimed for; the
kit for Letter Workshop is still about 6 KB smaller than Pond Hop's. Trim candidates are in the kit README.

**Still open:** website support (HostInit `wall`, `kind: "word"` rewards in `progress.ts`, parent tips for the letter
mistake kinds), recorded word audio through `skin.say`, real touch devices, the owner's `v0.4.0` tag.
