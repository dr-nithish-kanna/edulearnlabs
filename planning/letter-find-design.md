# letter-find: kit design for Letter Station (kit v0.6.1 to v0.7.0)

Status: DESIGN ONLY, 2026-11-17. Opus design pass asked for in `planning/letter-tap-design.md` section 6. Nothing is
built. The owner reviews section 1 (flaws found in the plan) and section 16 (owner decisions) before an agent
implements it from section 15.

Files read for this design: main repo `CLAUDE.md`, `planning/game-playbook.md` (all sections), `planning/letter-tap-design.md`,
`planning/tap-count-design.md`, `planning/pair-match-design.md`, `planning/slot-build-design.md` (voice and look-alike parts),
`planning/framework-spec.md`, `planning/style-guide.md`, `planning/mvp-games.md`, `templates/game-repo/GAME_RULES.md`, website
`src/scripts/progress.ts` (mastery, start level, reward stores, tips) and `src/data/skills.json`, `src/data/games.json`.
Kit v0.6.1 at commit `256bea19a544ef019b27e3290e011aeb28725e47` (fetched by name from `claude/amazing-albattani-g2r7l1`, read in a
throwaway worktree in the scratchpad; the session checkout is stale at v0.1.0 and was not touched): `src/tap.ts`,
`src/mechanics/tap-count.ts`, `src/mechanics/fill-order.ts`, `src/mechanics/fill-common.ts` (exports), `src/mechanics/common.ts`,
`src/types.ts`, `src/content.ts`, `src/session.ts`, `src/game.ts`, `src/index.ts`, `src/host.ts`, `src/strings.ts`, `src/pitch.ts`,
`src/audio.ts`, `src/random.ts`, `src/slot.ts` (look-alike table), `src/styles/tap.css`, `src/styles/fonts.css`,
`build/validate.mjs`, `build/check-size.mjs`, `vite.config.ts`, `dev/tap.ts`, `dev/tap-game.json`, `README.md` (size tables).

**What I verified, not only read** (throwaway code in the scratchpad worktree, nothing in any repo):
- Built the kit pages and ran `build/check-size.mjs` on each: quiz page entry JS **9.7 KB**, tap-count page with no skin and
  no fill player **15.8 KB**, Hedgehog playground **18.3 KB** entry plus a **7.6 KB** lazy fill chunk, and a quiz page that
  imports only `planObjects` from `src/tap.ts` **10.2 KB** (the reducer strings are absent from that bundle, so tree shaking
  drops the counting code). Andika (the reading font) is already in the tap page's Before Play (18.8 KB), so letters cost no
  new font bytes.
- A prototype letter planner (section 7) on top of the real `planObjects`, run as a vitest file: 270 000 boards (every
  target in every level, 2000 seeds each, two ladders). 0 planner failures, 0 boards with a "song cue", every centre at
  least 112 scene px apart, 0 hit circles outside the play area, the answer equally often in every position (within
  about 1 point), and at the top level a look-alike of the target was on the board in 44 000 of 44 000 boards that could
  have one. The look-alike table is symmetric.
- The real `Session` class with 6, 8 and 10 rounds, every round first try, from level 1: with 6 rounds the record says
  `maxDifficulty: 4` while **no round was played at level 4** (levels played 1,1,2,2,3,3). Flaw F12.
- Mastery arithmetic from `progress.ts` (`pct >= 0.85`): 6 rounds need 6 of 6, 8 rounds 7 of 8, 10 rounds 9 of 10.

Not verified: anything on screen (no letter-find screen exists), speech synthesis of letter names on a real
Chromebook, and every size in section 13 marked "estimate".

## 0. The big idea in six lines

1. **Hear a name, find the shape.** The fox says "Find M!"; the letters sit on parcels on the platform; the child taps
   one. A tap is a judgement (right or not yet), not a count, so this is a new mechanic, `letter-find`, that imports
   tap-count's proven layout planner and nothing else from it.
2. **The request is spoken, never written.** Showing "M" in the bubble would turn name recognition into shape matching
   (tap-count's F3 again). The letter card is a hint the child can ask for.
3. **Rules are a pure reducer** (`src/find.ts`): tap, click, Enter and the letter key all send the same `pick` action.
4. **Boards are planned, not random**: no look-alikes below the top level, a planned look-alike at the top level,
   sound-alike names only from level 3, no alphabet-song order, the answer equally often in every spot.
5. **Hints narrow, they never reveal early**: a wrong letter dims and says its own name, the second miss narrows the
   board to two, only the third miss leaves the answer.
6. **The train is the website's.** The game reports `{ id, kind: "car", letter, at }` per solved round and gets
   `HostInit.train = { cars }` to draw it. The kit stores nothing. Protocol stays 1.

## 1. Flaws found in `letter-tap-design.md` (look at these first)

Fourteen real flaws (F1 to F14) and five smaller conflicts with existing rules.

| # | Flaw | Why it matters | Proposed fix |
|---|---|---|---|
| F1 | **"Idle hint: the target twinkles after a few seconds."** | A free twinkle on the right letter is the answer, given for waiting. A child who waits 5 s never has to know the letter, and first try would still count. Breaks "hints only, never the answer first". | Idle repeats the spoken request and makes **every** letter shimmer once in reading order (a "look at all of them" cue that points at nothing). The target is never singled out before the last rung. Decision 5. |
| F2 | **The request has no stated visual form, and the obvious one ("Find M" in the bubble) gives the skill away.** | With "M" on screen the child matches shape to shape. That is a real Pre-K skill, but not this one (name to shape). Same trap as tap-count F3 (a visible numeral turned How many? into copying). | The bubble shows a speaker icon (tap to hear again, free), never the letter. The letter card ("It looks like this!") is a costed hint rung. Decisions 2 and 3. |
| F3 | **"After two misses the other letters dim, leaving the answer."** | With 8 letters, two misses then a reveal means the answer appears after only 2 of 7 wrong letters were ruled out: the hint does the work. With 3 letters the rule does nothing (two misses already leave one). | Narrowing ladder: miss 1 dims that letter; miss 2 dims all but two (the answer plus one planned rival, the look-alike when there is one); miss 3 leaves only the answer. The child always makes the last tap. Decision 4. |
| F4 | **"Voice says the letter name, then the sound and a word."** | Browser speech cannot say a letter sound (/b/) reliably: it reads "buh" or the letter name (slot-build design 19: "the kit never speaks single letters"). Sounds are also MVP game 11 (phonics); mixing them in blurs the one micro-skill and the parent tip. | Name and word only: "M! M is for moon." A sound line can come with recorded voice, as its own decision then. Decision 7. |
| F5 | **Letter names in speech synthesis are not stable.** | "A" alone can be read as the article "uh". "Z" is "zee" on en-US voices and "zed" on en-GB and en-IN voices, and the kit's voice picker (`audio.ts`) accepts all three. A child would hear two names for one letter across devices. | A per-letter `say` field in `game.json` (spelling tuned by ear, for example "ay" if a voice says "uh"), and the owner picks "zee" or "zed" once. Decision 14. |
| F6 | **Level 4 look-alikes with uppercase only.** The classic reversals (b d, p q) are lowercase. The kit's look-alike table (`LOOK` in `slot.ts`) is lowercase only. The website's `look-alike` tip says "like b and d ... say its sound". | Reusing either would plan nothing useful for capitals and tell the parent the wrong thing. | A new uppercase table in `find.ts` (section 7.2): M W N Z (turns), E F, P R B, O Q C G D (a stroke or tail), U V Y, I L T, K X. A letter-recognition tip on the website ("E and F"). |
| F7 | **Alphabetical pools (A to H, A to M, A to T, A to Z) bring U to Z and look-alikes at the same step.** | At level 4 a miss on W cannot be told apart: "has not met W yet" or "confuses W with M". Two difficulty steps at once also makes the top level (the one mastery needs) a wall. Level 1 "A to H" is also tight: the prototype found target E has exactly the 2 legal rivals it needs, so any extra rule would break it. | Pools by shape distinctness and frequency, growing 8, 14, 20, 26 (section 6.1), so level 4 adds only 6 new letters and the look-alike measure lands mostly on letters already met. Pools are data, so the owner can still pick alphabetical. Decision 8. |
| F8 | **A child who knows the alphabet song but not the shapes.** | If the letters read A B C left to right, "find B" is "the middle one", no shape needed. Children who sing "elemenopee" cannot pick L M N O P apart, and a run like L M N on screen invites the song. | The planner never builds a song cue: no run of 3 alphabet neighbours in reading order, and with 4 or more letters never the whole board in alphabetical order. Verified: 0 in 270 000 boards, answer position still uniform. (Banning every sorted order of 3 letters biased the answer away from the middle, 38 / 24 / 38 percent, so the rule is the run, not "any sorted 3".) |
| F9 | **Per-item labels in crowded scenes, and the pile planner rotates art.** | The letter is the item, so it must never be covered or turned. `planObjects` gives pile objects -25 to 25 degrees of rotation and `tap-count` rotates the whole art. A turned N reads as Z, a turned M as W. Props shaped like letters (a lamp post is I or T, a clock is O, a horseshoe is U) and any text in the backdrop ("STATION", clock numerals) are extra letters on screen. | The carrier (parcel) may tilt by `rot * 0.3` at most; the glyph is a separate upright layer on top of its carrier. One carrier shape with a flat face, colours varied by seed. Art rule for the preview: no letters, numerals or letter-shaped props anywhere in the scene. Decision 18. |
| F10 | **Guessing odds with 3 letters.** | A guesser taps right 1 time in 3 and gets 2 in a row 1 time in 9, which moves level 1 to 2 by luck. | Accept at level 1 (a 3 year old must be able to win), never use 3 letters above it. 5 letters: 1 in 5 and 1 in 25; 6: 1 in 6 and 1 in 36; 8: 1 in 8 and 1 in 64. Mastery lives at 8. |
| F11 | **"Six rounds per session, about 3 minutes."** | Finding one letter plus the car beat is about 10 to 18 s, so 6 rounds is 1 to 2 minutes (GAME_RULES 1 asks 2 to 5). And with 6 rounds "Mastered" needs 6 of 6 (85 percent of 6 is 5.1): one slip in a session can never count. | 10 rounds, 180 s. Mastered then needs 9 of 10 (one slip allowed), Getting it 8 of 10. Decision 10. |
| F12 | **Mastery can come from sessions that never played the top level** (kit `Session`, also live in Hedgehog Picnic). | `move()` raises `maxDifficulty` when the level is *reached*, at the resolve of the round that earned it. Verified: 6 first-try rounds from level 1 play levels 1,1,2,2,3,3 and record `maxDifficulty: 4`. The website's Mastered rule (`maxDifficulty >= top`) then counts a session with 0 top-level boards. Hedgehog Picnic (6 rounds, 4 levels) has exactly this shape today. | Kit fix: raise `maxDifficulty` in `next()` when a question at that level is actually asked. It changes records, so it ships as its own small kit release (v0.6.2) with a README note, and games take it on purpose. 10 rounds makes it rarer, not gone. Decision 12. |
| F13 | **"Lowercase later is a new level set, not a new game."** | New levels raise the skill's `topDifficulty` (4 to 6). Every child marked Mastered drops back to Getting it the day it ships (tap-count F12). Lowercase is also a different skill (most early print is lowercase). | Lowercase is its own skill (`language.letters.lowercase-recognition`) and its own game page, same mechanic, new data. Decide now so ids stay stable. Decision 15. |
| F14 | **Letters with sound-alike names** (B D E G P T V Z, M N, F S X, A J K). | Through a tablet speaker and synthetic voice, "Find D" with B and P on the board is a hearing test as much as a shape test. A wrong tap would be logged as a shape slip and the parent tip would be wrong. | Sound-alike rivals only from level 3, recorded as a new mistake kind `name-alike`, so the parent sees "mixes up letters whose names sound alike" separately from look-alikes. Decision 16. |

Smaller conflicts:

| # | Item | Fix |
|---|---|---|
| F15 | GAME_RULES 3 "number keys 1 to 4" mean nothing on a board with no visible numbers (tap-count F9 had the same trap). | Letter keys pick by value (press M to pick the M parcel), digits are ignored. Decision 13. |
| F16 | Draft "never drop below the current level on a miss" differs from Hedgehog Picnic's locked 7(b) (down after 2 rounds in a row that needed the strong hint). | Same rule as Hedgehog: a round that reached the narrow rung is a miss; two in a row move down one level. Decision 11. |
| F17 | 26 reward pictures (apple to zebra) in the entry JS would take 5 to 9 KB of the 30 KB entry budget, and `check-size.mjs` counts every `.svg` file as Before Play even if it loads later (`BEFORE` holds `.svg`). | Car pictures in an `import()` chunk (already counted as Lazy JS). Decision 17. |
| F18 | Reward words: X has no word that starts with its usual sound, and words like "ice" or "owl" start with the long vowel. | Since this game teaches names, pick words whose first letter is plainly the letter and whose first sound is its common sound; X uses "box" with the x shown at the end. Art preview question. |
| F19 | "Wrong tap ... says its own name **softly**." `audio.say` has no volume option. | Additive `say(text, { volume })` in `audio.ts` (SpeechSynthesisUtterance supports it), or the normal volume. Small, part of step 6. |

Checked and **not** a flaw:
- The tap-count play area fits 8 letters with 64 px targets on a 667 x 375 phone (104 scene px circles, 112 apart): the
  planner places up to 10 and the prototype re-checked it with letters attached.
- Look-alike rules below the top level never starve the planner, even with the extra "no two look-alikes anywhere on the
  board" rule: the fewest legal rivals for any target is 3 (need 2) at level 1, 6 (need 4) at level 2, 17 (need 5) at
  level 3. The validator still checks pool size (section 12).
- `letterPitch` (kit v0.4.0) already gives every letter its own pentatonic note, the same note it has in Letter Workshop.
- The session already supports a mechanic that plans its own choices (`noChoices`): one more name in that line.

## 2. The skill and the errors to prevent

- Grade Pre-K, `language.letters.letter-recognition`, MVP number 9. One micro-skill: **hear an uppercase letter name and
  find that letter among others** (name to shape).
- Errors and how the design treats each:

| Error | What the child does | Design |
|---|---|---|
| Look-alike | Taps W for M, F for E | Planned only at the top level, recorded `look-alike`, the narrow rung keeps the look-alike so the last choice is "M or W?" |
| Name-alike | Taps D for B (hears "dee") | Planned from level 3, recorded `name-alike`; the wrong letter says its own name, so the child hears the difference |
| Song, not shape | Finds letters by alphabet position | Planner never builds a song cue; boards are scattered at levels 3 and 4 |
| Does not know it yet | Taps anything | Recorded `wrong-letter`; the letter comes back as practice (every 3rd round, if it fits the level) |
| Copies a shape | Matches a visible model | The model card is a costed hint, so first try means "from the name alone" |

## 3. Owner decisions taken as given (from letter-tap-design.md)

Letter hunt in a scene; fox station master asks, Hazel hosts; reward is an alphabet train, one car per solved letter
with the letter and an object; voice first, a visual twin for every sound; uppercase first; title Letter Station;
speech synthesis now, recorded voice later; upright phones get the rotate prompt; up after 2 correct in a row.

## 4. The open question: a find mode in tap-count, or a new mechanic?

**Answer: a new mechanic `letter-find` (`src/find.ts` plus `src/mechanics/letter-find.ts`) that imports the layout
planner from `src/tap.ts`.** The owner's lean was right. Evidence from the v0.6.1 code:

| Part | What tap-count does (file) | What letter find needs | Shareable as is? |
|---|---|---|---|
| Layout | `planObjects(n, layout, seed)`, pure, exported (`tap.ts`) | The same positions, plus a letter per object | **Yes.** Measured: importing only it adds 0.5 KB and no reducer code |
| Constants | `TAP_AREA`, `TAP_HIT`, `TAP_MIN` (`tap.ts`) | The same targets and spacing | **Yes** |
| Round plan | `TapPlan { n, kind, choices, mistakes: DistractorKind, answer: String(n) }`; `planTap` reads `countOf(item.id) ?? Number(item.answer)` | A target letter, a letter per object, letter mistake kinds | No: "B" becomes `NaN`, choices are numbers |
| Reducer | `count` pushes to `order` (the number belongs to the tap), `again` is a neutral re-tap, `all-counted`, `ask`, then `name` judges a **choice button** | Every tap on an object **is** the judgement; no order, no ask phase, no choices | No: the core action means the opposite thing |
| Hints | `rest` twinkles *uncounted* objects, `along` and `recount` replay the tap order | Dim, narrow, last; idle shimmer of all | No |
| Runner | `runTap`: parade cycle from `def.reward.type === 'parade'`, `friendFor(def.friends)` with counting kinds, `kindWord`, `numberWords`, badge, Done bell, digit keys by value, fill chunk loader | Train from solved letters, one fox, letter names, letter keys, no badge, no fill | No: one function, so a mode is an `if` in most of it |
| Validator | tap-count levels must have `generator.type === "count"` and reward `parade` (`validate.mjs` lines 116 to 118) | A letter generator and reward `train` | Every tap-count rule would branch by mode |
| Scene | `mountUi` from `fill-common.ts` (960 x 600, Hazel, Help, shelf strip, live region), `use`, `enter`, `friendArt`, `cap`, `fmt`; `friendPose`, `pictureFor` | The same scene | **Yes**, already exported |
| Session | `noChoices` for tap-count | The same | One name added |

Why a mode would hurt:
1. **Bytes both ways.** A mode lives inside `runTap` and `reduceTap`, and Rollup cannot drop an unused branch of a used
   function. Letter Station would ship the counting screen (badge, recounts, Done bell, digit keys, fill loader: about
   6 KB measured for the tap screen plus scene over quiz) and Hedgehog Picnic would grow by the find code (estimate 4 to
   5 KB) for nothing.
2. **Risk to a live game.** Every change to `reduceTap` re-opens Hedgehog Picnic's 266 unit tests and 124 browser checks
   for a feature it does not use. A new mechanic is additive: tap-count does not change at all.
3. **Bent rules.** tap-count's own comment says "the number belongs to the tap, not to the object". In a find round the
   letter belongs to the object and the tap is a guess. One reducer holding both would need a `mode` check in every case.

What letter-find reuses (no copies): `planObjects`, the `TAP_*` constants, `mountUi` and the scene helpers, `wait`,
`praiseCycle`, `juice`, `letterPitch`, `hashSeed`, `seeded`, `shuffle`, the `tap.css` scene rules (`[data-variant="tap"]`:
friend spot, shelf padding, round object buttons). The only near copy is the bottom strip renderer (about 20 lines,
`renderParade` is module private); generalise it when a third strip game comes.

*Not chosen:* a generic "tap-object" core with plug-in judges. Cleaner on paper, but it rewrites a live mechanic to
serve a second user; revisit if a third tap game appears (odd one out, MVP 19, may be that game).

## 5. Mechanic behaviour (what the child sees and hears)

### 5.1 One round

1. The fox steps in (the friend entrance from fill), the parcels pop in one after another (60 ms apart), each with its
   letter upright on its face. The bubble shows a speaker icon. The fox says **"Find M!"** (spoken only). Parcels are
   tappable at once.
2. **Right tap:** the M parcel hops at the tap and plays `letterPitch("m")` (note first, within 0.3 s), it glows, the
   fox turns happy, then the voice says "M! M is for moon." (awaited), then a short rising run and the chord, then the
   parcel slides into a new train car at the bottom strip with the moon picture, and a praise line.
3. **Wrong tap:** see the ladder (5.3). Never a red X, a buzzer, a shake, a counter of mistakes, or a timer.

### 5.2 Rules

- One target letter per round, exactly once on the board. The board shows 3 to 8 different letters.
- A tap on a dimmed letter gives the neutral answer (soft click and a ring pulse), no name, no cost.
- Taps after the round is solved do nothing. Nothing waits for animation: the judgement happens at the tap.
- A key for a letter that is not on the board gives a soft click and nothing else (no cost; a toddler on a keyboard is
  not making letter mistakes).

### 5.3 Hint ladder (hints only, never the answer first)

| Step | Trigger | What happens | Costs first try |
|---|---|---|---|
| Hear again | Tap the bubble or the fox, any time | The request again ("Find M!") | no |
| Nudge | 7 s idle, at most 2 in a row | The request again, the fox bobs, every letter shimmers once in reading order (opacity) | no |
| Card | Tap Hazel (Help) | The fox holds up a card with the letter shape; bubble "It looks like this!" The board is unchanged. | yes (a hint) |
| Not it | 1st wrong tap | That letter dims (stays visible, not tappable) and says its own name: "That's W." then "Find M!" again | yes |
| Narrow | 2nd wrong tap | Every letter but two dims: the answer and one rival (the planned look-alike if still lit, else a name-alike, else a planned other). Voice: "That's N. Find M!" | yes |
| Last | 3rd wrong tap | Only the answer stays lit. Voice: "Find M!" The child makes the final tap | yes |

*Why the wrong letter says its own name:* it turns the mistake into a lesson with no judgement in it ("that one is W")
and it is how a parent would help. *Why the narrow keeps the look-alike:* "M or W?" is exactly the discrimination the
top level exists to teach. *Check against the playbook rule:* the answer is never marked; it only remains, after three
real tries, which is how fill and tap-count end their ladders.

With 3 letters the ladder is shorter by itself (two misses leave one). With 5 letters: 4, then 2, then 1 left.

### 5.4 Voice and tones (voice first)

| Moment | Order |
|---|---|
| Round start | Parcels pop in silently, then "Find M!" |
| Right tap | Note at the tap (the one exception, like counting taps: feedback within 0.3 s, and the note ends before speech starts), then "M! M is for moon." awaited (4.5 s cap), then the rising run and chord, then the car |
| Wrong tap | Soft click at the tap (UI sound, not a judgement), dim, then "That's W." awaited (2.5 s cap), then "Find M!" only if no newer tap came. No tones |
| Hints | Bubble line and voice awaited, then any shimmer; no tones under speech |
| Fast tapper | Each new tap cancels older speech (`audio.say` already cancels); the newest name wins |

## 6. Data shape

### 6.1 game.json (Letter Station)

```json
{
  "mechanic": "letter-find",
  "session": { "maxQuestions": 10, "maxSeconds": 180 },
  "adapt": { "upAfterCorrect": 2, "downAfterWrong": 2 },
  "reward": { "type": "train" },
  "letters": {
    "A": { "word": "apple" }, "B": { "word": "ball" }, "M": { "word": "moon" }, "Z": { "word": "zebra", "say": "zee" }
  },
  "strings": { "findTask": "Find {name}!", "findNot": "That's {name}.", "findCard": "It looks like this!",
               "findFound": "{name}! {name} is for {word}.", "hear": "Hear it again", "train": "Your train is growing!",
               "trainTitle": "My train" },
  "levels": [
    { "id": "three", "difficulty": 1, "generator": { "type": "letter", "pool": "ABCDEMOS" },
      "find": { "letters": 3, "layout": "row" } },
    { "id": "five", "difficulty": 2, "generator": { "type": "letter", "pool": "ABCDEMOSFGHIPT" },
      "find": { "letters": 5, "layout": "row" } },
    { "id": "six", "difficulty": 3, "generator": { "type": "letter", "pool": "ABCDEMOSFGHIPTKLNRUW" },
      "find": { "letters": 6, "layout": "pile", "nameAlikes": true } },
    { "id": "eight", "difficulty": 4, "generator": { "type": "letter", "pool": "ABCDEFGHIJKLMNOPQRSTUVWXYZ" },
      "find": { "letters": 8, "layout": "pile", "nameAlikes": true, "lookAlikes": true } }
  ]
}
```

Notes on the data:
- **Item ids are `uc-m`**, "find the uppercase letter M", in every level (stable forever, GAME_RULES 17). Answer `"M"`.
  A missed `uc-w` comes back as practice at any level whose pool holds W (the existing `itemFitsLevel` path). Lowercase
  later uses `lc-m` in its own game (decision 15), so ids never change meaning.
- **Pools** (decision 8): level 1 is 8 common, mostly distinct capitals (A B C D E M O S); level 2 adds F G H I P T;
  level 3 adds K L N R U W; level 4 adds J Q V X Y Z. Targets and rivals both come from the pool. The generator prefers
  letters not used yet this session (same rule as the count generator), so 10 rounds rarely repeat a letter.
- **`letters`**: one entry per letter used in any pool. `word` is the car's object (the picture comes from the skin),
  `say` (optional) is how the voice spells the name when the plain letter is read badly. The bubble never shows it.
- **`reward: { "type": "train" }`**: no cycle list. The car is the letter just solved, so the reward is fixed by what the
  child did, never random.

### 6.2 types.ts (additive, mirrors the existing style)

```ts
// 'letter-find' (v0.7.0) is the hear-a-name, tap-the-letter mechanic (Letter Station).
export type Mechanic = ... | 'tap-count' | 'letter-find';
/** v0.7.0 adds name-alike: a letter whose name sounds like the target's (D for B). Letter games only. */
export type LetterMistake = 'letter-order' | 'wrong-vowel' | 'look-alike' | 'wrong-letter' | 'name-alike';

/** v0.7.0: "find letter X" items. Ids uc-a ... uc-z, answer "A" ... "Z". pool: uppercase letters, no repeats. */
export interface LetterGenerator { type: 'letter'; pool: string }
export type Generator = ArithmeticGenerator | CountGenerator | LetterGenerator;

/** Level form for letter-find. */
export interface FindLevel {
  /** Letters on the board, 3 to 8 (the target plus rivals). */
  letters: number;
  /** row (letters <= 5), rows, or pile (letters <= 10): the tap-count planner. */
  layout: TapLayout;
  /** Sound-alike names allowed as rivals. Default false. */
  nameAlikes?: boolean;
  /** One planned look-alike of the target when the pool has one. Default false (no look-alikes anywhere on the board). */
  lookAlikes?: boolean;
}

/** Spoken name and car word per letter. */
export interface LetterInfo { word: string; say?: string }

/** One letter on a planned board: a tap-count position plus its letter. */
export interface FindObject extends TapObject { letter: string }

/** A planned round: what the letter-find screen receives. */
export interface FindPlan {
  target: string;
  /** Object id of the target. */
  answer: number;
  layout: TapLayout;
  /** Reading order, ids 0..n-1 (also the Tab order). */
  objects: FindObject[];
  /** Planned kind per rival letter. */
  mistakes: Record<string, LetterMistake>;
  /** Rival object ids in the order the narrow rung prefers to keep them (look-alike, name-alike, others). */
  keep: number[];
}

/** v0.7.0: the alphabet train. One car per solved round, the car is the solved letter. Stored by the website. */
export interface TrainRewardDef { type: 'train' }
/** HostInit.train: letters on the child's train, oldest first, newest 64 at most. */
export interface TrainView { cars: string[] }
/** v0.7.0: a train car fact. Repeats of a letter are normal; the website dedupes by id. */
export interface CarReward { id: string; kind: 'car'; letter: string; at: string; species?: never }
SessionRecord.rewards?: (Reward | WordReward | PatchReward | AnimalReward | CarReward)[];
ResolveOutcome.reward: ... | { kind: 'car'; letter: string };

Level.find?: FindLevel;                 // letter-find only
GameDef.letters?: Record<string, LetterInfo>;  // letter-find only

/** v0.7.0: a letter-find game definition. */
export interface FindGameDef extends Omit<GameDef, 'reward'> { reward?: TrainRewardDef; letters: Record<string, LetterInfo> }

// GameStrings (v0.7.0 letter-find lines; {name} the spoken letter name, {word} the car word)
findTask?, findNot?, findCard?, findFound?, train?, trainTitle?   // hear? already exists (slot-build)
```

*Risk in widening `Generator` again:* `content.ts` branches on `g.type === 'count'` and then reads `g.a`; each of
`generate`, `itemFitsLevel` and `itemFromId` gets a `letter` branch first. Game repos never touch `Generator`.

*Why `letter` is uppercase in the reward:* the car shows the letter the child found. Lowercase cars (a later game) are
then different facts, which is honest.

### 6.3 Message contract (protocol stays 1)

- `GameCompleted.session.rewards` gets `{ id: "<session id>-<question index>", kind: "car", letter: "M", at }` per
  solved round, first try or not (effort is rewarded, as with the garden, quilt and parade).
- `HostInit.train = { cars: ["B", "M", ...] }`, newest 64, oldest first, sent only when the catalog reward is `"train"`.
- Unknown fields are ignored on both sides, so a v0.7.0 game on today's website plays fine and its cars are dropped by
  `validRewards`, with no error.

## 7. Planners (pure, `src/find.ts`)

### 7.1 Positions: the tap-count planner, unchanged

`planObjects(letters, level.layout, seed)` from `src/tap.ts`, so every board inherits its proof: hit circles 104 scene
px (65 px on a 667 x 375 phone), centres at least 112 apart, all inside `TAP_AREA`, deterministic per seed. The screen
uses `rot` only on the carrier, scaled by 0.3 (so at most about 8 degrees), and never on the glyph (F9). `scale` (0.9 to
1.05 in a pile) sizes carrier and glyph together, which gives the "mixed sizes" of the draft's level 3 without letting a
glyph get too small (section 12).

Seed: `hashSeed(sessionId + '|' + index)` like tap-count and pair-match, so boards change every session (a remembered
board would reward memory, not letters).

### 7.2 Letters: `planFind(item, level, seed): FindPlan`

Tables (uppercase, symmetric; a test proves the symmetry):

```ts
const LOOK_UC: Record<string, string> = {
  M: 'WN', W: 'MV', N: 'MZ', Z: 'N', E: 'F', F: 'E', O: 'QCD', Q: 'O', C: 'GO', G: 'C', D: 'O',
  P: 'RB', R: 'PB', B: 'PR', U: 'V', V: 'UWY', Y: 'V', I: 'LT', L: 'I', T: 'I', K: 'X', X: 'K',
};
/** Letter names that rhyme or share a sound: "bee dee pee", "em en", "ay jay kay", "eye why", "you cue double-you". */
const NAME_GROUPS = ['BCDEGPTVZ', 'AJK', 'FLMNSX', 'IY', 'QUW'];
```

Algorithm:
1. Board starts with the target.
2. `lookAlikes` level: add one look-alike of the target from the pool (seeded pick) when one exists.
3. Fill from the shuffled pool. A rival is allowed when it is not on the board yet, and (below `lookAlikes`) it is not a
   look-alike of **any** letter already on the board (so E and F never sit together at level 2 even when the target is
   A), and (below `nameAlikes`) its name does not rhyme with the target's.
4. Positions from 7.1. The answer slot is a seeded uniform pick; rivals are shuffled into the other slots. If the reading
   order holds a run of 3 alphabet neighbours (L M N) or, with 4 or more letters, is fully alphabetical, reshuffle the
   rivals (at most 12 tries; the prototype never needed the fallback).
5. Mistake kind per rival: `look-alike` if in `LOOK_UC` of the target, else `name-alike` if in its name group, else
   `wrong-letter`. `keep` lists rivals look-alike first, then name-alike, then the rest in seeded order.
6. If step 3 runs out of rivals, the plan is still made with what fits and a validator rule makes that impossible for
   any shipped pool (section 12): the planner never breaks the look-alike rule to fill a board.

Verified in the prototype (section header): 0 failures, 0 song cues, uniform answer position, a look-alike present on
every top-level board that could have one.

`nextCar` is not needed: the car is the solved letter.

## 8. Reducer (`src/find.ts`)

```ts
export const FIND_IDLE_MS = 7000;
export type FindPhase = 'find' | 'complete';

export interface FindState {
  readonly plan: FindPlan;
  readonly phase: FindPhase;
  /** Wrong object ids, in tap order. */
  readonly wrong: readonly number[];
  /** Object ids dimmed by the ladder (wrong taps plus narrow and last). */
  readonly dimmed: readonly number[];
  readonly card: boolean;
  /** Costed hints: Card, plus each wrong tap. Feeds SessionRecord.hints. */
  readonly hints: number;
  /** Each kind at most once per round (a spam tapper is not five mistakes). */
  readonly mistakes: readonly LetterMistake[];
  readonly idleMs: number;
  readonly idleHints: number;
}

export type FindAction =
  | { type: 'pick'; object: number }        // tap, click, Enter or Space on a parcel
  | { type: 'key'; letter: string }         // a letter key: becomes pick of that parcel, or 'absent'
  | { type: 'hear' }                        // tap the bubble or the fox: free repeat
  | { type: 'help' }                        // tap Hazel: the letter card
  | { type: 'tick'; ms: number };

export type FindEffect =
  | { type: 'found'; object: number }                                  // hop, note letterPitch, glow
  | { type: 'not-it'; object: number; letter: string; mistake: LetterMistake }  // dim it, say its name
  | { type: 'narrow'; dim: number[] }                                  // 2nd wrong: two left
  | { type: 'last'; dim: number[] }                                    // 3rd wrong: one left
  | { type: 'again'; object: number }                                  // tap on a dimmed parcel: neutral
  | { type: 'absent'; letter: string }                                 // key for a letter not on the board
  | { type: 'request'; replay: boolean; shimmer: boolean }             // "Find M!" (hear: no shimmer; idle: shimmer)
  | { type: 'card' }
  | { type: 'complete'; outcome: FindOutcome };

export interface FindOutcome {
  /** No card and no wrong tap. */
  firstTry: boolean;
  /** Not first try, and the narrow rung was not needed (at most 1 wrong tap). Ends the up streak, never moves down. */
  steady: boolean;
  hints: number;
  mistakes: LetterMistake[];
}
```

| Action | Rule | Effects |
|---|---|---|
| `pick` | Ignored after complete or for an unknown id. A dimmed id: `again`. The answer: complete. Else wrong: push to `wrong`, dim it, hints + 1, its kind once per round; 2nd wrong also dims all but the answer and the first lit id in `keep`; 3rd wrong dims every rival | `found` + `complete`; or `not-it` (+ `narrow` or `last`) |
| `key` | Case-insensitive A to Z. A letter on the board becomes `pick` of that id; any other key: `absent` (no state change) | as `pick`, or `absent` |
| `hear` | Free at any time before complete; resets idle | `request { replay: true, shimmer: false }` |
| `help` | First time: `card: true`, hints + 1. Again: free repeat of the card line | `card` |
| `tick` | 7 s idle: `request { replay, shimmer: true }`, at most 2 in a row, any input resets. Time never costs | as said |

`replayFind(plan, actions)` runs a list of actions (tests prove tap, Enter and the letter key give the same state).

## 9. Session length, adapt and mastery

| Item | Value | Why |
|---|---|---|
| `maxQuestions` | 10 (validator 5 to 15) | 10 rounds of about 12 s plus beats is about 2.5 to 3 minutes; 85 percent of 10 allows one slip (F11) |
| `maxSeconds` | 180 (validator 60 to 300) | GAME_RULES 1 |
| `upAfterCorrect` | 2 (validator: 2 or more outside pair-match) | Owner pick; a strong child reaches level 4 at round 6 and plays 4 rounds there |
| `downAfterWrong` | 2 | Two rounds in a row that needed the narrow rung (F16, Hedgehog 7(b)); a 1-miss round is `steady` |
| Start level | Website: one below the highest reached last time (existing `startLevel`) | Warm-up success |
| Practice | Missed `uc-*` ids, every 3rd round when they fit the pool (existing session rule) | Look-alike letters come back |
| Getting it | A session at difficulty 3 or more with 80 percent first try (existing rule): 8 of 10 | unchanged |
| Mastered | 2 sessions on different days at difficulty 4 with 85 percent first try: 9 of 10, at 8-letter boards with a planned look-alike | Honest only after the F12 fix (decision 12) |
| `skills.json` | `language.letters.letter-recognition`, `topDifficulty` 4 | Section 14 |

Verified with the real `Session`: 10 first-try rounds from level 1 play levels 1,1,2,2,3,3,4,4,4,4.

## 10. Rewards: the alphabet train (website owned)

- One car per solved round, first try or not. The car carries the solved letter and the skin's picture for
  `letters[L].word` (B and a ball). Repeats are normal: two M cars means M was found twice.
- In the scene: the bottom strip shows the newest 8 cars coupled behind a small engine (fill's shelf element, hidden while
  a round is open, as the parade strip is). The new car rolls in from the right (fades in place with reduced motion).
- End screen: up to 16 newest cars, this session's marked new, line `strings.train`.
- Growth by rounds solved, never by time; nothing ever leaves the train; no streaks.
- Car pictures (26 small SVG symbols) load in an `import()` chunk started at Play and awaited before the first car rolls
  in; until it lands (or offline) a car shows the letter alone (F17, decision 17).

## 11. Sound and voice

| Moment | Sound | Visual twin (for muted play) |
|---|---|---|
| Request | voice "Find M!" | speaker icon pulses in the bubble; the fox's beak moves |
| Right tap | `audio.tone(letterPitch("m"))`, voice "M! M is for moon.", rising run, `chord` | hop, glow, happy fox, confetti, car rolls in |
| Wrong tap | `audio.tap()` (soft click), voice "That's W." | the parcel dims, Hazel tilts her head |
| Narrow, last | voice "Find M!" | rivals dim |
| Card | voice "It looks like this!" | the fox holds up the letter card |
| Idle | voice "Find M!" | all letters shimmer once, the fox bobs |
| Re-tap of a dimmed parcel | `audio.tap()` | ring pulse |

- **Voice first** (section 5.4). Every hint line is awaited (`Promise.race` with a cap) before any tone.
- **Spoken names come from data** (`letters[L].say ?? L`), so a bad synthetic reading is fixed in JSON, and the
  `skin.say` hook plays recorded voice later with no kit change.
- **Muted play** (`settings.audio` false): the child cannot hear the request, so the card shows from the start of each
  round. Decision 3 says how that round counts.

## 12. Sizes, input and accessibility

- **Targets:** parcels 104 scene px round buttons (65 px on a 667 x 375 phone), the bubble's speaker 104, Hazel as today.
- **Glyph:** Andika (style guide: built for early readers), cap height 60 scene px at scale 1 (37 px on a 667 x 375
  phone, 54 to 63 scene px across pile scales). Ink colour on a light parcel face (8:1 or better), never white on a
  bright colour. A 60 x 55 glyph box has a diagonal of about 81 px, so it fits inside the 96 px art circle.
- **Keyboard:** parcels are buttons in reading order (Tab walks top to bottom, left to right), Enter or Space picks,
  letter keys pick by value (decision 13), digits do nothing. Focus moves only on key input (fill's rule). Tab also
  reaches the speaker and Hazel.
- **Screen reader:** a parcel is "letter M" (the name is the content, not the answer: every parcel says its own); the
  polite live region says the request "Find M", "That's W", and the found line.
- **Reduced motion:** pop-in becomes fade, hop becomes glow (opacity), shimmer is opacity only, the car fades in place,
  confetti off. Transform and opacity only everywhere.
- **Upright phones:** the existing rotate prompt.

Validator rules (build time only):
- `mechanic: "letter-find"`: `letters` maps each uppercase letter used by any pool to `{ word, say? }`; `letters` is
  refused for every other mechanic.
- Each level has a `find` block and a `letter` generator (no hand-written items): `letters` 3 to 8, `row` needs
  letters <= 5, `pile` and `rows` <= 10; `pool` is 3 or more distinct uppercase letters; `lookAlikes` and `nameAlikes`
  booleans; for every target in the pool the pool must hold at least `letters - 1` legal rivals under that level's rules
  (the check the prototype ran, done exactly at build time).
- `generator.type: "letter"` and `find` blocks are refused outside letter-find.
- `reward` is `{ "type": "train" }`, refused for every other mechanic.
- `upAfterCorrect` 2 or more, `maxQuestions` 5 to 15 (unchanged rules).

## 13. Size and budget

Budgets: Entry JS 30 KB, Before Play 100 KB (firm), kit near 15 KB (about 18 KB accepted).

| Page | JS brotli | Source |
|---|---|---|
| Quiz page | 9.7 KB | measured (v0.6.1) |
| Quiz page plus `planObjects` only | 10.2 KB | measured |
| tap-count page, no skin, no fill player | 15.8 KB | measured |
| Hedgehog playground (entry + lazy fill) | 18.3 + 7.6 KB | measured |
| `find.ts` (planner tables, reducer) | about 1.2 KB | estimate |
| letter-find screen and train strip | about 3.4 KB | estimate (tap screen is about 6.1 KB with the scene; find has no badge, recounts, bell, fill loader or digit keys) |
| fill-common scene (shared) | about 1 KB | estimate, from the tap page minus the tap code |
| **Letter page entry JS, no art** | **about 15 to 16.5 KB** | estimate |
| Game art in the entry (fox two poses, station backdrop, parcel, engine and car frame) | about 3 to 5 KB | estimate |
| **Letter Station entry JS** | **about 19 to 21 KB of 30** | estimate |
| CSS (base + fill + tap + find) | about 5.5 KB | estimate (tap page CSS measured 5.0 KB) |
| Fonts (Fredoka, Andika, already loaded) | 34.9 KB | measured, no change |
| **Before Play** | **about 60 to 63 KB of 100** | estimate |
| Car pictures chunk (26 symbols) | about 5 to 9 KB, Lazy JS, After Play | estimate |

Other games do not change size (new mechanic, tree shaken). A find mode inside tap-count would put a letter page at
about 20 KB before art and add about 4 to 5 KB to Hedgehog Picnic (estimate, section 4).

## 14. Website (one paragraph)

The website adds, the same way as the parade (playbook section 13): a catalog entry (`mechanic` `letter-find`, `reward`
`"train"`, game id `letter-tap-prek`, page `/language-games/letter-recognition-for-preschool/`); `skills.json` gets
`language.letters.letter-recognition` with `topDifficulty` 4 (it is not in the list today); a store section
`trains[profile][game] = { "v": 1, "cars": [{ "id": "s_x81ka2-0", "letter": "M", "at": "...", "session": "s_x81ka2" }], "folded": 0 }`
with the quilt and parade rules (own `v`, newer-`v` guard, facts only, deduped by reward `id`, never more cars than
questions in a session, at most 200 per child per game with the oldest folded into `folded`, profile deletion deletes
it); `validRewards` accepts `kind: "car"` with `letter` matching `/^[A-Z]$/`; `player.ts` sends `HostInit.train = { cars }`
(newest 64, oldest first) only when the catalog reward is `"train"`; parent tips for `language.letters.*` skills: a
capital-letter `look-alike` tip ("Sometimes mixes up letters that look alike, like E and F. Trace the letter with a
finger and count its lines together."), a new `name-alike` tip ("Sometimes mixes up letters whose names sound alike,
like B and D. Say the name slowly and look at the shape together."), and `wrong-letter`; privacy text names the train.
Protocol stays 1. A parent "My train" page is later work.

## 15. Implementation steps (in order, test after each)

Work from kit commit `256bea1` (branch `claude/amazing-albattani-g2r7l1`), not the stale checkout. Kit CLAUDE.md: do not
commit or push unless the owner asks (or the implementation prompt says so).

| # | Step | Files | Rough size |
|---|---|---|---|
| 0 | (Decision 12) `maxDifficulty` counts levels played, own patch v0.6.2, README note, golden diff reviewed | `src/session.ts`, `tests/session.test.ts` | 5 lines + 3 tests |
| 1 | Types and spec mirror | `src/types.ts`, main repo `planning/framework-spec.md` | 90 lines |
| 2 | Letter generator: `generate`, `itemFromId` (`uc-m`), `itemFitsLevel`, tests | `src/content.ts`, `tests/content.test.ts` | 35 lines + 10 tests |
| 3 | Tables, `planFind`, tests first (symmetry, no look-alikes below top, name-alikes only when allowed, look-alike present at top, no song cue, uniform answer position, deterministic, never relaxes) | `src/find.ts`, `tests/find.test.ts` | 120 lines + 20 tests |
| 4 | Reducer `initFind`, `reduceFind`, `replayFind`, `outcomeOfFind`, tests first | `src/find.ts`, `tests/find.test.ts` | 150 lines + 30 tests |
| 5 | Session: `letter-find` in `noChoices`, `car` reward kind; golden files unchanged | `src/session.ts` | 10 lines + 5 tests |
| 6 | Host `HostInit.train`; `audio.say` volume option (F19) | `src/host.ts`, `src/audio.ts` | 10 lines |
| 7 | Validator rules (section 12) | `build/validate.mjs`, `tests/validate.test.ts` | 70 lines + 15 tests |
| 8 | Screen and CSS: `letterFind`, `FindSkin extends FillSkin` (fields below), train strip, end train, car picture loader | `src/mechanics/letter-find.ts`, `src/styles/find.css`, `src/index.ts`, `package.json` exports | 380 lines + 100 CSS |
| 9 | Playground: plain skin, placeholder parcels and cars, `dev/find.html`, `vite.config.ts` page | `dev/` | 120 lines |
| 10 | Browser checks (section 17) | `tests/find-e2e.cjs`, `package.json` `test:e2e` | 400 lines |
| 11 | Measure sizes (each page alone), README, version 0.7.0, then ask before pushing | `README.md`, `package.json` | |

`FindSkin` fields (all optional; without a skin the kit draws plain round tags with the letter, no fox, plain cars):
`tapBackdrop` (reuse the name), `customers` (the fox, with `happy`), `parcels` (one or more carrier symbols, picked by
`pictureFor` and the object id), `card` (the fox's card art), `engine`, `car` (car frame symbol), `pictures` (a loader
`() => Promise<Record<word, symbolSvg>>`, the lazy chunk), `say(text)` (recorded voice hook).

## 16. Owner decisions

Default = my recommendation, except where it differs from an explicit owner pick; then the default is the owner's pick
and the recommendation is noted.

1. **Mechanic.** (a) New `letter-find` mechanic that imports `planObjects` and the scene helpers. (b) A find mode inside
   tap-count. *Recommend (a); default (a)* (also the owner's lean). Evidence in section 4.
2. **How the request shows (F2).** (a) Spoken only, speaker icon in the bubble, the letter card is a costed hint.
   (b) The letter in the bubble from the start. *Recommend (a); default (a).* (b) turns the game into shape matching.
3. **Muted play.** (a) The card shows from the start and the round costs one hint (honest: first try means "from the
   name"). (b) The card shows from the start and first try still counts (kinder stars, but a muted child can earn
   Mastered by matching). *Recommend (a); default (a).* The end screen still gives at least one star and praise.
4. **Hint ladder (F3).** (a) Dim, narrow to two, last. (b) The draft: dim, then after two misses every other letter
   dims. *Recommend (a); default (a).*
5. **Idle hint (F1).** (a) Repeat the request and shimmer every letter. (b) The draft: the target twinkles.
   *Recommend (a); default (a).* (b) gives the answer for waiting.
6. **Wrong-tap voice.** (a) "That's W." then "Find M!" again. (b) The name only. *Recommend (a); default (a).*
7. **Found line (F4).** (a) "M! M is for moon." (b) Name, sound and word (needs recorded voice; overlaps MVP 11).
   *Recommend (a); default (a).*
8. **Letter pools (F7).** (a) Distinctness bands: ABCDEMOS, + FGHIPT, + KLNRUW, + JQVXYZ. (b) The draft's alphabetical
   bands. *Recommend (a); default (b) is the owner's draft, so I need a yes.* It is data only either way.
9. **Level ladder.** 3 letters in a row, 5 in a row, 6 in a pile with name-alikes, 8 in a pile with name-alikes and one
   planned look-alike. *Recommend and default these.*
10. **Rounds (F11).** (a) 10 rounds, 180 s. (b) The draft's 6. *Recommend (a); default (b) is the owner's draft, so I
    need a yes.* With 6, Mastered needs a perfect session.
11. **Moving down (F16).** (a) Down after 2 rounds in a row that reached the narrow rung (Hedgehog 7(b)). (b) Never.
    *Recommend (a); default (b) is the owner's draft, so I need a yes.*
12. **Mastery on levels reached but not played (F12).** (a) Kit patch v0.6.2 (`maxDifficulty` counts levels asked),
    before v0.7.0, so Hedgehog Picnic can take it alone. (b) Inside v0.7.0. (c) Leave it. *Recommend (a); default (a).*
13. **Keys (F15).** (a) Letter keys pick by value, digits ignored. (b) Tab and Enter only. *Recommend (a); default (a).*
    It differs from GAME_RULES 3 wording (number keys 1 to 4), like tap-count decision 10.
14. **Z: "zee" or "zed" (F5).** One spelling in `letters.Z.say`. *Recommend "zee"* because most alphabet songs that Pre-K
    children know rhyme on "zee"; "zed" if the owner wants Indian and British usage. *Default "zee"; owner call.*
15. **Lowercase (F13).** (a) Its own skill and game page later, same mechanic, ids `lc-*`. (b) New levels in this game.
    *Recommend (a); default (a).*
16. **Name-alike mistake kind (F14).** (a) New `name-alike` kind with its own parent tip. (b) Fold into `wrong-letter`.
    *Recommend (a); default (a).*
17. **Car pictures (F17).** (a) Lazy `import()` chunk, the car shows the letter alone until it lands. (b) In the entry
    JS. *Recommend (a); default (a).*
18. **Carriers and scene art (F9).** One flat parcel shape in varied colours, no letters, numerals or letter-shaped
    props anywhere in the station. *Recommend and default; checked in the art preview.*
19. **Reward words (F18).** One picturable word per letter with a plain first letter and its common first sound; X is
    "box". *Art preview question; default list in the preview.*
20. **Title.** Letter Station (owner default). No change recommended.

## 17. Test plan

**Unit (`tests/find.test.ts`, plus content, session and validator tests)**
- Tables: `LOOK_UC` symmetric; every name group letter maps back to its group.
- Planner, every level of the shipped ladder, every target, 2000 seeds: letters distinct, target exactly once, no
  look-alike pair below `lookAlikes`, no name-alike of the target below `nameAlikes`, a look-alike present at the top
  when the pool has one, no song cue, answer position within 3 points of uniform, positions equal `planObjects` for the
  same seed, deterministic per seed, `keep` order look-alike first.
- Reducer: right on first tap completes with first try; wrong 1 dims and records once; wrong 2 leaves exactly two lit
  (answer plus the first lit `keep`); wrong 3 leaves one; a dimmed tap gives `again` with no state change; a key equals a
  pick; an absent key changes nothing; `hear` never costs; `help` costs once; idle at 7 s, at most 2 in a row, any input
  resets, time never costs; spam taps record each kind once; outcome first try, steady and miss as in section 8;
  replay equals step by step.
- Content: `uc-m` round trips through `itemFromId`, fits the right pools, the generator prefers fresh letters.
- Session: no session choices, `car` rewards in the record with the solved letter, steady never moves down; every
  existing test and the golden files unchanged (except the reviewed v0.6.2 diff, if decision 12(a)).
- Validator: every rule in section 12; the pool check rejects a pool too small for its rules; the playground passes.

**Browser (`tests/find-e2e.cjs`), throttled profile: 4x CPU, about 1.6 Mbps, 150 ms. Tap Play first.**
- The letter page bundle has no drag code and no counting code (no `recount`, no badge class).
- Every parcel at least 64 px at 667 x 375; glyph cap height at least 36 px there; no glyph rotated (computed transform).
- The request is never shown as text on screen before the card hint (no element in the scene holds the target letter
  except its own parcel).
- Ladder: wrong 1 dims one and speaks its name (fake `speechSynthesis` records "That's W."), wrong 2 leaves two, wrong 3
  leaves one; no red, no buzzer, no `tryAgain` call on a wrong tap.
- Voice before tones: with a 2.5 s fake voice line, no tone starts during a hint line; on a right tap the note comes
  before the found line.
- Keyboard: Tab order is reading order, Enter picks, a letter key picks, a digit does nothing.
- Muted: a full session with audio off shows the card each round and finishes; every step shows its visual twin.
- Session: 10 rounds, climb 1 to 4 with 2 right in a row each, record has levels, hints, mistakes by kind, 10 car rewards
  with the right letters, end-screen train; the car pictures chunk blocked (offline): cars show the letter, no error.
- Reduced motion: no transform animations. Upright phone: rotate prompt.
- Scene at 667 x 375 and 960 x 600: back button, fox, bubble and Hazel never overlap a parcel.

**Lesson to apply:** a check that silently skips proves nothing. Every new check prints one "ok" line, the script ends
with the count of ok lines, and the run is read for that count. Long browser runs go in the background with an
until-loop on the final line (grep the real final line, not "Error", which matches "GameError").

## 18. What a game must implement

```ts
import '@edulearnlabs/kit/styles.css';
import '@edulearnlabs/kit/fill.css';
import '@edulearnlabs/kit/tap.css';
import '@edulearnlabs/kit/find.css';
import { startGame, letterFind, type GameDef } from '@edulearnlabs/kit';
import def from '../game.json';
import { skin } from './skin';   // a FindSkin: fox, parcels, card, engine and car, backdrop, lazy pictures, optional voice
void startGame(def as unknown as GameDef, { mechanics: { 'letter-find': letterFind }, skin });
```

## 19. Risks

1. **Speech synthesis of single letters** on real devices (F5): the `say` field fixes spelling, but a voice may still
   blur B, D and P. Real-device check on a Chromebook and a phone before release; recorded voice is the real fix.
2. **The F12 fix changes session records** for every game that upgrades. Small and correct, but it needs its own
   release note and a reviewed golden diff.
3. **Muted play** (decision 3) gives muted children low stars by design; watch for owner or parent feedback.
4. **Art can break the planner's promise** (letters in the backdrop, letter-shaped props, tilted glyphs). The art preview
   must be checked against F9 in screenshots at 667 x 375.
5. **The website must add `train`** (HostInit and store) and the skill; until then cars are dropped silently.
