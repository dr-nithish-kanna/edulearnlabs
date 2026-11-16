# Hedgehog Picnic, website side: judgment calls and defaults (2026-11-16)

Scope: website support only (progress store, player, pages, catalog, tests, docs) for game 5, `count-objects-prek`.
The game is built in its own repo and synced in a later step. Each entry: what, why, how hard to change.

1. **Parade store mirrors the quilt exactly.** `parades[profile][game] = { v: 1, animals: [{ id, animal, at, session }], folded? }`,
   facts only, own `v`, a newer `v` is kept and never written to, corrupt data (no `v`) starts fresh, stores saved before parades load
   with `parades: {}` and keep top-level `schema: 1`. Why: the quilt rules were reviewed and tested; a second shape would be a second
   thing to get wrong. Easy to change (`march()`, `paradeView()` in `src/scripts/progress.ts`).
2. **Cap 200, oldest fold into `folded`.** Same reason as the quilt (decision 1 of the memory-match log): the game picks the next animal
   after the newest one, so freezing the parade at the cap would freeze the cycle. 200 animals is about 33 sessions of 6 rounds.
3. **Each stored animal keeps its reward `id`** (the dedupe key). Repeats of an animal are normal (a 6 animal cycle), so `animal` can
   never be the key. A replayed session or a repeated `GameCompleted` adds nothing.
4. **HostInit sends `parade: { animals }`, newest 64, oldest first,** only when the catalog `reward` is `"parade"`. Field names follow
   the kit types (`HostInit.parade: ParadeView = { animals: string[] }` in kit v0.6.0 `src/host.ts` and `src/types.ts`). The kit types
   and `tap-count-design.md` section 7 agree, so there was nothing to reconcile.
5. **Reward kind is `"animal"` with field `animal`** (kit `AnimalReward`). Never more animals than questions in one session (one per
   solved round, and a round is a question). Animal slug check `^[a-z][a-z0-9-]{0,31}$`, the same as patch slugs. The game's sixth
   animal is the slug `goat` (shown as a kid goat), not `kid-goat`; the check accepts both.
6. **Protocol stays 1.** Only optional additions (`HostInit.parade`, `kind: "animal"`). An older website drops animal rewards silently,
   an older game ignores `parade`.
7. **Counting tips are skill aware.** The kit records `skipped` (Done bell rung with objects left, level 3) and the planned distractor
   kinds `off-by-one` and `off-by-two`. For `math.counting.*` skills the tips speak about counting ("one object was skipped or counted
   twice", "did we count them all?"). Addition and subtraction keep their own one-away wording. Same 3 times in the last 5 sessions
   threshold as every other tip. Easy to change (`COUNT_TIPS` in `progress.ts`).
8. **`CountMistake = 'skipped'` added to `MistakeKind`** in `progress.ts`, mirroring the kit type. Stored `mistakes` were already
   copied as is, so no storage change.
9. **Skill `math.counting.count-objects`, name "Counting objects", `topDifficulty` 4** (four levels; level 4 is "give me N"). So the
   Grown-ups mastery "Flower" needs two strong sessions that reached level 4 on different days. Grade `prek`.
10. **Ages "3 to 5"** in the catalog, the page title and the JSON-LD (`typicalAgeRange` 3-5), because the owner asked for a page aimed at
    parents of 3 to 5 year olds. The game CLAUDE.md says the words are written for ages 5 to 7; I read that as "keep words short", not as
    the audience. The math category heading changed from "Pre-K (ages 4 to 5)" to "Preschool and Pre-K (ages 3 to 5)". The home and other
    category descriptions still say 4 to 8; left alone (one line to change if the owner wants 3 to 8 everywhere).
11. **URL `/math-games/counting-for-preschool/`, H1 and keyword title "Counting Games for Preschool".** Title tag: "Counting Games for
    Preschool: Free Count to 10 Game for Ages 3 to 5 | EduLearnLabs" (keyword, age, benefit). It is long (about 80 characters), so Google
    may cut the brand; the keyword comes first so that is fine.
12. **No new category page.** `/math-games/` already existed. It gains a link to the new game in its Pre-K section and its "How our math
    games work" text no longer says "three right answers in a row" (Hedgehog Picnic steps up after 2), it says "a few".
13. **Catalog order: appended last.** The home page features `games[0]` (Addition Garden), so putting the counting game first would change
    the home hero button. The math page therefore lists Addition, Subtraction, then Counting. Reorder if the owner wants grade order.
14. **"Count objects 1 to 10" removed from the coming-soon list,** so the home page now says "3 games ready, 5 on the way" for math.
15. **Placeholder poster path and PENDING commit,** exactly like Quilt Picnic before its sync. Until the sync the poster 404s on the home,
    math and game pages; the smoke test counts those 404s and prints the count instead of hiding them.
16. **Page copy claims only what the design locks:** rows of 2 to 5, rows of five up to 10, a pile with the Done bell, "give me N" from 3
    to 10 with a Done tap, a silent count-along after the first wrong choice and a voiced recount after the second, digit keys, steps up
    after 2 first-try rounds and down after 2 rounds in a row that needed the voiced recount, 6 baby farm animals in a fixed order. It
    does not say who voices the recount (Hazel or a plain voice) because the kit does not show a mascot line for it; "a voice counts with
    them". It makes no learning outcome claims: "It is one small part of learning to count, best next to counting real things at home."
17. **The page does not mention the friend's happy pose** (a known kit gap for v0.6.1) and does not mention recorded voice.
18. **Privacy page** names the Hedgehog Picnic parade (which animal each solved round earned, and when). Its "last updated" date was not
    changed (no new kind of data, only a new reward like the quilt).
19. **No "My parade" parent page** (later work, like the other reward pages).
20. **Smoke test:** the play round trip runs against a labelled STAND-IN frame (playbook section 10). Every such check prints
    `[STAND-IN frame (game build not synced)]`, and one line prints `SKIPPED: game build not synced: Hedgehog Picnic real game frame`.
    After the sync the same checks print `[real game frame]` and the SKIPPED lines go away. Also added: page checks for the counting page
    (H1, title, words, wiring, poster, order, links, no dashes, no prices or external links), sitemap, privacy, a parade store round trip
    through the Grown-ups page (byte for byte, with a newer-v parade), the Counting objects skill and the skipped tip on the Grown-ups page,
    profile delete removes the parade, and Quilt Picnic gets no parade.
21. **No sync, no change to `public/play/`, no kit or game repo change,** as asked.
