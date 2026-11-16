# Bead Parlor, website side: judgment calls and defaults (2026-11-16, unattended)

Scope: website support only (progress store, player, pages, catalog, tests, docs) for game 6, `pattern-repeat-k`
(MVP number 18, Color pattern repeat, Kindergarten). The kit and the game are built elsewhere and synced later.
Each entry: what, why, how hard to change.

1. **Bracelet store mirrors the quilt and the parade exactly.** `bracelets[profile][game] = { v: 1, bracelets: [{ id, beads, at, session }], folded? }`,
   facts only, own `v`, a newer `v` is kept and never written to, corrupt data (no `v`) starts fresh, stores saved before bracelets
   load with `bracelets: {}` and keep top-level `schema: 1`. Why: the quilt and parade rules were reviewed and tested; a fourth shape
   would be another thing to get wrong. Easy to change (`threadBeads()`, `braceletView()` in `src/scripts/progress.ts`).
2. **Cap 200, oldest fold into `folded`.** Same reason as the quilt and the parade: the game may continue from the newest items, so
   freezing the shelf at the cap would be wrong. 200 bracelets is about 40 sessions of 5.
3. **Dedupe by reward `id` only.** `id` is the session id plus the question index. A repeated bead sequence is normal (a pattern
   repeats, and a child will finish red-blue-red-blue many times), so `beads` can never be the key. A replayed session or a repeated
   `GameCompleted` adds nothing.
4. **Bead validation (defensive).** `beads` must be an array of 1 to 7 strings, each matching `^[a-z][a-z0-9-]{0,15}$`. The brief says
   "a short slug of lowercase letters"; I also allow digits and a hyphen (same family as patch and animal slugs) so a future bead id
   such as `dark-blue` is not silently dropped. A reward with 0 or 8 beads, a non-string bead or a bad slug is dropped as a whole,
   not trimmed, because a trimmed bracelet would draw a different pattern than the child finished. Reward `id` length 1 to 64 and
   `at` at most 40 characters, as for the other kinds. Never more bracelets than questions in one session.
5. **Stored beads are copied,** and `braceletView` returns copies, so a caller changing the view never changes the store (unit test).
6. **HostInit sends `bracelets: { bracelets: string[][] }`,** newest 64, oldest first, only when the catalog `reward` is `"bracelet"`.
   No profile id, no timestamps, no session ids. A newer-schema shelf sends nothing (the key is absent). Protocol stays 1: only
   optional additions, so an older website drops bracelet rewards silently and an older game ignores `bracelets`.
7. **Reward kind `"bracelet"`, shape `BraceletReward = { id, kind, beads, at }`.** Stored sessions never keep `rewards`. Old-tab
   sessions that still carry bracelet rewards are harvested on the next load, like the other kinds.
8. **Mistake kinds `unit-order` and `outside-unit`** added to `MistakeKind` (`PatternMistake`). Stored `mistakes` were already copied
   as is, so no storage change. Tips are skill aware, for `logic-memory.patterns.*` only (`PATTERN_TIPS`), same 3 times in the last
   5 sessions threshold as every other tip. The wording is the one in the brief, with no blame and no dashes. A pattern kind on a
   math skill gives no tip, and an unknown kind gives no tip.
9. **Skill `logic-memory.patterns.repeat`, name "Color and shape patterns", `topDifficulty` 5,** grade `k`. Parent label "Seeing a
   repeating pattern and continuing it".
10. **Catalog entry:** id `pattern-repeat-k`, title Bead Parlor, keyword title "Pattern Games for Kindergarten", category
    `logic-games`, slug `pattern-repeat-for-kindergarten`, ages "5 to 6", reward `bracelet`, minutes "2 to 4", poster
    `play/pattern-repeat-k/poster.webp` and source commit `PENDING` until the sync. Appended last, so the home hero button
    (`games[0]`) does not change. `mechanic` is `slot-build` (the design says the kit generalizes slot-build to tokens). It is
    display and taxonomy data only on the website, so if the Opus kit pass picks another name (a thin `pattern-fill` runner), change
    that one field.
11. **Page title tag:** "Pattern Games for Kindergarten: Free Color and Shape Pattern Game for Ages 5 to 6 | EduLearnLabs" (keyword,
    age, benefit). Long, so the brand may be cut in results; the keyword comes first. Meta description has no mention of ads or prices.
12. **Page copy claims only what the design locks:** a friendly spider and bracelets with gaps, a tray, drag or tap then tap or
    keyboard, a right bead clicks in and plays its note, a wrong bead wobbles and hops back, no buzzer, the three hint rungs
    (start of the repeat pulses, next gap glows, needed beads glow, never the answer), the pattern plays as a tune, 5 bracelets
    about 3 minutes, a voice that says "What comes next?" and never names colors, every bead pairs its color with a shape (circle,
    square, triangle, star, diamond, heart), steps up after a few bracelets without help and back after a few that needed a lot.
    It names no spider name (undecided in the art preview) and does not mention the look-alike shapes level (needs the owner's
    tablet check first). Hazel appears only as the hint giver, as in the other pages.
13. **No prices and no ads on the page,** including the meta description (the other pages say "no ads"; this one stays silent, as
    asked). The smoke test checks this on the built text. The `AdSlot` component is the same as on the other game pages (off by flag).
14. **Color-blind safety is in the page text** (about 1 in 12 boys is color blind; every bead has its own shape). That is a real
    accessibility claim, so the game's own grayscale check must hold it up (design section 3).
15. **Logic category page:** now 2 games (Bead Parlor next to Quilt Picnic, from data), "Color pattern repeat" removed from coming
    soon (home counts become logic "2 games ready, 2 on the way"). Added a short "What is a pattern?" section, a link in the
    Kindergarten text and the reward sentence now names the bracelet shelf. The Pre-K and Grade 1 and 2 text is unchanged and the
    page still does not promise games that do not exist (Odd one out and Pattern completion stay on coming soon).
16. **Privacy page** names the Bead Parlor bracelet shelf (which beads each finished bracelet has, and when). The "last updated" date
    was not changed (no new kind of data, only a new reward like the quilt and the parade).
17. **No "My bracelets" parent page** (later work, like the other reward pages).
18. **Smoke test:** page checks (H1, title, description, words, wiring, poster, order, links, no dashes, no prices, ads or external
    links), logic category, home count and card, sitemap, privacy, bracelet store round trip through the Grown-ups page byte for
    byte (a repeated sequence, `folded`, a newer-v shelf), the Color and shape patterns skill and the unit-order tip, profile delete
    removes bracelets, Hedgehog Picnic and Quilt Picnic get no bracelets. The play round trip runs against the labelled STAND-IN
    frame and prints `SKIPPED: game build not synced: Bead Parlor real game frame` until the sync; after the sync the same checks
    print `[real game frame]`.
19. **No sync, no change to `public/play/`, `brand/`, the kit repo or `planning/token-slot-design.md`,** as asked. `game-playbook.md`
    is left for the owner.
