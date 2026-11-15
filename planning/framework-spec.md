# Shared game framework spec (v1.1, 2026-11-11)

Status: **v1.1, approved by owner 2026-11-11.** No code yet.
Builds on `planning/decisions.md` (engine decision, "juicy but fair", budgets).

## 0. The big picture

```
Website (Astro, static)                         Game (own repo, Vite build)
+------------------------------------+          +---------------------------+
| SEO text, poster, Play button      |          | ell-kit (shared library)  |
| profile picker, parent gate        | postMsg  |  - host bridge            |
| progress store (localStorage)      | <------> |  - session engine         |
| ad slots + ad on/off flag          |          |  - juice, audio, drag     |
| <iframe src="/play/<game-id>/">    |          | game.json + content JSON  |
+------------------------------------+          +---------------------------+
```

Three ideas carry the whole design:
1. **The website owns everything about the child** (profiles, progress, settings, ads). The game owns only play.
2. **The game is a guest in an iframe** and talks to the website only through a small message protocol.
3. **Store facts, derive opinions.** We save what happened (sessions, answers). Stars, mastery and stickers are
   calculated from those facts, so we can change the formulas later without losing anyone's progress.

## 1. Taxonomy and IDs

Every ID is lowercase, stable, and never reused. Changing an ID breaks saved progress, so pick carefully.

| Field | Values | Example |
|---|---|---|
| `grade` | `prek`, `k`, `1` to `12` (array, a game can span grades) | `["1"]` |
| `subject` | `math`, `language`, `science`, `logic-memory` | `math` |
| `topic` | free slug inside a subject | `addition` |
| `skill` | global micro-skill ID, `subject.topic.detail` | `math.addition.within-20` |
| `mechanic` | `quiz`, `match`, `sort`, `order`, `memory`, `drag-drop`, `number-line`, `fill-container`, `slot-build`, `pair-match` (`drag-drop` and `memory` stay reserved, unused) | `quiz` |
| `difficulty` | integer 1 to 5, per level | `2` |

The list of valid skills lives in one file in the website repo: `content/skills.json`. A game may only use a skill
that is in that list. **Why:** mastery is tracked per skill, not per game. Later, two games (say a quiz and a number
line game) can both build mastery of `math.addition.within-20`, and the parent sees one honest skill picture.

## 2. Game definition: `game.json`

One file per game repo. It describes the game, and holds the content as levels.

```json
{
  "schema": 1,
  "id": "addition-grade-1",
  "version": "1.0.0",
  "title": "Addition Garden",
  "grade": ["1"],
  "subject": "math",
  "topic": "addition",
  "skill": "math.addition.within-20",
  "mechanic": "quiz",
  "session": { "maxQuestions": 10, "maxSeconds": 180 },
  "adapt": { "upAfterCorrect": 3, "downAfterWrong": 2 },
  "levels": [
    { "id": "l1", "difficulty": 1, "generator": { "type": "arithmetic", "op": "+", "a": [0, 5], "b": [0, 5], "resultMax": 10 } },
    { "id": "l2", "difficulty": 2, "generator": { "type": "arithmetic", "op": "+", "a": [1, 9], "b": [1, 9], "resultMax": 10 } },
    { "id": "l3", "difficulty": 3, "generator": { "type": "arithmetic", "op": "+", "a": [2, 10], "b": [2, 10], "resultMax": 20 } },
    { "id": "l4", "difficulty": 4, "items": [ { "id": "q-7-8", "prompt": { "text": "7 + 8", "say": "seven plus eight" }, "answer": "15" } ] }
  ],
  "choices": { "count": 3, "distractors": ["off-by-one", "off-by-two", "wrong-operation"] }
}
```

### Items and generators
A level holds either **items** (written by hand) or a **generator** (rules that produce items). Both are data.
- Use **items** for language games: words, sentences and pictures need a human to choose them.
- Use **generators** for math: 400 hand-written sums are slow to write and easy to get wrong. A generator with
  ranges is 1 line and always correct.

Every item, written or generated, has the same shape once loaded:

```json
{
  "id": "q-3-4",
  "prompt": { "text": "3 + 4", "say": "three plus four", "image": null, "visual": { "type": "dots", "groups": [3, 4] } },
  "choices": ["6", "7", "8"],
  "answer": "7"
}
```
- `id` must be stable (`q-3-4` always means 3 + 4). It is saved when missed, so we can practice weak facts later.
- `say` is the text for the voice line. Audio files are made at build time (section 7), so `say` maps to a file.
- `choices` are optional in content. If missing, the engine builds them from `choices.distractors`.

### Distractors (wrong choices) teach us something
A random wrong answer tells us nothing. A **planned** wrong answer tells us which mistake the child made.
For 3 + 4: `6` or `8` is off by one (counting slip), `1` is the wrong operation (subtracted). The engine records
which kind of mistake was picked, and the parent page can later say "often subtracts instead of adds".

### Mechanic-specific fields
Each mechanic adds its own small fields on top of the shared item shape. Examples:
- `sort`: `"bins": ["noun", "verb"]`, each item has `"bin": "noun"`.
- `order`: `"sequence": ["2", "4", "6", "8"]`.
- `match` and `memory`: `"pairs": [["cat", "img:cat"], ["dog", "img:dog"]]`.
- `fill-container` (kit v0.2.0, first game: Addition Garden): a level-wide `"fill"` block (`variant` basket or
  ten-frame, `goal` parts or total, `spare`, `prefill`, `binKind`, `ask`). Hand-written items carry an item-form
  `fill` (`target`, `bins`). Full shape: `planning/fill-container-design.md` section 2 and the kit's
  `build/schemas/fill-container.schema.json`.
  Kit v0.3.0 (first game: Pond Hop) adds take-away: `direction` `"remove"` (the container starts with `a`, the child
  moves items out to one destination; generator op `-`, `binKind` required, no `spare`, `prefill` only `"a"`) and
  `goal` `"keep"` (remove only: stop when N are left; at a keep level `q-8m5` reads "8, keep 5, how many left? 3",
  so the How many? answer is always `item.answer`). Hand-written items cannot use remove or keep yet. Optional
  game.json block `"sessionReward": { "type": "lights" }`: one light per solved order, drawn in the session only,
  never stored and never sent to the website; not allowed together with `reward`. Full shape:
  `planning/fill-container-remove-design.md` section 2.
- `slot-build` (kit v0.4.0, first game: Letter Workshop): letter tiles dragged into ordered slots to spell a word.
  Words are hand-written items (no generator, no `choices` block): `answer` is the word in lowercase a to z (2 to 8
  letters), `prompt.say` is what the voice says, `prompt.image` names the picture. A level-wide `"slot"` block plans the
  tray: `distractors` (0 to 4, default 1), `vowelTrap` (one distractor is a wrong vowel), `lookAlikes` (allow b/d style
  traps, default off), `given` (slots that start filled: a count or `[min, max]`). An item may add
  `"slot": { "given": [0], "tray": ["e", "h"] }`. At most 8 tiles per tray. A word id means one word in every level.
  Game-level `"reward": { "type": "wall" }`: one word card per solved word, stored by the website (the word wall).
  Letter mistakes are recorded as `letter-order`, `wrong-vowel`, `look-alike`, `wrong-letter` (each at most once per
  word). Full shape: `planning/slot-build-design.md`.
We define each one when its first game is built, not now. **Why:** designing 7 mechanics up front means guessing.
Designing each one against a real game means getting it right.

### Validation
A JSON Schema per mechanic checks content at **build time** (and in the editor). The validator is not shipped to
the browser. **Why:** it would cost bytes on every play to catch mistakes we can catch once, before release.

## 3. Session rules (built into the engine)

- **Length:** ends at `maxQuestions` or `maxSeconds`, whichever comes first. Never endless.
- **Start level:** the website passes a suggested start level based on past sessions (section 4). New children start at level 1.
- **Adapt:** 3 first-try correct in a row moves up one level. 2 wrong in a row moves down one level. Never spike
  more than one level.
- **Attempts:** wrong first try: gentle hint ("Let's count the dots"), then a second try. Wrong again: a stronger hint
  (never the answer itself; for example dim a wrong choice), so the child always makes the final tap. The character
  says "Now you know it!". No red X, no buzzer. Decided 2026-11-12: hints only.
- **First-try correct** is what counts for stars and mastery. Second tries still feel like wins to the child.
- **End screen:** always at least 1 star for finishing. Big Play Again button, and Back to Games. No autoplay.

## 4. Progress and mastery (stored by the website)

### Storage
- One localStorage key: `ell:v1`. One JSON document. Expected size: a few KB per child.
- If storage fails (private mode, full, blocked), the site keeps data in memory for that visit and the game still
  works. A child must never see an error because of storage.
- Changes in another tab are picked up through the `storage` event.

### Document shape

```json
{
  "schema": 1,
  "updatedAt": "2026-11-11T15:20:00Z",
  "activeProfile": "p_7k2m9q",
  "settings": { "audio": true, "music": true, "reducedMotion": false },
  "profiles": {
    "p_7k2m9q": { "id": "p_7k2m9q", "avatar": "fox", "color": "orange", "createdAt": "2026-11-11T15:00:00Z" }
  },
  "sessions": [
    {
      "id": "s_x81ka2",
      "profile": "p_7k2m9q",
      "game": "addition-grade-1",
      "gameVersion": "1.0.0",
      "skill": "math.addition.within-20",
      "startedAt": "2026-11-11T15:10:00Z",
      "durationSec": 142,
      "questions": 10,
      "firstTry": 8,
      "levelStart": 1,
      "levelEnd": 3,
      "maxDifficulty": 3,
      "completed": true,
      "missed": ["q-7-8", "q-6-9"],
      "mistakes": { "off-by-one": 2 }
    }
  ],
  "stickers": { "p_7k2m9q": [ { "id": "first-garden", "at": "2026-11-11T15:12:00Z" } ] }
}
```

Reward sections (website owned, facts only, each with its own sub-schema `v` so it can change without a top-level
`schema` bump; an unknown newer `v` is kept as is and never written to; a stored session never keeps `rewards`;
deleting a profile deletes both; stores saved before a section existed load with an empty one):
- `gardens[profile][game]`: `{ "v": 1, "items": [{ "id", "species", "at", "session" }], "meadow": {} }` (garden games).
- `walls[profile][game]`: `{ "v": 1, "words": [{ "wordId": "w-cat", "at": "2026-11-13T10:00:00Z", "session": "s_x81ka2" }] }`
  (word wall games, since 2026-11-13). Oldest first in the order saved on the device, one card per `wordId` (the first
  time stays), at most 200 cards per child per game. HostInit sends only `{ "words": [ids] }`.
- `quilts[profile][game]`: `{ "v": 1, "patches": [{ "id": "s_x81ka2-0", "patch": "dots-blue", "at": "2026-11-14T10:00:00Z", "session": "s_x81ka2" }], "folded": 0 }`
  (quilt games, kit v0.5.0, built on the website 2026-11-13). Oldest first in the order saved on the device, every patch
  kept (repeats of a patch slug are normal), deduped by reward `id` (which is kept in the entry), never more patches than
  questions in one session. At most 200 per child per game: past that the OLDEST fold into the `folded` count (the game
  continues its pattern from the newest patch, so freezing the quilt would freeze the pattern). HostInit sends only
  `{ "patches": [slugs] }`, at most the newest 64, oldest first. A stored session keeps `misses` (pair-match, 0 or more).

### Why this shape is ready to sync later
- **Sessions are facts** and are only ever added, never edited. Merging two devices later is simple: put both lists
  together and drop duplicates by `id`. No conflicts.
- **IDs are random** (`p_` and `s_` plus random characters), made on the device. No server needed to create them.
- **Times are UTC ISO strings.** **`schema` number** plus small migration functions let us change the shape safely.
- **Cap:** keep the last 50 sessions per profile per game. Older ones are folded into a small per-skill summary
  (`totals: { sessions, questions, firstTry }`) so nothing important is lost and storage stays small.

### Derived values (calculated, never stored as truth)

**Stars per session:** 1 star for finishing, 2 stars at 70% or more first-try correct, 3 stars at 90% or more.

**Mastery per skill**, 4 stages a parent can read and a child can see as a growing plant:

| Stage | Plant | Rule |
|---|---|---|
| New | seed | no sessions yet |
| Practicing | sprout | 1 or more sessions |
| Getting it | bud | a session at difficulty 3 or more with 80% or more first try |
| Mastered | flower | 2 sessions on **different days** at the top difficulty with 85% or more first try |

**Why "different days":** the spacing effect. Getting it right today, and still right on another day, shows the
skill is remembered, not just warmed up. This is the honest kind of "retention psychology": it builds memory, and it
gives a natural reason to come back without any pressure. The plant never wilts if a child stops playing.

**Suggested start level** for the next session: one level below the highest level reached last time, so the child
warms up with a success.

**Stickers** are earned at fixed milestones (first finished game, each mastery stage, first 3-star game). They are
never random. When a sticker is earned, the child **chooses** one of 3 designs for their book. Choice gives a
feeling of ownership without the slot-machine pull of a mystery reward.

## 5. Several children on one device (no personal data)

- **Profiles are an animal avatar plus a color.** Up to 12 per device (fits one 4 by 3 picker screen on a tablet). No names, no ages, no photos, no typing.
  **Why no free text:** kids type their real names, and then we hold personal data. Pre-readers also recognize
  "my orange fox" faster than a written name.
- **Grade is not stored per child.** The parent picks games by grade on the site. The engine adapts difficulty
  anyway, so we do not need it.
- **Who's playing?** The website shows a big avatar picker before Play when there are 2 or more profiles. With one
  profile, it is skipped (keeps "max 2 clicks to play").
- A first visit creates one profile automatically so a child can play straight away. Anyone can add a profile.
- **Delete profile and clear all data** sit in a small "Grown-ups" area and need a hold-to-confirm (press and hold
  3 seconds) plus "Are you sure?". **Why:** stops a child from wiping a sibling's garden by accident.
- **No parent gate at MVP** (owner decision 2026-11-11, see section 9). Add one when pricing, subscription or any
  external link arrives. Plan for it then: "type the number forty-seven" style, friction not security.
- Classrooms (30 children on one device) are a different product (teacher mode) and are out of scope here.
- Nothing about the child leaves the device. When accounts and sync come later, the parent creates the account,
  and the existing local profiles are uploaded under it with the parent's consent.

## 6. Game and website contract

### Hosting and embedding
- Game builds are served by the website at `/play/<game-id>/` (same domain). The game page has the SEO text first,
  then a poster image with a Play button.
- **Preload:** after the page has loaded and the browser is idle, the site prefetches the files in the game's
  `asset-manifest.json`. The bytes sit in the browser cache, so Play feels instant. Before Play, nothing heavy runs.
- **On Play:** the site replaces the poster with
  `<iframe src="/play/addition-grade-1/" sandbox="allow-scripts allow-same-origin" allow="autoplay; fullscreen" title="Addition Garden game">`.
  The sandbox blocks popups and navigating the top page, which enforces "no external links in games".
- **Why an iframe:** the game's CSS and JS cannot break the page, the page's ads and scripts cannot touch the game,
  and every game works the same way whatever the website changes.
- **Audio unlock:** browsers block sound until the user taps. The game's first screen is a big animated "Tap to
  start" character. That tap unlocks audio on every browser, including iPad Safari.

### Messages (postMessage, JSON, `protocol: 1`)
Both sides check that `event.origin` equals their own origin and ignore anything else.
Unknown fields are ignored on both sides. `protocol` only goes up when a field changes meaning or a new field becomes
required, so website and games can upgrade in any order.

**Website to game**

| Type | Data | When |
|---|---|---|
| `HostInit` | `protocol`, `avatar`, `color`, `startLevel`, `practiceItems` (recently missed item IDs), `settings`, optional `garden` (garden view, garden games only), optional `wall` (`{ words: string[] }`, word ids already on the child's word wall for this game, oldest first; word wall games only, kit v0.4.0), optional `quilt` (`{ patches: string[] }`, patch ids on the child's quilt for this game, oldest first; quilt games only, kit v0.5.0) | right after `GameReady` |
| `HostSettings` | `settings` | audio, music or motion toggled on the site |
| `HostPause` / `HostResume` | none | tab hidden or shown |

**Game to website**

| Type | Data | When |
|---|---|---|
| `GameReady` | `protocol`, `gameId`, `version` | game code loaded |
| `GameStarted` | `sessionId`, `startedAt` | child taps start |
| `GameCompleted` | the session record from section 4, without `profile`; fill-container games add optional `hints`, and garden games (stored `reward`) add `rewards`. Since kit v0.3.0 a fill game with no stored reward (Pond Hop, `sessionReward` lights) sends no `rewards` key at all. Since kit v0.4.0 word wall games (slot-build) send `hints` and one `rewards` entry per solved word, `{ id, kind: "word", wordId, at }` (`id` is session id plus question index, repeats of a word allowed: the website keeps the first per `wordId`), and `mistakes` may use the letter kinds. Since kit v0.5.0 quilt games (pair-match) send `hints` (Peeks and Sparkles), `misses` (total misses, never shown to the child) and one `rewards` entry per finished board, `{ id, kind: "patch", patch, at }` (repeats of a patch id are normal; the website keeps every entry, deduped by `id`) | end screen shown |
| `GameExit` | `reason`: `"home"` | child taps the in-game back button |
| `GameError` | `code` | something broke; site shows a friendly "Let's try again" |

The game never receives a profile ID, and never reads or writes localStorage itself. The website adds the profile
ID when it saves `GameCompleted`. **Why:** one owner of the data means one place to get privacy right.

**Dev mode:** when a game runs on its own (not in an iframe), ell-kit uses a tiny fake host that logs messages to
the console. You can build and test a game without the website.

### Ads (website only)
- Config in the website repo: `ads: { enabled: false }`. Read at **build time**, so ad slots are either in the
  layout or not. **Why build time:** a slot that appears after load pushes content down and breaks CLS 0.
- Slots sit below the game and in the sidebar on wide screens. Never over the game, never between Play and the
  game, never interstitial, never in the parent area.
- The game knows nothing about ads. Turning ads on later needs zero game changes.
- Analytics, if any, are cookieless and aggregate on the website only (page views, how many games finished).
  Nothing per child, nothing from inside the game to a third party.

## 7. ell-kit, the shared library

Its own repo (`edulearnlabs-kit`). Games install it pinned to a tag, for example `github:<owner>/edulearnlabs-kit#v1.0.0`.
**Why pinned:** updating the kit never silently changes a game that is already live. Each game upgrades on purpose.

| Module | Job |
|---|---|
| `host` | postMessage bridge, dev fake host |
| `content` | load `game.json`, run generators, build distractors |
| `session` | question loop, adapt, attempts, timing, end rule, session record |
| `juice` | spring animations (Web Animations API), squash and stretch presets, particle bursts, screen shake-free celebration, reduced-motion fallbacks |
| `drag` | Pointer Events drag with lift, shadow, magnetic snap, tap-tap fallback, keyboard support |
| `audio` | Web Audio manager, unlock, sound sprites, voice queue, music ducking under voice, mute |
| `ui` | tap-to-start screen, progress indicator, shared mascot slot, end screen with stars, back button |
| `mechanics/quiz` | the first mechanic. Others are added when their first game needs them |
| `mechanics/fill-container`, `mechanics/slot-build`, `mechanics/pair-match` | opt-in mechanics (v0.2.0 to v0.5.0); a game registers only the one it uses, so others ship none of their code (pair-match has no drag code at all) |

Budget: kit code 15 KB brotli or less. Game code on top: 15 KB or less. Art and audio are separate (after Play).

### Audio pipeline
- Voice lines from `say` fields are generated at build time with a good text-to-speech voice, reviewed by a human,
  and stored as files. **Why not the browser's built-in voice:** quality differs wildly between devices.
- Format: mono, 22 kHz, MP3 at 48 to 64 kbps (works everywhere). Short sound effects packed into one sprite file.

## 8. What a new game repo needs

```
game.json                  taxonomy, session rules, levels (content)
src/main.ts                starts ell-kit with the mechanic and theme
src/theme.css              colors and character for this game (from the style guide)
assets/img/                sprite atlases, 512 px max per sprite
assets/audio/              voice lines and sound sprite
public/poster.webp         poster for the website game page
scripts/check-size.mjs     fails the build if over budget
tests/smoke.spec.ts        Playwright: plays one full session, throttled
README.md                  game card, size and load table, any budget exception with reason
CLAUDE.md, GAME_RULES.md   copied from templates/game-repo/
```

Build output in `dist/`: the game files plus `asset-manifest.json` (list of files for the website to prefetch).
The SEO text for the game page lives in the **website** repo, because it is website content, not game content.

**Release flow (MVP):** tag a version in the game repo, a GitHub Action builds it and attaches `dist` to the release.
The website lists pinned game versions in `content/games.json` and copies those builds into `/play/` at build time.

## 9. Owner decisions (2026-11-11)
1. Friendly title on screen ("Addition Garden"), keyword name in URL and H1 ("Addition for Grade 1"). **Yes.**
2. Profiles per device: **12** (owner asked for more than 6).
3. Parent gate: **not at MVP.** Destructive actions use hold-to-confirm instead. Gate arrives with pricing or
   subscription. This updates the locked line in CLAUDE.md ("Settings and pricing sit behind a simple parent gate").
4. **One shared mascot** across all games. Outfits unlock through mastery and carry across games. The mascot is
   designed in the style guide step. The mascot reacts and celebrates, and never guilts a child into staying.
