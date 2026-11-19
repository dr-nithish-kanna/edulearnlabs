# tap-count: kit design for Hedgehog Picnic (kit v0.5.0 to v0.6.0)

Status: DESIGN ONLY, 2026-11-15. Opus design pass for the mechanic asked for in `planning/count-objects-design.md`
section 4. Nothing is built. The owner reviews section 13 (owner decisions) and section 1 (flaws found in the plan)
before a Sonnet or Opus agent implements it from section 12.

Files read for this design: main repo `CLAUDE.md`, `planning/game-playbook.md`, `planning/count-objects-design.md`,
`planning/pair-match-design.md`, `planning/slot-build-design.md`, `planning/framework-spec.md`, `planning/decisions.md`,
`planning/style-guide.md`, `templates/game-repo/GAME_RULES.md`, `src/scripts/progress.ts` (quilt store); kit v0.5.0 at
commit `03ced46` (read in a throwaway worktree, the session checkout is stale at v0.1.0): `src/types.ts`, `src/session.ts`,
`src/content.ts`, `src/game.ts`, `src/index.ts`, `src/host.ts`, `src/pitch.ts`, `src/audio.ts`, `src/random.ts`,
`src/strings.ts`, `src/fill.ts`, `src/pair.ts`, `src/mechanics/quiz.ts`, `src/mechanics/common.ts`,
`src/mechanics/fill-common.ts`, `src/mechanics/fill-container.ts`, `src/mechanics/pair-match.ts`, `src/styles/fill.css`,
`build/validate.mjs`, `build/check-size.mjs`, `README.md`, `package.json`.

What I verified, not only read: a throwaway prototype of the pile planner (section 5.3) placed 4 to 10 objects for
5000 seeds each (35 000 plans): no object outside the play area, smallest centre distance exactly 112 scene px (the
rule), every hit target 65 px on a 667 x 375 phone. I did not build the kit (no `node_modules` in the worktree), so
every size in section 10 is an estimate from the measured v0.5.0 table, not a measurement.

## 0. The big idea in six lines

1. **Each tap is one number.** A tap on an uncounted object makes it hop, plays the next note and shows the next
   number in a single badge on top. The count follows the child's own order, because the number belongs to the tap,
   not to the object.
2. **The game cannot count wrong, so the test is cardinality.** Tapping can never skip or double count (the
   mechanic guards it), so "How many?" is the real question: the badge fades first, and the child must remember the
   last number said. That is exactly the micro-skill.
3. **Rules are a pure reducer** (`src/tap.ts`), like `fill.ts`, `slot.ts` and `pair.ts`: tap, click and keys send the
   same `count` action, and every rule is tested without a browser.
4. **Layouts and choices are planned, not random**: a row, two rows of five, or a scatter from a seeded planner
   that can never hide an object; choices are a window of neighbouring numbers that always holds an off-by-one, never
   repeats, never shows 0, and moves the answer between left, middle and right.
5. **One game, two mechanics, no registry change**: the tap-count runner owns the session loop and hands "give me N"
   levels to the fill-container order player, loaded only when the child gets near that level.
6. **The parade is the website's.** The game reports `{ id, kind: "animal", animal, at }` per solved round and gets
   `HostInit.parade = { animals }` to draw it. The kit stores nothing. Protocol stays 1.

## 1. Flaws found in `count-objects-design.md` (look at these first)

The fill-container pass found one real flaw last time. This pass found four real ones (F1 to F4) and several smaller
conflicts with existing rules.

| # | Flaw | Why it matters | Proposed fix |
|---|---|---|---|
| F1 | **Level 4 "give me N" can be won without counting.** fill-container with goal `total` finishes by itself the moment the basket holds N (`goalMet` then `finishBuild` in `fill.ts`), and the item past N bounces back. | The child just drags until the game says stop. The skill of level 4 is *knowing when to stop*, and the game does it for them. Adding the How many? step does not help: the order bubble already shows the numeral N, so it would be a copy task. | New additive fill option `finish: "done"`: reaching N does not end the order, the child may put in more (up to the stock), and a Done bell judges it (section 6.3). Decision 1. |
| F2 | **Skipping can never happen, so level 3 cannot teach or measure it.** The plan says choices appear only after every object is counted. On a messy pile a child who misses one apple just sees nothing happen. | Level 3 exists "so skipping is easy", but the error is silently blocked, the child may feel stuck, and the parent never learns "skips objects in a pile". | Always: an idle "find the rest" hint (uncounted objects twinkle). Optional per level: `finish: "done"`, the child taps Done when they think they are finished, and Done with objects left counts as a `skipped` mistake. Decision 6. |
| F3 | **A visible last badge turns "How many?" into copying a numeral.** | If "7" is still on screen when the choices appear, the child matches the shape 7 to the button 7. That is numeral matching, not cardinality. | The badge fades before the choices appear (section 4.4). Decision 3. |
| F4 | **"Then a slow voiced recount ends on the total" after the first wrong choice says the answer.** | The last word of a recount *is* the answer. That conflicts with the playbook rule "hints only, never the answer" and with what fill-container does today (its How many? count-along lights the items with notes but speaks no numbers). | Ladder: 1st wrong, silent count-along (lights and notes, the child counts); 2nd wrong, the other wrong choices dim (only the answer is left, as in fill today) and a voiced recount models "the last number is how many". Decision 2. |
| F5 | "Three requests per session" | The validator requires `maxQuestions` 5 to 15, and with "up after 2 correct in a row" a 3 round session can climb at most once. | 6 rounds (2 per friend), `maxSeconds` 180. Decision 8. |
| F6 | The kit's count badge is 34 scene px (`.ell-count-badge`). | On a 667 x 375 phone that is 21 px with a 12.5 px numeral. The style guide asks for numbers of 64 to 96 px. | A tap-count badge of 84 scene px with a 60 px numeral (53 px and 38 px on that phone), drawn ON the counted object, not above it (section 4.4). |
| F7 | "Messy pile" | With 64 px targets on a phone (104 scene px) and "nothing may hide anything", a real heap is impossible: at most 11 objects fit the play area. | Be honest in the art preview: it is a *scatter*, not a heap. The planner (section 5.3) is proven to keep spacing. |
| F8 | "Tapping a counted object does nothing (no error, no sound)" | GAME_RULES 11 says "sound on every tap". A tap with no response at all also reads as "the game is broken" to a 4 year old. | A neutral answer: the soft UI tap click plus a ring pulse, never a number and never a count note. Decision 4. |
| F9 | Number keys 1 to 4 (GAME_RULES 3) | Keys are positional in quiz and fill: with choices 5, 6, 7, pressing "7" does nothing and pressing "3" picks 7. For number answers that is a trap. | Digit keys pick the choice with that value ("0" is 10). Decision 10. |
| F10 | One game, two mechanics | `GameDef.mechanic` is one value and `startGame` picks one runner that owns the whole session loop. Two mechanics in one game is not supported today. | Smallest change in section 6. No change to `game.ts`. |
| F11 | Size | tap-count plus fill-container plus art lands near the 30 KB "Game code (JS)" budget in `check-size.mjs`, and a lazy chunk is still counted as Before Play by that script. | Lazy-load the fill player and teach `check-size` which chunks load after Play (section 10). Decision 12. |
| F12 | Mastery | "Mastered" needs sessions at the *top* difficulty. If level 4 ships later, the top difficulty moves from 3 to 4 and a child marked Mastered drops back to Getting it. | Ship level 4 in the first release, or accept the step once. Part of decision 1. |

Checked and **not** a flaw: counting in any order does not break the voice recount, as long as the recount replays
the stored tap order (`state.order`). Each badge then lands on the same object the child gave that number to. A
recount in reading order would put "3" on a different apple than the child's "3", which is confusing, so the reducer
keeps the order and the screen never re-sorts it.

Can a child win by guessing? Spam-tapping every object is easy (that part is not the test). The test is How many?
with 3 choices: a guesser gets about 1 in 3 first try, so mostly 1 star and no level up after 2 in a row (1 in 9).
Good enough for Pre-K, and every miss teaches.

## 2. The skill and the errors to prevent

- Grade Pre-K, `math.counting.count-objects`, MVP number 1. One micro-skill: **count a set one object at a time, and
  know the last number said is the total** (one-to-one correspondence plus cardinality).
- Errors and how the design treats each:

| Error | What the child does | Design |
|---|---|---|
| Double count | Counts one apple twice | Prevented: a counted object never takes a second number (the re-tap is neutral). The ring shows it is done. |
| Skip | Misses an object, often in a pile | Taught: idle "find the rest" twinkle, and in `finish: "done"` levels it is a real, recorded mistake (`skipped`). |
| No cardinality | Counts "1, 2, ... 7" fine, then answers "How many?" by counting again or guessing | Measured: the badge fades before the choices, the first tap on How many? decides first try. |
| Stable order | Says numbers out of order | Modelled: the game says the number words in order on every tap; the child hears the sequence 6 rounds a session. |

*Why not let the child make double-count errors on purpose?* Because a tap that adds a second number to an apple
teaches the wrong thing out loud and in pictures. Preventing it and showing a ring is the "juicy but fair" choice: the
child sees "this one is done" every time.

## 3. Owner decisions taken as given (from count-objects-design.md)

Hedgehog, duck and mouse ask for apples, pebbles and acorns. Reward: parade of animals, one per solved round. Mechanic:
new `tap-count` for levels 1 to 3 plus existing `fill-container` for level 4. Advance after 2 correct in a row, never drop
below the current level on a miss. Speech synthesis voice now, recorded voice later. Upright phones get the rotate prompt.

## 4. Mechanic behaviour (what the child sees and hears)

### 4.1 One round

1. The friend arrives (fill's customer entrance), the objects pop in one after another (60 ms apart), the bubble shows
   the kind picture and "Count the apples!", spoken. Objects are tappable at once.
2. **Count phase.** Tap an uncounted object: it hops, a warm ring appears under it (stays), the single badge moves onto
   it with the next number, its note plays (`pitchFor(k)`, k = taps so far), the number word is spoken. The first tap
   stops the instruction voice so the note is never masked.
3. **All counted.** The last note rings, a 500 ms beat, the badge fades (F3), the friend asks "How many apples?"
   (voice first), then 3 number choices bounce into the bottom strip (where the parade strip was, same as fill's shelf).
4. **How many?** Right on the first tap: a soft pop on the button, the voice says "Seven apples!", then a quick rising
   run of notes 1 to n with each object lighting, then `chord(n)`. An animal walks into the parade. Praise line.
5. **Wrong** (hints only, section 4.3).

### 4.2 Rules

- Each object takes exactly one number, in tap order. The number belongs to the tap: the 1st tap is 1 on any object.
- A tap on a counted object is ignored by the reducer (no state change). The screen gives the neutral answer of
  decision 4 (soft click and ring pulse, no number, no count note).
- Taps on objects during How many? or after the round is solved do nothing.
- Nothing waits for animation: the count changes at the tap, so a fast tapper can never get two numbers for one tap.
- Never a red X, a buzzer, a failure screen, a timer or a counter of mistakes.

### 4.3 Hint ladder (hints only, never the answer first)

| Step | Trigger | What happens | Costs first try |
|---|---|---|---|
| Nudge | 8 s idle with nothing counted, at most 2 in a row | The task line again, the friend bobs | no |
| Find the rest | 6 s idle with some counted and some left, at most 2 in a row | Uncounted objects twinkle once (opacity), bubble "Did we count them all?" | no |
| Help (count phase) | Tap Hazel | Uncounted objects twinkle | yes (a hint) |
| Done too early | Done tapped with objects left (`finish: "done"` levels only) | Uncounted objects twinkle, the Done bell wobbles; `skipped` recorded once per round | yes |
| Count with me | 1st wrong choice, or Hazel tap during How many? | Wrong choice dims (stays visible, not tappable). Objects light one after another in the child's tap order, each with its note, no number words and no badges. Bubble "Count with me!" | yes |
| Show me | 2nd wrong choice | Every other wrong choice dims, so only the answer is left (fill does the same today). Voiced recount in tap order: badge plus number word plus note per object, ending on the total, then "How many apples?" again. The child taps the last button | yes |

*Why time alone never costs:* a 4 year old looks away. Fill uses the same rule ("time alone never goes past H1").

*Check against the playbook rule.* "Hints only, never the answer" holds until the 2nd wrong choice. After that, the
only button left is the answer, which is how fill-container already behaves, and the voiced recount turns that moment
into a cardinality lesson. The child still makes the final tap. *Flag:* the **quiz** mechanic still shows the answer
after a second miss ("It's {answer}! Now you know it.", `src/mechanics/quiz.ts`), which conflicts with framework-spec
section 3 and GAME_RULES 5. tap-count does not use the quiz runner, so it is not affected. Changing the quiz changes
live quiz games, so it stays a separate kit release (decision 14).

### 4.4 The badge (playbook lesson: one badge at a time in a top layer)

- One element for the whole round, in the top layer of the scene (`z-index` above every object), `pointer-events: none`
  so it never steals the next tap.
- 84 scene px circle, numeral 60 px Fredoka, sun yellow with a white rim (style guide). On a 667 x 375 phone: 53 px and
  38 px (F6).
- It sits **centred on the object just counted**, not above it. *Why:* above the object it would cover the object
  in the row above (rows are 112 px apart); on the object it covers only something already counted, whose ring still
  shows around the badge. So a crowded pile stays legible: there is only ever one number, and it never hides an
  uncounted object.
- It moves to the next object on the next tap (no fade between, so muted players always see the running count), and
  fades 500 ms after the last count, before How many? (F3).
- Counted objects keep a non-number mark: a warm ring under the object plus the skin's optional "counted" art. Never a
  green tick (a tick means "right", and counting is not right or wrong).

## 5. Data shape

### 5.1 game.json (Hedgehog Picnic)

```json
{
  "mechanic": "tap-count",
  "session": { "maxQuestions": 6, "maxSeconds": 180 },
  "adapt": { "upAfterCorrect": 2, "downAfterWrong": 2 },
  "reward": { "type": "parade", "animals": ["duckling", "bunny", "piglet", "lamb", "chick", "puppy"] },
  "friends": [
    { "id": "hedgehog", "kind": "apple" },
    { "id": "duck", "kind": "pebble" },
    { "id": "mouse", "kind": "acorn" }
  ],
  "kinds": { "apple": ["apple", "apples"], "pebble": ["pebble", "pebbles"], "acorn": ["acorn", "acorns"] },
  "strings": { "tapTask": "Count the {kinds}!", "tapAsk": "How many {kinds}?", "tapTotal": "{n} {kinds}!",
               "tapRest": "Did we count them all?", "tapAlong": "Count with me!", "give": "Give me {n} {kinds}, please!",
               "parade": "Your parade is growing!", "paradeTitle": "My parade" },
  "levels": [
    { "id": "row",   "difficulty": 1, "generator": { "type": "count", "n": [2, 5] },  "tap": { "layout": "row" } },
    { "id": "rows",  "difficulty": 2, "generator": { "type": "count", "n": [5, 10] }, "tap": { "layout": "rows" } },
    { "id": "pile",  "difficulty": 3, "generator": { "type": "count", "n": [4, 10] }, "tap": { "layout": "pile" } },
    { "id": "give",  "difficulty": 4, "generator": { "type": "count", "n": [3, 10] },
      "fill": { "variant": "basket", "goal": "total", "ask": "none", "spare": [2, 3], "finish": "done" } }
  ]
}
```

Notes on the data:
- **Item ids are `n-7`**, "the number 7", in every level, like a word id in slot-build. A missed `n-7` at level 3 can
  come back as practice at level 2 or as "give me 7" at level 4 (the existing `itemFitsLevel` rule: it fits when 7 is
  in the level's range). Answer `"7"`.
- **Ranges** differ from the draft ladder on purpose (decision 9): 1 object makes How many? trivial and pins the
  answer to the left button; level 2 is "more objects", so it starts at 5 (rows of 5 plus some more); a scatter of 2 is
  not messy.
- **`downAfterWrong` is ignored by tap-count** in the owner's "never drop" mode: every non-first-try round resolves as
  `steady` (the v0.5.0 outcome: ends the up streak, listed in `missed`, never moves down). No session change needed.
- **`friends`** cycle by question index (round 1 hedgehog, 2 duck, 3 mouse, 4 hedgehog ...). The skin's
  `customers` list draws them in the same order, so level 4 shows the same friend the cycle expects.

### 5.2 types.ts (additive, mirrors the existing style)

```ts
// 'tap-count' (v0.6.0) is the tap-each-object counting mechanic (Hedgehog Picnic).
export type Mechanic = ... | 'pair-match' | 'tap-count';
/** v0.6.0, tap-count with finish "done": Done was tapped while objects were still uncounted. At most once per round. */
export type CountMistake = 'skipped';
export type MistakeKind = DistractorKind | LetterMistake | CountMistake;

// ---- tap-count (v0.6.0). Everything below is optional, so other games are unaffected. ----

/** v0.6.0: "count N objects" items. Ids n-2 ... n-10, answer "2" ... "10". */
export interface CountGenerator { type: 'count'; n: [number, number] }
export type Generator = ArithmeticGenerator | CountGenerator;

export type TapLayout = 'row' | 'rows' | 'pile';

/** Level form: how every round at this level is laid out. */
export interface TapLevel {
  /** row: one row (n <= 5). rows: rows of 5, the second row left aligned (n <= 10). pile: a seeded scatter (n <= 10). */
  layout: TapLayout;
  /** How many? choices, 2 to 4. Default 3. */
  choices?: 2 | 3 | 4;
  /** auto: How many? appears when every object is counted. done: the child taps a Done bell. Default auto. */
  finish?: 'auto' | 'done';
}

/** A friend who asks for things to count. kind is a key of GameDef.kinds. */
export interface TapFriend { id: string; kind: string }

/** One object on a planned round. x, y: centre in scene px (960 x 600). rot and scale change the art only. */
export interface TapObject { id: number; x: number; y: number; rot: number; scale: number }

/** A planned round: what the tap-count screen receives. */
export interface TapPlan {
  n: number;
  kind: string;
  friend: string;
  layout: TapLayout;
  /** Reading order (top to bottom, then left to right), ids 0..n-1. This is also the Tab order. */
  objects: TapObject[];
  /** How many? choices, ascending, as strings. */
  choices: string[];
  /** Planned distractor kind per wrong choice. */
  mistakes: Record<string, DistractorKind>;
  answer: string;
  finish: 'auto' | 'done';
}

Level.tap?: TapLevel;                       // tap-count only
FillLevel.finish?: 'auto' | 'done';         // v0.6.0, fill add + total goal only (F1)
GameDef.friends?: TapFriend[];              // tap-count only

/** v0.6.0: the parade. One animal per solved round, in a fixed cycle. Stored by the website. */
export interface ParadeRewardDef { type: 'parade'; animals: string[] }
/** The parade the website shows the game (HostInit.parade). Animal slugs, oldest first. */
export interface ParadeView { animals: string[] }
/** v0.6.0: a parade fact. Repeats of an animal are normal; the website dedupes by id. */
export interface AnimalReward {
  id: string;
  kind: 'animal';
  animal: string;
  at: string;
  /** Never set. Declared so code written for garden rewards (r.species) still type checks. */
  species?: never;
}
SessionRecord.rewards?: (Reward | WordReward | PatchReward | AnimalReward)[];

/** v0.6.0: a tap-count game definition. Its reward is the parade and friends are required. */
export interface TapGameDef extends Omit<GameDef, 'reward'> { reward?: ParadeRewardDef; friends: TapFriend[] }

// GameStrings (v0.6.0 tap-count lines; {kinds} plural word, {n} number word)
tapTask?, tapAsk?, tapTotal?, tapRest?, tapAlong?, give?, done?, parade?, paradeTitle?
```

*Why the `tap` prefix on strings:* `count`, `ask` and `look` already mean fill's hint lines. New names avoid changing
what an existing key means in a live game.

*Risk in widening `Generator`:* `content.ts` reads `g.op` in `generate`, `fits` and `itemFitsLevel`; each needs a
`type` check first. Game repos never touch `Generator`, so no game breaks.

### 5.3 Planners (pure, `src/tap.ts`)

Scene constants (scene px; the scene is 960 x 600 and shrinks to scale 0.625 on a 667 x 375 phone):

| Constant | Value | Why |
|---|---|---|
| `TAP_AREA` | x 216, y 120, w 560, h 340 | Right of the friend (x 24 to 200), left of Hazel (x 788), below the back button (it covers to about y 112 on that phone), above the bottom strip (choices at y 472) |
| `TAP_HIT` | 104 (round button) | 104 x 0.625 = 65 px, at least 64 px on the smallest landscape phone (slot-build used the same number) |
| `TAP_ART` | at most 96 | Art inside the hit circle, so art never overlaps a neighbour's art |
| `TAP_MIN` | 112 centre to centre | 104 plus an 8 px gap: hit circles never touch, so a tap always lands on exactly one object and no object hides another |

Round buttons hit-test inside their `border-radius` in every current browser, which is why the distance rule is a
circle rule, not a square one.

`planObjects(n, layout, seed): TapObject[]`
- `row` (n <= 5): one row, pitch 112, centred in the area, rot 0, scale 1.
- `rows` (n <= 10): first row 5, second row the rest, **left aligned under the first** (so 7 reads "5 and 2 more",
  the ten-frame idea), rows 112 apart, the block centred.
- `pile` (n <= 10): 11 slots in 3 staggered rows (4, 3, 4) over the centre box x 268 to 724, y 172 to 408 (row pitch
  118, column pitch 152). Seeded shuffle picks n slots. Then 3 passes: each object tries up to 8 seeded nudges of 10 to
  40 px and keeps the first that stays inside and keeps 112 from every other. Art rotation -25 to 25 degrees, scale 0.9
  to 1.05. *Verified:* 35 000 plans (n 4 to 10, 5000 seeds each), 0 outside, minimum distance 112.0, average 1.5 or more
  nudges per object, so no pile looks like a grid. The fallback (no nudge fits) is the slot itself, which is always
  legal, so the planner can never fail or relax.
- Objects are then sorted into reading order (by row band of 56 px, then x) and numbered 0..n-1.

`planCountChoices(n, count, seed, max = 10): { choices, mistakes }`
- A window of `count` consecutive numbers that contains n, inside 1..max. With 3 choices the windows are
  [n-2, n], [n-1, n+1], [n, n+2]; the seed picks among the legal ones, so the answer is left, middle or right equally
  often (a naive "n-1, n, n+1" sorted row always puts the answer in the middle, which a child learns in 3 rounds).
- Ascending order (number-line order helps pre-readers; the moving window keeps it fair).
- Never 0, never a duplicate, always at least one off-by-one (a window of 2 or more that holds n always has a neighbour).
- Kinds: distance 1 is `off-by-one` (a skip or a double count), distance 2 or more is `off-by-two`. No new
  `DistractorKind`, so the website's existing tips work.
- Edges: n = 1 gives 1, 2, 3; n = 10 gives 8, 9, 10. *Why max 10:* "11" is beyond the Pre-K range.

`planTap(item, level, friend, seed): TapPlan` joins the two. **Seed:** `hashSeed(sessionId + '|' + index)` like
pair-match, so layouts change every session (a remembered pile would reward memory, not counting). Tests pass fixed seeds.

`nextAnimal(cycle, last)`: the animal after `last` in the cycle, or the first; same rule as `nextPatch`.

### 5.4 Reducer (`src/tap.ts`)

```ts
export const TAP_IDLE_MS = 8000;      // nudge
export const TAP_REST_MS = 6000;      // find the rest
export type TapPhase = 'count' | 'ask' | 'complete';

export interface TapState {
  readonly plan: TapPlan;
  readonly phase: TapPhase;
  /** Object ids in tap order. order.length is the running count. */
  readonly order: readonly number[];
  readonly wrong: readonly string[];
  readonly dimmed: readonly string[];
  /** Costed hints shown (Help, Done too early, Count with me, Show me). Feeds SessionRecord.hints. */
  readonly hints: number;
  readonly mistakes: readonly MistakeKind[];
  readonly skipped: boolean;
  readonly idleMs: number;
  readonly idleHints: number;
}

export type TapAction =
  | { type: 'count'; object: number }      // tap, click, Enter or Space on an object
  | { type: 'done' }                       // the Done bell (finish "done" only)
  | { type: 'name'; choice: string }       // a How many? choice
  | { type: 'help' }                       // tap on Hazel
  | { type: 'tick'; ms: number };          // time passes (the screen stops ticking while paused)

export type TapEffect =
  | { type: 'counted'; object: number; n: number }          // hop, ring, badge n, note pitchFor(n), word n
  | { type: 'again'; object: number }                       // re-tap of a counted object: neutral answer only
  | { type: 'all-counted' }                                  // auto: then ask follows in the same step
  | { type: 'ask' }                                          // badge fades, How many? appears
  | { type: 'nudge'; replay: boolean }
  | { type: 'rest'; objects: number[]; costed: boolean }    // uncounted objects twinkle
  | { type: 'dim'; choices: string[]; mistake?: DistractorKind }
  | { type: 'along'; order: number[] }                      // silent count-along
  | { type: 'recount'; order: number[] }                    // voiced recount, ends on the total
  | { type: 'complete'; outcome: TapOutcome };

export interface TapOutcome {
  /** No costed hint and How many? right on the first tap. */
  firstTry: boolean;
  /** Owner mode "never drop": always !firstTry. Decision 7 alternative: !firstTry && wrong.length < 2. */
  steady: boolean;
  hints: number;
  mistakes: MistakeKind[];
}
```

| Action | Rule | Effects |
|---|---|---|
| `count` | Ignored unless phase `count`. Unknown id: ignored. Counted id: `again`. Else push to `order` | `counted`; when the last object is counted and finish is auto: `all-counted`, `ask`, phase `ask` |
| `done` | Only finish `done`, phase `count`. All counted: `ask`. Some left: hints + 1, first `skipped` adds the mistake | `ask`, or `rest { costed: true }` |
| `name` | Only phase `ask`, a shown, not dimmed choice. Right: complete. 1st wrong: dim it, hints + 1. 2nd wrong: dim every wrong, hints + 1 | `complete`; or `dim` + `along`; or `dim` + `recount` |
| `help` | phase `count`: `rest { costed }` (or `nudge` when nothing is counted). phase `ask`: `along` (never `recount`: the answer is never on demand). Costs a hint | as said |
| `tick` | 8 s idle with 0 counted: `nudge`; 6 s idle with some left: `rest { costed: false }`; at most 2 in a row, any input resets | as said |

`replayTap(plan, actions)` runs a list of actions (tests prove tap and keys give the same state).

## 6. Level 4 in the same game (two mechanics, one game id)

### 6.1 What the registry supports today

`startGame` picks **one** runner from `def.mechanic`, and each runner owns the whole session loop (`session.next()`
to the end screen). So a game cannot use two mechanics today. But the kit already has the pattern we need:
`runFill(ctx, session, cancel, ext)` lets `fillTakeAway` plug a second per-order player into the fill loop.

### 6.2 Smallest change (recommended)

- `def.mechanic` is `"tap-count"`. The game registers one runner: `mechanics: { 'tap-count': tapCountWith({ fill }) }`.
- The tap-count runner owns the loop. For each question it looks at the level: a `tap` block plays a tap round, a
  `fill` block calls the injected fill player. Same idea as `FillExt.remove`.
- `src/mechanics/fill-order.ts` (new, a subpath export `@edulearnlabs/kit/fill-order`): a thin adapter that builds the
  `FillQuestion` (`buildFill` with the friend's kind, `ask: "none"`, no garden reward, the spoken line from
  `strings.give`) and calls fill-container's existing per-order `playOrder`, which only needs `export` added. The fill
  code itself does not change apart from section 6.3.
- **One scene for both.** tap-count draws into the fill scene from `mountUi` in `fill-common.ts` (960 x 600, Hazel
  helper, Help button, shelf strip, live region). *Why:* two scenes would each move Hazel and add a second Help button
  to her (both `mountUi` functions append one). With one scene, fill's backdrop swap (`backdrop.dataset.variant`) already
  switches the art between `tap` and `basket`. `fill-common.ts` imports no drag code, so a tap-only game still ships
  none.
- The runner, not the fill player, calls `session.resolve(...)` with the parade reward, so fill's garden logic is
  never used.
- *Not chosen:* a per-level `mechanic` field and a shared session loop in `game.ts`. Cleaner for a third mixed game,
  but it rewrites every live runner. Revisit then.

### 6.3 The fill fix for F1: `fill.finish: "done"` (additive, default `auto`)

- Reaching N does not end the order. Overfill does not block below the stock, so the child can put in too many.
- A Done bell (104 scene px, `aria-label` from `strings.done`, default "Done!") appears after the first item.
- `done` with count = N: complete. Count < N or > N: Hazel says "Let's count!", the basket's items light one by one with
  notes and no numbers (fill's count-along), the order stays open; too many can be tapped back out (fill's existing
  `remove`, free). First wrong Done records `off-by-one` (distance 1) or `off-by-two` (2 or more), once per order, and
  costs first try. The numeral N stays in the order bubble (it is the request, not the answer).
- Reducer: one new action `done`, two effects `short` and `over`, in `fill.ts`. The golden files and every fill and
  pond browser check must pass unchanged (default `auto`).

### 6.4 How the session picks the mechanic

The session picks the level (start level from the website, up after `upAfterCorrect` first-try rounds in a row, never
more than one step), and the level's block picks the player. Nothing in `Session` knows about mechanics apart from
`noChoices` (tap-count plans its own choices). Never drop: tap-count and its fill rounds resolve every non-first-try
round as `steady`. Practice items (`n-7`) fit whichever level's range holds them.

Loading: the runner starts `import()` of the fill player when a round at the level just below the first fill level
begins, and awaits it when the fill level starts (the website has usually prefetched it from `asset-manifest.json`, so it
is instant). If the import fails (offline), that round is played as a pile tap round with the same n, and the record is
still honest.

## 7. Rewards: the parade (website owned)

- `reward: { "type": "parade", "animals": [2 or more slugs] }`. One animal per **solved round**, first try or not
  (effort is rewarded, as with the garden and quilt). Level 4 rounds earn one too.
- Fixed cycle: the next animal after the last one in `HostInit.parade.animals`, never random (decisions.md bans
  variable rewards). Growth is by rounds solved, never by time; nothing ever leaves the parade.
- Fact sent in `GameCompleted.session.rewards`: `{ id: "<session id>-<question index>", kind: "animal", animal, at }`.
  Repeats of an animal are normal.
- In the scene: the bottom strip shows the newest 8 animals marching (fill's shelf element, hidden during How many?,
  same CSS rule as the garden shelf). End screen: up to 16 newest, this session's marked new, line `strings.parade`.
- **Website store** (mirrors quilts exactly):
  `parades[profile][game] = { "v": 1, "animals": [{ "id": "s_x81ka2-0", "animal": "bunny", "at": "...", "session": "s_x81ka2" }], "folded": 0 }`.
  Facts only, its own `v`, newer-`v` guard (kept as is, never written to), stores saved before it existed load with an
  empty one, deduped by reward `id`, never more animals than questions in one session, oldest first in save order, at
  most 200 per child per game with the oldest folded into `folded` (the cycle continues from the newest, so freezing
  would freeze the pattern), `HostInit.parade = { animals }` newest 64 at most, sent only when the catalog reward is
  `"parade"`, profile deletion deletes it. Animal slug check like `PATCH_RE`.
- **Protocol stays 1.** `HostInit.parade` is a new optional field and `kind: "animal"` a new reward kind; unknown
  fields are ignored on both sides. Until the website ships its part, a v0.6.0 game works and its animals are dropped
  by `validRewards`, with no error.
- A parent "My parade" page is later work, like the other reward pages.

## 8. Sound and voice

| Moment | Sound | Visual twin (for muted play) |
|---|---|---|
| Object counted | `audio.count(k)`: `pitchFor(k)`, C4 D4 E4 G4 A4 C5 D5 E5 G5 A5 for 1 to 10, then the number word | hop, ring, badge with k |
| Re-tap of a counted object | `audio.tap()` (neutral click) | ring pulse |
| All counted | nothing new (the last note rings) | badge fades, choices bounce in |
| Right answer | voice "Seven apples!", then a rising run 1..n, then `chord(n)` | objects light in tap order, then all glow |
| Wrong answer | none (decision 5) | the choice dims, Hazel tilts her head |
| Count with me | voice "Count with me!", then one note per object | each object lights in turn |
| Show me | voice "Count with me!", then per object: badge, number word, note | badge per object |
| Animal joins | soft chord | the animal walks into the strip |

- **Voice first.** Every hint line and the How many? line are awaited (`Promise.race` with 4.5 s, the fill pattern
  `sayThen`) before any tone starts. In the recounts each step is: light and badge, number word (awaited, at most 1.2 s),
  then the note, with a 450 ms minimum step so muted play keeps a steady beat.
- **Counting taps are the one exception**, like pair-match decision 17: the note plays at the tap (feedback within
  0.3 s beats a talking Hazel), then the number word follows. The note comes first, so speech never masks its start. The
  first tap stops the instruction line. A fast tapper hears the newest number (`say` cancels the older one).
- Muted play works because every row in the table has a visual twin, and `audio.say` resolves at once when audio is off.

## 9. Accessibility and input

- **Tap and click:** one `click` listener per object (no Pointer Events and no drag, like pair-match), and
  `touch-action: manipulation` from the base CSS removes the tap delay.
- **Keyboard:** objects are round `<button>`s in reading order, so Tab walks the row or pile top to bottom, left to
  right; Enter or Space counts. The number still follows press order, the same rule as taps. Counted objects stay
  focusable (removing a focused button loses focus); Enter on them gives the neutral answer. After all are counted,
  focus moves to the first choice only if the last input was a key (fill's rule: a focus ring after a tap would read as a
  hint). Choices: Tab and Enter, and digit keys by value (decision 10). Tab reaches Hazel (Help) and the Done bell.
- **Targets:** objects 104 scene px (65 px on a 667 x 375 phone), choices 160 x 104, Done bell 104.
- **Screen reader:** an object is "apple" or "apple, counted 3". Never "3 of 7" (that says the total). The polite live
  region says each number, the How many? line and "Seven apples!". Upright phones get the existing rotate prompt.
- **Reduced motion** (transform and opacity only, everything has a version):

| Animation | Full | Reduced |
|---|---|---|
| Objects arrive | pop in, staggered | fade in |
| Count | hop (translateY) | ring fades in |
| Badge | scale spring | opacity |
| Choices | `bounceIn` | fade |
| Recounts | small hop per object | glow (opacity) |
| Twinkle | scale and opacity | opacity |
| Animal joins | walk in (translateX) | fade in place |
| Confetti | on | off |

## 10. Size and lazy loading

Budget: kit JS near 15 KB brotli (about 18 KB accepted). `check-size.mjs` also fails a game over 30 KB of JS in total.

| Page (estimates from the v0.5.0 table, not measured) | JS brotli |
|---|---|
| Quiz page today | 9.4 KB |
| tap.ts (reducer, two planners, nextAnimal) | about 1.4 KB |
| tap-count screen | about 3.2 KB |
| fill-common scene shared code (new for a tap-only game) | about 0.9 KB |
| Shared session, content and type changes (every page) | about 0.2 KB |
| **Tap-only page (levels 1 to 3), no art** | **about 15 KB** |
| fill-order chunk (fill-container, drag, fill.ts, finish done) | about 11 KB |
| **Hedgehog Picnic, all four levels, plus 2 to 4 KB of art** | **about 28 to 31 KB** |
| tap.css (fill.css also needed for the scene) | about 1 KB |

Plan:
1. The fill player is a separate chunk loaded by `import()` (section 6.4). Before Play stays near 60 KB.
2. `check-size.mjs` today counts every `.js` file as Before Play and as game code, so a lazy chunk saves nothing on
   paper. Teach it: a file is Before Play only if `index.html` loads it (a `<script>` or `modulepreload`); other chunks
   are After Play, and the code budget becomes "entry JS 30 KB" plus "lazy JS" reported on its own line. Without this
   change Hedgehog Picnic may fail its own build (decision 12).
3. Trim candidates if needed: default art strings, the end-screen parade. A further step (later, not v0.6.0): let
   `startGame` take a runner loader, so the whole mechanic loads after Play.

## 11. Versioning

- New minor **v0.6.0**. Every change is additive: quiz, fill, pond, word and pair games behave the same (the golden
  files and all existing browser checks prove it). README "Size" and "What a game must implement" sections updated,
  framework-spec section 1 mechanic list and section 2 get a `tap-count` bullet, `types.ts` and the spec change together.
- Tag pushes are blocked in cloud sessions. The owner creates `v0.6.0` on GitHub (and the older `v0.2.0` to `v0.5.0`).
  Until then the game pins the **full commit SHA** in `package.json`.
- Kit CLAUDE.md says do not commit or push unless the owner asks. The implementation agent must ask (or be told in its
  prompt) before pushing the kit branch.
- Work on top of commit `03ced46` (branch `origin/ccr-4d0bb17c-4dbh4d`), not the stale session checkout.

## 12. Build steps (in order, test after each)

| # | Step | Files | Rough size |
|---|---|---|---|
| 1 | Types and spec mirror | `src/types.ts`, main repo `planning/framework-spec.md` | 90 lines |
| 2 | Count generator: `generate`, `itemFromId` (`n-7`), `itemFitsLevel`, `buildFill` accepts `n-7` as N plus 0, tests | `src/content.ts`, `tests/content.test.ts` | 40 lines + 12 tests |
| 3 | Planners `planObjects`, `planCountChoices`, `planTap`, `nextAnimal`, tests first | `src/tap.ts`, `tests/tap.test.ts` | 150 lines + 20 tests |
| 4 | Reducer `initTap`, `reduceTap`, `replayTap`, `outcomeOfTap`, tests first | `src/tap.ts`, `tests/tap.test.ts` | 170 lines + 30 tests |
| 5 | Session: `tap-count` in `noChoices`, `animal` reward kind; golden files unchanged | `src/session.ts`, `tests/session.test.ts` | 15 lines + 6 tests |
| 6 | Host: `HostInit.parade` | `src/host.ts` | 3 lines |
| 7 | Validator rules (below) | `build/validate.mjs`, tests | 70 lines + 15 tests |
| 8 | fill `finish: "done"`: reducer, Done bell, `short` and `over`; golden and fill e2e unchanged | `src/fill.ts`, `src/mechanics/fill-container.ts`, `src/styles/fill.css`, `tests/fill.test.ts` | 80 lines + 10 tests |
| 9 | `export playOrder`, adapter, subpath export | `src/mechanics/fill-order.ts`, `package.json` | 50 lines |
| 10 | Screen and CSS: `tapCount`, `tapCountWith({ fill })`, `TapSkin extends FillSkin` | `src/mechanics/tap-count.ts`, `src/styles/tap.css`, `src/index.ts` | 450 lines + 150 CSS |
| 11 | Playground: plain skin plus simple placeholder art (no game art in the kit) | `dev/tap.html`, `dev/tap.ts`, `dev/tap-game.json`, `dev/tap-skin.ts` | 150 lines |
| 12 | Size script: lazy chunks are After Play | `build/check-size.mjs` | 30 lines |
| 13 | Browser checks (section 14) | `tests/tap-e2e.cjs`, `package.json` `test:e2e` | 400 lines |
| 14 | Measure sizes, README, version 0.6.0, then ask before pushing | `README.md`, `package.json` | |

`TapSkin` fields (all optional, the kit draws plain dots and a plain friend without it): `symbols`, `tapBackdrop` (SVG on 960 x 600; `FillSkin.backdrop` is keyed by fill variant, so the tap scene gets its own field),
`items` (art per kind, reused by fill at level 4), `counted` (art per kind for a counted object), `customers` (the
friends, same field fill uses), `animals` (art per parade slug), `say(text)` (recorded voice hook).

Validator rules (build time only):
- `mechanic: "tap-count"`: `friends` is a list of 1 or more `{ id, kind }` slugs, every kind is in `kinds`;
  `friends` is refused for every other mechanic.
- Each level has exactly one of `tap` or `fill`. A `tap` level: `generator.type` is `count`, `n` within 1..10 with
  min <= max, layout `row` needs max <= 5, `rows` and `pile` need max <= 10, `choices` 2 to 4, `finish` auto or done.
- A `fill` level in a tap-count game: `variant` basket, `goal` total, `direction` add, `ask` none, `finish` done, a count
  generator with max <= 10. At least one `tap` level comes first (the game starts by counting).
- `generator.type: "count"` is refused outside tap-count; `tap` blocks are refused outside tap-count; `fill.finish` is
  allowed in fill-container games too (it is a fill option).
- `reward` is `{ "type": "parade", "animals": [2 or more slugs] }`, refused for every other mechanic.
- `upAfterCorrect` 2 or more (unchanged rule).

## 13. Owner decisions

### LOCKED 2026-11-15: owner said "take your recommendations"

Where the default and the recommendation differed, the recommendation wins. Final picks:
1(a) ship level 4 now with `fill.finish: "done"`. 2(a) silent count-along on the 1st wrong, voiced recount on the 2nd.
3(a) 84 px badge on the object, fades before How many?. 4(a) neutral click and ring pulse on a re-tap.
5(a) no sound on a wrong choice. 6(b) Done bell on level 3, skipping is a recorded mistake. 7(b) move down after 2 rounds
in a row that needed the voiced recount. 8: 6 rounds, 180 s. 9: ranges 2 to 5, 5 to 10, 4 to 10, 3 to 10.
10(a) digit keys pick by value. 11(a) note then word, newest wins. 12(a) lazy fill chunk plus the `check-size` change.
13(a) ring under the counted object. 14: quiz reveal fix in its own kit release. 15: 6 baby farm animals, friends not in the parade.
The options below are kept for the record.

Default = my recommendation, except where it differs from an explicit owner pick; then the default is the owner's pick
and the recommendation is noted.

1. **Level 4 and the auto-stop flaw (F1).** (a) Ship level 4 now with `fill.finish: "done"` (step 8). (b) Ship levels
   1 to 3 now, level 4 in a later kit minor. (c) Ship level 4 as fill is today. *Recommend (a); default (a).* (c) teaches
   nothing new. If step 8 slips, fall back to (b) and accept the one-time mastery step (F12).
2. **How many? ladder (F4).** (a) Silent count-along on the 1st wrong, voiced recount on the 2nd. (b) Voiced recount on
   the 1st wrong (the draft). *Recommend (a); default (a)*, because (b) says the answer as the second reaction and breaks
   "hints only".
3. **Badge (F3, F6).** (a) 84 px, on the counted object, fades before How many?. (b) Stays on screen. *Recommend (a);
   default (a).*
4. **Re-tap of a counted object (F8).** (a) Neutral click and ring pulse. (b) Fully silent, no visual. *Recommend (a);
   default (b) is the owner's draft wording, so I need a yes.* (a) keeps GAME_RULES 11 and avoids "is it broken?".
5. **Sound on a wrong choice.** (a) None, the dim and Hazel's head tilt carry it (pair-match does this for a miss).
   (b) fill's two soft falling notes (`audio.tryAgain`). *Recommend (a); default (a).* Falling notes read as "wrong".
6. **Finish mode on level 3 (F2).** (a) Auto everywhere, plus the idle "find the rest" twinkle. (b) Done bell on level 3,
   so skipping is a real, recorded, taught mistake. *Recommend (b); default (a)*, the owner's pick. It is one data field
   (`tap.finish`), so it can change without code.
7. **Moving down.** (a) Never (owner pick: every miss is `steady`). (b) Down after 2 rounds in a row that needed the
   voiced recount. *Recommend (b)* (a child stuck on 10-object scatters learns more from 2 neat rows); *default (a).*
8. **Rounds per session (F5).** 6 rounds (2 per friend), 180 s. *Recommend and default 6.*
9. **Number ranges.** Level 1: 2 to 5, level 2: 5 to 10, level 3: 4 to 10, level 4: 3 to 10. *Recommend and default
   these.* The draft's 1 to 5 and 1 to 10 make some rounds trivial.
10. **Digit keys on How many? (F9).** (a) A digit picks the choice with that value ("0" is 10). (b) Positional 1 to 4
    like quiz and fill. *Recommend (a); default (a).* Note: it differs from GAME_RULES 3 wording and from fill.
11. **Number words on every tap.** (a) Note then word, newest wins. (b) Notes only while counting, words only in the
    recount. *Recommend (a); default (a).* Hearing the count words is how Pre-K learns the sequence. Switch to (b) if
    speech is too slow on a real Chromebook.
12. **Size (F11).** (a) Lazy fill chunk plus the `check-size` change. (b) Accept the overage with `ELL_ALLOW_OVER` and
    a README note. *Recommend (a); default (a).*
13. **Counted mark.** (a) Ring under the object (stays in place). (b) Counted objects slide into a line ("move them
    aside", a real counting strategy, but it tidies the pile and changes the level). *Recommend (a); default (a).*
14. **Quiz reveal after a second miss.** Fix in its own kit release, not in v0.6.0 (it changes live quiz games).
    *Recommend and default: separate.*
15. **Parade animals and art.** The cycle list (6 slugs above are placeholders) and whether the friends (hedgehog,
    duck, mouse) also appear in the parade. Art preview question, *default: 6 baby farm animals, friends not in the parade.*

## 14. Test plan

**Unit (`tests/tap.test.ts`, plus session, content, fill and validator tests)**
- Tap order: numbers follow press order for any order, 1..n with no gaps; `order` keeps the sequence.
- Double-tap guard: a counted object gives `again` and no state change; a fast double tap counts once.
- Phase guards: taps ignored during `ask` and after `complete`; `name` ignored during `count`; dimmed choices ignored.
- Finish auto: the last count gives `all-counted` and `ask` in the same step. Finish done: `done` with some left gives
  `rest`, costs a hint, adds `skipped` once; `done` with none left gives `ask`.
- Ladder: 1st wrong dims one and gives `along`; 2nd wrong dims every wrong and gives `recount`; Help in ask never gives
  `recount`; `recount.order` equals the tap order.
- Idle: nudge at 8 s with 0 counted, rest at 6 s with some left, at most 2 in a row, any input resets, time never costs.
- Outcome: first try, steady in both adapt modes, hints, mistakes; replay equals step-by-step.
- Planner never overlaps: every layout, n 1..10 allowed by the layout, 2000 seeds each: all hit circles inside
  `TAP_AREA`, every pair at least 112 apart, ids in reading order, deterministic per seed, `rows` second row left
  aligned under the first.
- Distractors valid: every n 1..10, counts 2..4, 500 seeds: answer included once, no duplicates, no 0, nothing above
  10, ascending, at least one off-by-one, kinds match distances, and over the seeds the answer appears in every
  position its edges allow.
- Content: `n-7` round trips through `itemFromId`, fits the right ranges, `buildFill` gives one bin with target 7.
- Session: tap-count questions have no session choices, `animal` rewards in the record, cycle continues from HostInit,
  steady never moves down; every existing test and the golden files unchanged.
- Fill `finish: "done"`: short, over, remove extras, mistakes once per order; `auto` unchanged.
- Validator: every rule in section 12, the playground game passes.

**Browser (`tests/tap-e2e.cjs`), throttled profile: 4x CPU, about 1.6 Mbps, 150 ms latency. Tap Play first.**
- Tap page bundle has no drag code and no other mechanic's code; the fill chunk loads only near level 4.
- Hit targets: every object at least 64 px at 667 x 375, for each layout and n = 10.
- Tap play: numbers follow a scrambled tap order; re-tap gives no number and no count note; one badge element only,
  on top, `pointer-events: none`, centred on the last counted object.
- Badge is gone before the choices show; choices appear only after the last count (auto).
- Keyboard: Tab order is reading order, Enter counts, digit keys pick by value.
- Ladder: wrong 1 dims one and lights objects with no number words; wrong 2 leaves one button and the recount's spoken
  numbers (fake `speechSynthesis`) equal the tap order; no red, no buzzer element or sound call on a wrong tap.
- Voice before tones: with a 2.5 s fake voice line, no hint tone starts before it ends; a counting tap stops the
  instruction line.
- Muted: a full session with audio off finishes, every step shows its visual twin.
- Session: climb levels 1 to 4 with 2 right in a row each, a give-me-N order with Done short, over, then right; record
  has 6 questions, levels, hints, mistakes, 6 animal rewards continuing the HostInit cycle; end-screen parade.
- Offline fill chunk (blocked request): level 4 round falls back to a pile round, no error message.
- Reduced motion: no transform animations, fades only. Upright phone: rotate prompt.
- Scene at 667 x 375 and 960 x 600: back button, friend, bubble and Hazel never overlap an object.

**Lesson to apply:** a check that silently skips proves nothing. Every new check prints one "ok" line (for example
`ok  pile n=10 seed 7: 10 objects, min gap 112`), the script ends with a count of ok lines, and the run is read for
that count, not only for "no errors". Long browser runs go in the background with an until-loop on the final line.

## 15. What a game must implement

```ts
import '@edulearnlabs/kit/styles.css';
import '@edulearnlabs/kit/fill.css';
import '@edulearnlabs/kit/tap.css';
import { startGame, tapCountWith, type GameDef } from '@edulearnlabs/kit';
import def from '../game.json';
import { skin } from './skin';   // a TapSkin: friends, kinds, counted art, parade animals, backdrop, optional voice
const fill = () => import('@edulearnlabs/kit/fill-order').then(m => m.fillOrder);
void startGame(def as unknown as GameDef, { mechanics: { 'tap-count': tapCountWith({ fill }) }, skin });
```

A tap-only game passes `tapCount` instead and never loads the fill chunk.

## 16. Risks

1. **Level 4 needs a fill change (step 8)**, the first change to shared fill logic since v0.3.0. Default off and golden
   files make it safe, but it is the step most likely to slip.
2. **Size**: Hedgehog Picnic sits near the 30 KB JS budget until `check-size` understands lazy chunks.
3. **Speech synthesis on old Chromebooks**: a number word per tap may lag or cut off on fast tapping. Real-device
   check before release; decision 11 (b) is the fallback. Real touch on tablets is still untested for every mechanic.
4. The website must add `parade` to HostInit and accept `kind: "animal"`; until then animals are dropped silently.
