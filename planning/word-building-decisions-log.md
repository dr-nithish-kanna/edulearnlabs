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
