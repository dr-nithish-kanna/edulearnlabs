# Memory Match (flip cards for Pre-K and Kindergarten): design plan

Status: 2026-11-13, DRAFT for owner critique. Owner picked "Memory flip cards" (MVP number 17), asked for the basics
only and went to sleep, so every open question below has a default I chose. Nothing is built yet.
Friendly title: **Quilt Picnic**. Keyword title and H1: **Memory Games for Preschool and Kindergarten**.
URL: `/logic-games/memory-match-for-preschool` (new category page `/logic-games/`). Game id `memory-match-prek`,
repo `dr-nithish-kanna/memory-match-prek`. Skill `logic.memory.matching-pairs`. Mechanic: new kit mechanic
`pair-match` (kit v0.5.0).

## 1. The game in one sentence
A picnic quilt lies on the grass. Each patch is a closed flap. The child lifts two flaps to find two friends that
look the same. A match makes the pair pop out with the same musical note and a patch joins their own quilt.

Micro-skill: hold a few things in mind and find the matching pair (visual memory, ages 4 to 6).

## 2. Ideas (the discussion I would have had, grouped as in the playbook)

### A. How the child does the skill
1. **Lift two flaps** (classic). Simple, known, no reading. Needs the new `pair-match` mechanic.
2. **Peek first, then hide**: cards show for 2 seconds, then close. Gentler for 4 year olds, but removes the
   "memory over time" part. Use only as a hint, not the base game.
3. **Match by meaning, later**: same animal in two art styles, or mother and baby, or shape and its shadow.
   Same mechanic, new content. Good for Kindergarten levels.
4. **Find the one I just saw**: one friend jumps in and hides, child finds it. More story, more new code. Not now.

### B. What the child gets
5. **Quilt patches (recommended)**: every finished board adds a patch to the child's own quilt on the website.
   Website-owned, facts only, same pattern as the word wall and the garden. No loss, no streak.
6. **Picnic basket fills**: one food item per match. Cute, but it ends (a full basket) and invites "more".

### C. How it feels
7. **Matching pairs share a note** (reuse `src/pitch.ts`): you can match by ear. Every sound has a visual twin
   (a soft glow), because many children play muted.
8. **Gentle flap physics**: flap lifts with a tiny bounce, closes slowly and softly. No flip-card turn (a 3D card
   flip is heavier on old Chromebooks); we use transform and opacity only.

## 3. Recommended combination
**1 + 3 later + 5 + 7 + 8**, with the peek (2) as a hint rung. Honest critique of the classic mechanic: memory games
can feel like failure when a child flips wrong again and again. So we protect the child:
- Mismatch is quiet: both flaps close gently, no buzzer, no red, no counter on screen.
- Hint ladder (hints only, never the answer): rung 1 after 3 misses in a row: all flaps lift for 1.5 seconds
  ("peek"). Rung 2 after 3 more: one flap of a not-yet-found pair sparkles. We never auto-match.
- Small boards for Pre-K. A 2x2 board is a real level, not a baby level.

## 4. A round (one board)
1. Hazel (owl, the picnic host) spreads the quilt. Flaps are closed. The voice says "Find two that match."
2. The child taps a flap. It lifts and shows a friend, with its note.
3. The child taps a second flap. If they match, both friends hop, sparkle and the pair stays up (both notes play as a
   chord). If not, both close after a short moment and the voice stays silent.
4. When every pair is up, a tune of all the notes plays, the quilt glows and a new patch is sewn on the child's quilt.
5. A session is 5 boards or about 180 seconds.

Input: tap or click, keyboard (arrow keys move, Enter or Space lifts), no drag. Targets at least 96 px on a Pre-K board.
Voice first: speech finishes before any tone (existing rule).

## 5. Levels (difficulty 1 to 5)
| Level | Board | Cards | Content rule |
|---|---|---|---|
| 1 | 2x2 | 2 pairs | very different pictures |
| 2 | 2x3 | 3 pairs | very different pictures |
| 3 | 2x4 | 4 pairs | two share a category (two animals) |
| 4 | 3x4 | 6 pairs | similar pairs (cat and dog art style close) |
| 5 | 4x4 | 8 pairs | colour variants (red and blue ball) as distractors |
Adapt rule like the other games: up after a board solved with few misses, down after a board needing the sparkle hint
twice. Pictures are data (`game.json` items), never hardcoded.

## 6. Feel and look
- Cozy meadow, a patchwork quilt, warm afternoon light. New look: garden was sunny, pond was dusk, workshop was wood.
- Cast: the friends on the flaps (about 16 simple picture ids: ladybug, snail, bee, rabbit from earlier games plus
  fox, duck, hedgehog, mouse, apple, ball, star, cup and others). Reusing earlier cast links the games together.
- Reduced-motion version of every animation, transform and opacity only.

## 7. Reward (website owned)
**Your Quilt**: one patch per finished board, shown as a small picture on a grid. The website stores patch ids per
profile and game as facts (own `v`, newer-schema guard like the word wall). The game receives the list in `HostInit`
and shows the quilt at start and end of a session. The game only reports `rewards` in `GameCompleted`.
A "My quilt" parent page is a later follow-up, same as "My garden" and "My word wall".

## 8. Kit work (Opus-sized, do not start on Sonnet)
New mechanic `pair-match` in kit v0.5.0 (branch continues from `ccr-d63a6d4f-g77ft0`, kit v0.4.0 at
`fc6a32b5c2a9de112875d38ceb1e1eb2f9ef21d8`). Needs, before code, a short design pass:
- Pure reducer (`lift`, `resolveMiss`, `hintLevel`) with unit tests: board generation with planned distractors,
  hint ladder, miss counting (never shown), adapt rule.
- Board layout that survives the rotate prompt and 667x375 screens (lesson from Addition Garden).
- Quiz-only games ship no drag code, and this one should ship no drag code either (registry stays lean).
- Validator rules for `game.json` pictures, pair count and level shapes.
Why Opus: every game depends on the kit and on the session and reward data shapes.

## 9. Website work (Sonnet is fine)
`/logic-games/` category page (500 to 1000 words), game page (300 to 600 words), catalog entry in `src/data/games.json`,
`quilts` store next to `walls` in `src/scripts/progress.ts`, `HostInit.quilt`, smoke checks, sitemap entry.

## 10. Open questions for the owner (defaults used if no answer)
1. Title **Quilt Picnic**. Default: yes. Alternative: "Flap Friends".
2. Voice says only "Find two that match", never names the pictures. Default: yes (reading load and naming noise).
   Alternative: speak the friend's name when a flap lifts (helps vocabulary, adds audio files or speech noise).
3. Pictures: reuse earlier cast plus new simple pictures, hand-drawn SVG. Default: about 16 pictures in v1.
4. Quilt reward in v1, parent page later. Default: yes.
5. Level 5 colour variants. Default: yes, but only after the owner has tried levels 1 to 4 on a tablet.
6. Art preview first (`brand/memory-match/index.html`), owner approves, then build. Default: yes, same as the others.

## 11. Next steps (proposed order)
1. Owner reads this, answers section 10 (or says "defaults").
2. Opus design pass for `pair-match` (kit repo, then a doc here). Task is in Notion.
3. Static art preview in `brand/memory-match/`, owner approves.
4. Build bottom-up: kit reducer and tests, content, screen, browser tests, docs. Then game repo, sync, website, ship.
