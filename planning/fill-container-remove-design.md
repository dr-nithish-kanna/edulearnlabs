# fill-container take-away: kit design for Pond Hop (kit v0.2.0 to v0.3.0)

Status: DESIGN, 2026-11-12. Opus design pass, nothing is built from this yet. Follows the style of
`planning/fill-container-design.md`. Every open point is decided in section 11 ("Decisions made"), because the owner
is asleep and accepted all defaults of `planning/subtraction-pond-design.md` section 10.

Files read for this design: main repo `CLAUDE.md`, `planning/game-playbook.md`, `planning/subtraction-pond-design.md`,
`planning/fill-container-design.md`, `planning/framework-spec.md`, `templates/game-repo/GAME_RULES.md`,
`src/scripts/progress.ts` (rewards handling), `src/scripts/player.ts`; kit `CLAUDE.md`, `README.md`, `src/fill.ts`,
`src/mechanics/fill-container.ts`, `src/content.ts`, `src/types.ts`, `src/session.ts`, `src/pitch.ts`, `src/audio.ts`,
`src/drag.ts`, `src/game.ts`, `src/index.ts`, `build/validate.mjs`, `build/schemas/fill-container.schema.json`,
`tests/fill.test.ts`, `tests/content.test.ts`, `tests/session.test.ts`, `tests/validate.test.ts`, `tests/fixture.ts`,
`tests/fill-e2e.cjs`, `dev/garden-skin.ts`, `dev/fill-game.json`, `dev/fill.ts`, `vite.config.ts`, `tsconfig.json`.

## 0. The big idea in five lines

1. Take-away is the same rule run backwards: the container starts full, items move from the container to a
   destination, and "count" means **what is still in the container**. With that one definition, most of the reducer
   (overfill, hint ladder, naming, outcome) works unchanged.
2. **`keep` is the existing `total` rule run backwards** ("stop when the container holds N"). It costs about ten
   lines in the reducer. The real work is on the screen, not in the logic.
3. **Keep items are read the other way round:** at a keep level, `q-8m5` means "8 frogs, leave 5, how many hopped
   away? 3". Then `item.answer` is always the number the child names, so `buildChoices`, the planned distractors,
   the session record and the item ids need no change at all.
4. The remove screen is a **new, separate order player** (`src/mechanics/fill-take.ts`) behind a new opt-in runner
   `fillTakeAway`. Addition Garden keeps importing `fillContainer`, so it ships none of the new screen code.
5. The firefly reward lives **only in the session**: a new game.json block `sessionReward` (not `reward`), drawn by a
   skin hook, never sent to the website. `GameCompleted.session.rewards` is omitted for Pond Hop. Protocol stays 1.

## 1. What must not change (the invariants)

Addition Garden 2.0.0 is pinned to kit `9eb375e`. Nothing changes for it until it re-pins on purpose. When it does
re-pin to v0.3.0 with no other change, all of this must hold:

| Invariant | How it is kept | How it is proven |
|---|---|---|
| I1. Every `reduce` call on a `direction: "add"` spec returns the same state and the same effects as v0.2.0 | Every new branch is guarded by `spec.direction === 'remove'` or `goal === 'keep'` (keep is only valid with remove). The add code in the `drop` case is not edited | Golden file test written FIRST, on v0.2.0 code (section 8.1, step 0) |
| I2. `buildFill`, `fillQuestion`, `kindCycle` give the same output for addition items and the garden reward | The remove branch is entered only when `level.direction === 'remove'`; the garden reward check becomes `def.reward?.type === 'garden'`, which is the same truth value for every valid game.json | Golden file test of 10 seeded fill questions, written on v0.2.0 |
| I3. Addition Garden session records are byte for byte the same JSON | `record()` keeps the key order `{ ..., hints, rewards }`. `rewards` is now added only when at least one `resolve` carried a reward. Addition Garden passes a reward on every resolve, so it always has the field | Golden record test plus the existing record tests |
| I4. `session.solved` gives the same numbers for Addition Garden | `solved` now counts resolved orders. In Addition Garden every resolved order earns exactly one reward, so the count is equal | Existing test "grants a reward on every solved order" (`solved` is 2) |
| I5. Addition Garden ships no take-away screen code | New code lives in `fill-take.ts`, reachable only from the new `fillTakeAway` runner | Size check of the fill page before and after (section 9) |
| I6. Message contract unchanged, `protocol: 1` | No new message, no new HostInit field; `GameCompleted.session` simply lacks `rewards` for Pond Hop, which the website already handles (`validRewards(undefined)` returns `[]`) | Existing `host.test.ts`; Pond e2e checks `rewards` is absent |
| I7. Quiz games unchanged | No quiz file touched; `types.ts` changes are additive optional fields and widened unions on fill-only types | Existing quiz tests and quiz page size |

**Why golden files first.** The reducer is the heart of the live game. A golden test written before the change is a
photograph of today's behavior. If one byte of an add path changes, the test fails and points at it. It turns
"I believe it is equivalent" into "it is equivalent".

## 2. Data shape

### 2.1 Words used in this doc

| Word | Add (Addition Garden) | Remove (Pond Hop) |
|---|---|---|
| container | basket or ten-frames | lily pad or lantern ten-frames |
| bin | where items come from (crate, stone pile) | where items go: the **destination** (water, night sky). Always one bin, id `a` |
| `prefill` | items already in the container | **the starting count `a`** (the container starts full) |
| `placed` (reducer state) | items the child moved in | items the child moved out |
| `totalCount` | `prefill + placed.length` | `prefill - placed.length` (what is still in the container) |
| `target` | the container count when the goal is met | the container count when the goal is met (`a - b` for parts, `N` for keep) |
| `want` on the bin | how many of this kind to put in | how many must leave (parts only) |
| `stock` on the bin | how many the bin holds | `0` (the water starts empty). Not used by the remove rules |

The one rule to remember: **`totalCount` is always "what is in the container now"**. That is why the drop note
(`audio.count(count)`) automatically falls 7, 6, 5 when 3 of 8 frogs leave. No new audio code.

### 2.2 types.ts (additive)

```ts
// v0.3.0
export type FillDirection = 'add' | 'remove';
/** parts: each part is named. total: any mix reaching the target (add).
 *  keep (v0.3.0, remove only): stop when the container holds exactly target; How many? asks how many LEFT it. */
export type FillGoal = 'parts' | 'total' | 'keep';

export interface FillLevel {
  variant: FillVariant;
  goal: FillGoal;
  /** "add" (default) or "remove" (v0.3.0: the container starts with `a`, the child moves items out). */
  direction?: FillDirection;
  /** add, ten-frame: which addend starts on the frame. remove: always "a" (may be left out). */
  prefill?: 'a' | 'b' | 'bigger' | number;
  frames?: 1 | 2;
  /** Item kind. add: the ten-frame bin. remove: required, the kind in the container ("frog", "firefly"). */
  binKind?: string;
  /** add only. Not allowed with remove: the full container already makes the child count. */
  spare?: [number, number];
  ask?: 'total' | 'none';
}

export interface FillSpec {
  variant: FillVariant;
  goal: FillGoal;
  direction: FillDirection;   // was 'add'
  target: number;
  prefill: number;
  frames: number;
  bins: FillBin[];
  /** "total" turns on the How many? step. It names item.answer: the container count, or the number moved out in keep. */
  ask: 'total' | 'none';
}

/** v0.3.0: a reward that lives only in this session. Drawn by the skin, never stored, never sent to the website. */
export interface SessionRewardDef { type: 'lights' }

export interface GameDef {
  // ... unchanged fields ...
  reward?: { type: 'garden'; species: string[] };   // unchanged: a reward the WEBSITE stores
  /** v0.3.0, fill-container: one light per solved order, gone when the session ends. Not with `reward`. */
  sessionReward?: SessionRewardDef;
}

export interface GameStrings {
  // ... unchanged ...
  // v0.3.0 take-away lines. {n} number word, {kind} singular or plural word, {is} "is" or "are".
  take?: string;          // pad order:      "{n} {kind} {is} going for a swim!"
  takeFrame?: string;     // lantern order:  "{n} {kind} {is} flying home!"
  keep?: string;          // keep order:     "Leave {n} {kind} on the pad!"
  askLeft?: string;       // "How many {kind} are on the pad?"
  askLeftFrame?: string;  // "How many {kind} are still here?"
  askGone?: string;       // keep: "How many {kind} hopped away?"
  takeAway?: string;      // after the right answer: "{a} take away {b} leaves {left}!"
  dragOut?: string;       // first-order pill: "Help them hop!"
  slotsOut?: string;      // H3 for parts: "Look at the ripples!"
  slotsKeep?: string;     // H3 for keep: "These ones stay!"
  glow?: string;          // end screen line: "The pond is glowing!"
  here?: string;          // aria label of the container, basket variant ("Lily pad")
  away?: string;          // aria label of the destination, basket variant ("Water")
  hereFrame?: string;     // "Lantern"
  awayFrame?: string;     // "Night sky"
}
```

`FillItemSpec` (hand-written items) gets no `direction`: **hand-written remove items are not supported in v0.3.0**
(validator rejects them). Pond Hop only uses generators. This keeps the item form, its tests and its defaults
untouched. `FillEffect` gains one member, `{ type: 'ten-broken' }` (section 3).

**Why `sessionReward` and not `reward: { type: "lights" }`.** Two reasons. (1) Meaning: `reward` already means
"the website stores this fact for the child". The fireflies are the opposite: nothing stored, nothing lost. A
separate name keeps the data honest and lets the validator say "not both". (2) Safety: widening `reward` to a union
breaks the TypeScript build of existing code that reads `def.reward.species` (the kit's own `content.test.ts`
line 157 does, and a game may too). A new optional field breaks nothing. This is the one place this doc departs
from the task brief's wording ("game.json with `reward`").

### 2.3 Keep: the data shape decision

The child sees "8 frogs. Leave 5 on the pad." and is asked "How many hopped away?" (answer 3).

| Option | Item at the keep level | Naming answer | What has to change |
|---|---|---|---|
| A. Same item as hop-away | `q-8m3` (answer "5") | 3, which is NOT `item.answer` | The mechanic rebuilds choices around 3, the session's choices are thrown away, `fq.choices` no longer equals `q.choices`, a second "answer" field travels beside the item, and every test that says "naming answer is item.answer" gets an exception |
| **B. Read the fact the other way (chosen)** | `q-8m5` = "8 - 5 = 3": 8 frogs, keep 5, 3 hopped away | 3 = `item.answer` | Only `buildFill` (target = b, the kept number) and the screen |

**Why B.** `q-8m5` still means exactly 8 - 5 (GAME_RULES rule 17), and that fact is exactly the keep situation:
start 8, the part that stays is 5, the unknown part is 3. `Session.next` already builds the right choices:
`buildChoices` on `q-8m5` gives 3, off by one (2 or 4), and wrong operation = 8 + 5 = 13, the sum of the two numbers
the child sees. The session record, `missed`, practice items and the parent's mistake counts need zero new code.
A missed keep item `q-8m5` may come back at level 2 as "5 frogs go for a swim, how many left? 3". Same fact, other
picture, which is what practice should do.

The keep level's generator therefore reads `b` as **the number kept**: level 3 "a 5 to 10, b 2 to 8, result 1 to 8"
from the game design maps directly (b = frogs that stay, result = frogs that hop away, at least 1).

### 2.4 Loaded question (what the order player receives)

Example 1, level 2 hop away, `q-8m3`:
```json
{
  "item": { "id": "q-8m3", "prompt": { "text": "8 - 3", "say": "Three frogs are going for a swim!" }, "answer": "5" },
  "fill": {
    "variant": "basket", "goal": "parts", "direction": "remove", "target": 5, "prefill": 8, "frames": 1,
    "bins": [ { "id": "a", "kind": "frog", "want": 3, "stock": 0 } ], "ask": "total"
  },
  "choices": ["4", "5", "11"], "mistakes": { "4": "off-by-one", "11": "wrong-operation" },
  "level": 2, "difficulty": 2, "index": 3
}
```
(The kit renders the prompt text with a real minus sign, as `arithmeticItem` already does. No `reward` key: Pond
Hop has no stored reward.)

Example 2, level 3 keep, `q-8m5`:
```json
{
  "item": { "id": "q-8m5", "prompt": { "text": "8 - 5", "say": "Leave five frogs on the pad!" }, "answer": "3" },
  "fill": {
    "variant": "basket", "goal": "keep", "direction": "remove", "target": 5, "prefill": 8, "frames": 1,
    "bins": [ { "id": "a", "kind": "frog", "stock": 0 } ], "ask": "total"
  },
  "choices": ["3", "2", "13"], "mistakes": { "2": "off-by-one", "13": "wrong-operation" },
  "level": 3, "difficulty": 3, "index": 5
}
```

Example 3, level 5 lantern, break ten, `q-13m5`:
```json
{
  "item": { "id": "q-13m5", "prompt": { "text": "13 - 5", "say": "Five fireflies are flying home!" }, "answer": "8" },
  "fill": {
    "variant": "ten-frame", "goal": "parts", "direction": "remove", "target": 8, "prefill": 13, "frames": 2,
    "bins": [ { "id": "a", "kind": "firefly", "want": 5, "stock": 0 } ], "ask": "total"
  },
  "choices": ["9", "8", "18"], "mistakes": { "9": "off-by-one", "18": "wrong-operation" },
  "level": 5, "difficulty": 5, "index": 8
}
```
The lantern starts with frame 1 shown as the "10" token and 3 fireflies on frame 2. The 3rd firefly out empties
frame 2; the reducer emits `ten-broken`; the token opens back into ten fireflies; the last 2 come out of the ten.
The child sees 13 - 5 = 13 - 3 - 2.

### 2.5 content.ts

```ts
/** The two numbers of a subtraction id (q-8m3), or null. */
export function minusParts(id: string): [number, number] | null {
  const m = /^q-(\d+)m(\d+)$/.exec(id);
  return m ? [Number(m[1]), Number(m[2])] : null;
}

export function buildFill(item: Item, level: FillLevel | undefined, kinds: [string, string], rng: Rng): FillSpec {
  if (item.fill) { /* unchanged */ }
  if (level?.direction === 'remove') return buildTake(item, level);   // NEW, before the addition path
  /* addition path unchanged */
}

/** Take-away layout. Uses no rng: the container holds exactly a, so the picture is the same every time. */
function buildTake(item: Item, level: FillLevel): FillSpec {
  const ab = minusParts(item.id);
  if (!ab) throw new Error(`Item ${item.id} is not a subtraction item; a "remove" level needs op "-"`);
  const [a, b] = ab;
  const keep = level.goal === 'keep';
  return {
    variant: level.variant, goal: level.goal, direction: 'remove', prefill: a,
    target: keep ? b : a - b,
    frames: level.variant === 'ten-frame' ? level.frames ?? (a > 10 ? 2 : 1) : 1,
    bins: [{ id: 'a', kind: level.binKind ?? kinds[0], want: keep ? undefined : b, stock: 0 }],
    ask: level.ask ?? 'total',
  };
}

/** "Three frogs are going for a swim!", "One frog is going for a swim!", "Leave five frogs on the pad!" */
export function takeLine(def: Pick<GameDef, 'kinds'>, spec: FillSpec,
  t: { take?: string; takeFrame?: string; keep?: string }): string | null {
  if (spec.direction !== 'remove') return null;
  const keep = spec.goal === 'keep';
  const n = keep ? spec.target : spec.bins[0]?.want ?? 0;
  const tpl = keep ? t.keep : spec.variant === 'ten-frame' ? t.takeFrame : t.take;
  if (!tpl) return null;
  const line = tpl.replace('{n}', numberWords(n)).replace('{kind}', kindWord(def, spec.bins[0]?.kind ?? '', n))
    .replace('{is}', n === 1 ? 'is' : 'are');
  return line.charAt(0).toUpperCase() + line.slice(1);
}
```

Changes to existing functions (each is a no-op for Addition Garden):
- `kindCycle`: `def.reward?.species` stays as is (type unchanged, section 2.2).
- `fillQuestion`: new optional `opts.takeTemplates`; `say = orderLine(...) ?? takeLine(def, fill, opts.takeTemplates ?? {})`.
  `orderLine` already returns null for anything that is not a basket parts order with 2 bins, so add orders are
  untouched. The garden reward line stays `def.reward ? ... : undefined`.
- `buildChoices`: no change. For `q-8m3` its wrong-operation candidate is already `8 + 3 = 11` (the `m` branch of
  the existing ternary computes the sum). This is the "wrong operation is the sum" rule, for free.

### 2.6 JSON Schema (`build/schemas/fill-container.schema.json`)

```json
"goal":      { "enum": ["parts", "total", "keep"],
               "$comment": "keep (v0.3.0) needs direction remove" },
"direction": { "enum": ["add", "remove"], "default": "add",
               "$comment": "remove (v0.3.0): level form only, generator op '-', binKind required, no spare, prefill only 'a'" },
```
Everything else stays. The existing test "agrees with build/schemas/fill-container.schema.json on every enum" keeps
both files in step, so `FILL.goal` and `FILL.direction` in `validate.mjs` change in the same commit.

### 2.7 validate.mjs: exact new rules

```js
export const FILL = {
  variant: ['basket', 'ten-frame'], goal: ['parts', 'total', 'keep'], direction: ['add', 'remove'], ask: ['total', 'none'],
  prefill: ['a', 'b', 'bigger'], binIds: ['a', 'b'],
  maxStock: 12, maxSpare: 5,
  /** v0.3.0: most items a pad (basket, remove) shows. Two rows of 5 stay countable at a glance. */
  maxPad: 10,
};
```

| # | Where | Rule | Message (shown to the game author) |
|---|---|---|---|
| R1 | common | `direction` is `add`, `remove` or missing | `fill.direction must be "add" or "remove"` (replaces the "reserved" message) |
| R2 | common | `goal: "keep"` needs `direction: "remove"` | `fill.goal "keep" only works with direction "remove"` |
| R3 | common | `goal: "total"` is not allowed with remove | `direction "remove" uses goal "parts" or "keep" ("keep" is the take-away version of "total")` |
| R4 | item form | no `direction: "remove"`, no `goal: "keep"` | `hand-written items cannot use direction "remove" or goal "keep" yet; use a generator level` |
| R5 | level | op must match direction: `+` for add, `-` for remove | `direction "remove" needs a generator with op "-"` / `direction "add" needs a generator with op "+"` (the second replaces "take-away is not built yet") |
| R6 | level, remove | no `spare` | `fill.spare has no meaning for direction "remove": the container starts full` |
| R7 | level, remove | `prefill` missing or `"a"` | `direction "remove" starts with "a" in the container; prefill can only be "a"` |
| R8 | level, remove | `binKind` is a slug | `direction "remove" needs fill.binKind, the item kind (for example "frog")` |
| R9 | level, remove | `generator.b[0] >= 1` | `direction "remove" needs b of 1 or more (parts: something leaves; keep: something stays)` |
| R10 | level, remove | `generator.resultMin >= 1` | `direction "remove" needs resultMin 1 or more: an empty container is not taught yet` (design decision 5, zero left) |
| R11 | level, remove, basket | every fitting `a <= maxPad` (walk the generator, as today) | `a pad could start with {a} items; at most 10 fit (two rows of 5)` |
| R12 | level, remove, ten-frame | every fitting `a <= 10 * (frames ?? 2)` | `the lantern could start with {a}, more than {cap} spaces on {frames} frame(s)` |
| R13 | level, basket | the existing "basket levels need reward.species or kinds" applies to add only | unchanged text |
| R14 | game | `sessionReward`, when present, is `{ "type": "lights" }`, only with `fill-container`, never together with `reward` | `sessionReward.type must be "lights"` / `sessionReward is only used by the fill-container mechanic` / `use "reward" (stored garden) or "sessionReward" (lights, never stored), not both` |
| R15 | common | `ask: "total"` needs a `choices` block | unchanged, now also covers keep |

R9 plus R10 together guarantee: at least one item moves, at least one stays, `b <= a`. "b cannot exceed a" is
implied (`a - b >= 1`); no separate rule needed. The generator walk that today computes `worstBin` gets a remove
branch that computes `worstA` instead (`spare` and bins of 12 do not apply).

## 3. Reducer (`src/fill.ts`)

### 3.1 State, actions, effects

- `FillState`: **no new fields.** `placed` now reads "items the child moved", and `tenMade` gets a remove meaning:
  "the first ten is still whole (drawn as the 10 token)". `initFill` is unchanged: `tenMade: prefill >= 10` is
  exactly right for a lantern that starts at 11 to 18.
- `FillAction`: **no new actions.** `drop` means "move one item forward the way the order goes" (into the basket,
  or out of the pad into the water, `bin` = the destination). `remove` means "undo one move" (free). The screen
  maps pad, water, tap, drag and keys onto these two, exactly like the add screen.
- `FillEffect`: one new member, `{ type: 'ten-broken' }`. The existing `placed` effect is reused: `count` is
  everything still in the container (the note to play), `part` is how many went to this bin.

**Why reuse instead of new action names.** Same action list means the input-paths test, the hint ladder, the idle
timer and `replay` all work for take-away with no copy. The meaning flips with direction, and that is documented in
one sentence on the type. New names (`takeOut`, `putBack`) would add code to every layer for zero new behavior.

### 3.2 Code shape

```ts
export const totalCount = (s: FillState) =>
  s.spec.direction === 'remove' ? s.spec.prefill - s.placed.length : s.spec.prefill + s.placed.length;

export function goalMet(s: FillState): boolean {
  if (s.spec.goal === 'total' || s.spec.goal === 'keep') return totalCount(s) === s.spec.target;
  return s.spec.bins.every(b => partCount(s, b.id) === (b.want ?? 0));   // parts, both directions
}

export function needBin(s: FillState): BinId | undefined {
  if (s.spec.goal === 'keep') return goalMet(s) ? undefined : s.spec.bins[0]?.id;   // NEW line
  /* existing two lines unchanged (parts covers remove parts too) */
}

// in reduce(), case 'drop', right after `if (!bin) return none;`:
if (s.spec.direction === 'remove') return takeOut(s, bin);
// everything below is the unchanged add code

function takeOut(s: FillState, bin: FillBin): Step {
  const base = touched(s);
  const left = totalCount(s);
  if (left <= 0) return { state: base, effects: [{ type: 'empty', bin: bin.id }] };   // defensive
  const part = partCount(s, bin.id);
  const tooMany = s.spec.goal === 'keep' ? left <= s.spec.target : part >= (bin.want ?? 0);
  if (tooMany) return overfillStep(s, base, bin.id);
  let next: FillState = { ...base, placed: [...s.placed, bin.id] };
  const count = totalCount(next);
  const effects: FillEffect[] = [{ type: 'placed', bin: bin.id, count, part: part + 1 }];
  const met = goalMet(next);
  if (s.spec.variant === 'ten-frame' && count === 10 && s.tenMade && !met) {
    next = { ...next, tenMade: false };
    effects.push({ type: 'ten-broken' });
  }
  return met ? finishBuild(next, effects) : { state: next, effects };
}
```

`overfillStep` and `finishBuild` are the existing overfill block (4 lines) and goal tail (7 lines) of the add
`drop` case, **moved verbatim** into helpers and called from both places. The golden test (I1) proves the move
changed nothing. If the implementer prefers not to touch the add case at all, duplicating those 11 lines inside
`takeOut` is acceptable; it costs about 60 bytes.

The `remove` (undo) case needs **no change**: it pops the last move and emits `returned` with
`count = totalCount(next)`, which for remove is the container count going back up. `tenMade` is not touched, so after
a break and a put-back the lantern shows 10 loose fireflies plus 1, which is the true picture. `tick`, `help` and
`name` are unchanged.

### 3.3 Transition table for `drop` in direction remove (build phase)

`c` = container count before the drop, `o` = moves so far, `W` = `want`, `T` = `target`.

| Case | Condition | New state | Effects (in order) |
|---|---|---|---|
| D1 nothing left | `c <= 0` (cannot happen with validated data) | idle reset only | `empty(a)` |
| D2 overtake, parts | `o >= W` | `overfills + 1`; first time adds `off-by-one` to `mistakes`; hint raised to `min(3, overfills)` | `overfill(a)`, `hint(level, need)` |
| D3 overtake, keep | `c <= T` | same as D2 | same as D2 |
| D4 move | otherwise | `placed + a` | `placed(a, count = c - 1, part = o + 1)` |
| D5 break ten | D4 and ten-frame and `c - 1 === 10` and `tenMade` and goal not met after the move | D4 plus `tenMade: false` | D4 then `ten-broken` |
| D6 goal | D4 and goal met after the move | D4 plus `phase: naming` (ask total) or `complete` | D4 (and D5 never), then `goal`, then `complete(outcome)` if no naming |

Worked examples (these become tests):
- `q-8m3` parts: drops give counts 7, 6, 5, goal on the 3rd. A 4th drop is D2: count stays 5.
- `q-8m5` keep: same moves, goal when `c` reaches 5. A 4th drop is D3.
- `q-13m5` lantern: counts 12, 11, 10 (D5 `ten-broken` right after the 3rd `placed`), 9, 8, goal.
- `q-14m4` lantern (level 4): counts 13, 12, 11, 10 and the goal lands on 10, so **no** break (D5 needs "goal
  not met"). Right: nothing more needs to come out of the ten.
- After a break, `remove` then `drop` again: count 11 then 10, `tenMade` is already false, no second `ten-broken`.

### 3.4 Session.resolve mapping (unchanged rules, new situations)

| What happened in the order | `firstTry` | `hints` | `mistakes` |
|---|---|---|---|
| Clean build, right naming on the first tap | true | 0 | none |
| Idle H1 only ("Look") | true | 0 | none |
| Overtake (1 or more times) | false | H2 and H3 reached by the 2nd and 3rd overtake count | `off-by-one` once per order |
| Hazel tapped | false | 1 per new H2 or H3 | none |
| Wrong naming tap, parts ("how many left?") | false | H2 count-along counted once | planned kind of that choice: `off-by-one` (4 or 6), `off-by-two`, `wrong-operation` = the sum (11) |
| Wrong naming tap, keep ("how many hopped away?") | false | as above | `off-by-one` (2 or 4), `off-by-two`, `wrong-operation` = 8 + 5 = 13 |
| Calling a frog back (undo) | no cost | 0 | none |

The kit already computes all of this in `outcome()`; nothing changes in `fill.ts` or `session.ts` for it.

### 3.5 Session changes (`src/session.ts`)

```ts
private solvedCount = 0;
private rewarded = false;   // some resolve carried a stored reward (garden)

resolve(o: ResolveOutcome): Reward | null {
  /* existing lines */
  this.solvedCount++;
  if (o.reward) { this.rewarded = true; /* existing reward lines */ }
  /* existing lines */
}

/** Orders solved so far (with or without a stored reward). Drives the garden cycle and the session lights. */
get solved() { return this.solvedCount; }

// record():
...(this.resolved ? { hints: this.hints, ...(this.rewarded ? { rewards: this.rewards.map(r => ({ ...r })) } : {}) } : {}),
```

Pond Hop's record: `{ ..., mistakes, hints }`, no `rewards`. Addition Garden's record: unchanged (I3, I4).
Side effect to note in the README: a fill game with no reward at all used to send `rewards: []`; it now sends no
`rewards` key. No such game is live, and the website treats both the same.

## 4. Interaction (the take-away screen)

### 4.1 Screen state machine (one order)

```
 intro --(order spoken or first input)--> idle
 idle  --pointerdown on the pad--> pressing
 pressing --moved > 8 px--> dragging           (the top frog lifts out, under the finger)
 pressing --released, no move--> picked        (tap-to-pick: the top frog lifts and glows)
 idle  --Enter/Space on the pad--> picked      (keyboard)
 idle  --key 1--> sending                      (fast path, GAME_RULES number keys)
 picked --tap or Enter on the water--> sending
 picked --tap the pad again / Escape--> idle   (settles back, no cost)
 dragging --release over the water (+24 px)--> sending
 dragging --release elsewhere / pointercancel--> idle (springs back to the pad, no cost)
 sending --D4--> idle        (exit animation, note of the count still on the pad, ripple)
 sending --D5--> idle        (bell, the 10 token opens into ten fireflies)
 sending --D2/D3--> hop-back --(leaps toward the water, wobbles, hops back)--> idle
 sending --D6--> settle --(about 650 ms, the pad goes calm)--> naming (ask total) --> complete
 idle  --drag an item from the water to the pad, or Backspace--> idle (returned, free)
 naming --wrong tap--> naming (that choice dims, count-along of the asked group)
 naming --right tap--> complete (chord, glow, line, the friend leaves, a light appears in the sky)
```

Same rules as the add screen: the reducer applies the move at once, only the flying frog ignores input until it
lands (about 300 ms), the board never locks.

**Which frog leaves.** Always the frog in the last occupied slot (highest index), but the floating ghost starts
under the finger. **Why:** the pad keeps a tidy, countable layout (rows of 5, no holes), and H3 "stay" rings can be
drawn on slots 0 to N-1. A child who touches the 2nd frog still sees "a frog" come up under the finger. The add
screen already does this with bin stock.

### 4.2 Elements and hooks (all inside the board, rebuilt per order)

| Element | Class and data | Notes |
|---|---|---|
| Container (pad or lantern) | `button.ell-fill-target` with `data-start` (a), `data-count` (live), `data-keep` (N, keep only) | The SOURCE in remove. Same class as the add container so the shared layout and focus styles apply. aria-label from `strings.here` / `hereFrame` |
| Destination (water or sky) | `button.ell-fill-dest` with `data-want` (b, parts only) | The drop zone, at least 64 by 64 px (it is about 300 by 170 scene px). aria-label from `strings.away` / `awayFrame` |
| Items in the container | `span.ell-fill-item` (basket slots) or `.ell-cell` (lantern) | Decorative, `aria-hidden` |
| Items that left | `span.ell-fill-out` inside the destination | Drawn with `items['<kind>-out']` if the skin has it (a swimming frog head), else the item symbol at 85 percent |
| Ripple | `i.ell-ripple` (kit CSS ring, `--ell-ripple` color) | Visual twin of each leave note |
| Order bubble | `.ell-fill-order` | Parts: up to b small item icons in rows of 5 plus the numeral b; each icon turns into a ripple outline as a frog leaves (the per-part twin, like the add badge). Keep: the word line plus the numeral N and a small pad icon. Lantern: "13 - 5" with `data-part="pre"` and `data-part="take"` |
| Keep pad badge | `.ell-fill-badge.is-total` on the pad | Running pad count, keep only (counting the pad IS the keep task, like the add `total` badge) |
| Choices | `.ell-fill-choices .ell-choice` | Unchanged component |
| Session lights | `.ell-fill-lights` layer in the scene (outside the board, survives orders), one `.ell-fill-light` per solved order | Section 5.4 |

`ui.view.dataset.direction = 'remove'` is set by the take player at the start of each order and deleted when it
ends, so Addition Garden's DOM never carries it. All take-away CSS is scoped under
`[data-direction="remove"]` in a new `src/styles/fill-take.css` (exported as `@edulearnlabs/kit/fill-take.css`), so the
garden pays no CSS bytes either.

Layout sketch on the 960 by 600 scene (the art preview may move these; they are starting points):
- Basket: friend and order bubble top left as today, pad centered at x 250 to 590, y 300 to 480, water at x 620 to
  930, y 340 to 540, Hazel top right.
- Lantern: frames centered at y 300 to 470 inside the lantern art, night sky panel at x 600 to 930, y 120 to 290,
  Hazel (the lantern keeper) left. Session lights live along the top edge, y 20 to 110, above everything else.

### 4.3 Keyboard and screen readers
- `1`: send one (fast path). `Backspace`: call the last one back. Enter or Space on the pad picks; Enter on the water
  sends. Arrow keys move focus pad, water, help. Escape puts a picked frog down. Naming: `1` to `3` choose.
- The polite live region **never says the number the child will be asked for.** Parts: it says the water count
  ("2 frogs in the water."). Keep: it says the pad count ("Pad: 6 frogs."). Same rule as the add screen, which never
  says the total before the child names it.
- Focus is visible; after pointer input the naming step does not move focus (existing rule, existing code path).

### 4.4 Hint ladder (hints only, never the answer)

| Level | Name | Parts (hop away, lantern) | Keep | Trigger and cost (unchanged) |
|---|---|---|---|---|
| H1 | Look | Hazel points at the pad, the pad pulses, the order is spoken again (first time), `look` line on replays | same | 7 s idle or 1st overtake. Free |
| H2 | Count | "Let's count!" (voice finishes first), then badges 1, 2, 3 with ascending notes: first on the frogs already in the water, then on the pad frogs that should leave next (top slots) up to b | "Let's count!", then badges 1 to c on the frogs still on the pad, so the child can compare with N | 2nd overtake or a Hazel tap. Costs first try |
| H3 | Slots | Ghost ripples (`.ell-ghost-ripple`, dashed rings) in the water for the `W - o` frogs still to send; lantern: dashed ring on the cells that should empty (`.ell-cell.is-go`) | Stay rings (`.is-stay`) on pad slots 0 to N-1: "These ones stay!" | 3rd overtake or a 2nd Hazel tap. Costs first try |
| Naming H2 | Count-along | Wrong "how many left?" tap: that choice dims, the frogs still on the pad light one by one with ascending notes 1, 2, 3 | Wrong "how many hopped away?" tap: the frogs in the water light one by one | Existing rule: after 2 wrong taps only the right choice is left, and the child taps it |

**Why none of these is the answer.** Parts asks for what is left; H2 and H3 only mark the b frogs that leave, which
the order already says. Keep asks for what left; H2 counts the pad and H3 marks the N that stay, both given by the
order. The kit never shows, says or highlights the asked number before the child taps it (same test as today,
extended to remove and keep).

**Two kinds of notes, on purpose.** Leaving plays the count **still in the container** (falling: 7, 6, 5).
Counting plays **1, 2, 3** (rising). Leaving is "how many are here now"; counting is "how many have I counted".
Both come from `pitchFor`, so they always agree with each other.

### 4.5 Overtake (the overfill rule run backwards)
One too many: the frog leaps about 60 percent of the way to the water, wobbles in the air, and hops back to its
slot (420 ms). `audio.tryAgain()`, Hazel tilts her head (`nudge`). No buzzer, no red, the count never changes.
Recorded as `off-by-one` once per order (the child counted one past), exactly as overfill in the garden.

### 4.6 Reduced motion
Dragging still follows the finger. Removed: lift scale, leaps, drift sway, wobble, blink, the fold, confetti, the
end drift. Replaced by: the item fades out of the pad (150 ms) and fades in at the destination; the ripple becomes a
soft glow (opacity only, no scale); the hop-back fades out and back in at its slot; the 10 token cross-fades to the
loose fireflies; session lights are static (no blink); the end screen lantern fades its glow in.
Everything uses transform and opacity only.

## 5. Skin contract

### 5.1 New optional FillSkin fields (all additive; Addition Garden's skin sets none of them)

```ts
export type ExitStyle = 'fly' | 'leap' | 'drift';

export interface FillSkin {
  // ... existing fields unchanged ...
  /** v0.3.0. Container art per variant, drawn behind the items: lily pad (SVG on 340 x 180), lantern (SVG on
   *  620 x 260 around the two frames). Only the take player reads it. */
  container?: Partial<Record<FillVariant, string>>;
  /** v0.3.0. Destination art per variant (water, night sky): SVG on 320 x 180. */
  dest?: Partial<Record<FillVariant, string>>;
  /** v0.3.0. How an item of this kind leaves. Default "fly". */
  exit?: Record<string, ExitStyle>;
  /** v0.3.0, sessionReward "lights": the light symbol, its sky positions (scene px), and the end-screen lantern. */
  lights?: { symbol: string; viewBox?: string; at?: [number, number][]; lantern?: string; lanternViewBox?: string };
}
```
Item symbols keep the existing `items` map: `items.frog`, `items['frog-out']` (optional swimming pose),
`items.firefly`, `items['firefly-out']` (optional).

**Why named exit styles and not a skin callback.** A callback would let game code run arbitrary animation inside
the kit, and the kit could no longer promise "transform and opacity only, always with a reduced-motion version".
Three presets cover frogs, fireflies and a plain default; a fourth game that needs a new exit adds a preset to the
kit (reviewed once, used by everyone).

### 5.2 Exit presets (kit code in `fill-take.ts`)

| Preset | Motion (normal) | Twin at landing | Reduced motion |
|---|---|---|---|
| `fly` (default) | existing `fly()` arc 36 px, 240 ms | small glow at the landing spot | fade out, fade in |
| `leap` (frog) | squash (scale 1.1, 0.9) 80 ms, then `fly()` with arc 90 px, 320 ms | `.ell-ripple` ring: scale 0.3 to 1.6, opacity 0.8 to 0, 600 ms | fade, ripple becomes a soft glow |
| `drift` (firefly) | float up over 700 ms with a sideways sway of 12 px (3 keyframes), opacity blinks 1, 0.5, 1 | brief glow where it settles in the sky | fade, glow |
| hop back (overtake) | the same preset toward the destination for 60 percent, wobble, then back to the slot, 420 ms | none | fade out and back in |
| put back (undo) | the same preset, reversed, from the destination to the next free slot | none | fade |

### 5.3 Kit default skin (no art at all, the playground and tests still work)
- Items: the existing `ell-dot-sky` and `ell-dot-pink` circles.
- Container: the existing basket art for the basket variant, plain frames for the ten-frame variant.
- Destination: a rounded rectangle in soft blue (`basket`) or deep navy (`ten-frame`), 320 by 180.
- Exit: `fly`. Lights: a 12 px yellow circle at 10 fixed positions along the top edge; end lantern: a rounded
  rectangle with a glow layer. All inline SVG strings, about 0.3 KB brotli.

### 5.4 Session lights (the firefly reward)

- **What the kit does.** When `def.sessionReward?.type === 'lights'`, the runner shows no garden shelf. After each
  `session.resolve`, it adds light number `session.solved - 1` at `skin.lights.at[i]` (default positions if absent),
  rising from the container to its spot (600 ms, transform). Each light blinks with a fixed rhythm from a table,
  `BLINK = [2.4, 3.1, 2.7, 3.6, 2.2, 3.3, 2.9, 3.8, 2.5, 3.0]` seconds with offsets `i * 0.37 s`.
  **Fixed, never random** (decisions.md bans random rewards; "each with a different rhythm" only needs variety).
- **End screen.** `renderEndLights(endEl, before, skin, count, line)`: the lantern symbol in the middle, the `count`
  lights drift into it one by one (transform, 120 ms apart), then its glow layer fades to `0.3 + 0.07 * count`
  opacity. Line: `strings.glow` ("The pond is glowing!"). Count 0 (left before solving anything): nothing is drawn.
- **No sound of its own.** The right-answer chord already marks the moment; a second sound would crowd it.
- **What is NOT sent.** No `Reward` fact, no `rewards` field (section 3.5), no new message. The lights exist only in
  the DOM of this session. Play Again starts with an empty sky. Leaving early loses nothing that was promised.
- Website: the catalog entry for Pond Hop has no `"reward": "garden"`, so `HostInit` carries no `garden`.

## 6. Sound

| Moment | Call | Visual twin (always shown, sound on or off) |
|---|---|---|
| A frog or firefly leaves | `audio.count(count)` from the `placed` effect, where count is what is still in the container (8 frogs, 3 leave: 7, 6, 5) | Ripple ring (frog) or glow (firefly); the order bubble icon turns into a ripple outline |
| The ten breaks | `audio.bell()` | The 10 token opens into ten fireflies (the make-ten flip played backwards) |
| Overtake | `audio.tryAgain()` | Hop back with a wobble, Hazel tilts her head |
| Put back (undo) | `audio.tap()` | The item returns to its slot |
| Goal (pad goes calm) | none | Remaining items settle with one small bob, ripples fade |
| Right answer | `audio.chord(Number(item.answer))`: the number the child just named | The named group glows and bounces once (pad frogs for "how many left", water frogs for keep), big numeral |
| Then the sentence | voice: `takeAway` "Eight take away three leaves five!" | Text in the bubble |
| Hint lines, order | voice | Hazel pose plus the hint visual |

- **No new audio helper.** `count`, `bell`, `chord`, `tryAgain`, `tap` and `say` cover everything. `pitch.ts` is
  reused exactly as it is.
- **Voice finishes before tones** (playbook lesson): H2 counting and the naming count-along use the existing
  `sayThen` (voice with a 4.5 s cap, then notes). The right-answer chord plays at the tap (the 0.3 s feedback rule),
  and the sentence follows, as in the garden.
- **Crossing ten in the countdown.** `pitchFor` reuses notes 1 to 10 for 11 to 20 with the low ten bell under them.
  So 13, 12, 11 fall (E4, D4, C4, each with the bell) and then 10 jumps up to A5 without the bell. Inside each ten
  the notes always fall; the jump happens exactly when the ten opens, together with the bell and the fold. That is the
  same place-value story the garden tells going up, and the reason not to change `pitch.ts` (owner: "reuses
  `pitch.ts` as is").
- **Chord in keep mode.** The chord plays the number the child named (3 hopped away), with the 3 water frogs glowing.
  One rule for every mode: the chord is the sound of the answer, and the glow shows which group it counts.

## 7. game.json sketch for Pond Hop (`subtraction-grade-1`)

```json
{
  "schema": 1, "id": "subtraction-grade-1", "version": "1.0.0", "title": "Pond Hop",
  "grade": ["1"], "subject": "math", "topic": "subtraction", "skill": "math.subtraction.within-20",
  "mechanic": "fill-container",
  "session": { "maxQuestions": 10, "maxSeconds": 180 },
  "adapt": { "upAfterCorrect": 3, "downAfterWrong": 2 },
  "choices": { "count": 3, "distractors": ["off-by-one", "wrong-operation", "off-by-two"] },
  "sessionReward": { "type": "lights" },
  "kinds": { "frog": ["frog", "frogs"], "firefly": ["firefly", "fireflies"] },
  "strings": {
    "take": "{n} {kind} {is} going for a swim!",
    "takeFrame": "{n} {kind} {is} flying home!",
    "keep": "Leave {n} {kind} on the pad!",
    "askLeft": "How many {kind} are on the pad?",
    "askLeftFrame": "How many {kind} are still here?",
    "askGone": "How many {kind} hopped away?",
    "takeAway": "{a} take away {b} leaves {left}!",
    "dragOut": "Help them hop!",
    "look": "Look at the order!",
    "slotsOut": "Look at the ripples!",
    "slotsKeep": "These ones stay!",
    "glow": "The pond is glowing!",
    "here": "Lily pad", "away": "Water", "hereFrame": "Lantern", "awayFrame": "Night sky"
  },
  "levels": [
    { "id": "within-5", "difficulty": 1,
      "generator": { "type": "arithmetic", "op": "-", "a": [2, 5], "b": [1, 4], "resultMin": 1, "resultMax": 4 },
      "fill": { "variant": "basket", "goal": "parts", "direction": "remove", "binKind": "frog", "ask": "total" } },
    { "id": "within-10", "difficulty": 2,
      "generator": { "type": "arithmetic", "op": "-", "a": [4, 10], "b": [1, 7], "resultMin": 1, "resultMax": 9 },
      "fill": { "variant": "basket", "goal": "parts", "direction": "remove", "binKind": "frog", "ask": "total" } },
    { "id": "keep", "difficulty": 3,
      "$comment": "b is the number KEPT on the pad; the result is the number that hopped away (section 2.3)",
      "generator": { "type": "arithmetic", "op": "-", "a": [5, 10], "b": [2, 8], "resultMin": 1, "resultMax": 8 },
      "fill": { "variant": "basket", "goal": "keep", "direction": "remove", "binKind": "frog", "ask": "total" } },
    { "id": "teen-minus-small", "difficulty": 4,
      "generator": { "type": "arithmetic", "op": "-", "a": [11, 15], "b": [1, 4], "resultMin": 10, "resultMax": 14 },
      "fill": { "variant": "ten-frame", "goal": "parts", "direction": "remove", "binKind": "firefly", "frames": 2, "ask": "total" } },
    { "id": "cross-ten", "difficulty": 5,
      "generator": { "type": "arithmetic", "op": "-", "a": [11, 18], "b": [3, 9], "resultMin": 3, "resultMax": 9 },
      "fill": { "variant": "ten-frame", "goal": "parts", "direction": "remove", "binKind": "firefly", "frames": 2, "ask": "total" } }
  ]
}
```
Notes:
- `$comment` on a level is for this doc only. The validator does not reject unknown level keys today, but the
  implementer should drop it from the real file (or move it to the game README) to keep game.json clean.
- Level 5: `resultMax: 9` with `a >= 11` forces every question to cross ten (a - b < 10 < a). Level 4:
  `resultMin: 10` forces no crossing. Both are checked by the generator walk (enough questions: 14 and 40).
- Hit targets: the pad, the water, Hazel's help button and the choices are each at least 64 px at 1024 by 768 and at
  667 by 375 landscape (e2e checks it, section 8.3).

## 8. Tests

### 8.1 Existing tests that must stay green

Unchanged and green after every step:
- `tests/fill.test.ts`: every test in "fill: building", "fill: ten-frame", "fill: hint ladder", "fill: How many?",
  "fill: input paths", "speciesFor", "planEndGarden" (32 tests).
- `tests/content.test.ts`: "generate" (3), "buildChoices" (2), "levels and words" (2), "fill-container content"
  (13, including "refuses an item it cannot lay out", which still throws because `word-cat` is neither an addition
  nor a subtraction id and the level is add).
- `tests/session.test.ts`: "Session" (11), "starsFor" (1), "Session.resolve (fill-container)" (8, including
  "leaves quiz records exactly as in v0.1.0" and "grants a reward ... `solved` is 2").
- `tests/pitch.test.ts` (5), `tests/host.test.ts` (2).
- `tests/validate.test.ts`: all, including "agrees with build/schemas/fill-container.schema.json on every enum"
  (passes because both enums change together) and "the fill playground game validates".
- `tests/fill-e2e.cjs`: every existing Addition Garden check on `/fill.html`, unchanged.

**The one deliberate test edit:** `validate.test.ts` "rejects direction \"remove\" (reserved) and an unknown variant"
asserts the old message `direction can only be "add"`. "remove" is no longer reserved, so this test becomes
"rejects direction \"remove\" on an addition generator, and an unknown variant": same fixture
(`levels[0].fill.direction = 'remove'` on an op `+` level), now expecting `/direction "remove" needs a generator
with op "-"/` and `/variant must be/`. This is the only existing assertion that changes, and it changes because the
feature it guarded now exists.

### 8.2 New unit tests

`tests/fill-golden.test.ts` (written in step 0, on v0.2.0 code, before any change):
- "add reducer replays match the v0.2.0 golden file": 12 scripted action lists over the existing `basket`, `frame`,
  teen, total and tiny specs (drops, overfills, removes, ticks to 30 s, help taps, wrong and right names), each
  replayed with `replay`, the `{ state, effects }` list stored with `toMatchFileSnapshot('golden/fill-add.json')`.
- "fill questions and garden records match the v0.2.0 golden file": a seeded `Session` on `fillDef`, 10 questions
  through `fillQuestion` (seeded rng), resolved with a fixed script (first try, miss, overfill mistakes, rewards), the
  10 `FillQuestion`s plus `record()` (with `id`, `startedAt` and reward `id`/`at` masked) stored as
  `golden/garden-session.json`.

`tests/fill.test.ts`, new describe "fill: take away (direction remove)", spec `q-8m3` (prefill 8, want 3, target 5):
1. "starts full: totalCount is a, and a move reports the count still in the container": first `drop` gives
   `placed { bin: 'a', count: 7, part: 1 }`.
2. "8 frogs, 3 leave: the notes are the counts 7, 6, 5": `placed` counts equal `[7, 6, 5]`.
3. "the goal is met when exactly b have left, then How many? opens": phase `naming`, effects include `goal`, not
   `complete`.
4. "a 4th frog hops back: count stays 5, overfill then H1": last two effects `overfill`, `hint` level 1, `overfills` 1.
5. "overtake is one off-by-one per order and climbs H1, H2, H3": three overtakes give hint levels `[1, 2, 3]`,
   `mistakes` equal `['off-by-one']`, `hintsShown` 2.
6. "calling a frog back is free": drop, remove gives `returned { count: 8 }`, `hint` 0, `overfills` 0.
7. "never takes from an empty container (defensive)": a state with 8 placed returns `empty`.
8. "naming: right on the first tap gives a first-try outcome; a wrong tap dims and records its planned kind": with
   naming `{ answer: '5', choices: ['4', '5', '11'], mistakes: { 4: 'off-by-one', 11: 'wrong-operation' } }`.
9. "never emits the answer before the child taps it": as the existing test, effects JSON has no `"5"`.
10. "keyboard, tap and drag give identical states for take-away": as the existing input-paths test.

New describe "fill: keep", spec `q-8m5` (prefill 8, target 5, no want):
11. "goal when the container holds N": three drops, phase `naming`.
12. "taking the container below N hops back": 4th drop is `overfill`, count stays 5.
13. "H1 points at the destination until the goal": `need: 'a'` before, `undefined` after.
14. "the naming answer is what left (item answer of q-8m5 is 3)": naming built from `buildChoices(itemFromId('q-8m5'))`
    contains `'3'` as the answer and `'13'` as `wrong-operation`.
15. "overtake and hints map to the same outcome as add": `complete.outcome` equals
    `{ firstTry: false, hints: 0, mistakes: ['off-by-one'] }` after one overtake.

New describe "fill: lantern (ten-frame remove)":
16. "starts with the first ten whole": `initFill(q-13m5).tenMade` is true.
17. "13 - 5 breaks the ten once, right after the move that empties frame 2": counts `[12, 11, 10, 9, 8]`,
    `ten-broken` appears exactly once, at effect index 3 (right after the 3rd `placed`).
18. "no break when the goal lands on 10 (14 - 4)": no `ten-broken`, phase `naming`.
19. "no second break after a put-back and a new move": one `ten-broken` total.
20. "teen minus small never breaks (15 - 3)": no `ten-broken`.
21. "add specs never emit ten-broken": every golden add script has no `ten-broken`.

`tests/content.test.ts`, new describe "fill-container take-away content":
22. "q-8m3 at a remove level: prefill 8, want 3, target 5, one destination bin of the level's binKind, no spare".
23. "q-8m5 at a keep level: target 5 (kept), no want, answer 3".
24. "lantern frames: 2 when a > 10, 1 otherwise".
25. "take-away layout ignores the rng": two seeds give equal specs.
26. "a remove level refuses an addition item" (`q-3-4` throws with the op "-" message).
27. "fillQuestion keeps the item id, answer, choices and planned distractors; wrong-operation is the sum": over a
    seeded Pond session, `fq.choices` equals `q.choices`, and for `q-8m3` the `wrong-operation` choice is `'11'`.
28. "takeLine: 'Three frogs are going for a swim!', 'One frog is going for a swim!', 'Leave five frogs on the pad!',
    'Five fireflies are flying home!'".
29. "no garden reward on take-away questions": `fq.reward` is undefined for the Pond def.
30. "a missed keep item comes back as a hop-away practice order": `practiceItems: ['q-8m5']` at level 2 gives a
    parts order with want 5, target 3.

`tests/session.test.ts`:
31. "omits rewards but keeps hints when no order carried a reward": record has `hints`, no `rewards` key.
32. "solved counts every resolved order, reward or not".

`tests/pitch.test.ts`:
33. "inside one ten a countdown strictly falls": `pitchFor` of 8, 7, 6, 5 and of 15, 14, 13, 12, 11 strictly fall.

`tests/validate.test.ts`, new describe "validateGameDef: take-away":
34. "accepts the Pond Hop design (section 7)".
35. "remove needs op '-', add needs op '+'" (R5).
36. "keep needs remove, total is not allowed with remove" (R2, R3).
37. "remove rejects spare and a prefill other than 'a', and needs binKind" (R6, R7, R8).
38. "remove needs b of 1 or more and resultMin of 1 or more" (R9, R10).
39. "a pad shows at most 10 and a lantern at most 10 per frame" (R11, R12).
40. "hand-written items cannot use remove or keep yet" (R4).
41. "sessionReward is lights, fill-container only, not with reward" (R14).
42. "the pond playground game validates" (`dev/pond-game.json`).

### 8.3 Browser tests (`tests/fill-e2e.cjs`) and the dev fixture

Dev fixture (new files, kit repo):
- `dev/pond-game.json`: the section 7 game with id `kit-pond-playground`, `maxQuestions: 10` (the playbook lesson:
  a 5-order fixture let checks skip silently).
- `dev/pond-skin.ts`: placeholder art only (green frog circle with two eye bumps, `frog-out` head, yellow firefly,
  green pad, blue water, navy sky, simple lantern, dusk backdrop), `exit: { frog: 'leap', firefly: 'drift' }`,
  `lights` with 10 positions. Target under 2 KB brotli.
- `dev/pond.ts` and `dev/pond.html`: like `dev/fill.ts`, but
  `startGame(def, { mechanics: { 'fill-container': fillTakeAway }, skin: pondSkin })` and both CSS files.
- `vite.config.ts`: add `pond: 'dev/pond.html'` to the inputs and `ELL_PAGE=pond`.

`fill-e2e.cjs` changes:
- `hostPage` takes `?page=` (default `fill`), so every existing call is unchanged.
- An init script (per context) wraps `OscillatorNode.prototype.start` to push `this.frequency.value` into
  `window.__notes`, and stubs `speechSynthesis` to record utterance start and end times (the playbook's way to prove
  voice-before-tones).
- New helpers: `readTake(g)` reads `data-start`, `data-want`, `data-keep` (never text) and returns
  `{ start, send, answer }`; `dragOut`, `tapOut` (tap pad, tap water) and keys `1`.

New runs, each printing one `ok` line per check:
1. `pond-l1` (level 1, modes drag, tap, keys): every order builds and names; order 1 notes: the primary notes after
   the order equal `pitchFor(start - 1 ... start - send)` ("ok pond-l1: leave notes fall 7, 6, 5"); a wrong choice
   dims and the right one stays enabled; a light appears per solved order (`.ell-fill-light` count equals orders).
2. `pond-overtake` (level 2): send `send + 1`; after 800 ms `data-count` still equals `start - send`, no element with a
   failure class, phase still `build` or `naming`; H1 effect visible (Hazel `is-point`).
3. `pond-keep` (level 3): orders read `data-keep`; the choices include `start - keep`; naming right completes.
4. `pond-lantern` (level 5): `.ell-frame.is-ten` count is 1 at the start, 0 after the move that empties frame 2
   ("ok: the ten opens"), the bell frequency (130.81 Hz) is recorded at that move.
5. `pond-reduced` (level 2, `reduced=1`, `audio=0`): the session completes; lights have no running animations
   (`getAnimations().length === 0`).
6. `pond-phone` (667 by 375 landscape): pad, water, help and choices are at least 64 by 64 px.
7. `pond-voice` (level 2): a Hazel tap during build; the first count note starts after the "Let's count!" utterance
   ended.
8. End of each Pond run: `GameCompleted` sent, `'rewards' in session` is false, `hints` is a number, `completed`
   true, no `profile` anywhere; end screen shows `.ell-fill-endlights` with as many lights as solved orders and the
   `glow` line.
9. Regression: the full existing garden suite on `/fill.html` runs first and must print exactly the same checks as
   before (no new skips).

Outside the kit (step 11 below): re-pin `addition-grade-1` to the new kit commit with no other change, then
`npm run build`, `npm run typecheck`, `npm run test:e2e`. They must pass unchanged. That is the real proof of I1 to I5.

## 9. Size budget

| Piece | Who pays | Estimate (brotli) |
|---|---|---|
| Reducer remove branch, `goalMet`/`needBin` lines | all fill games | +0.15 KB |
| `buildTake`, `takeLine`, `minusParts` | all fill games | +0.25 KB |
| Session `solvedCount`, `rewarded` | all games (session is shared) | +0.03 KB |
| `fill-take.ts` (take player: board, input wiring, exits, ripple, H2/H3 views, settle, celebrate) | `fillTakeAway` only | +3.0 KB |
| Session lights and end lantern | `fillTakeAway` only | +0.5 KB |
| Kit default art for dest, lights, lantern | `fillTakeAway` only | +0.3 KB |
| `fill-take.css` | games that import it | +0.9 KB CSS |
| Validator and schema | build time only | 0 |

- Addition Garden after a re-pin: about **+0.4 KB** JS, 0 CSS. Quiz games: about +0.03 KB.
- Pond Hop: kit JS about **21 KB** (today's fill kit about 17 KB plus about 4 KB). That is over the 15 KB target the
  owner already set aside; record it in the README numbers table. Before Play stays far under 100 KB (the garden
  page is 59 KB; Pond adds about 5 KB).
- Trim candidates if it ever matters: share the input wiring between `playOrder` and `playTakeOrder` (about 1 KB,
  but touches the garden screen, so only with a garden re-test), drop the end lantern drift, default art.

**Why a separate take player costs more bytes but is still right:** the add screen is about 700 lines of closures
around one order. Putting a direction branch into each of its pieces would be smaller, but every branch would be a
new way to break the live garden. A separate file means the garden screen code is not edited at all. The bytes only
land in games that import `fillTakeAway`.

## 10. Risks and the cut line

### 10.1 Risks
1. **Two kinds of fireflies on lantern levels.** The child's items fly into the sky, and reward lights also live in
   the sky. A child might count the reward lights. Mitigation: reward lights stay on the top edge, smaller (60
   percent) and dimmer; the destination is a framed sky panel; the art preview must show both at once.
2. **"How many left" then "how many hopped away".** At level 3 the question flips. The most natural wrong answer is
   N itself (naming what stayed), which is not a planned distractor (`off-by-two` sometimes produces it). Mitigation:
   the first keep order shows the `dragOut` pill and Hazel says the keep line; the ask line is spoken; when the
   question appears, the water frogs bob once (points at the group, not at a number). If parents' data shows many
   misses at level 3, a later release can add an "other group" distractor kind (a website change, so not now).
3. **The countdown note jumps up at 10** (section 6). Accepted, mirrors place value, together with the bell.
4. **Shared reducer regression.** Mitigated by the golden tests (written first) and the garden re-pin smoke test.
5. **Website parent tip is addition-only.** `mistakeTip['wrong-operation']` says "subtracts instead of adding". For
   Pond Hop it must read "adds instead of taking away". This is a website change (Sonnet), keyed by the game's
   `topic` or `skill`. Without it, the grown-ups page gives a wrong tip.
6. **Crowded landscape scene on the lantern** (two frames, lantern art, sky panel, Hazel, order). Settle it in the
   static art preview before building the screen.
7. **Lifting "the last frog" instead of the touched one** may surprise a child (section 4.1). Watch in the browser
   check; switching to "the touched frog leaves and the rest re-pack" is screen-only and does not touch the reducer.
8. **Touch on real tablets** is still unverified for the garden too (known gap). Same mitigation: tap-to-pick works.

### 10.2 Cut line (cut in this order, stop as soon as it fits)
1. **End-screen drift.** Show the lantern with its glow and the lights already inside. Saves about 0.2 KB and a
   tricky end animation. Teaching impact: none.
2. **The animated fold.** Keep the reducer's `ten-broken` effect and its tests (cheap and important), but play the
   reduced-motion version for everyone: the bell plus a 300 ms cross-fade from the 10 token to ten fireflies. The
   child still sees the ten open; only the flip animation goes. Do NOT cut the token itself: a lantern that never
   shows the ten as one unit loses the "13 = 10 and 3" picture, which is the point of level 5.
3. **Lantern art hooks** (`container['ten-frame']`). Plain frames with the night backdrop. Pure looks.
4. **Keep (level 3).** Only if the screen work for it slips (the reducer part is about 10 lines and should stay).
   Remove `goal: "keep"` from `FillGoal`, the schema enum, R2 and R3, the keep tests (11 to 15, 23, 30), and the keep
   view code (badge, stay rings, water count-along). Pond Hop level 3 becomes another hop-away level:
   `{ "id": "bigger-within-10", "generator": { "op": "-", "a": [6, 10], "b": [3, 7], "resultMin": 1, "resultMax": 7 },
   "fill": { "variant": "basket", "goal": "parts", "direction": "remove", "binKind": "frog", "ask": "total" } }`.
   Same level count, so start levels stay valid. What is lost: difference 3 from the game design ("a different
   question, not a reversed one"). My verdict: keep is small and should ship.

Never cut: overtake hop-back, tap and keys paths, the hint ladder, reduced motion, 64 px targets, the golden tests.

## 11. Implementation plan (for the implementer, in order)

Run `npm test` and `npm run typecheck` after every step. Commit to the working branch after each green step.

0. **Golden photographs (before touching any source).** Add `tests/fill-golden.test.ts` (section 8.2, two tests).
   Run once to write `tests/golden/fill-add.json` and `tests/golden/garden-session.json`. Commit. From now on these
   files must never change.
1. **Types** (`src/types.ts`): `FillDirection`, `FillGoal` with keep, `FillLevel.direction`, `FillSpec.direction`,
   `SessionRewardDef`, `GameDef.sessionReward`, new `GameStrings` keys, `ten-broken` in `FillEffect` (in `fill.ts`).
   Mirror in `planning/framework-spec.md` (fill-container paragraph, `sessionReward`, the `GameCompleted` note "garden
   games add `rewards`"). Typecheck.
2. **Reducer** (`src/fill.ts`): `totalCount`, `goalMet`, `needBin`, `takeOut`, the `drop` guard, `overfillStep` and
   `finishBuild` moved verbatim. Write tests 1 to 21. Golden must stay green.
3. **Session** (`src/session.ts`): `solvedCount`, `rewarded`, record rule. Tests 31, 32. Golden green.
4. **Content** (`src/content.ts`): `minusParts`, `buildTake`, `takeLine`, `fillQuestion` option. Tests 22 to 30, 33.
   Golden green.
5. **Validator and schema**: FILL enums, R1 to R15, the one edited test, tests 34 to 41. Add `dev/pond-game.json`
   and test 42.
6. **Shared screen helpers**: move `use`, `bump`, `cap`, `fmt`, `stripUndefined`, `symbolFor`, `mountUi`, `Ui`,
   `KIT_SYMBOLS`, `enter` verbatim from `fill-container.ts` to `src/mechanics/fill-common.ts`; turn the session loop
   into `runFill(ctx, session, cancel, ext?)` with `export const fillContainer = (c, s, x) => runFill(c, s, x)`.
   With no `ext`, `runFill` runs exactly today's code. **Checkpoint:** `npx vite build && node tests/fill-e2e.cjs`,
   garden suite fully green, fill page size unchanged within 0.05 KB.
7. **Take player** (`src/mechanics/fill-take.ts`): `playTakeOrder` (board, input wiring through `dragArea` with
   sources `pad` and `dest`, render, exits, ripple, hint views, settle, naming, celebrate), `createLights`,
   `renderEndLights`, and `export const fillTakeAway = (c, s, x) => runFill(c, s, x, { remove: playTakeOrder, lights })`.
   `runFill` chooses the order player by `fq.fill.direction` and throws `GameError` code
   `direction-not-supported:remove` if a remove order reaches plain `fillContainer`. Add `src/styles/fill-take.css`
   and the `./fill-take.css` export in `package.json`. Export `fillTakeAway` and `ExitStyle` from `src/index.ts`.
8. **Dev fixture**: `dev/pond-skin.ts`, `dev/pond.ts`, `dev/pond.html`, Vite input. Play it by hand with
   `npm run dev` on `/pond.html?level=1` to 5; read your own screenshots (playbook rule).
9. **Browser tests**: the `page` parameter, the note and speech stubs, runs 1 to 9 (section 8.3). Run in the
   background with an until-loop (playbook: never in the foreground). Look at two screenshots yourself.
10. **Size and docs**: `ELL_PAGE=fill` and `ELL_PAGE=pond` builds with `check-size.mjs`; add both numbers to the
    README table. README "v0.3.0" section (draft below). `package.json` version `0.3.0`. GAME_RULES needs no change.
11. **Garden regression outside the kit**: in `addition-grade-1`, change only the kit pin to the new commit,
    run build, typecheck and the throttled smoke test. Must pass with no edits. Revert the pin if the owner wants
    the garden to stay on v0.2.0 for now (it does not need anything from v0.3.0).
12. **Owner**: creates the `v0.3.0` tag on GitHub (tag pushes are blocked in cloud sessions). Until then Pond Hop
    pins the full commit SHA.

README note draft:
> **v0.3.0 (2026-11): take-away for fill-container.** New `direction: "remove"` (the container starts full and the
> child moves items out to a destination) and `goal: "keep"` (stop when N are left, then name how many left), the
> "break ten" moment on ten-frames, exit animations per item kind (`leap`, `drift`), and session lights
> (`sessionReward: { "type": "lights" }`, never stored). Opt in with the new runner `fillTakeAway` and
> `@edulearnlabs/kit/fill-take.css`. All additive: `fillContainer` and Addition Garden behave exactly as in v0.2.0
> (golden tests), quiz games are untouched, protocol stays 1. One small change: a fill game whose orders carry no
> stored reward now sends no `rewards` field instead of an empty list.

## 12. Decisions made (owner asleep; recommendation and reason for each)

1. **Reuse the reducer with a direction flag, no new state or action types.** "Count" always means what is in the
   container, so notes, overfill, hints and naming fall out for free. Fewer moving parts, one tested rule set.
2. **At a keep level, `q-AmB` reads "start with A, keep B, how many hopped away? A - B".** So `b` is the number
   kept and `item.answer` is the number that left. The naming answer is always `item.answer`, so
   choices, distractors, ids, practice and records need no code. (Brief's example `q-8m3` with asked 3 becomes
   `q-8m5` with answer 3 for the same picture.)
3. **Keep's wrong-operation distractor is the sum of the two shown numbers (8 + 5 = 13)**, computed by the existing
   `buildChoices`. Consistent with "wrong operation is the sum" and needs no new distractor kind (a new kind would
   need a website change).
4. **A separate take player behind an opt-in runner `fillTakeAway`.** The garden screen is not edited, and the
   garden ships none of the new bytes. Costs about 1 KB more than branching inside the add screen; safety wins for a
   live game.
5. **`sessionReward: { "type": "lights" }`, not `reward`.** `reward` keeps meaning "the website stores it";
   widening its type would break existing TypeScript. The kit sends nothing for lights.
6. **`rewards` is omitted from the record when no order carried a reward**; `solved` counts resolved orders. Both are
   provably identical for Addition Garden.
7. **The break-ten moment is "the 10 token opens back into ten fireflies"** (make-ten played backwards), emitted when
   the container reaches 10 by a move and more must still leave. The emptied second frame stays visible (empty
   cells), because seeing 10 left is the point.
8. **No new audio helper.** `audio.count(stillInContainer)` gives the falling notes; `pitch.ts` unchanged, including
   the jump at 10, which coincides with the bell and the fold.
9. **The right-answer chord is the number the child named** (remaining for hop away, removed for keep), with the
   named group glowing.
10. **Named exit presets (`fly`, `leap`, `drift`) instead of skin callbacks**, so the kit keeps its motion and
    reduced-motion promises.
11. **No spare items, no hand-written remove items, no zero result in v0.3.0** (validator rules R4, R6, R10). Each is a
    later, separate decision.
12. **The leaving item is always the last slot**, the ghost starts under the finger; the pad stays tidy and H3
    stay rings stay simple.
13. **The live region never announces the number that will be asked**: water count for parts, pad count for keep.
14. **Lights blink on a fixed rhythm table**, never random.

## 13. Where this doc and `planning/subtraction-pond-design.md` disagree or sharpen it

1. Game design section 5: "the frame folds into the 10 token". Here the opposite motion: the token **opens** into
   ten fireflies (break ten is make-ten backwards); the empty second frame stays.
2. Game design section 7: "the right answer plays the chord of the remaining number". True for levels 1, 2, 4, 5. For
   keep this doc plays the chord of the number named (how many hopped away).
3. Game design section 3: "Notes that go down". They go down inside each ten; at 11 to 10 the note jumps up with the
   ten bell (pitch.ts reused as is, as the design asked).
4. Game design section 6 "Not touched: session record". The record shape for Pond Hop differs in one way: no
   `rewards` key. Addition Garden's record is unchanged.
5. Game design section 3 table: reward is a "skin and a small kit hook". It is a kit feature (`sessionReward`,
   lights layer, end lantern) with skin art, about 0.5 KB.
6. Game design level 3 "b 2 to 8": read here as b = frogs that **stay** (section 2.3). Same numbers, now with a
   precise meaning.
7. Game design section 6 says the website needs no new store. Correct, but the parent tip for `wrong-operation`
   must become topic-aware (risk 5), or the grown-ups page gives an addition tip for a subtraction game.
8. Game design H2 "badges on the frogs that should leave" applies to hop-away levels; on keep, H2 counts the frogs
   still on the pad instead (the frogs to leave are not given in a keep order).

## 14. Implementation notes (kit v0.3.0, 2026-11-12)

Built on the kit working branch `ccr-d39a02df-81y4w7`, steps 0 to 10 of section 11, one commit per step. Steps 11
(garden re-pin) and 12 (tag) are left for the owner. Nothing from the cut line (section 10.2) was cut: the end-screen
drift, the animated fold, the lantern art hooks and keep all shipped.

**Golden files.** Written first on untouched v0.2.0 code (commit `6e79d3b`) and never changed after: 12 add reducer
scripts (`tests/golden/fill-add.json`) and a seeded Addition Garden session that starts at level 3 and climbs to the
ten-frame levels (`tests/golden/garden-session.json`), so both variants are photographed.

**Where the build differs from this doc, and why**
1. **Overtake cannot happen through the screen.** With one destination bin, the goal fires on the exact move that
   reaches `b` (parts) or `N` (keep), so the build is over before a child can send one too many (D6 always wins over
   D2 and D3). The hop-back exists and is unit tested (tests 4, 5, 12, 15), but in the browser the extra send is simply
   ignored. Browser check 2 therefore became "an extra send after the goal is ignored, nothing fails, idle gives H1"
   (`pond-extra`). Teaching effect: a child can keep sending until the pad goes calm without counting `b`. The
   How many? step still tests the skill. If this matters, a later release can let the child overtake (goal on a
   "Done" tap, or allow one extra move before the goal), which is a reducer decision for Opus.
2. **runFill sets `data-direction` per order** (`if (ext) ui.view.dataset.direction = fq.fill.direction`) instead of
   the take player setting and deleting it. Deleting it at the end of an order made the board jump back to the garden
   layout during the 900 ms praise pause. Plain `fillContainer` passes no `ext`, so the garden DOM never carries it.
3. **Container art boxes follow the approved art, not section 4.2.** Lily pad art is drawn on 560 x 200 (the pad in
   `brand/subtraction-pond`), the lantern art on a 440 x 500 box with the frames at (54, 144) (the jar). Kit default
   pad is a plain green ellipse instead of the basket art (the basket does not fit a 560 x 200 pad).
4. **Small additive skin and string fields not in section 5.1:** `customers[].happy` (the friend's happy pose on a
   solved order, the art has one per friend), `lights.at` may be one list or one list per variant (the pad sky and the
   lantern sky have different free space: the jar fills the lantern sky), and `strings.slotsOutFrame` (the lantern H3
   line; "Look at the ripples!" was wrong for dashed cells). Item poses are looked up by suffix: `<kind>-lift` (being
   dragged), `<kind>-air` (in flight), `<kind>-out` (in the destination), `<kind>-gone` (ghost in an emptied
   lantern cell). All optional.
5. **Lantern lights live over the water at the left**, not along the top edge. The top edge sits under the shell's top
   bar on phones and wide screens, and the right side is the night-sky drop zone, where the child's own fireflies go
   (risk 1). Pad lights form an arc in the open sky between the order bubble and Hazel.
6. **The How many? card** moves to the top middle on the pad (narrower than drafted, so Hazel's bubble never covers
   it) and stays in the left bubble on the lantern (a centered card covered the jar).
7. **Fill page cost of the shared loop.** Step 6 alone grew the Addition Garden page JS by 0.17 KB brotli, not the
   0.05 KB the checkpoint asked for: the direction dispatch, the GameError for a remove order on plain
   `fillContainer`, and the lights hook live in the shared loop. The garden screen code itself is unchanged and the
   garden browser suite printed exactly the same 137 checks as v0.2.0. Whole release on the garden page: +0.53 KB
   (section 9 estimated +0.4 KB). Pond page: 27.6 KB JS with 5.4 KB of art, so about 22 KB of kit (estimated 21).
8. **Pond dev skin is the real approved art**, not placeholder shapes (owner request), so it is about 6 KB brotli
   instead of under 2 KB. It only ships in the playground and in Pond Hop.

**Pre-existing flake.** The v0.2.0 baseline browser run (before any change) failed once on "H2: exactly one count
badge is showing" (a timing check); later runs passed it.

**Results.** 138 unit tests (94 before, plus the 2 golden tests and tests 1 to 42 of section 8.2), typecheck clean.
Browser: garden 137 checks ok, pond 190 checks ok (`tests/fill-e2e.cjs`; `ELL_E2E=pond` reruns only the pond part).
Sizes per page are in the kit README, section v0.3.0.

**Still open for the owner:** step 11 (re-pin addition-grade-1 and run its smoke test), step 12 (tag v0.3.0), the
website parent tip for `wrong-operation` (risk 5), and real touch devices (risk 8).
