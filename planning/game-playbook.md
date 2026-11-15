# Game playbook: how we plan, build and ship an EduLearnLabs game

Written 2026-11-12 after Addition Garden 2.0. Read this first in any new session, then the CLAUDE.md files.
It records what worked, what went wrong, what is reusable, and what is still open.

## 1. State of play (end of 2026-11-12)

| Item | State |
|---|---|
| Website (`dr-nithish-kanna/edulearnlabs`) | Live on GitHub Pages at niftygamesstudios.in/edulearnlabs/. Last deploy: PR 4 merged, run succeeded. |
| Kit (`dr-nithish-kanna/edulearnlabs-kit`) | v0.2.0 at commit `9eb375e`. **The tag is NOT on GitHub yet** (tag pushes are blocked in cloud sessions). Owner creates it, then re-pin the game to `#v0.2.0`. |
| Game (`dr-nithish-kanna/addition-grade-1`) | Addition Garden 2.0.0, pinned to kit `9eb375e` by full SHA. Synced into the website at game commit `c8a9ce7`. |
| Working branch (all three repos) | `ccr-f8003f39-7xjp6m`. Main of the website already contains it (PRs 3 and 4). |
| Owner's testing | Owner played it and said it works. A formal checklist on a real tablet and phone was offered but not confirmed. |

Open items: kit tag, real-device touch and sound check, a parent "My garden" page on the website,
small kit items (duplicate symbol ids on the end screen, `strings.drag` overrides both variants,
`FillSkin.garden` allows one seed and one sprout for all species, back button touches the order bubble at 667x375,
a thin sand edge under the shelf on some wide screens), a real portrait layout (today portrait phones get a
"Turn your phone sideways" screen), and the quiz mechanic still shows the answer after a second miss
(conflicts with the "hints only" rule; changing it changes live quiz games, so it needs its own kit release).

## 2. The process that worked (repeat it for every game)

1. **Creative planning first, no code.** Owner said the first build felt "like an AI slip". So every game now starts
   with a discussion: 5 to 9 ideas grouped as (A) how the child does the skill, (B) what the child gets, (C) how it
   feels. Owner picks. Then write a design doc in `planning/` and let the owner critique it.
2. **One hands-on mechanic per game, with its own reward and feel.** Not "cards with dots". The child moves things
   and sees the skill happen (combine groups, make ten, sort, build).
3. **Lock decisions in writing** (owner decisions section in the design doc), including the defaults you chose.
4. **Opus for shared logic and data shapes** (kit changes, schemas, message contract, storage). Run it as a
   background Opus subagent with a long, self-contained prompt. Sonnet is fine for art, copy, CSS, small fixes.
5. **Design pass before code**, written to a doc, with a numbered list of owner decisions and a recommendation each.
   Example: `planning/fill-container-design.md` (it found a real flaw in our plan: bins that hold exactly the two
   parts let a child win without adding, so the order names the parts, bins hold spares, then a "How many?" tap).
6. **Art preview approved before development.** A static HTML/SVG page in `brand/<game>/` (see
   `brand/addition-garden/index.html`). Owner approves look, cast and reward, then development starts.
7. **Build bottom-up, test after every step:** pure logic with unit tests, then content generation, then the
   screen layer, then browser tests, then docs.
8. **Verify in a real browser** with the pre-installed Playwright Chromium. Read the screenshots yourself.
9. **Ship order:** kit commit, re-pin game, game smoke test, sync build into website, website tests, PR to `main`,
   merge, confirm the Pages run succeeded.

## 3. Design principles we settled on (apply to every game)

- Child plays, parent pays. No login, no ads or prices in games, no external links, no child data collected.
- Hints only, never the answer. A wrong choice dims, an overfilled item hops back. No red X, no buzzer, no failure
  screen, no streaks, no leaderboards, no wilting rewards.
- Rewards are light and the website owns them: Your Own Garden in Addition Garden (one seed per solved order,
  fixed species cycle, growth by sessions played never by time). The game only reports `rewards`.
- Tiny stories frame each round (a customer with an order). Cast for Addition Garden: ladybug, snail, bee, rabbit.
- Sound: numbers map to a pentatonic scale (1 to 10 on C4, 11 to 20 reuse notes plus a low "ten bell"). Every sound
  has a visual twin because many children play muted.
- Voice first: the voice line finishes BEFORE any tone starts (we had to fix tones masked by speech).
- Hit targets at least 64 px. Drag plus tap-to-pick then tap-to-place plus keyboard. Reduced-motion version of
  every animation, transform and opacity only.
- Reading load: short words, pictures and voice carry meaning (ages 5 to 7).
- Budget is secondary to feel for now: before Play 100 KB firm, kit about 18 KB (over the 15 KB target, accepted).

## 4. What is reusable now

- **fill-container** (kit v0.2.0): drag items from bins into a container until a target is reached, then a
  "How many?" naming step. Variants: `basket` (two part bins) and `ten-frame` (stones). Also fits counting,
  subtraction (take away), make-ten and sharing games with new content and a new skin.
- **Kit pieces:** session record and adapt rules (`Session.resolve()`), content generators with planned
  distractors, pitch helpers (`src/pitch.ts`), drag layer (`src/drag.ts`), hint ladder (look, count, slots),
  rotate prompt for upright phones, `planEndGarden`, mechanic registry (quiz-only games ship no drag code).
- **Website:** local progress store with garden section, newer-schema guard (never overwrite a newer saved
  document), `player.ts` that sends `garden` in HostInit and stores `rewards` from GameCompleted, game catalog
  `src/data/games.json`, `npm run sync-game -- ../<game-repo>`.
- **Template:** `templates/game-repo/` (CLAUDE.md and GAME_RULES.md) for each new game repo.

## 5. Lessons and pitfalls (each one cost us time)

- **Labels on overlapping objects get hidden.** Numbers on every flower hid behind neighbours and bringing them to
  the front was ugly. Fix: one badge at a time in a top layer. Rule: never rely on a per-item label inside a
  crowded group.
- **Check every character and every screen size in a real screenshot.** Rabbit ears were clipped (SVG viewBox
  had no headroom), a snail eyestalk started outside the neck, and wide screens showed a seam between the side
  bands and the scene. Extend backdrop art past the scene edges (`overflow: visible`, sky and hills drawn far
  beyond 0 to 960, gradients in `userSpaceOnUse`). Cropping the top instead pushed the order bubble under the top bar.
- **A test check that silently skips proves nothing.** Two of our new checks never ran (the element was already
  hidden, and the dev fixture had only 5 orders). Make every new check print an "ok" line and look for it.
  Pure logic (like `planEndGarden`) should have unit tests so it does not depend on a long browser session.
- **The scene is built after Play is tapped.** Tests must tap Play before looking for game elements.
- **Fixed 960 x 600 scene shrinks on upright phones** (about 39 percent, targets about 25 px). Today: rotate prompt.
  A true portrait layout is future work and should be designed per scene.
- **Speech synthesis:** wait for the voice promise (with a timeout) before counting tones. In tests, stub
  `speechSynthesis` to prove ordering.
- **Hooks and permissions:** a stop hook keeps asking to commit. The owner now trusts us to commit and push to the
  working branch, then ping after. See the CLAUDE.md rule updated on 2026-11-12.
- **Tag pushes are blocked in cloud sessions** ("unexpected disconnect"). Branch pushes and PRs work. The owner makes
  tags and releases on GitHub. Until then, pin an exact commit SHA.
- **Do not run a long browser test in the foreground** (120 s limit). Start it in the background and wait with an
  until-loop that checks for the final line. Do not start two copies at once.
- **Subagent reports are claims.** Open at least two screenshots yourself and re-run the key test before telling the
  owner it works.
- **Never use em dashes** in docs or copy (owner rule). Brand is "EduLearnLabs".

## 6. Commands cheat sheet

- Kit: `npm test`, `npm run typecheck`, `npx vite build && node tests/fill-e2e.cjs <screenshot dir>` (about 2 minutes),
  size check `node build/check-size.mjs dist`.
- Game: `npm run typecheck`, `npm run build` (size check included), `npm run test:e2e` (throttled profile).
- Website: `node --test tests/progress.test.ts`, `npm run build && npm run test:e2e`,
  `npm run sync-game -- ../<game>` (game repo must be committed and clean).
- Deploy: push branch, open PR into `main`, merge, check the "Deploy website to GitHub Pages" run.
- Notion: log each work session in "Nithish Kanna's Dashboard", Study Sessions database (Topic "Other" fits project
  work; fields: Session, Date, Topic, Exercises done, Mistakes to remember, Next step, Minutes).

## 7. Template for planning the next game (do this before any building)

1. Pick the game from `planning/mvp-games.md` (or propose one). State the one micro-skill and the grade.
2. Offer 5 to 9 creative ideas in three groups: how the child does the skill, the reward, the feel.
   Say which reusable mechanic each needs (existing `fill-container`, `quiz`, or a new kit mechanic).
3. Recommend a short combination. Critique the owner's picks honestly. Flag Opus-sized work.
4. Ask the owner only the questions that change art or data (cast, reward species, wording level).
5. Write `planning/<game>-design.md` with defaults for unanswered questions, then the owner critiques it.
6. If a new kit mechanic is needed: Opus design pass doc first, then implementation.
7. Static art preview in `brand/<game>/`, owner approves, then build.

## 8. Update 2026-11-13: Letter Workshop (game 3, first language game)

- Built unattended, same process as Pond Hop. Game repo `dr-nithish-kanna/word-building-grade-1` (synced at `36d8b2e`),
  kit v0.4.0 at `fc6a32b5c2a9de112875d38ceb1e1eb2f9ef21d8` (new mechanic `slot-build`, design in
  `planning/slot-build-design.md`). Both are untagged; the owner makes tags `v0.2.0`, `v0.3.0` and `v0.4.0` on GitHub.
- Website: persistent word wall in the progress store (`walls`, own `v`, facts only), `HostInit.wall`, `/language-games/` category
  (nav says "Reading games"), game page, letter mistake tips. Decisions: `planning/word-building-decisions-log.md`.
- New lesson: check `git log` of every repo against section 1 at the start. The kit checkout was stale (v0.1.0) while the real work
  was on another branch. Fan out in parallel (kit Opus agent, scene art, picture art), then game build and website store in parallel.
- Open: parent "My word wall" page, real-device touch and speech check, friends hold a placeholder card, kit layout is fixed
  (slots centered) so the preview's easel-left layout was not reproduced, recorded voice for words, portrait layout.

## 9. Update 2026-11-13 (later): game 4 planning started, Memory Match (Quilt Picnic)

- Owner chose MVP number 17, asked for basics only, then went to sleep. Draft design with defaults: `planning/memory-match-design.md`.
  Nothing built. Needs an Opus design pass for the new `pair-match` kit mechanic before any code.
- Reminder: the kit's latest work (v0.4.0) is on branch `ccr-d63a6d4f-g77ft0`, not on the branch the session started on. Check `git branch -r` first.

## 10. Update 2026-11-13 (night): website support for Quilt Picnic (game 4, first logic and memory game)

- Built unattended, same recipe as Letter Workshop (commits `cdef932`, `e784fb2`, `82677bb`). Game id `memory-match-prek`, kit v0.5.0
  mechanic `pair-match`, reward type quilt. Decisions: `planning/memory-match-decisions-log.md`.
- Progress store: `quilts[profile][game]` (own `v`, newer-schema guard, facts only, deduped by reward id, 200 cap that folds the oldest
  into a count), `HostInit.quilt` (newest 64 slugs, oldest first), `kind: "patch"` rewards stored by `addSession`, `misses` kept in the
  stored session. Protocol stays 1.
- Pages: `/logic-games/` (nav label "Memory games") and `/logic-games/memory-match-for-preschool/`, catalog entry, skill
  `logic-memory.memory.matching-pairs`, home card, privacy text. The sitemap is generated, so it needed no change.
- New testing trick: before a game is synced, the play round trip runs against a labelled STAND-IN frame (the site's own 404 page posting
  `GameReady`, same origin and sandbox). It proves the website side only. After the sync, the same checks run against the real frame.
- Still to do by the owner or the next session: sync the game (`npm run sync-game -- ../memory-match-prek`), which also brings
  `poster.webp` (the catalog points at `play/memory-match-prek/poster.webp` and the source commit says PENDING until then), then
  `npm run build && npm run test:e2e` and look for the lines that say `[real game frame]` and no `SKIPPED` line. Open: parent "My quilt" page.

## 11. Update 2026-11-13 (night): Quilt Picnic built and synced (game 4)

- Game repo `dr-nithish-kanna/memory-match-prek`, branch `ccr-4d0bb17c-4dbh4d`, synced at `cb9cbc9`, pinned to kit v0.5.0 at
  `24257a2e4c97354baafc24751f5668ce40808aac` (untagged; owner creates `v0.2.0` to `v0.5.0`). Not merged to `main` and not deployed.
- Built unattended: Opus agent for the kit mechanic and design (`planning/pair-match-design.md`), Sonnet agents for the art preview and
  website support, game built by hand from the Letter Workshop pattern. Game smoke test 50 of 50, website e2e 120 ok with the real game
  frame, progress tests 59 of 59, `planBoard` never relaxed for any picture on any level.
- Open: owner reviews design defaults (title, `upAfterCorrect` 1, level 5 colour variants), real-device touch check, "My quilt" parent
  page, pair-match card art has the matched pair staying on the board (the preview showed matched cards collected top left).
