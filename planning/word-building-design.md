# Letter Workshop (Word Building for Grade 1): design plan

Status: 2026-11-13. Owner picked option A and accepted every default. Built unattended; see
`planning/word-building-decisions-log.md` for each judgment call.
Friendly title: **Letter Workshop**. Keyword title and H1: **Word Building for Grade 1**.
URL: `/language-games/word-building-for-grade-1`. Game id `word-building-grade-1`,
repo `dr-nithish-kanna/word-building-grade-1`. Skill `language.phonics.word-building`. Mechanic: new kit mechanic
`slot-build` (kit v0.4.0).

## 1. The game in one sentence
A craft-room friend (mouse, hedgehog, bunny or robin) holds up a picture and the voice says the word ("cat").
The child drags letter tiles from a tray into slots to spell it. Each tile clicks in with its own note. When the word
is complete, the letters light one by one and the word is spoken, then a card of the word joins the child's word wall.

Micro-skill: blend and spell short words from letter tiles (CVC first, then blends, then 5 letters).

## 2. Why this game
First language game and first non-counting mechanic. Proves the kit works beyond `fill-container` and fills the
biggest gap (0 of 8 language games). Reuses drag layer, hint ladder, session record, pitch helpers, host contract.

## 3. A round
1. A friend arrives at the workshop door and holds a picture card. Hazel is the shop owner.
2. Voice says the word. The picture shows in a frame. The word itself is NOT shown (that would be copying, not spelling)
   except as the hint "Look".
3. Slots (3 to 5) sit on a workbench. The tray below holds letter tiles: the needed letters plus planned distractors.
4. The child drags (or taps tile then slot, or types the letter key) tiles into slots.
5. A right tile clicks in with its note. A wrong tile wobbles and hops back to the tray (no red mark, no buzzer).
6. Full word: letters light left to right with their notes, then the whole word is spoken. The friend is happy, a card
   goes onto the word wall.
7. Hints (hints only, never the answer): Look (Hazel points at the picture, the word is spoken again), Letter (the
   first empty slot glows), Tiles (the tiles that belong light softly). Hints ramp up on repeated wrong tiles.

## 4. Levels (difficulty 1 to 5)
| Level | Content | Tray |
|---|---|---|
| 1 | CVC words, 3 slots | exact letters + 1 distractor |
| 2 | CVC words, vowel trap | exact letters + 2 distractors including a wrong vowel |
| 3 | Missing letter: CVC with 1 or 2 slots already filled | exact needed letters + 2 distractors |
| 4 | 4-letter words with a blend (frog, stop, clap, drum) | exact + 2 distractors |
| 5 | 5-letter picture words (truck, plant, bread) | exact + 3 distractors |
Adapt rule like the other games (up after 3 correct, down after 2 wrong). Session ends at 8 words or 180 seconds.
Words are hand-written data in `game.json` items (language games use items, not generators), with a picture id each.

## 5. Reward (website owned)
**Word wall**: each word spelled correctly on the first full attempt or after hints is shown on a shelf as a small
picture card. The website stores the list of word ids per profile and game (facts, local, no login); the game gets the
list in HostInit and shows the shelf at the start and end of a session. A word counts once. No streaks, no loss.
Stored as facts, "My word wall" parent page is a later follow-up.

## 6. Feel
- Workshop room: warm wood, paper, craft shelves, soft lamp. Distinct from sunny garden and dusk pond.
- Each letter has a note (reuse `src/pitch.ts`): a-z map onto the pentatonic scale in 3 octaves, so a word is a tune.
  Every sound has a visual twin (tile glows).
- The voice says the whole word. We do not use speech for single letter sounds (browser speech says "see" for c).
- Reduced motion version of every animation, transform and opacity only.
- Hit targets at least 64 px. Drag, tap-then-tap and keyboard letter keys.

## 7. Cast
Mouse, hedgehog, bunny, robin (they bring the word requests), Hazel the owl is the shop owner.

## 8. Word bank (v1)
About 40 picture words (not 60): the art pipeline is hand-drawn SVG, and quality matters more than count.
Only words a 6 year old can recognise from a simple picture. Distribution about: L1 10, L2 8, L3 8 (reuse CVC),
L4 8, L5 6. Easy to extend: add a picture, add an item.

## 9. Owner decisions already made (defaults accepted 2026-11-13)
Game A, repo created, cast as above, word bank written by me, merge and deploy authorised when tests pass,
art preview reviewed by me, kit commits pinned by full SHA.
