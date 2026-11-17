# token slots: kit design for Bead Parlor (kit v0.7.0, mechanic `pattern-fill`)

Status: DESIGN and BUILT, 2026-11-16. Opus design pass, then implementation on the kit branch
`claude/upbeat-davinci-c55nml` (from kit v0.6.1, commit `256bea1`). Follows the style of
`planning/slot-build-design.md`. The owner was away (unattended run), so every open point is decided in section 1 with a
recommendation and a reason. Section 12 records where the build differs from this doc.

Files read for this design: main repo `CLAUDE.md`, `planning/game-playbook.md`, `planning/pattern-repeat-design.md`,
`planning/slot-build-design.md`, `planning/framework-spec.md`, `planning/style-guide.md`,
`brand/pattern-repeat/index.html` and `build.py`; kit `CLAUDE.md`, `README.md`, `src/slot.ts`,
`src/mechanics/slot-build.ts`, `src/types.ts`, `src/session.ts`, `src/content.ts`, `src/pitch.ts`, `src/drag.ts`,
`src/host.ts`, `src/game.ts`, `src/mechanics/fill-common.ts`, `src/styles/slot.css`, `build/validate.mjs`,
`build/check-size.mjs`, `tests/slot.test.ts`, `tests/word-e2e.cjs`, `dev/word.*`.

## 0. The big idea in five lines

1. **A gap wants one bead id, judged by position**, exactly like a slot wants one letter. The right bead clicks in with
   its note and stays; a wrong bead wobbles back. No red, no buzzer. The child always finishes and gets the bracelet.
2. **The slot-build reducer is reused unchanged.** Bead ids are mapped to one-character "glyphs", so a bead string is
   an ordinary slot word for `src/slot.ts`. Placement, cursor, hint ladder, idle replays and outcome are the same code
   Letter Workshop runs. Only the mistake names are pattern-specific.
3. **Patterns are data, planned not random:** a unit (`"AB"`, `"ABB"`, `"AABB"`) plus a length and a letter-to-bead
   mapping, gaps at the end, in the middle, or "copy" mode, and a tray of needed beads plus spares, all seeded from
   the item id and the level id, so the same item at the same level always gives the same string and tray.
4. **A new thin runner** `patternFill` (`src/mechanics/pattern-fill.ts`, `@edulearnlabs/kit/pattern.css`). Games
   that do not register it ship none of it. Letter Workshop, quiz, fill, pair and tap games are untouched.
5. **The bracelets are the website's**: one `{ id, kind: "bracelet", beads, at }` per finished string in
   `GameCompleted.session.rewards`, and `HostInit.bracelets = { bracelets: string[][] }` to draw the board.

## 1. Owner decisions (owner away; recommendation and reason for each)

1. **Option (b): a thin new runner that reuses `slot.ts`, not a generalized `slot-build`.**

   | | (a) generalize `slot-build` to tokens | (b) thin runner `pattern-fill` reusing `slot.ts` |
   |---|---|---|
   | Shared code touched | `SlotSpec.word` becomes a token list, `classify`, `letterPitch`, the tray planner and the 563 line screen all get a token path | `slot.ts` and `slot-build.ts`: zero lines. New files only, plus additive types and two lines in `session.ts` |
   | Letter Workshop | Its code path changes; its bundle grows; only tests prove it still behaves | Its slot code is byte-identical; the page grows by 4 bytes (the shared `session.ts` branch) |
   | Reuse | One reducer, one screen | One reducer (the exact `reduceSlot`), a second screen file |
   | Size for a bead game | about the word page | about the word page (similar screen) |
   | Risk if a bead rule needs to differ later | Every bead rule is a branch inside Letter Workshop's code | The bead screen and planner change alone |

   *Recommendation: (b).* It is the least risky for shared code: the slot reducer is reused as it is (so every slot
   rule, already proven by 34 unit tests and 66 browser checks, is the bead rule too), and nothing Letter Workshop
   loads changes. The price is a second screen file (about 5 KB brotli) that copies the slot-build screen's patterns;
   only bead games ship it. *Why not (a):* the screen is where the two games really differ (a picture and a spoken
   word versus a pattern card, a spider, a bracelet), and folding both into one screen makes every future bead tweak a
   Letter Workshop release.
2. **Mechanic id `pattern-fill`.** A new value in `Mechanic` (and in the validator's list). `game.json` says
   `"mechanic": "pattern-fill"`. *Why a new id:* the validator, the session ("no choices") and the registry all key on
   the mechanic, and a bead `game.json` must never be read by the slot-build checks (which demand a lowercase word).
   **Note for the website:** the planning doc said "slot-build generalized"; the catalog entry for `pattern-repeat-k`
   should say `"mechanic": "pattern-fill"` (the catalog field is descriptive only; nothing breaks if it says slot-build).
3. **The glyph mapping (how the slot reducer judges beads).** `planPattern` returns a `PatternSpec` with bead ids. The
   pure function `toSlotSpec(spec)` gives every distinct bead id one character (`a`, `b`, ...) in order of first
   appearance, so the string becomes a slot "word" and every tray bead a slot "tile". `reduceSlot` then does exactly
   what it does for letters: "slot i wants glyph g". The wrapper `reducePattern` only (1) re-names the mistake with the
   bead rule (decision 10) and keeps its own per-string mistake list, and (2) maps effects back to bead ids. The slot
   reducer's own letter classification is never shown or recorded. The slot `type` action (letter keys) is not used.
4. **Data shape** (section 2). Game-level `beads` (the palette, which also fixes each bead's note), a level-level
   `pattern` block (mode, letter-to-bead mapping, gaps, spares), an item-level `pattern` block (unit, length, optional
   mapping and gap positions). Items need no `prompt` or `answer`: the voice line is the game string `next`.
5. **Notes.** A bead's note is `pitchFor(k + 1)` where `k` is its index in the game-level `beads` list (default
   `red, blue, yellow, green, purple, orange`, so C4 D4 E4 G4 A4 C5, as in the art preview). Stable per bead id across
   levels, pentatonic, so every pattern is a little tune that never sounds wrong, and a repeating unit is a repeating
   melody. *Why the game list and not each level's list:* the brief asked for "order of ids in the bead list decides"
   and "stable per id"; a per-level order would give red two notes in two levels.
6. **The string.** `unit` repeated and cut to `length` (`"AB"`, 6: A B A B A B), each letter mapped to a bead id by
   the item's `beads` or else the level's `beads` (A is the first, B the second, ...). At most 7 beads (7 x 104 + 6 x 14
   = 812 scene px). Units are 2 to 4 letters, use at least 2 different letters, and name letters in order of first
   appearance (`ABB`, `AAB`, `ABA`, `ABC`, `AABB`, `ABCD`; never `BA`).
7. **Gaps** (positions the child fills), seeded from `hash(itemId + "|" + levelId)`:
   - `copy` mode (level 1): the full string is shown on a card above; the build row starts empty (every position is
     a gap). No spider (the card takes its place, as in the approved art).
   - `end` mode (default): the last `gaps` positions.
   - `middle` mode (level 4): the last position is always a gap ("what comes next" stays the task), the others are
     picked from the positions after the first unit, and at least one of them has a given bead after it (a real middle
     gap). The validator demands the room for that.
   - In both continue modes **the first full unit is always shown** (positions `0..unit-1` are never gaps), so the
     pattern is readable and the H1 Look hint has something to point at. An item may list exact `gaps` positions.
8. **Tray planner (exactly one right bead id per gap, by position).** The tray holds one bead per gap (the needed
   beads) plus `spares` (default 1) extra beads. Rightness is judged per gap against the bead id that position wants,
   and beads of one id are interchangeable (like the three p tiles in "puppy"), so **a gap can never have two right
   answers**, whatever the spares are: a spare red is just one more red. What spares can do is let a child "use up" the
   wrong red on the wrong gap; that is not possible either, because a red on a gap that wants blue is rejected. So the
   rule is about teaching value, not ambiguity. Spares are taken in this order, never two of the same while another
   kind is left:
   1. a level bead that is not in this pattern at all (an `outside-unit` trap),
   2. a pattern bead that no gap needs (a `unit-order` trap, for example red when only blue is missing),
   3. an extra copy of a needed bead (a harmless decoy; only levels with two colors reach this, like level 1).
   Shuffled with the seeded random. **Never in answer order:** if the needed beads, read left to right in the tray,
   contain the gap order as a subsequence (so a child could copy the tray row), the planner tries the next rotations,
   and if every rotation does, it groups the tray by bead in reverse order of first need, which can never contain it.
   Only checked when the gaps want 2 or more different beads (two reds in a row cannot give anything away).
9. **At most 8 beads in the tray** (8 x 104 + 7 x 12 = 916 scene px, 65 px each on a 667 x 375 phone).
10. **Mistake kinds (new, pattern games only)**, each at most once per string: `unit-order` (a bead that is in this
    pattern but not at this spot: the child knows the beads but not the order) and `outside-unit` (a bead that is not
    in the pattern at all, a spare). Typed `PatternMistake`; `MistakeKind` widens. Existing kinds are unchanged.
11. **Hint ladder (hints only, never the answer)**, the slot ladder unchanged:

    | Level | Name | What happens | Trigger | Cost |
    |---|---|---|---|---|
    | H1 | Look | The first repeat unit pulses (on the string, or on the card in copy mode), Hazel points, bubble `look` ("Look!"), the prompt is said again | 7 s idle (at most 2 replays) or the 1st wrong bead | free |
    | H2 | Gap | The cursor gap (first empty, left to right) glows; bubble `gap` ("Start here!") | 2nd wrong bead or a Hazel tap | first try |
    | H3 | Beads | The beads still needed glow softly; bubble `beads` ("These beads help!") | 3rd wrong bead or a 2nd Hazel tap | first try |

    None of them says which bead goes where: H2 only says where to work next, H3 which beads are in the answer (with
    a two-gap ABAB they still have to order them). A wrong bead never counts as first try.
12. **Inputs.** Drag (Pointer Events through `src/drag.ts`, no magnetic snap), tap a bead then tap a gap, and keyboard:
    Tab between beads and gaps, Enter or Space picks a bead and places it on a gap, Escape drops the pick, and the
    digit keys 1 to 8 place the tray bead in that position onto the cursor gap (the keyboard twin of "drag to the next
    gap"). Cursor = the first empty gap, left to right, same rule as slot-build.
13. **Completion beat.** The last right bead plays its note at once. Then: (1) wait for any voice line (at most
    4.5 s), (2) the beads light left to right, about 280 ms apart, each with its note (the pattern plays as a tune),
    (3) the bracelet is tied: a soft chord, the spider's happy pose, the finished bracelet appears where the tray was,
    (4) it flies to the "My bracelets" board, confetti. Reduced motion: fades and glows only (no flight, no confetti).
    The spoken word step of slot-build is dropped (there is no word; the voice never names colors).
14. **Reward: bracelets.** `"reward": { "type": "bracelet" }`. One bracelet per finished string, first try or not.
    The fact is `{ id, kind: "bracelet", beads, at }`: `id` = session id plus question index, `beads` = the finished
    string's bead ids left to right, `at` = UTC ISO time. Type `BraceletReward`, in the `SessionRecord.rewards` union.
15. **Board and HostInit.** `HostInit.bracelets?: { bracelets: string[][] }` (`BraceletView`): bead id lists of the
    child's newest 64 bracelets, oldest first. The board ("My bracelets", scene 24..224 x 116..300) shows the newest 6
    as mini bracelets and a count; each finished string joins it. The end screen shows this session's bracelets (newest
    10). The kit stores nothing. Protocol stays 1.
16. **Voice.** Says only the prompt, never a color or shape name: `strings.next` ("What comes next?") in continue
    modes and `strings.copy` ("Make this one!") in copy mode (see section 12, note 2). Through `skin.say(text, item)` if
    the game has recordings, else the kit voice.
17. **Accessibility.** Every default bead differs by shape and color (circle, square, triangle, star, diamond, heart),
    asserted by a unit test. Beads in the tray and given beads have an aria label with color and shape ("red circle",
    from `skin.names` or the kit defaults); a gap is "Gap 2 of 3, empty". The live region says what was placed and how
    many gaps are left, never what a gap wants. `data-want` on gaps is for tests and tools only.
18. **Reduced motion.** Dragging still follows the finger. Removed: lift scale, wobble, hop arcs, the spider's drop,
    the bracelet flight, confetti. Replaced by 150 ms fades and opacity glows. All motion is transform and opacity.
19. **Lean registry and shared code.** A game opts in with `mechanics: { 'pattern-fill': patternFill }` and imports
    `@edulearnlabs/kit/pattern.css`. Shared files touched (all additive): `types.ts` (new types and optional fields),
    `session.ts` (no choices for `pattern-fill`; a `bracelet` reward branch), `host.ts` (type only),
    `index.ts` (exports), `validate.mjs` (pattern rules), `package.json` (export map). `slot.ts`, `slot-build.ts`,
    `slot.css`, `drag.ts`, `pitch.ts`, `content.ts` and every other mechanic: zero lines.
20. **Adapt.** Unchanged `Session.resolve()`: up after `upAfterCorrect` first-try bracelets, down after
    `downAfterWrong` bracelets that were not first try.

## 2. Data shape

### 2.1 game.json (levels 1 to 5 of Bead Parlor)

```json
{
  "mechanic": "pattern-fill",
  "reward": { "type": "bracelet" },
  "beads": ["red", "blue", "yellow", "green", "purple", "orange"],
  "strings": { "next": "What comes next?", "copy": "Make this one!", "look": "Look!", "gap": "Start here!",
               "beads": "These beads help!", "bracelets": "Your bracelets are shining!", "braceletTitle": "My bracelets" },
  "levels": [
    { "id": "copy-ab", "difficulty": 1, "pattern": { "mode": "copy", "beads": ["red", "blue"], "spares": 1 },
      "items": [ { "id": "ab-4", "pattern": { "unit": "AB", "length": 4 } } ] },
    { "id": "next-ab", "difficulty": 2, "pattern": { "beads": ["red", "blue"], "gaps": 1, "spares": 1 },
      "items": [ { "id": "ab-6", "pattern": { "unit": "AB", "length": 6 } },
                 { "id": "ab-5", "pattern": { "unit": "AB", "length": 5 } } ] },
    { "id": "three", "difficulty": 3, "pattern": { "beads": ["red", "blue", "yellow"], "gaps": 2, "spares": 1 },
      "items": [ { "id": "aab-7", "pattern": { "unit": "AAB", "length": 7 } },
                 { "id": "abb-6", "pattern": { "unit": "ABB", "length": 6 } },
                 { "id": "abc-6", "pattern": { "unit": "ABC", "length": 6 } } ] },
    { "id": "middle", "difficulty": 4, "pattern": { "mode": "middle", "beads": ["red", "blue", "yellow"], "gaps": [2, 3], "spares": 1 },
      "items": [ { "id": "ab-7", "pattern": { "unit": "AB", "length": 7 } },
                 { "id": "abc-7", "pattern": { "unit": "ABC", "length": 7, "beads": ["blue", "yellow", "red"] } } ] },
    { "id": "long", "difficulty": 5, "pattern": { "beads": ["green", "purple", "orange", "blue"], "gaps": 3, "spares": 1 },
      "items": [ { "id": "abcd-7", "pattern": { "unit": "ABCD", "length": 7 } },
                 { "id": "aabb-7", "pattern": { "unit": "AABB", "length": 7 } } ] }
  ]
}
```

Field rules (the validator checks every one):
- `beads` (game, optional, default the six above): 2 to 8 distinct slugs. Order fixes the notes.
- `level.pattern.mode`: `"copy"`, `"end"` (default) or `"middle"`.
- `level.pattern.beads`: the letter mapping (A, B, C, D) and the spare pool. Every id in the game list.
- `level.pattern.gaps`: count or `[min, max]`, default 1 (ignored in copy mode, where every position is a gap).
- `level.pattern.spares`: 0 to 3, default 1.
- `item.pattern.unit`: 2 to 4 capital letters, 2 or more different, letters in order of first appearance.
- `item.pattern.length`: 2 to 7; continue modes: at least unit + gaps (end) or unit + gaps + 1 (middle);
  copy mode: 2 to 6 (the card).
- `item.pattern.beads`: optional mapping override; `item.pattern.gaps`: optional exact positions (continue modes only,
  each after the first unit, at least one).
- Tray (needed plus spares) at most 8. Every unit letter must have a bead in the mapping. An item id means one
  pattern (unit and length) in every level.

### 2.2 types.ts (additive)

```ts
export type Mechanic = ... | 'pattern-fill';
export type PatternMistake = 'unit-order' | 'outside-unit';
export type MistakeKind = DistractorKind | LetterMistake | CountMistake | PatternMistake;
export type PatternMode = 'copy' | 'end' | 'middle';
export interface PatternLevel { mode?: PatternMode; beads: string[]; gaps?: number | [number, number]; spares?: number }
export interface PatternItemSpec { unit: string; length: number; beads?: string[]; gaps?: number[] }
export interface PatternBead { id: number; bead: string; trap?: PatternMistake }
export interface PatternSpec { mode: PatternMode; string: string[]; unit: number; given: number[]; tray: PatternBead[] }
Item.pattern?: PatternItemSpec;   Level.pattern?: PatternLevel;   GameDef.beads?: string[];
export interface BraceletRewardDef { type: 'bracelet' }
export interface BraceletView { bracelets: string[][] }           // HostInit.bracelets
export interface BraceletReward { id: string; kind: 'bracelet'; beads: string[]; at: string; species?: never }
SessionRecord.rewards?: (Reward | WordReward | PatchReward | AnimalReward | BraceletReward)[];
export interface PatternGameDef extends Omit<GameDef, 'reward'> { reward?: BraceletRewardDef }
GameStrings: next?, copy?, gap?, beads?, bracelets?, braceletTitle?   (look is shared)
```

### 2.3 Message contract (protocol stays 1)

- `HostInit.bracelets?: { bracelets: string[][] }`: newest 64, oldest first, bead ids only. Bracelet games only.
- `GameCompleted.session.rewards`: one `{ id, kind: "bracelet", beads, at }` per finished string (repeats normal,
  dedupe by `id`), and `hints` (H2 and H3 steps). `mistakes` may carry `unit-order` and `outside-unit`.

## 3. Rules (`src/pattern.ts`, pure)

- `beadString(item, level)`, `planGaps`, `planPattern(item, level, levelId)` (deterministic), `toSlotSpec(spec)`.
- `initPattern(spec)`, `reducePattern(state, action)` with actions `place { tile, slot? }`, `tick { ms }`, `help`;
  effects `placed { tile, slot, bead, left }`, `wrong { tile, slot, bead, mistake }`, `hint { level, slot, replay? }`,
  `complete { outcome }`. `outcome = { firstTry, hints, mistakes: PatternMistake[] }` (from the slot outcome, with
  the bead mistakes). `classifyBead(spec, bead)`, `neededBeads(state)`, `patternCursor(state)`, `beadNote(def, id)`.
- `DEFAULT_BEADS` (ids), `DEFAULT_BEAD_LOOK` (color and shape per default id), `braceletOf(state)`.

## 4. Screen (`src/mechanics/pattern-fill.ts`, `src/styles/pattern.css`)

Scene 960 x 600, scaled by one transform, bottom-anchored (as slot-build). Layout (from `brand/pattern-repeat`):
board 24..224 x 116..300, spider (`skin.cast`) at 215..385 x 118..274 on a thread, Hazel at `skin.hazel` (default
770, 104), string row top y 318 (104 px beads, 14 px apart, centered, on a cord), tray top y 470 (104 px, 12 px
apart, on a dish), copy card 270..690 x 124..270 with the example at 84 px beads (smaller when it holds more than 4).
Hooks for tests: `.ell-bead-view[data-phase]` (`build`, `lighting`, `reward`), `[data-hint]`, `[data-mode]`,
`.ell-bead-gap[data-i][data-want]` (never shown or spoken), `.is-given`, `.is-filled`, `.is-lit`, `.is-cursor`,
`.is-unit` (H1), `.ell-bead[data-id][data-bead]` (tray), `.is-used`, `.is-picked`, `.is-help`, `.ell-bead-mini`
(board), `.ell-bead-endrow .ell-bead-bracelet` (end screen).

## 5. Skin contract (`BeadSkin`, exported from the kit; every field optional)

| Field | What it is |
|---|---|
| `symbols` | `<symbol>` markup, injected once. A symbol `bead-<id>` (viewBox 0 0 100 100) draws that bead; a bead without one uses the kit's plain shape |
| `names` | aria names per bead id ("red circle"); defaults for the six kit ids |
| `backdrop` | SVG markup on 960 x 600 (may extend past the edges) |
| `gap` | SVG markup on 104 x 104 for an empty gap |
| `tray` | the tray dish: SVG markup, or `(width) => markup`, on width x 132 |
| `cast` | the bead maker: `{ symbol, viewBox, happy? }`, drawn in 170 x 156 on a thread |
| `hazel` | Hazel's top left in scene px, default `{ x: 770, y: 104 }` |
| `board` | board art behind the mini bracelets, SVG on 200 x 184 |
| `card` | copy-mode card art, SVG on 420 x 146 |
| `bracelet(beads)` | full `<svg>` markup of a bracelet; default: a cord loop with the bead symbols |
| `say(text, item)` | voice hook: return a promise to play a recording, or nothing for the kit voice |

## 6. Size

Target: quiz, fill, pond, word, pair and tap pages within 0.1 KB of v0.6.1 (only `session.ts` grows, by two short
branches). A bead page about the size of the word page. Measured numbers: kit README, v0.7.0.

## 7. Tests

Unit (`tests/pattern.test.ts`): string building, gap planning (copy, end, middle, item gaps, first unit kept,
determinism), tray planner (counts, spare order, never in answer order, determinism, at most 8), the six default beads
(six shapes, six colors), notes, reducer (right, wrong with both mistake kinds and per-string dedupe, cursor, ladder,
idle, complete, outcome, bracelet), session record with bracelet rewards and pattern mistakes, validator rules, the dev
bead game. Existing tests and golden files unchanged.
Browser (`tests/bead-e2e.cjs`, throttled): hit targets, the board from HostInit, drag, tap-tap, digit keys, wobble back,
no red, given beads, copy card, H1 to H3, the beat order with a slow fake voice, notes per bead, session end with
bracelet rewards and record, Back, reduced motion and muted, 667 x 375 phone, rotate prompt.

## 8. Implementation steps

1. Types. 2. `src/pattern.ts` with tests first. 3. Session and validator. 4. Screen and CSS. 5. Playground
(`dev/bead.html`, `bead.ts`, `bead-game.json`, `bead-skin.ts`). 6. Browser checks. 7. Size, README, version 0.7.0.

## 9. Risks

1. Real touch on iPad Safari and cheap Android still untested (same as slot-build).
2. The website must add `bracelets` to HostInit and accept `kind: "bracelet"` rewards.
3. Parent tips need lines for `unit-order` and `outside-unit`.
4. A spider can frighten some children (art preview question); the kit does not care, the skin decides.

## 10. What a game must implement

```ts
// src/main.ts
import '@edulearnlabs/kit/styles.css';
import '@edulearnlabs/kit/pattern.css';
import { patternFill, startGame, type GameDef } from '@edulearnlabs/kit';
import def from '../game.json';
import { skin } from './skin';          // a BeadSkin: bead symbols, spider, backdrop, board, optional voice
void startGame(def as unknown as GameDef, { mechanics: { 'pattern-fill': patternFill }, skin });
```

## 11. Framework spec additions (for the owner to merge into `planning/framework-spec.md`)

Not edited directly (the main repo is being committed by another agent). Proposed text:
- Section 1, `mechanic` row: add `pattern-fill`.
- Section 2, mechanic-specific fields, new bullet: "`pattern-fill` (kit v0.7.0, first game: Bead Parlor): beads
  placed into gaps of a repeating pattern. Game-level `"beads"` (2 to 8 bead ids; the order fixes each bead's
  pentatonic note; default red, blue, yellow, green, purple, orange). A level-wide `"pattern"` block: `mode` (`copy`,
  `end` default, `middle`), `beads` (unit letter A, B, ... to bead id; also the spare pool), `gaps` (count or
  `[min, max]`, default 1), `spares` (0 to 3, default 1). Items are `{ "id", "pattern": { "unit": "AB", "length": 6,
  "beads"?, "gaps"? } }` (no prompt or answer). Strings at most 7 beads, tray at most 8. Game-level
  `"reward": { "type": "bracelet" }`: one bracelet per finished string, stored by the website. Pattern mistakes are
  `unit-order` and `outside-unit` (each at most once per string). Full shape: `planning/token-slot-design.md`."
- Section 4, reward sections: "`bracelets[profile][game]`: `{ "v": 1, "bracelets": [{ "id", "beads": [...], "at",
  "session" }], "folded": 0 }` (bracelet games, kit v0.7.0). Same rules as quilts and parades. HostInit sends only
  `{ "bracelets": [[bead ids], ...] }`, the newest 64, oldest first." (Website shape is the website's call; this is
  the suggestion.)
- Section 6, HostInit row: "optional `bracelets` (`{ bracelets: string[][] }`, bead ids of the child's newest 64
  bracelets for this game, oldest first; bracelet games only, kit v0.7.0)".
- Section 6, GameCompleted row: "Since kit v0.7.0 bracelet games (pattern-fill) send `hints` and one `rewards` entry
  per finished string, `{ id, kind: "bracelet", beads, at }` (`beads` = bead ids left to right; deduped by `id`), and
  `mistakes` may use `unit-order` and `outside-unit`."
- Section 7, mechanics row: add `mechanics/pattern-fill` (v0.7.0).

## 12. Implementation notes (kit v0.7.0, 2026-11-16)

Built on the kit branch `claude/upbeat-davinci-c55nml` in small commits (logic, screen and checks, docs). Nothing from
sections 1 to 11 was cut. `git diff 256bea1` touches no existing test, no golden file, and not `src/slot.ts`,
`src/mechanics/slot-build.ts` or `src/styles/slot.css`.

**Deviations from the brief, said loudly**
1. **Mechanic id is `pattern-fill`, not `slot-build`.** The website catalog entry for `pattern-repeat-k` should say
   `"mechanic": "pattern-fill"` (descriptive only there; nothing breaks if it says slot-build). game.json must say
   `pattern-fill`, or the slot-build validator rejects it.
2. **Copy mode speaks `strings.copy` ("Make this one!"), not "What comes next?"**, because nothing "comes next" when
   copying. Still a prompt only, never a color. A game that wants one line everywhere sets `"copy": "What comes next?"`
   (the card title uses the same string).
3. **Notes come from a game-level `beads` list** (new optional field, default the six kit beads), not from each
   level's list. The brief asked for "stable per id" and "order of ids in the bead list decides the note"; a per-level
   order would give one bead two notes. Bead Parlor can leave `beads` out if it uses exactly the six kit ids.
4. **The board shows no count.** The website sends only the newest 64, so a count would stop at 64 and be wrong.
5. **No spider in copy mode** (the card takes her place, as in the approved art preview, scene 2).
6. **The copy card's aria label is only its title.** The example is the answer, so its bead names are not put in the
   DOM (the brief's rule). A screen reader child therefore cannot read the example; acceptable for level 1 only.
7. **Level 4 "look-alike shape" trap is not built.** Shapes belong to the skin, so the kit cannot know which look
   alike. Spares are planned by pattern membership (`outside-unit`, then `unit-order`, then decoy copies).
8. **Middle mode needs at least 2 gaps** (the last position plus a real middle gap); the validator says so.
9. **The brief counted 266 existing unit tests; the branch had 274** (v0.6.1 added 8). All 274 pass unchanged.

**Other notes**
- Keyboard: Tab, Enter or Space to pick and place, Escape to drop the pick, digits 1 to 8 place that tray bead on
  the cursor gap. A digit for a used bead wobbles it and costs nothing.
- `HostInit.bracelets` entries that are not lists of strings are dropped silently (never shown, never an error).
- The reward copies the bead list, so the fact never changes after it is made (unit tested).
- A kit bead symbol list is built by a function, not a module constant: a top-level call would have stayed in every
  game's bundle (it cost quiz games 0.43 KB until fixed).

**Checks.** See the kit README, section v0.7.0, for the final numbers.
