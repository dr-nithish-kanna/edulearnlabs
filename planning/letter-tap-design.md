# Design: Letter tap (game 6, MVP number 9)

Draft 2026-11-17. Status: owner picked the recommendation, defaults below, waiting for the owner's critique. Nothing built.

## 1. The skill

- Grade: Pre-K. Subject: language. Topic: letters. Taxonomy id: `language.letters.letter-recognition`.
- One micro-skill: **hear a letter name and find that letter among others** (uppercase first).
- Common Pre-K errors this game must handle: look-alike letters (b and d, p and q, M and W), mixing up letters with
  similar sounds, and knowing a letter's song but not its shape.

## 2. Owner decisions (2026-11-17, "your recommendation")

| # | Decision | Pick |
|---|---|---|
| 1 | Game | #9 Letter tap, Pre-K |
| 2 | How the child plays | Letter hunt: letters hide in a scene, the voice asks for one, the child taps it |
| 3 | Reward (website-owned) | Alphabet train: one car per solved letter, with the letter and an object ("B, ball") |
| 4 | Feel | Voice says the letter name, then the sound and a word. Every sound has a visual twin |
| 5 | Cast | A fox station master asks for letters. Hazel stays as host |

## 3. Defaults I chose (owner may change)

1. Title: **Letter Station**. Alternative: Fox and the Alphabet Train.
2. Letter set: start with 8 letters and grow by level, so a 3 year old is never faced with 26 at once.
3. Uppercase only at launch. Lowercase later (it is a new level set, not a new game).
4. Voice: browser speech synthesis now, recorded voice later, as in the other games.
5. Portrait phones: the "turn your phone sideways" prompt, as in the other games.

## 4. Level ladder

| Level | Letters in the scene | Letter pool | Notes |
|---|---|---|---|
| 1 | 3 | A to H, no look-alikes together | Big, spread out, easy |
| 2 | 5 | A to M | Adds look-alike awareness in the planner |
| 3 | 6 | A to T | Mixed sizes |
| 4 | 8 | A to Z | Includes look-alikes (b and d is lowercase later, so M and W, E and F, O and Q first) |

Defaults: advance after 2 correct rounds in a row, never drop below the current level on a miss, a miss only repeats
the hint.

## 5. Mechanic: letter hunt

- Reuses the `tap-count` scattered-objects scene and its planner (no overlap, 64 px minimum targets), but the question
  changes: **"Find B"** instead of "count them". Expect a small kit change, a new mode or a new mechanic id. Needs a
  short Opus check before any kit work (flag below).
- Letters sit on scene objects (a sign, a suitcase, a lamp) so a letter is never hidden behind another. Never rely on
  per-item labels in a crowded group (playbook lesson).
- The voice says the letter name first, then the child taps. The correct letter hops, glows and plays its note, and
  the train car appears.
- Wrong tap: that letter dims and says its own name softly. Never a red X or buzzer. After two misses the other letters
  dim, leaving the answer (hints only, same ladder as fill).
- Idle hint: the target twinkles after a few seconds.
- Keys and touch: Tab and Enter work. Hit targets at least 64 px. Reduced-motion version of every animation.

## 6. Open design question for the Opus pass

Reuse `tap-count` with a new "find" mode, or add a small `letter-find` mechanic? The test is whether the reducer and
planner can be shared without bending tap-count's rules (its numbers belong to the tap order, a letter belongs to the
question). My lean: a new mechanic that imports the planner. Decide before building.

## 7. Story and sound

- The fox station master has a train that needs one letter per car. Six rounds per session, about 3 minutes.
- Voice line finishes before any tone starts. Letter notes map onto the existing pentatonic scale.
- Words for the car objects are short and picture-led (A apple, B ball, C cat). Reading load is minimal.

## 8. Reward: Alphabet train (website-owned)

- The game only reports `rewards` as facts, for example `{ id, kind: "car", letter, at }`.
- The website stores them like the parade, quilt, word wall and garden: own schema version, newer-schema guard, 200 cap
  that folds the oldest into a count, no streaks, growth by rounds solved and never by time.
- A parent "My train" page is a later item, like the other reward pages.

## 9. Website and SEO

- Game id: `letter-tap-prek`. Page: `/language-games/letter-recognition-for-preschool/`.
- Title with keyword, age and benefit. 300 to 600 words of real text. Catalog entry in `src/data/games.json`, skill
  `language.letters.letter-recognition`, home card, privacy text mentions the train.
- No ads, prices or external links in the game.

## 10. Flags

- **Opus**: mechanic choice (section 6) and the kit data shape. Everything else (art, copy, content JSON, pages) is Sonnet.
- Check `git branch -r` in the kit first. The session checkout is stale (v0.1.0). The latest kit work is on
  `claude/amazing-albattani-g2r7l1` at v0.6.1 (`256bea19a544ef019b27e3290e011aeb28725e47`).

## 11. Next steps

1. Owner critiques this doc.
2. Opus design pass: `planning/letter-find-design.md`.
3. Static art preview in `brand/letter-tap/` (fox, station, train cars, scene objects). Owner approves.
4. Build bottom-up: kit mechanic with tests, content, game screens, browser tests, website support, sync.
