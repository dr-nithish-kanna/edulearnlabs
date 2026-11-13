# Letter Workshop: decisions made while the owner was away (2026-11-13)

Owner accepted all defaults of the pitch and asked for an unattended build. Each entry: what, why, how hard to change.

1. **Game repo** `dr-nithish-kanna/word-building-grade-1` (empty, created by the owner). Kit branch for this work:
   `ccr-d63a6d4f-g77ft0`, based on the v0.3.0 commit `0e03b6e` (the local checkout had been the stale v0.1.0).
2. **Word bank is about 40 words, not 60.** Each needs a hand-drawn SVG picture; quality over count. Easy to extend.
3. **Word wall is persistent but the parent page is not built.** The website stores word ids as facts. Follow-up.
4. **'nut' renamed 'acorn' and moved to level 5**: the picture is an acorn, which a 6 year old names as acorn. Level 5 now has 7 words, level 3 reuses CVC words.
5. **Art preview accepted by me, not by you** (`brand/word-building/index.html`, built by `build.py`, exports `scene.ts`). I read the
   960x600 and mid-drag screenshots: no clipping, no seam, tiles read clearly. Known weak spots, all cheap to change:
   robin tail looks a little odd, Hazel's pointing pose is subtle, letter shapes are hand-drawn paths (i, j, l, y, t are the
   least polished, please look at the alphabet sheet), and on a 667x375 phone tiles show at about 55 px (below the 64 px
   target) because the fixed 960x600 scene shrinks. The game will need a bigger-tile layout on small screens or the rotate prompt.
6. **Kit v0.4.0 built by Opus** (kit commit `fc6a32b5c2a9de112875d38ceb1e1eb2f9ef21d8`, branch `ccr-d63a6d4f-g77ft0`).
   I re-ran 172 unit tests and typecheck (pass) and read two screenshots. Design doc: `planning/slot-build-design.md` (13 decisions).
   Make the `v0.4.0` tag on GitHub at that commit when you like. Key calls: a tile is judged against the slot it lands on (wrong
   tile wobbles back, right tile stays); trial and error is allowed but never counts as first try; keyboard letters fill the
   first empty slot left to right; no magnetic snap; wall shows pictures only during play (so a child cannot copy a spelling off
   the wall) and picture plus word on the end screen. Kit JS for a word game is about 16.9 KB brotli (over the 15 KB target, accepted
   like the other games). Known flakes in the older fill tests (one timing check failed once per run, one also on untouched v0.3.0).
   Not verified: real touch devices and real speech quality (cat and cut can sound alike).

## Website step (2026-11-13)

7. **Word wall store shape.** `walls[profile][game] = { v: 1, words: [{ wordId, at, session }] }`, next to `gardens`
   and built the same way: facts only, its own sub-schema `v`, a wall with an unknown newer `v` is kept and never
   written to (and HostInit then sends no wall), word rewards are moved out of the stored session, deleting a player
   deletes their walls. `session` is kept (like garden items) so a later sync or parent page can tell where a card came
   from. **No top-level schema bump**: gardens showed it is not needed, an old store simply loads with `walls: {}`.
   Hard to change once live (stored data): a new shape needs `v: 2` and a migration, the newer-v guard keeps it safe.
8. **Wall order is the order cards were saved on this device**, not the reward clock, so a wrong device clock cannot
   shuffle the shelf (same reasoning as garden growth). A word earned again keeps its first time and place. Easy.
9. **Cap: 200 cards per child per game. Past the cap, new words are not added; earned cards are never dropped.**
   The bank is 36 words and a word counts once, so a real child never gets near it. The cap only bounds storage if a
   buggy game sends made-up ids, and then the child's real cards should win. Easy (one constant).
10. **Strict word ids**: letters, digits, `_` and `-`, 1 to 48 characters, and `at` at most 40 characters. Anything else is
    dropped, as are unknown reward kinds. Ids go back to the game and may be shown on a parent page, so no markup can
    sneak in. Also never more cards than questions in one session (like seeds). Easy.
11. **Stored sessions get no card count** (gardens keep `seeds` because growth needs it; nothing derived needs a word
    count). Easy to add later, but old sessions would not have it.
12. **HostInit is built by a pure function, `hostInitFor()` in `progress.ts`**, so the garden, wall and Pond Hop cases
    are unit tested in node (`player.ts` cannot be imported by node). The catalog `reward` decides: `garden` sends the
    garden, `wall` sends `{ words }` oldest first, anything else sends neither. Addition Garden and Pond Hop messages are
    unchanged (unit tests plus the existing smoke checks). Easy.
13. **Parent tips for the four letter mistakes**, written to say the slip is normal and give one thing to try together
    (stretch the word, point left to right, trace b and d). A mistake kind the site does not know now returns no tip;
    before, it leaked `undefined`. Easy (copy only).
14. **Category URL `/language-games/`, but the label parents see is "Reading games"** (nav, home card, breadcrumbs),
    H1 "Free reading and language games for kids". Parents search for "reading games" far more than "language games";
    the H1 and title carry both. The URL is hard to change once indexed (needs a redirect); labels are easy.
15. **Home page**: "Start playing" now shows every ready game (it showed only Addition Garden), the subject cards count
    "games ready, on the way" from the catalog and coming-soon list instead of hand-typed numbers, the Reading games card
    is a link, and the hero has a "See reading games" button. Easy.
16. **`subject` added to every skill in `src/data/skills.json`** (math for the two math skills, language for the new
    one), additive, nothing reads it yet. Easy.
17. **`GamePlayer` takes a `posterAlt`**: the old alt text described "a sum, three answer buttons" for every game. Easy.
18. **Privacy page now names both stored rewards**, the garden flowers (missing before) and the word wall cards. Easy.
19. **Game page copy is written from the design docs, not from the finished build** (the game repo was still being
    built). Claims to check once it is synced: 36 words, "Eight words, about 3 minutes", the five level descriptions,
    tap the picture to hear the word, tap Hazel for help, typing letters on a keyboard. Title says ages 5 to 7 (the page
    is for "about 5 to 7"); the catalog card says 6 to 7 like the other Grade 1 games. Easy (copy only).
20. **`source.commit` is "PENDING" in `src/data/games.json`.** The site never reads it, so the build works. `npm run
    sync-game -- ../word-building-grade-1` writes the real short SHA into it by itself. Until the sync, the poster and
    asset manifest 404 on the new pages. Easy.
21. **Site smoke test**: the new page, navigation, sitemap, privacy and store round trip checks always run. The checks
    that need `/play/word-building-grade-1/` print `SKIPPED: game build not synced` lines and a final count, and the 404s
    for the missing build are counted and reported, not hidden among errors. After the sync they run with no edits. Easy.
22. **Still not built**: the parent "My word wall" page (entry 3). The store already has what it needs.
