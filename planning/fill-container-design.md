# fill-container: kit mechanic design (draft for review)

Status: DRAFT, 2026-11-12. Design only, nothing is built. Step 1 of the build order in `planning/addition-garden-design.md`.
Covers the kit mechanic, the question data, the message contract, the garden data on the website, sound hooks,
versioning and tests. Owner decisions are collected at the end (section 10.3).

Files read for this design: `CLAUDE.md`, `planning/decisions.md`, `planning/framework-spec.md`,
`planning/style-guide.md`, `planning/addition-garden-design.md`; kit `CLAUDE.md`, `README.md`, `src/types.ts`,
`src/game.ts`, `src/session.ts`, `src/content.ts`, `src/host.ts`, `src/audio.ts`, `src/juice.ts`,
`src/mechanics/quiz.ts`, `src/ui/shell.ts`, `build/validate.mjs`, `build/vite-plugin.mjs`, `tests/*`;
game `game.json`, `GAME_RULES.md`, `src/main.ts`, `tests/smoke.cjs`; website `src/scripts/progress.ts`,
`src/scripts/player.ts`, `src/data/games.json`, `tests/progress.test.ts`.

## 0. One critique before the design

The agreed plan says: order is 7, the two bins hold exactly 3 and 4. A child can then solve every order by
emptying both bins, without adding at all. The game would feel good and teach "move everything".

The design below supports three goal modes so we can choose (decision 1 in section 10.3):

| Mode | Order says | Bins hold | What the child does | Math situation |
|---|---|---|---|---|
| `total`, exact stock (plan as drafted) | "7 flowers" | exactly 3 and 4 | empties both bins | none really |
| `total`, spare stock | "7 flowers" | 5 and 6 | any mix that makes 7 | composing 7 (good for counting games) |
| `parts`, spare stock, then name it | "3 tulips and 4 daisies" | 5 and 6 | builds both groups, sees them merge, taps "How many?" (3 choices) | put together, total unknown (the core Grade 1 addition situation) |

**Recommendation: `parts` with spare stock and a short naming step.** Why: it follows "concrete, then abstract".
The child builds 3 and 4 with their hands (concrete), watches them merge, then names 7 (abstract). The naming tap
also gives us honest first-try data and reuses the planned distractors (off by one, wrong operation), so the parent
tips on the grown-ups page keep working. It is one tap, not a worksheet.

## 1. How fill-container fits the kit

### 1.1 What exists today (kit commit c883268, v0.1.0)

| File | What it does now | Reused as is? |
|---|---|---|
| `src/session.ts` | `Session`: picks items, two tries per question via `answer(choice)`, adapt up after 3 first-try right, down after 2 misses, end at `maxQuestions` or `maxSeconds`, builds the `SessionRecord` | Yes for level, adapt, timing, practice items, record. Needs one new method (`resolve`) |
| `src/content.ts` | `generate` (arithmetic generator), `itemFromId` (rebuilds `q-7-8`), `itemFitsLevel`, `pickItem`, `buildChoices` (planned distractors) | Yes, all of it. Adds `buildFill` |
| `src/host.ts` | postMessage bridge, `HostInit`, `GameMessage` union, dev fake host | Yes. Two optional fields added (section 5) |
| `src/game.ts` | `startGame`: shell, audio, host, then `runQuiz`. Rejects any mechanic that is not `quiz` | Changes: a small mechanic registry |
| `src/mechanics/quiz.ts` | The quiz screen loop, praise cycle, hint and reveal | Not touched. Its `wait` and `praiseCycle` helpers move to a shared file |
| `src/audio.ts` | Synthesized marimba notes on a 10 note pentatonic `SCALE`, `say` via browser speech | Yes. Adds `count(n)` and `chord(total)` (section 7) |
| `src/juice.ts` | `pop`, `wobble`, `bounceIn`, `pulse`, `confetti`, all with reduced-motion versions | Yes, all of it |
| `src/ui/shell.ts` | Start, play and end screens, Hazel, progress, speech bubble | Yes. Adds an end-screen slot for the game's reward scene |
| `build/validate.mjs` | Hand-written game.json checks at build time | Extended with `fill` checks |

### 1.2 What is new

| New file | Job | Pure? |
|---|---|---|
| `src/fill.ts` | The fill-container rules as a reducer: `reduce(state, action, now) -> { state, effects }` | Yes, fully unit tested |
| `src/pitch.ts` | Number to pentatonic pitch, chord of a total | Yes, tested |
| `src/drag.ts` | Pointer Events drag helper with tap-tap fallback (the `drag` module the framework spec already lists in section 7) | No (DOM), covered by the smoke test |
| `src/mechanics/fill-container.ts` | The screen: renders bins, container, order slip; turns pointer and key input into reducer actions; plays the effects | No (DOM) |
| `src/styles/fill.css` | Layout, lift shadow, slots, ten-frame, reduced-motion overrides | |
| `build/schemas/fill-container.schema.json` | JSON Schema for editors (VS Code autocompletes game.json). `validate.mjs` stays the build gate | |

**Why a reducer.** The kit rule is "logic goes in pure modules with tests". If the rules live in `fill.ts`, a test can
say "drop 4 tulips when 3 are wanted" and check that the 4th bounces back, with no browser. The DOM file only draws
what the reducer says. It also means tap, drag and keyboard all send the same actions, so they cannot drift apart.

**Why the logic never waits for animation.** A child who taps fast should not be able to drop 9 flowers while the
first one is still flying. The reducer updates the count at once; animations catch up. Overfill is decided at the
moment of the drop, not when the animation lands.

### 1.3 Mechanic registry (so quiz games do not pay for drag code)

Today `game.ts` imports `runQuiz` directly. If it also imported fill-container, every quiz game would ship the drag
code too. Proposal:

```ts
// game repo src/main.ts
import { startGame, fillContainer } from '@edulearnlabs/kit';
startGame(def as GameDef, { mechanics: { 'fill-container': fillContainer }, skin, endScene });
```

Quiz stays built in, so `startGame(def)` in existing games works unchanged. Vite drops any mechanic a game does not
import (tree shaking). `skin` gives the art for item kinds (tulip SVG, stone SVG) and `endScene` draws the garden.
**Why the game owns the art:** the kit is shared by 20 games. Tulips and lily pads belong to one of them. The kit ships
plain circles in sky and pink as the default skin, so the dev playground works with no art.

## 2. Question data

### 2.1 Design rule: keep the item, add a `fill` block

The loaded item keeps the exact shape from framework spec section 2 (`id`, `prompt`, `answer`). The mechanic adds one
`fill` block. **Why:** the id `q-3-4` already means 3 + 4 in the quiz version. Keeping it means:
- items a child missed in the old quiz (`practiceItems`) come back as Seed Stall orders after the upgrade;
- `itemFromId` and `itemFitsLevel` work with no change;
- the parent's skill picture stays continuous across the switch.

Levels keep the existing `arithmetic` generator. The layout comes from a level-wide `fill` block. **Why not a new
generator type:** the generator already guarantees correct sums, avoids repeats and is validated. A second generator
would duplicate all of that.

### 2.2 game.json (Addition Garden, proposed)

```json
{
  "schema": 1, "id": "addition-grade-1", "version": "2.0.0", "mechanic": "fill-container",
  "choices": { "count": 3, "distractors": ["off-by-one", "wrong-operation", "off-by-two"] },
  "reward": { "type": "garden", "species": ["sunflower", "tulip", "daisy", "lavender", "strawberry", "small-tree"] },
  "kinds": { "tulip": ["tulip", "tulips"], "daisy": ["daisy", "daisies"], "stone": ["stone", "stones"] },
  "strings": { "order": "{a} {kindA} and {b} {kindB}, please!", "ask": "How many flowers?" },
  "levels": [
    { "id": "within-5", "difficulty": 1,
      "generator": { "type": "arithmetic", "op": "+", "a": [1, 4], "b": [1, 4], "resultMax": 5 },
      "fill": { "variant": "basket", "goal": "parts", "spare": [1, 2], "ask": "total" } },
    { "id": "within-10", "difficulty": 2,
      "generator": { "type": "arithmetic", "op": "+", "a": [1, 9], "b": [1, 9], "resultMax": 10 },
      "fill": { "variant": "basket", "goal": "parts", "spare": [1, 3], "ask": "total" } },
    { "id": "bigger-within-10", "difficulty": 3,
      "generator": { "type": "arithmetic", "op": "+", "a": [3, 9], "b": [1, 7], "resultMin": 6, "resultMax": 10 },
      "fill": { "variant": "basket", "goal": "parts", "spare": [1, 3], "ask": "total" } },
    { "id": "teen-plus-small", "difficulty": 4,
      "generator": { "type": "arithmetic", "op": "+", "a": [10, 15], "b": [1, 5], "resultMax": 20 },
      "fill": { "variant": "ten-frame", "goal": "parts", "prefill": "a", "binKind": "stone", "spare": [1, 2], "ask": "total" } },
    { "id": "cross-ten", "difficulty": 5,
      "generator": { "type": "arithmetic", "op": "+", "a": [5, 9], "b": [5, 9], "resultMin": 11, "resultMax": 18 },
      "fill": { "variant": "ten-frame", "goal": "parts", "prefill": "bigger", "binKind": "stone", "spare": [1, 2], "ask": "total" } }
  ]
}
```

Notes:
- Level 1 changes `a` from `[0, 5]` to `[1, 4]`. "0 tulips and 3 daisies" is a fine idea for a later zero game,
  but at age 5 an empty bin you must not touch is confusing. Same level ids, so start levels still line up.
- `prefill: "bigger"` puts the bigger number on the frame first (for `q-5-8`, 8 stones are already there). That is
  the "start from the bigger number" strategy that makes crossing ten easy. The prompt still reads "5 + 8", which
  quietly shows that order does not matter.
- `spare` is how many extra items each bin holds beyond what is wanted. It uses the session's rng but never
  changes the item id, so practice and records are unaffected.
- `kinds` gives the singular and plural word for the voice line. Bin kinds for Seed Stall come from the reward
  species cycle (section 6.4), so "the tulip customer" earns a tulip seed. Ten-frame levels use `binKind`.

### 2.3 Loaded question (what the mechanic receives)

Example 1, Seed Stall, `q-3-4` at level 2:
```json
{
  "item": { "id": "q-3-4", "prompt": { "text": "3 + 4", "say": "Three tulips and four daisies, please!" }, "answer": "7" },
  "fill": {
    "variant": "basket", "goal": "parts", "target": 7, "prefill": 0, "direction": "add",
    "bins": [ { "id": "a", "kind": "tulip", "want": 3, "stock": 5 }, { "id": "b", "kind": "daisy", "want": 4, "stock": 6 } ],
    "ask": "total"
  },
  "choices": ["6", "7", "1"], "mistakes": { "6": "off-by-one", "1": "wrong-operation" },
  "reward": { "kind": "garden", "species": "tulip" },
  "level": 2, "difficulty": 2, "index": 4
}
```

Example 2, Stepping Stones, `q-5-8` at level 5 (crossing ten):
```json
{
  "item": { "id": "q-5-8", "prompt": { "text": "5 + 8", "say": "five plus eight" }, "answer": "13" },
  "fill": {
    "variant": "ten-frame", "goal": "parts", "target": 13, "prefill": 8, "frames": 2, "direction": "add",
    "bins": [ { "id": "b", "kind": "stone", "want": 5, "stock": 7 } ],
    "ask": "total"
  },
  "choices": ["13", "12", "3"], "mistakes": { "12": "off-by-one", "3": "wrong-operation" },
  "reward": { "kind": "garden", "species": "lavender" },
  "level": 5, "difficulty": 5, "index": 7
}
```
The 2nd stone placed fills the first frame. The reducer emits `ten-made`, the frame turns into one "10" token, and
the last 3 stones land on frame 2. The child sees 8 + 5 = 8 + 2 + 3 without being told.

Example 3, a future counting game (hand-written item, total mode, no naming step):
```json
{ "id": "count-6-apples", "prompt": { "text": "6", "say": "Put six apples in the basket" }, "answer": "6",
  "fill": { "variant": "basket", "goal": "total", "target": 6,
            "bins": [ { "id": "a", "kind": "apple", "stock": 9 } ], "ask": "none" } }
```

### 2.4 JSON Schema outline (`build/schemas/fill-container.schema.json`)

```json
{
  "$id": "fill-container", "type": "object",
  "properties": {
    "variant":   { "enum": ["basket", "ten-frame"] },
    "goal":      { "enum": ["parts", "total"] },
    "direction": { "enum": ["add"], "default": "add", "$comment": "\"remove\" reserved for take-away games" },
    "prefill":   { "oneOf": [ { "enum": ["a", "b", "bigger"] }, { "type": "integer", "minimum": 0, "maximum": 20 } ] },
    "frames":    { "type": "integer", "minimum": 1, "maximum": 2 },
    "binKind":   { "type": "string", "pattern": "^[a-z-]+$" },
    "spare":     { "type": "array", "items": { "type": "integer", "minimum": 0, "maximum": 5 }, "minItems": 2, "maxItems": 2 },
    "ask":       { "enum": ["total", "none"] },
    "target":    { "type": "integer", "minimum": 1, "maximum": 20 },
    "bins": { "type": "array", "minItems": 1, "maxItems": 2, "items": { "type": "object",
      "required": ["id", "kind"],
      "properties": { "id": { "enum": ["a", "b"] }, "kind": { "type": "string" },
                      "want": { "type": "integer", "minimum": 0 }, "stock": { "type": "integer", "minimum": 1, "maximum": 12 } } } }
  },
  "required": ["variant", "goal"]
}
```
Level form uses `prefill`/`spare`/`binKind`; item form uses `target`/`bins`. `validate.mjs` adds the rules a schema
cannot say well: `stock >= want`, ten-frame `target <= 10 * frames`, `ask: "total"` needs `choices` at game level,
`goal: "parts"` needs `want` on every bin, at most 12 items on screen (hit targets must fit), and `fill` is only
allowed when `mechanic` is `fill-container`.

**Additive or breaking: additive.** Every new field is optional on `Level` and `Item`. `Mechanic` gains one value.
An existing quiz game.json validates exactly as before. Nothing existing changes meaning. **Why `direction` is
reserved now but only `"add"` is accepted:** the framework spec says to design each mechanic against a real game.
We know take-away is coming, so we reserve the word, but we do not guess its rules until that game is built.

## 3. Interaction

### 3.1 State machine (one question)

```
 intro --(order spoken or first input)--> idle
 idle  --pointerdown on bin item--> pressing
 pressing --moved > 8 px--> dragging
 pressing --released, no move--> picked            (tap-to-pick)
 idle  --Enter/Space on bin, or key 1/2--> picked  (keyboard)
 picked --tap or Enter on container--> dropping
 picked --tap same item / Escape--> idle            (put back, no cost)
 picked --tap other bin--> picked                   (switch)
 dragging --release over container (+24 px margin)--> dropping
 dragging --release elsewhere / pointercancel--> idle (springs home, no cost)
 dropping --fits--> idle  (effects: note n, count badge)
 dropping --fits and makes 10 (ten-frame)--> idle (effects: ten-made)
 dropping --too many--> overfill --(item returns to its bin)--> idle
 dropping --goal met--> merging --> naming (if ask: total) --> complete
 naming --wrong tap--> naming (that choice dims, hint level up)
 naming --right tap--> complete
 idle --tap item in container / Backspace--> idle (item goes back to its bin, no cost)
 complete --> next question (session.resolve)
```
Hint level (0 to 3) runs beside this machine. It never blocks input.

**Why "dropping" does not lock the board:** the reducer already applied the drop. Only that one flying item ignores
new input until it lands (about 200 ms). Locking the whole board would make fast children wait, and waiting feels
like being punished.

### 3.2 Pointer Events plan (`src/drag.ts`)
- `pointerdown` on an item: `setPointerCapture`, remember `pointerId`. Ignore other pointers until release
  (two siblings on one tablet cannot tear an item in half).
- `pointermove`: store the position, apply it once per `requestAnimationFrame` as `transform: translate3d()`.
  Read the container rect once at drag start, never during the move. **Why:** reading layout on every move forces
  the browser to recalculate layout 60 times a second, which is exactly what stutters on an old Chromebook.
- Lift: scale 1.1 and fade in a pre-drawn soft shadow element (`opacity`). Never animate `box-shadow` (it repaints).
- Magnetic snap: within 24 px of the container, the item eases toward the next free slot.
- `pointerup` over the container: drop action. Elsewhere: spring home, no penalty. `pointercancel` (a phone call,
  a system gesture): spring home.
- `touch-action: none` on items and the play area so dragging never scrolls the page. No HTML5 drag and drop API
  (no touch support, as `decisions.md` already notes).
- Hit area: each item is a 64 px button even if the art is 48 px. GAME_RULES rule 3 says 64 px; the plan says 56 px.
  I recommend 64 px (decision 5).

### 3.3 Keyboard and screen reader basics
- Bins and the container are real `<button>`s. Individual flowers are `aria-hidden` decoration.
  **Why:** a screen reader user should hear "Tulip bin, 5 left", not 11 separate flower buttons.
- Keys: `1` or `2` takes one from bin 1 or 2 and places it (fast path, matches GAME_RULES "number keys").
  Enter or Space on a bin picks; Enter on the container places. Backspace returns the last item. Arrow keys move
  focus between bins and container. In the naming step, `1` to `3` choose, as in the quiz.
- A polite live region says the state after each change: "Basket: 2 tulips, 3 daisies". In `parts` mode it
  never says the total before the child names it.
- Focus is visible (thick teal ring), never removed.

### 3.4 Reduced motion
Dragging still follows the finger (that is direct control, not decoration). Removed: lift scale, wobble, bounce,
confetti, frame flip. Replaced by: instant snap with a 150 ms fade, the overfill item fades out and back in at its bin,
the ten-frame cross-fades to the 10 token, completion is a leaf-green glow.

## 4. Hints and adaptivity

### 4.1 Hint ladder (hints only, never the answer)

| Level | Name | Build phase shows | Triggered by | Costs first try? |
|---|---|---|---|---|
| H1 | Look | Hazel points, the bin that still needs items pulses, the order is spoken again | 7 s with no progress, or the 1st overfill | No |
| H2 | Count | Number badges light on placed items (1, 2, 3), per-bin ticks glow | 2nd overfill, or child taps Hazel | Yes |
| H3 | Slots | Ghost outlines show the spaces still empty for each part, grouped in fives | 3rd overfill, or 2nd Hazel tap | Yes |

Naming step: a wrong tap dims that choice (it stays visible, it just cannot be tapped) and starts the H2 count-along:
placed items light up one by one with their notes. After 2 wrong taps only the right choice is left, and **the child
taps it themselves**. The kit never says, highlights or animates the correct number before the child taps it.

**Why time alone only reaches H1:** a slow, careful thinker must not lose a star for thinking. Only mistakes or
asking for help move up the ladder. After H1 has played twice with no input, the screen goes quiet (Hazel blinks),
no nagging.

**Why this replaces the quiz rule "wrong again: show the answer":** dimming plus counting always ends in success, and
the success is the child's. This needs an amendment to GAME_RULES rule 5 and framework spec section 3 for this
mechanic (doc change, after approval).

### 4.2 Feeding the session
New method on `Session`, beside the untouched `answer()`:

```ts
resolve(outcome: { firstTry: boolean; hints: number; mistake?: DistractorKind }): void
```
- `firstTry` is true when the build had no overfill and no H2 or H3, and the naming step (if any) was right on the
  first tap.
- `firstTry: true` runs the existing `onFirstTryRight` (adapt up after 3). `false` runs the existing `onMiss`
  (adds the id to `missed`, adapt down after 2). So the adapt rules and `game.json` `adapt` values are reused as is.
- `mistake`: a wrong naming tap uses the planned distractor kind from `buildChoices`. An overfill counts as
  `off-by-one` (counted one past), at most once per question. **Why reuse:** the website's `mistakeTip` already has
  the right parent sentence for it ("counting slowly helps"), and no new mistake kind means no contract change.
- Rewards are granted on every completed order, first try or not. Stars measure accuracy; the garden rewards effort.
  Using a hint must never take a seed away.

## 5. Message contract

All changes are **additive and optional**, so `protocol` stays `1`. Rule to write into the spec: unknown fields are
ignored on both sides; the protocol number only goes up when a field changes meaning or a new field becomes required.
**Why:** a bump forces both sides to upgrade together. Additive fields let website and games upgrade in any order.

| Message | Change | Who uses it |
|---|---|---|
| `HostInit` | + `garden?: GardenView` (section 6.3). Sent only when the catalog entry has `"reward": "garden"` | Addition Garden |
| `GameCompleted.session` | + `hints?: number` (H2 and H3 shown this session), + `rewards?: Reward[]` | fill-container games |
| `GameGardenLayout` (new, later) | `{ items: [{ id, x, y }] }` when the child moves plants in the sandbox | sandbox step 7 |

`Reward` fact: `{ "id": "s_k3j9x2qa-4", "kind": "garden", "species": "tulip", "at": "2026-11-12T10:04:11Z" }`.
The id is the session id plus the question index, so it is unique and needs no random number.

Why rewards ride inside `GameCompleted` and not a new per-order message: `game.ts` already sends `GameCompleted` when a
child leaves early, so seeds earned before Back are kept. One message, one place to validate. (A closed tab mid-session
loses that session's seeds, as it already loses the session record today. Acceptable for MVP.)

**The kit reports:** session id, item ids, level start and end, max difficulty, first-try count, missed item ids,
mistake counts, hint count, reward facts.
**The kit must NOT report:** any profile id, name or age; pointer paths, drag timings or per-tap timestamps; device or
browser details; free text; audio. Per-order timing is not needed for learning and is behavioral data about a child.

Old and new together:
- New website, old quiz build: `garden` in `HostInit` is ignored by the old kit. Fine.
- Old website, new build: `rewards` is stored inside the session record and ignored. No garden, no crash.
- Deploy order: website first (tolerant of both), then the new game build.

## 6. Garden data (website, local only)

### 6.1 Shape inside the existing `ell:v1` document

```json
"gardens": {
  "p_7k2m9q": {
    "addition-grade-1": {
      "v": 1,
      "items": [
        { "id": "s_k3j9x2qa-4", "species": "tulip", "at": "2026-11-12T10:04:11Z", "session": "s_k3j9x2qa" },
        { "id": "s_k3j9x2qa-5", "species": "daisy", "at": "2026-11-12T10:04:40Z", "session": "s_k3j9x2qa",
          "x": 0.42, "y": 0.7, "movedAt": "2026-11-13T09:00:00Z" }
      ],
      "meadow": { "sunflower": 0 }
    }
  }
}
```
- Keyed by profile, then game, because the garden "lives only inside Addition Garden".
- `stage` is **not stored**. It is derived (section 6.2): "store facts, derive opinions" from framework spec section 0.
- `x`, `y` (0 to 1, relative to the plot) only appear once the child moves a plant in the sandbox.
- `v` is a small schema number for the garden alone.

**Why the top-level `schema` stays 1:** today `parseStore` returns an empty store when `schema !== 1`. If we bumped
to 2, a parent with an old tab still open after a deploy would load the new document as "corrupt", start empty, and
the next `save` would wipe every profile. An optional `gardens` field is safe: the old code spreads unknown fields
(`{ ...s, ...d }`) and writes them back untouched. Separately, `parseStore` should be fixed now to never overwrite a
newer schema (decision 7).

### 6.2 Growth rule: grows only when the child plays

```
stage(item) = min(2, number of this profile's sessions of this game, with at least 1 question,
                     that started after item.session started)
0 = seed, 1 = sprout, 2 = bloom
```
- Time alone never changes a stage: a child who returns after a month finds exactly what they left. Nothing wilts.
- Folded sessions (the 50-per-game cap in `progress.ts`) are safe: an item whose session was folded away has at least
  50 newer sessions, so it is a bloom anyway.
- Early exits with at least one solved order count as play (decision 3).

### 6.3 How the game shows the garden without knowing the profile
At `GameReady`, `player.ts` computes a view and sends it in `HostInit`:
```json
"garden": { "total": 23, "items": [ { "id": "s_k3j9x2qa-4", "species": "tulip", "stage": 1, "nextStage": 2 } ],
            "meadow": { "tulip": 4 } }
```
- `nextStage` is what the stage becomes if this session counts. The website owns the rule; the kit only animates
  `stage -> nextStage` on the end screen when at least one order was solved. **Why:** the rule then lives in one
  place. If we change it, no game needs a rebuild.
- `items` is the newest 30 for the plot; older blooms are summed into `meadow` counts (drawn as a soft meadow band).
  Storage keeps up to 300 items per profile per game, then folds the oldest blooms into `meadow`. 300 items at about
  90 bytes is 27 KB, well inside localStorage.
- No profile id, no timestamps beyond what is needed: the view has ids, species and stages only.

### 6.4 Species are never random
Next species = `species[(total + solvedThisSession) % 6]`, using `total` from `HostInit`. Seed Stall uses that species
for bin A, so the child sells tulips and earns a tulip seed. **Why not random:** `decisions.md` bans random or variable
rewards. A fixed cycle also gives every child a balanced garden, with no "rare" species to chase.

### 6.5 Sync later
- Items are append-only facts with device-made unique ids, like sessions. Merge = union by `id`.
- Layout is the only mutable part: last write wins per item by `movedAt`.
- `meadow` is recomputed from the merged list, never merged as numbers (adding two devices' counts would double).
- The parent's account upload (framework spec section 5) sends `gardens` with the profiles, with consent.

### 6.6 Website files that change
| File | Change |
|---|---|
| `src/scripts/progress.ts` | `GardenItem` type, optional `gardens` in `Store`, `parseStore` keeps it (and never overwrites a newer schema), `addSession` moves `record.rewards` into `gardens` (dedupe by id) and strips them from the stored session, `deleteProfile` removes the profile's gardens, new `gardenView(store, profile, game)`, new `setLayout` for the sandbox later, `DistractorKind` unchanged |
| `src/scripts/player.ts` | Add `garden` to `HostInit` when the game entry has `reward: "garden"`; handle `GameGardenLayout` later |
| `src/data/games.json` | Addition Garden entry: `mechanic: "fill-container"`, `reward: "garden"`, new pinned commit |
| `src/pages/math-games/addition-for-grade-1.astro` | SEO copy describes dots and choices today; rewrite for Seed Stall and Stepping Stones |
| `tests/progress.test.ts`, `tests/site-smoke.cjs` | Section 9 |
| `public/play/addition-grade-1/` | New build via `npm run sync-game` |
| `planning/framework-spec.md`, `templates/game-repo/GAME_RULES.md` | Mechanic list, messages, store shape, rule 5 amendment (doc changes after approval) |

## 7. Sound hooks

### 7.1 Number to pitch (`src/pitch.ts`, pure)
```ts
pitchFor(n: number): { freq: number; degree: number; ten: boolean }
chordFor(total: number): number[]   // three frequencies
```
- Numbers 1 to 10 climb the C major pentatonic from C4: C4 D4 E4 G4 A4 C5 D5 E5 G5 A5 (262 to 880 Hz).
- Numbers 11 to 20 reuse the notes of 1 to 10 and add a soft low "ten bell" (C3) underneath.
  **Why:** 20 straight pentatonic steps span 4 octaves, and the top notes are shrill on tablet speakers. Reusing
  the notes mirrors place value: 13 sounds like "ten, and 3". The ten-frame flip and the sound tell the same story.
- `chordFor(total)` stacks the total's note with the 2nd and 4th pentatonic steps above it. Any pentatonic stack
  sounds pleasant, so there is no wrong-sounding total.
- Out of range clamps (0 plays nothing, above 20 plays 20). The existing `SCALE` in `audio.ts` moves into `pitch.ts`.

### 7.2 Audio calls and their visual twins
| Sound | Call | Visual twin (always shown, sound on or off) |
|---|---|---|
| Drop note for running count n | `audio.count(n)` | Count badge pops on the item, part tick fills |
| Ten made | `audio.count(10)` + bell | Frame glows and turns into a "10" token |
| Overfill | `audio.tryAgain()` (existing soft two-note) | Item wobbles back to its bin, Hazel tilts her head |
| Merge | quick rising run of the part notes | Groups slide together, sparkle |
| Named the total | `audio.chord(total)` | Big numeral, flowers bloom, seed drops on the shelf |
| Hint | Hazel's voice line | Hazel's pose plus the hint visual itself |

- Voice is used for the order, hints and the merge sentence ("3 and 4 make 7"), not for every drop. Browser speech
  can lag by half a second, which would break the 0.3 s feedback rule. Notes are instant.
- Mute (`HostSettings.audio: false`): notes and voice are skipped; every visual twin still plays. Text bubbles show
  every spoken line. Pause (`HostPause`) suspends audio and freezes the hint timer.

## 8. Versioning

### 8.1 Kit tag: v0.2.0 (minor)
Everything is additive: optional fields, one new mechanic value, one new `Session` method, new exports, quiz untouched.
Under semver, a 0.x minor is the right signal for "new features, check the notes". Not 1.0.0 yet: the message contract
and data shapes should survive 2 or 3 mechanics before we promise stability.

### 8.2 README note (draft text)
> **v0.2.0 (2026-11)**: adds the `fill-container` mechanic (drag items into a basket or ten-frame), the `drag`
> helper, number pitch sounds (`audio.count`, `audio.chord`) and garden rewards. All additive: quiz games and
> `startGame(def)` behave exactly as in v0.1.0. New optional message fields: `HostInit.garden`,
> `GameCompleted.session.hints` and `.rewards`. Protocol stays 1. To use the new mechanic, pass it to
> `startGame(def, { mechanics: { 'fill-container': fillContainer } })`.

### 8.3 Migration for addition-grade-1 (pinned to c883268, v0.1.0)
1. Bump the kit pin to `#v0.2.0` with **no other change**. Build, run the smoke test. It must pass unchanged.
   This proves the release is additive.
2. Switch `game.json` to `fill-container` (section 2.2), add the skin and theme, bump the game to `2.0.0`
   (play changes, records gain fields).
3. Level ids and count stay the same, so `startLevel` from old quiz sessions still points at the right level.
   Item ids stay the same, so old `missed` items come back as practice orders.
4. Website: deploy the garden-aware `progress.ts` and `player.ts` first, then `sync-game` the new build and update
   the pinned commit.

What stays untouched: the live site keeps serving the quiz build pinned at `4281ebc` until `sync-game` runs. Stored
sessions are never rewritten. Any other quiz game on v0.1.0 needs no change at all.

## 9. Test plan

### 9.1 Kit unit tests (vitest, pure modules)
- `fill.ts`: a drop adds one; dropping past `want` (parts) or `target` (total) returns the item and emits `overfill`;
  overfill counts as a mistake once per question; removing an item is free; goal met only when every part matches;
  total mode accepts any mix; prefill counts toward the target; `ten-made` fires exactly once when the frame hits 10
  and the next item lands in frame 2; time alone never passes H1; 2nd overfill gives H2, 3rd gives H3; Hazel taps
  raise the level; `firstTry` false after H2; naming: a wrong tap dims it, after 2 wrong only the answer is left;
  keyboard actions and pointer actions produce identical states (same action list).
- `content.ts` `buildFill`: stock is at least want plus spare minimum; two bins have different kinds; kinds follow
  the species cycle; `prefill: "bigger"` puts the bigger addend on the frame; ids equal the quiz ids for the same
  sum; `itemFromId` practice items get a fill block for fill levels.
- `session.ts` `resolve`: first-try counting, adapt up after 3 and down after 2, missed ids, `hints` and `rewards`
  in the record, reward ids `<session>-<index>` unique, a reward on a non-first-try order. All existing session tests
  pass unchanged.
- `pitch.ts`: 1 to 10 strictly rising; n and n + 10 share a degree and set `ten`; every frequency is in the
  pentatonic set; out-of-range clamps.
- `validate.mjs`: good fill game passes; `fill` on a quiz game, `want > stock`, ten-frame target above capacity,
  `ask: "total"` without `choices`, and more than 12 items on screen all fail with clear messages; the schema file
  and the validator agree on shared fixtures.
- `host.ts`: `garden` passes through `HostInit`; unknown fields are ignored.

### 9.2 Website unit tests (`node --test tests/progress.test.ts`)
- Rewards move from a session into `gardens`, duplicates ignored, rewards stripped from the stored session.
- Stages: 0, 1, 2 across three sessions; a fake clock jumping 60 days changes nothing; an early exit with one order
  counts; a session with 0 questions does not.
- `gardenView`: newest 30 items, older blooms in `meadow`, `nextStage` correct; fold at 300 items keeps the total.
- `deleteProfile` and `clearAll` remove gardens. A document without `gardens` loads. A document with `schema: 2`
  is never overwritten.

### 9.3 Smoke test changes (`addition-grade-1/tests/smoke.cjs`)
- Read each order from `data-` attributes on the order slip (not by parsing text) and solve it three ways across the
  session: real drag (`page.mouse` down, move in steps, up), tap-tap, and keys `1`/`2`.
- Overfill once on purpose: check the item returns, no element with a failure class appears, and the session goes on.
- Naming step: tap one wrong choice, check it dims and the right one stays enabled; never auto-selected.
- `GameCompleted`: `rewards.length` equals solved orders, `hints` is a number, no `profile` field anywhere.
- `HostInit` with a garden fixture: end screen shows the plants and the stage change.
- A second run with `reducedMotion: true` and `audio: false` completes and shows count badges.
- Hit targets: every bin, item and choice bounding box is at least 64 by 64 px.
- Website `tests/site-smoke.cjs` `playFullGame`: switch to the keyboard path (keys `1`/`2`, then the choice).

### 9.4 Throttled profile checks (4x CPU, 1.6 Mbps, 150 ms)
- Start screen under 5 s (existing check).
- During a 2 second drag at 4x CPU: no long task over 50 ms (PerformanceObserver), at least 50 fps counted with
  `requestAnimationFrame`.
- Drop to note under 300 ms (timestamp from `pointerup` to the `count` call).
- Kit size: `npx vite build && node build/check-size.mjs dist` stays near 15 KB brotli. Estimate: today 8.8 KB plus
  about 4.5 KB (fill 2.5, drag 1.2, pitch and reward glue 0.8). A quiz-only build must not grow.
- Before release, one run on a real low-end device or cheap Android tablet (touch drag is the risk `decisions.md` names).

## 10. Risks, rejected alternatives, owner decisions

### 10.1 Risks
1. **Touch drag on iPad Safari and old Android.** Pointer capture and scroll quirks. Mitigation: `touch-action: none`,
   tap-tap always works, test on a real device before release.
2. **Kit budget.** 13 to 14 KB of 15 KB leaves little room for the next mechanics. Mitigation: registry and tree shaking,
   measure each release.
3. **Garden inflation.** 10 seeds per session can make each seed feel cheap. Mitigation: the plot shows 30, the meadow
   holds the rest (decision 4 if you prefer fewer).
4. **Rule drift between docs.** GAME_RULES rule 5 and framework spec section 3 still say "show the answer". Must be
   amended with this release or a future game will copy the old rule.
5. **Speech lag** makes voice unsuitable for drop feedback. Notes carry the instant feedback, voice the sentences.
6. **The "Come back and watch them grow" line** is a gentle return cue. It is honest (nothing wilts), but keep it
   calm and never tie it to time ("tomorrow").

### 10.2 Rejected alternatives
- **Two mechanics (seed-stall, ten-frame).** Same drag, same rules, different container. A `variant` field is cheaper.
- **A new `fill` generator type.** Would duplicate the arithmetic generator, its validation and its ids.
- **HTML5 drag and drop, or a canvas layer.** No touch support; DOM is fine for under 30 items.
- **Kit or game storing the garden.** Breaks "the website owns child data".
- **Deriving the garden only from session records.** Sessions fold at 50 per game and the sandbox needs positions.
- **Random species.** Banned variable reward.
- **A new `overfill` mistake kind.** `off-by-one` already says the same thing with a ready parent tip.
- **Bumping store `schema` to 2 or `protocol` to 2.** Old tab wipe risk, and forced lock-step upgrades, for changes
  that are purely additive.
- **A per-order `GameReward` message.** More surface; `GameCompleted` on exit already keeps earned seeds.
- **Revealing the answer after 2 misses.** Replaced by dimming, so the child always makes the final tap.

### 10.3 Decisions for the owner
1. **What the child computes in Seed Stall.** Recommend `parts` order with spare stock plus a one-tap "How many?"
   naming step. The drafted plan (total order, exact stock) can be solved by emptying both bins.
2. **Naming step on all 5 levels.** Recommend yes, including Stepping Stones, where the 10 token makes 13 readable.
3. **What counts as playing for growth.** Recommend any session with at least one solved order, finished or not.
4. **Seeds per order or per session.** Recommend per order (instant joy), with the 30 plant plot and meadow fold.
5. **Hit target size.** Recommend 64 px from GAME_RULES rule 3, not 56 px from the plan.
6. **Kit tag.** Recommend v0.2.0 (minor, additive), 1.0.0 after 2 or 3 mechanics prove the contract.
7. **Fix `parseStore` now** so it never overwrites a newer schema. Recommend yes, in the same website change.
8. **Species order.** Recommend a fixed cycle matched to the bin flowers, not a child pick after every order
   (10 extra choices per session is too slow; a pick could come later in the sandbox).
9. **Taxonomy.** Add `fill-container` to the mechanic list in the framework spec and `types.ts`; leave the unused
   `drag-drop` value for now. Recommend yes.

Opus note: decisions 1, 3 and 4 shape child data and learning. Review them on Opus before we lock them.

## 11. Owner decisions (accepted 2026-11-12)

The owner accepted all nine recommendations in section 10 as written: (1) order names the parts, bins hold spare
items, then a one-tap "How many?"; (2) naming step on all five levels; (3) any session with at least one solved
order counts as playing for growth; (4) one seed per order, newest 30 shown, 300 cap; (5) 64 px hit targets;
(6) kit tag v0.2.0; (7) fix `parseStore` so it never overwrites a newer schema; (8) fixed species cycle matching
the bin flowers; (9) add `fill-container` to the framework spec and `types.ts`, leave `drag-drop` unused.
GAME_RULES rule 5 and framework spec section 3 were updated to "hints only". Rule 3 stays at 64 px.
Section 10 item 4 (rule drift) is resolved for rule 5; the spec taxonomy edit for decision 9 happens with the kit work.
