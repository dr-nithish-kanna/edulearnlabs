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
  kit v0.4.0 at `5913c4da18a044bf41d9c72f397ec2b393983007` (new mechanic `slot-build`, design in
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
  `03ced466bb005cd8ba5d777248e263fe7b2e86f4` (untagged; owner creates `v0.2.0` to `v0.5.0`). Not merged to `main` and not deployed.
- Built unattended: Opus agent for the kit mechanic and design (`planning/pair-match-design.md`), Sonnet agents for the art preview and
  website support, game built by hand from the Letter Workshop pattern. Game smoke test 50 of 50, website e2e 120 ok with the real game
  frame, progress tests 59 of 59, `planBoard` never relaxed for any picture on any level.
- Open: owner reviews design defaults (title, `upAfterCorrect` 1, level 5 colour variants), real-device touch check, "My quilt" parent
  page, pair-match card art has the matched pair staying on the board (the preview showed matched cards collected top left).

## 12a. Update 2026-11-15: parked ideas (Quilt Picnic)

- Owner wants MVP focus. The matching-pairs family for advanced grades (kit v0.6.0 "two different faces" idea) and a longer Quilt Picnic session are saved in `planning/post-mvp-ideas.md`. Do not start them until the owner says development has reached those grades.
- Quilt Picnic polish (mini quilt alignment, flap opening) is on the working branch; the owner has not yet asked for a PR for it.

## 12. Update 2026-11-15: game 5 planning started, Count objects (Hedgehog Picnic)

- Owner chose MVP number 1 (Count objects 1 to 10, Pre-K). Picks: hedgehog cast, parade of animals reward, new `tap-count` kit mechanic.
  Draft design with defaults: `planning/count-objects-design.md`. Nothing built. Needs an Opus design pass (`planning/tap-count-design.md`) first.
- Reminder: check `git branch -r` in every repo first. The kit checkout on the session branch is stale (v0.1.0).
- 2026-11-15 (later): Opus design pass done (`planning/tap-count-design.md`, found 4 flaws in the first plan). Owner took all recommendations
  (section 13 "LOCKED"). Next: static art preview in `brand/count-objects/`, owner approves, then kit v0.6.0 `tap-count` (build from the real
  kit branch `ccr-4d0bb17c-4dbh4d` at 03ced46, not the stale checkout).
- 2026-11-15 (later): art preview built in `brand/count-objects/` (index.html, build.py, shots/). Awaiting owner approval of look, cast and parade species. The four nits (bunny ear clip, grid-like scatter, yellow chick next to the yellow duck, owl perch touching the blanket) were fixed the same day and re-checked in screenshots.
- 2026-11-15 (later): art preview approved. Kit v0.6.0 `tap-count` built by an Opus agent and verified: kit branch `claude/amazing-albattani-g2r7l1`,
  commit `a2d5ff8fd2cec502af688056550a8f8f92aea693` (untagged, pin by full SHA; owner makes tags v0.2.0 to v0.6.0). Verified here: 266 of 266 unit tests,
  typecheck clean, tap browser suite 124 ok. Tap page built alone: entry JS 17.9 KB, Before Play 57.8 KB, lazy fill-order chunk 7.6 KB, all in budget.
  Deviations (Done bell position, friend-only bubbles, extra idle nudges, validator stock rule, placeholder playground art) are listed in the kit README.
  Still to do: update `planning/framework-spec.md` for tap-count, create the game repo (`count-objects-prek`, owner decides), game scenes and art from
  `brand/count-objects/`, website parade store and page, real-device touch and speech check. Lesson: a wait loop that greps for "Error" matches "GameError"; grep the real final line.
- 2026-11-16: game 5 built. Game repo `dr-nithish-kanna/count-objects-prek` (created by the owner, empty private repo), branch `claude/amazing-albattani-g2r7l1`,
  head `04e4892afb42ed22d968adf9738acb05a6429f9a`, pinned to kit v0.6.0 `a2d5ff8fd2cec502af688056550a8f8f92aea693`. Game id `count-objects-prek`, title Hedgehog Picnic,
  skill `math.counting.count-objects`, page to build `/math-games/counting-for-preschool/`. Not merged, not deployed, no tag.
  Verified here: typecheck clean, build in budget (Before Play 61.4 KB, entry JS 21.4 KB, lazy fill chunk 7.6 KB), smoke test on the throttled profile 166 ok, 0 FAIL, screenshots opened.
  Kit gaps found by the game agent (go to an Opus kit release, v0.6.1): the friend never swaps to its happy pose, one picture per object kind so the second pebble drawing is unused,
  at 667x375 the level 4 "Give me N" bubble touches the Back button corner. Still to do: website side (progress store for the parade, game page, catalog, home card, privacy text),
  `framework-spec.md` update for tap-count, sync (`npm run sync-game -- ../count-objects-prek`), real-device touch and speech check, owner makes kit tags v0.2.0 to v0.6.0.

## 13. Update 2026-11-16 (later): website support for Hedgehog Picnic (game 5)

- Same recipe as Quilt Picnic (section 10). Game id `count-objects-prek`, kit v0.6.0 mechanic `tap-count` (plus fill on level 4),
  reward type parade. Decisions: `planning/count-objects-decisions-log.md`.
- Progress store: `parades[profile][game]` (own `v`, newer-schema guard, facts only, deduped by reward id, 200 cap that folds the oldest
  into a count), `HostInit.parade = { animals }` (newest 64, oldest first), `kind: "animal"` rewards stored by `addSession`. Counting tips
  for `skipped`, `off-by-one` and `off-by-two` on `math.counting.*` skills. Protocol stays 1.
- Pages: `/math-games/counting-for-preschool/` (keyword title "Counting Games for Preschool", ages 3 to 5), link from the `/math-games/`
  Pre-K section, catalog entry (source commit PENDING and poster `play/count-objects-prek/poster.webp` until the sync), skill
  "Counting objects" (`topDifficulty` 4), home card from the data, privacy text names the parade. Sitemap is generated.
- Smoke test: page checks plus a play round trip against the labelled STAND-IN frame; one `SKIPPED` line for the real game frame.
- Next: sync the game after the kit update (`npm run sync-game -- ../count-objects-prek`), then `npm run build && npm run test:e2e` and look for
  `[real game frame]` lines for Hedgehog Picnic and no Hedgehog `SKIPPED` line. Open: "My parade" parent page, real-device touch and speech check.
- 2026-11-16 (later): kit v0.6.1 final at `4641118373cc1cea073e8ffd781e27085e552938` (happy pose, several pictures per kind, level 4 bubble clear of Back). The pond e2e
  "regression" turned out to be flaky tests (random "send 1" orders and an extra digit key that picked a choice), fixed in the kit tests; the kit code did not change. Lesson: 3 runs
  proved nothing, 8 per version showed v0.6.0 failing as often (4 of 8) as v0.6.1 (3 of 8). Game `count-objects-prek` upgraded and synced at game commit `a7c04f6`
  (smoke test 178 ok on the throttled profile). Website `npm run build && npm run test:e2e`: PASS, 158 ok, 18 `[real game frame]` lines. Not merged to `main`, not deployed, no tag.
  Open: owner reviews and approves the PR into `main` (deploy), kit tags v0.2.0 to v0.6.1, poster crops the left edge on desktop (cosmetic), "My parade" parent page,
  real-device touch and speech check, other fill checks still use fixed sleeps.
- 2026-11-17: owner found three problems on the live Hedgehog Picnic: the "Tap to play" focus ring looked misaligned (the 6px press edge ran into the ring), the Done bell overlapped the parade shelf, and nothing told the child to ring the bell. Fixed in kit v0.6.2 (ring wraps the press edge, CSS only) and v0.6.3 (bell in the bottom right corner, first-time cue "Ring the bell when you are done." with a pulse, idle nudge pulses the bell, `strings.ringBell`, `TapSkin.bellCue`). Kit `3e0352d3f7f8e12a4de70edc3b86ad099880b55b`, 284 unit tests, tap suite 253 and 256 ok, fill 327, word 66, pair 68. Game `count-objects-prek` at `5f9eb45` (245 ok on my run, measured bell gaps: 20 px to the shelf on a phone, bell 65 px). Website e2e PASS 158 ok. Lessons: look at every screenshot a smoke test saves, not a sample (the shelf overlap was visible in two I never opened); a new first-time cue needs a visual twin; the page-copy word-count check caught my own added sentence.

## 14. Update 2026-11-16: game 6 built unattended, Bead Parlor (Color pattern repeat, MVP 18)

- Planning was attended (ideas, design doc, art preview, all approved by "defaults" and picks), the build ran unattended while the owner slept.
  Design: `planning/pattern-repeat-design.md`. Kit design pass by an Opus agent: `planning/token-slot-design.md` (picked option b, a thin
  `pattern-fill` runner over the unchanged slot-build reducer, so Letter Workshop is untouched). Website decisions: `planning/pattern-repeat-decisions-log.md`.
- Kit v0.7.0 at `4f0499c1c885eed83112f6f720c9ed11ddea6f7a` on kit branch `claude/upbeat-davinci-c55nml` (untagged, owner makes tags). Verified here:
  330 of 330 unit tests, typecheck clean. Game repo `dr-nithish-kanna/pattern-repeat-k` (owner created it, branch `claude/upbeat-davinci-c55nml`),
  synced at game commit `4165a65`. Game smoke test on the throttled profile passes (full 5-bracelet session, every level, 667x375 phone, no console
  errors, no storage). Before Play 56.5 KB, entry JS 18.3 KB. Website: 89 of 89 progress tests, `npm run build && npm run test:e2e` PASS, 196 ok,
  5 `[real game frame]` lines for Bead Parlor, no SKIPPED, 0 FAIL.
- Pages: `/logic-games/pattern-repeat-for-kindergarten/`, skill `logic-memory.patterns.repeat`, reward `bracelet` (store `bracelets[profile][game]`).
- Lessons: (1) **Ask for the game repo at the START of a game**, not when the code is ready (owner asked for this). The session could not create a repo or
  attach one until the owner made it empty; `add_repo` with push access then worked. (2) A test that waits for the `build` phase right after the last
  bead reads the OLD string: wait for `reward` first, then `build` (my first smoke run failed on this, the game was fine). (3) Two sessions planned two
  games on the same day: check `git branch -r` and the Notion session log first. (4) A catalog `mechanic` written before the kit named it must be
  corrected afterwards (it said `slot-build`).
- 2026-11-17: **LIVE.** Owner asked for PR 13 ([dr-nithish-kanna/edulearnlabs#13](https://github.com/dr-nithish-kanna/edulearnlabs/pull/13)) to be merged; merged into `main` as `70a7234`.
  Deploy run 14 of "Deploy website to GitHub Pages" succeeded (build and deploy-pages jobs). Checked on the live site: game page 200, H1 "Pattern Games for Kindergarten",
  `play/pattern-repeat-k/` and every file in its manifest 200, `BUILD_INFO` game commit `4165a65`, page in the sitemap and linked from `/logic-games/`.
  Not checked live: actually playing it there (website tests ran the real game frame before the merge). Before the merge, `main` had moved (Hedgehog Picnic and Quilt Picnic polish),
  so the branch merged `main` in first; the only conflict was this playbook (kept both updates). Lessons: (5) a sandbox that blocks the live domain gives curl `000` (blocked connection),
  not a 404: allow the host in the cloud environment, then check; (6) count page words with an HTML parser, not a regex on one-line HTML.
- Open: kit tags v0.2.0 to v0.7.0 (then re-pin the games), real tablet touch and speech check, parent "My bracelets" page,
  the spider might scare some children (cast lives in `scripts/gen-skin.py`), level 4 look-alike shape trap not built, `package.json` of the game
  uses `file:../edulearnlabs-kit` until the tag exists.
