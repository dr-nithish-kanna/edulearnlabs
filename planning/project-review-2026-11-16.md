# EduLearnLabs project review (2026-11-16)

Independent review of plans, code, product, business and compliance. No code was changed.

## 0. What I read, and what I could not

- **Read in full:** `CLAUDE.md` (both repos), everything in `planning/`, `templates/game-repo/`, the website source
  (`src/`, `scripts/`, `.github/workflows/pages.yml`, `astro.config.mjs`), the kit at `main` (v0.1.0) and the kit at
  its newest branch `ccr-4d0bb17c-4dbh4d` (v0.5.0, commit `24257a2`).
- **Inspected as built output only:** the four games in `public/play/`. I measured sizes and searched the bundles
  for storage, network, speech and canvas use.
- **Not read:** the four game repos (`addition-grade-1`, `subtraction-grade-1`, `word-building-grade-1`,
  `memory-match-prek`). This session can only reach the website and kit repos. Anything I say about game source is
  inferred from bundles, design docs and decision logs.
- **Not done:** no real device, no live site check, no Search Console data, no keyword research. Market numbers
  below are my estimates and are marked as such.

Severity scale: **S1** fix this week, **S2** fix before building more games, **S3** fix before monetizing,
**S4** tidy when convenient.

## 1. Verdict in one paragraph

The engineering is better than most solo projects: the engine decision is right, the progress store is careful,
the privacy posture is clean, and four games shipped in five days. The weak side is everything that is not code.
No child has been observed playing, no game has been tested on a real touch device, three of four games were built
unattended with "all defaults accepted", there is no analytics, no keyword research, and the monetization plan
does not yet contain something a parent would pay for. The risk is not that Claude cannot build 20 games. It is
that you end up with 20 unvalidated games on a domain that cannot rank, with progress that silently disappears on
iPads. Slow the building, and spend your scarce hours on the things only a human can do.

## 2. Ranked problem list

| # | Sev | Problem | Evidence |
|---|---|---|---|
| 1 | S1 | Kit v0.2.0 to v0.5.0 exist only on throwaway session branches. `main` is still v0.1.0 and there are no tags. All four live games pin SHAs on those branches. One branch cleanup makes every game unbuildable. | `git ls-remote` on the kit: HEAD `c883268`, no tags, newest work on `ccr-4d0bb17c-4dbh4d`. Playbook sections 1, 8, 9 and 11 record the same confusion three times. |
| 2 | S1 | No game has been tested on a real phone or tablet, and no child has played under observation. The audience is touch-first. | Kit README "Known gaps" (touch untested for fill-container, slot-build, pair-match); playbook section 1 ("offered but not confirmed"); `decisions.md` test gap 2. |
| 3 | S1 | Wrong home for the site: a subpath of an India ccTLD owned by a different brand, with US school vocabulary. Every week on it makes the move costlier, because saved progress is tied to the origin as well as the search ranking. | `astro.config.mjs` (`site: https://niftygamesstudios.in`); `decisions.md` "Website and hosting" lists the SEO cost but not the progress loss. |
| 4 | S2 | Voice is the browser's speech synthesis, not the reviewed audio files the spec requires. In a game where the word is heard and never shown, the voice is the lesson. | Kit `src/audio.ts` (v0.5.0, line 54 onward); `framework-spec.md` section 7; Known gaps ("cat" and "cut" blur). |
| 5 | S2 | Progress lives only in localStorage. Safari deletes script-written storage after 7 days without a visit, so gardens, word walls and mastery vanish for iPad families. The "never wilts" promise breaks in the worst way. | `src/scripts/progress.ts` (single key `ell:v1`); `framework-spec.md` section 4. |
| 6 | S2 | No measurement at all. The ad trigger ("5k to 10k monthly visitors") and every product question (do kids finish, do they return) cannot be answered. | No analytics or Search Console tag anywhere in `src/`; `framework-spec.md` section 6 allows cookieless analytics but none exists. |
| 7 | S2 | Reuse is unproven. Four games needed four mechanics, four large design docs and three bespoke reward stores. | Kit sources: `fill-container.ts` 39 KB, `fill-take.ts` 38 KB, `slot-build.ts` 27 KB, `pair-match.ts` 23 KB. `progress.ts` holds separate garden, wall and quilt code. |
| 8 | S2 | Upright phones get "Turn your phone sideways" on a fixed 960 x 600 scene. A phone with rotation lock is a dead end. Most parents hand over a phone upright. | Playbook section 5; Known gaps (fill-container portrait). I could not confirm whether slot-build and pair-match behave the same. |
| 9 | S2 | Monetization has no product. "Subscription removes ads" is worth nothing when there are no ads and every game is free. Ads at 5k to 10k visitors earn pocket money and spend your best selling point. | `CLAUDE.md` "Product decisions"; `decisions.md` "Revenue". |
| 10 | S3 | The iframe sandbox is not a real boundary. `allow-scripts` plus `allow-same-origin` on a same-origin frame lets the game reach the parent page and localStorage. "The game never sees a profile id" is a convention, not an enforced rule. | `src/scripts/player.ts` line 56; `framework-spec.md` section 6 claims the opposite. |
| 11 | S3 | Pond Hop lets a child finish the take-away step without counting, because the pad stops for them. Only a one-in-three tap checks the skill. Known, live, not fixed. | Kit Known gaps ("Take-away"); `pond-hop-decisions-log.md` item 9. |
| 12 | S3 | Mastery is overstated. A session counts as "top difficulty" if it touched the top level for one question, and "different days" uses UTC dates, so 6:30 pm and 7:30 pm in New York count as two days. | `progress.ts` lines 544 to 559. |
| 13 | S3 | An external link to the Nifty Games Studios site sits in the footer of every page a child sees, with no parent gate. | `src/layouts/Base.astro` footer; `src/config.ts` `makerUrl`; rule in `CLAUDE.md` "Safety". |
| 14 | S3 | The deploy runs unit tests only. The smoke test that proves games load is not in CI, and every push to `main` goes live. | `.github/workflows/pages.yml` line 30. |
| 15 | S3 | Docs that Claude treats as instructions are stale and contradict each other. | Kit `CLAUDE.md` and templates name repo `edu-learn-labs` and `content/skills.json` (real: `edulearnlabs`, `src/data/`); template says "do not commit", main says commit; spec header says "No code yet"; playbook section 11 says Quilt Picnic is not deployed although PR 7 is merged. |
| 16 | S4 | No `robots.txt`, although `CLAUDE.md` requires one. On a project site it must live at the domain root, which is the other repo. | `public/` has none. |
| 17 | S4 | Each game ships its own copy of both fonts (36 KB), so nothing is shared between games or with the site. | Identical `andika` and `fredoka` files in each `public/play/*/assets/`. |
| 18 | S4 | Quiz mechanic still reveals the answer, against rule 5. No `CREDITS.md` although the style guide requires it. Hazel trademark check still open. | Playbook section 1; `style-guide.md` sections 8 and 9. |

## 3. Plan review: gaps and wrong assumptions

**3.1 "WebGL games" is not what you have, and that is good.** Your brief says WebGL. The bundles contain no canvas
or WebGL call at all. `decisions.md` chose DOM, CSS and SVG after a measured test (Phaser cost 277 KB and 8 s on the
throttled profile). Keep it. Update how you describe the project, because "WebGL" will steer future sessions wrong.

**3.2 The plan has no validation step.** `game-playbook.md` section 2 ends at "merge and confirm the Pages run".
Nothing says "watch a 6 year old play for five minutes". Automated tests check that buttons exist, not that a child
understands the goal in 5 seconds (your own golden rule 7). Three decision logs open with "built while the owner
slept". That is fine for code. It is not fine for deciding what is fun or what teaches.

**3.3 The MVP list is a curriculum list, not a demand list.** `mvp-games.md` has no search volumes, no competitor
check and no reason for the order. You do not know which of the 20 pages can rank.

**3.4 Twenty games is the wrong first milestone.** At this pace the temptation is to finish 20 in a month. Stop at
five or six, validate, then continue. More unvalidated games means more to rework when a real tablet shows a problem
in the shared kit.

**3.5 Time is your scarcest input and the repo layout wastes it.** Six repos today, 22 at MVP. Each kit fix means
re-pinning, rebuilding and re-syncing every game by hand (`scripts/sync-game.mjs` needs local checkouts of private
repos). Cloud sessions cannot push tags and lose track of branches (playbook sections 5, 8, 9).

**3.6 Spec and reality have drifted.** Planned and not built: recorded voice, music, stickers, mascot outfits,
tagged releases with a build action, start-level and practice items for non-quiz mechanics (I could not verify the
last one). None is urgent, but the spec should say what is real.

**3.7 Grades 3 to 12 and science are on the roadmap with no evidence the approach carries.** Tap-and-drag mechanics
fit ages 4 to 7. Older children need different content depth. Remove it from the plan until Pre-K to Grade 2 earns
money.

## 4. Architecture assessment

### What is right (keep it)
- **Engine choice.** Measured before Play payload is small. My numbers (brotli): JS 20.0 to 28.6 KB, CSS 3.3 to
  5.8 KB, fonts 35.7 KB, so 55 to 70 KB against a 100 KB budget.
- **"Store facts, derive opinions"** in `progress.ts`, with dedupe by id, field whitelisting in `addSession`, the
  newer-schema guard and a memory fallback. This is sync-ready, as intended.
- **Message contract.** Both sides check `origin` and `source` (`player.ts` line 63, kit `host.ts`).
- **No third parties.** Fonts are self-hosted. The bundles make no outside requests that I could find.
- **Content as data with build-time validation.**

### Performance (low-end phones and school PCs)
- Load weight is not your risk. **Runtime on cheap Android is**, and it is unmeasured. Scenes are large inline SVG
  with filters (4 to 10 filter uses per bundle) inside a scaled 960 x 600 stage. SVG filters are drawn on the CPU.
  I did not profile this, so treat it as a suspicion to test, not a finding.
- The only evidence for "old Chromebook" is headless Chrome with 4x CPU slowdown. The README table was measured on
  2026-11-11, before any current game existed.
- Speech synthesis is the least predictable part: voice quality, latency and availability differ per device, and a
  device with no voice makes `say()` resolve silently.
- GitHub Pages serves everything with a short cache life, so hashed assets are re-checked on each visit. Minor, and
  fixed by moving hosts.

### Scalability and maintainability
- **Reward stores do not scale.** Garden, wall and quilt are three near copies (about 250 lines plus tests). Each new
  reward type touches `progress.ts`, `player.ts`, the privacy page and the smoke test. Replace with one generic
  "collection" section (`{ v, items: [{ id, key, at, session }], folded }` plus a small policy per game: dedupe by id
  or key, cap, fold rule). Opus task, because it is a data shape.
- **Game pages are hand-written `.astro` files** with repeated JSON-LD. Fine at 4, painful at 40. Move to one dynamic
  route plus a Markdown content file per game. Keep the prose human-reviewed.
- **Adding a game touches about eight places** (`games.json`, `skills.json`, `coming-soon.json`, game page, category
  page, reward code, privacy text, smoke test). That is the real cost of a "new game from template".
- **Bundled kit copies.** Pinning protects live games, but at 20 games it also means 20 manual upgrades, so old games
  will rot on old kits.

### Security
Small attack surface (static site, no backend, no accounts). Real points only:
- Problem 10 above. Matters the day any third-party script runs on the page (ads, analytics) or a game pulls in a
  library. The clean fix is a separate origin for games and dropping `allow-same-origin`. Opus task: it changes the
  origin checks on both sides.
- The site shares its origin with everything else on `niftygamesstudios.in`. Any script there can read or wipe
  `ell:v1`.
- `site.ts` and `grown-ups.astro` write `p.color` and `p.id` from storage into HTML without escaping. Only
  exploitable by something that can already write your storage, so low. Validate profiles in `parseStore`.
- `missed` items and `mistakes` are stored without per-item type or length checks. Low while all games are yours.
- Workflow actions are pinned by major version, not by commit. Low.

### Can the pipeline be automated and reused? My honest answer: partly, and not yet proven
- **Automatable now:** content JSON, generators, validators, skins, SEO page drafts, tests, size checks. The playbook
  is a good process document.
- **Not automatable:** judging fun, judging learning, real-device feel, voice quality, final copy. These are also
  the steps currently being skipped.
- **The proof you still need:** build game 5 on an existing mechanic with no kit change. For example "Add with
  objects" (Kindergarten) or "Count to 20" on fill-container with a new `game.json` and skin. If that takes one
  evening including your review, the pipeline is real. If it needs another kit release, the "reuse mechanics" rule
  in `CLAUDE.md` is aspirational.
- **Recommendation: one monorepo** (kit, games, site as workspaces), with the smoke test of every game running on
  every kit change. That gives the safety pinning gives today, removes tags, re-pins, private-repo syncing and
  branch confusion, and lets one Claude session see everything. Do it at 4 games, not 20. I am fairly confident in
  this, but it is a judgment call: the cost is that a kit change can break an old game, so the per-game smoke tests
  must be trustworthy first.

## 5. Product and learning value

| Game | Does it teach? | Main concern |
|---|---|---|
| Addition Garden | **Yes, the strongest.** Joining two groups, ten-frames and make-ten are sound early-math practice, and the design pass caught a real flaw (bins that let a child win without adding). | The answer step is one of three choices, so guessing gives 33 percent, and 50 percent on the second try. |
| Pond Hop | **Partly.** | Problem 11: the action completes without counting. Fix before promoting it. |
| Letter Workshop | **Spelling, yes. Phonics, not really.** | The skill id says phonics, but the voice only says whole words (`word-building-design.md`: no letter sounds, because browser speech says "see" for c). Real phonics needs the separate sounds. That needs recorded audio. Until then call it spelling. |
| Quilt Picnic | **It is a memory game, not a lesson.** Fine as a gentle Pre-K entry game. | The page says "Train visual memory". Evidence that memory games improve memory beyond the game is weak. Soften the claim (see compliance 6.7). The 2 x 2 board is mostly luck. |

**Age fit.** Session length, no-fail feedback, 64 px targets, spoken prompts and no reading load are right for 4 to 7.
The "juicy but fair" list in `decisions.md` is well reasoned and a real differentiator. Open risks: drag on small
touch screens (untested), portrait phones, and colour-only differences on Quilt Picnic level 5.

**What would bring families back.** Today nothing does: no account, no reminder, no install, and progress that can
vanish. Fair, non-manipulative options, cheapest first:
1. **A "what next" tile** on the site after a game ends, following a simple path per grade. Not autoplay.
2. **A home-screen install (PWA).** Gives an icon to tap, works offline, and exempts storage from Safari's 7 day
   deletion. Biggest retention win for the effort.
3. **Printable certificate at mastery** with Hazel. Parents share these, which is also free marketing.
4. **A parent summary worth opening:** the mistake tips in `progress.ts` (`mistakeTip`) are your most original
   feature and are buried on the Grown-ups page. Show "this week" and "try this together" there.
5. **Backup code:** let a parent export and import progress as a file or code. No account, no server, no child data
   leaving the device unless the parent moves it.

## 6. Business view

**Expectation first.** A new children's site that relies on search usually needs 12 to 24 months to reach meaningful
traffic, and may never rank for head terms. "Addition games for grade 1" and "memory games for preschool" are held
by ABCya, SplashLearn, Math Playground, Education.com, PBS Kids, Starfall, Turtle Diary and Khan Academy Kids.
Treat this as a two year project with small, real milestones, not near-term income. These are my estimates, not
measured data.

**Where you can win.** Long-tail, specific pages ("make ten ten-frame game", "CVC spelling game no ads"), the honest
"no ads, no login, no data" position, and speed on school Chromebooks. Few competitors can claim all three.

**Decide the market now.** The site uses "Pre-K", "Kindergarten", "Grade 1" (US terms) on a `.in` domain that Google
ties to India by default. Indian parents search "Class 1", "LKG", "UKG". Either target the US and English-speaking
world on a `.com`, or target India with Indian terms. I would choose a `.com` in US English first (higher ad and
purchase value), and add Indian term pages later.

**Monetization options, ranked for a solo developer with little time:**

| Rank | Option | Why | Effort |
|---|---|---|---|
| 1 | **One-time printable packs** (worksheets, ten-frame mats, word cards) sold through a merchant of record | No accounts, no child data, tax handled by the seller platform, and Claude can generate them from the same content generators. Also strong on Pinterest and Teachers Pay Teachers, which doubles as marketing. | Low |
| 2 | **Paid app wrapper** (same games, offline, one-time price) in the app stores | Stores handle payment and parental approval, and are a discovery channel. Store rules for kids apps are strict. | Medium |
| 3 | **Teacher use, free now, licence later** | Teachers share links and school Chromebooks are your best device. Selling to schools needs contracts, invoices and data agreements, so only later. Add standards codes to `skills.json` now to be found. | Low now, high later |
| 4 | **Family subscription** | Only once you have retention data and something to sell: cross-device sync, reports, packs. Needs accounts, payments and verified parental consent, the heaviest build in the project. | High |
| 5 | **Ads** | Child-directed ads must be non-personalized, pay little, risk bad creatives and accidental taps next to a game, and cost you "no ads" as a selling point. My rough guess is tens of dollars a month at 10k visitors. Not before 100k monthly visits, possibly never. | Low, but costly in trust |

**Rough subscription arithmetic (my estimate):** USD 500 a month at USD 3.99 needs about 150 payers after fees. At a
1 percent conversion that is about 15,000 active families a month.

**Getting users without marketing skill:** (1) Search Console from day one, (2) one printable per game page,
(3) a short parent article per skill linking to 2 or 3 games (already in your SEO rules, none written),
(4) submit to free teacher resource lists and homeschool communities, (5) ask five parents and two teachers you
know to try it, and watch.

**Things I am unsure about and you must check:** payment providers that pay out to an Indian individual, GST and
income tax on foreign sales, and whether your internship or college rules restrict outside income.

## 7. Compliance: child privacy and safety

Current state is good: no accounts, no names, no third-party requests, and a plain-language privacy page. This is
not legal advice. Before taking money, pay for one hour with a lawyer who knows children's privacy law.

1. **COPPA (US).** The site is directed to children. Today you collect nothing, which keeps you mostly outside it.
   The amended rule's compliance deadline (April 2026) has passed, so anything you add later must comply from day
   one. Any analytics, ad or account feature changes your status.
2. **India DPDP Act and Rules.** You are an Indian operator. A child is anyone under 18. It requires verifiable
   parental consent for a child's personal data and bans tracking and targeted advertising to children. My
   understanding is the main duties start around mid 2027. Verify the dates.
3. **GDPR and the UK Children's Code.** Local progress storage is strictly necessary and needs no banner. Ad or
   analytics cookies would need parental consent, so in practice keep ads off for EU and UK visitors.
4. **Ads, if ever.** Mark the site as child-directed, contextual only, block sensitive categories, keep slots well
   away from Play and game controls, and update the privacy page first (it already promises this).
5. **Subscription design.** Make the account the parent's (email only). Keep child profiles as avatar and colour.
   Syncing a child's progress to a server is child data: use the card payment itself as the verified consent step.
   A parent gate is friction, not consent.
6. **Fix now:** the footer link to the studio site (problem 13). Either remove it from pages children use or move it
   to the Grown-ups page.
7. **Claims.** Avoid efficacy language such as "train visual memory" or "why it helps" stated as fact. Regulators
   have fined brain-training products for this. Say what the child practices, not what it improves.
8. **Speech synthesis.** The voice picker prefers voices whose name contains "google" (kit `audio.ts`, the voice
   regex). In desktop Chrome I believe those are network voices, which would send the spoken text and the device's
   IP address to Google. It is word text, not personal data, but it is a third-party request triggered inside a
   children's game, and the privacy page says nothing leaves the device. I am not fully certain of this behaviour.
   Recorded audio removes the question.
9. **Privacy page.** Add a direct contact email and the operator's name. State hosting logs as you do now. Keep
   "No data collected" literally true when analytics arrives, or reword it.
10. **Hosting.** GitHub Pages is not meant for commercial sites and gives you no data agreement or log control.
    `decisions.md` already says to move before monetizing. Move with the domain change.
11. **Brand.** Finish the Hazel trademark check, add `CREDITS.md`, and check the four game titles.

## 8. Roadmap: Now, Next, Later (ranked by impact over effort)

### Now (next 2 to 3 weeks, mostly small tasks)
1. Merge the kit branch into `main` and create tags `v0.2.0` to `v0.5.0`. Ten minutes, removes problem 1.
2. Play all four games on a real phone and a cheap Android tablet, then watch two or three children play. Write
   down what confused them. One evening, highest information value of anything on this list.
3. Buy a `.com`, move hosting (Cloudflare Pages or similar), add `robots.txt`, Search Console and cookieless
   aggregate analytics. Update the privacy page in the same change.
4. Remove or gate the footer external link. Soften the memory claim. Rename the word skill to spelling.
5. Fix stale docs (repo names, paths, commit rule, spec status) so future sessions stop being misled.
6. Add the smoke test to the deploy workflow.

### Next (1 to 3 months)
7. Recorded voice pipeline (build-time speech files, reviewed by ear). Prefer on-device voices meanwhile.
8. Portrait layout, or at least a layout that works with rotation lock.
9. Game 5 on an existing mechanic with zero kit changes, as the reuse proof.
10. Monorepo, generic collection store, one dynamic game route (Opus for the store design).
11. PWA install plus a progress backup code.
12. Fix Pond Hop's counting gap and the mastery rule (top-level share of the session, local dates).
13. First printable pack and three parent articles. Keyword research before choosing games 6 to 10.

### Later (after there is traffic and retention data)
14. Remaining MVP games, chosen by search demand and by what children replayed.
15. Separate origin for games, then any third-party script.
16. Paid packs through a merchant of record with a parent gate, then the app wrapper.
17. Parent accounts, sync and subscription, with a lawyer review.
18. Teacher mode and school licences. Grades 3 and up only after this.

## 9. Top 5 things to do first

1. **Secure the kit:** merge to `main` and tag. Your whole catalog depends on branches that look disposable.
2. **Test on real devices with real children** before building game 5. Everything else is guesswork until then.
3. **Move to your own `.com` and a proper host now,** and add Search Console and privacy-safe analytics in the same
   step. Waiting costs search ranking and every child's saved progress.
4. **Replace browser speech with recorded audio,** starting with Letter Workshop, where the voice is the lesson.
5. **Prove reuse and simplify the pipeline:** one game with no kit change, then the monorepo and the generic reward
   store, so that game 20 costs an evening and not a week.

Model note: items 10 and 15 and the subscription design are Opus-sized. The rest is routine.
