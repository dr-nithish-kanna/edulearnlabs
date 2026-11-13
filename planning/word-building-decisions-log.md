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
