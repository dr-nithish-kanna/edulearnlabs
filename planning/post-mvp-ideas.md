# Post-MVP ideas (parked on purpose)

Saved 2026-11-15 at the owner's request. These are NOT part of the MVP. Pick them up when development reaches the grade
they serve. The MVP stays 20 games for Pre-K to Grade 2 (`planning/mvp-games.md`).

## 1. Matching-pairs family: "two different faces" pairs (advanced games)

Owner feedback on Quilt Picnic: it is a good game, but it ends early and could serve advanced grades too.

**Observation.** `pair-match` (kit v0.5.0) pairs two identical pictures. The mechanic itself is content-agnostic. If a pair
can be two different faces that belong together (card A and card B), one mechanic covers every grade. Same rule as the main
`CLAUDE.md`: reuse mechanics, change content and difficulty, do not build new mechanics per grade.

**Game ideas that need only new content, a new skin and a reward each**
| Grade | Pair | Possible game |
|---|---|---|
| Kindergarten | numeral and its dots | Number Match |
| Pre-K / K | capital letter and small letter | Letter Match |
| Grade 1 | word and its picture | Word Match |
| Grade 1 to 2 | `4 + 3` and `7` | Fact Match |
| Grade 3+ | fraction and its picture, opposites, a science term and its meaning | later |

**Needed first (Opus-sized, shared data shape).** A kit change (likely v0.6.0) so a pair is two faces, not one picture twice:
the `pictures` items carry a second face, the board planner and validator know about it, and the voice never names the
pictures (a word face is read text, so the reading load rule needs a decision per grade). A short design pass doc comes first,
as with `planning/pair-match-design.md`. Quilt Picnic must keep working unchanged (identical faces stay the default).

**Why not just bigger boards.** Above 4x4 on a 667 x 375 phone the cards fall under the 64 px hit target. Harder content is
better than more cards.

## 2. Quick win for Quilt Picnic itself (small, no kit change)

A child who is clearing boards cleanly keeps playing: up to 8 boards instead of 5 (still ending at 3 minutes). Only
`game.json` `session.maxQuestions` and checks that the patch cycle (8 patches) and the end screen handle more patches.
More boards also means more patches on the quilt per session. Do this only if play-testing shows 5 boards feels short.

## Open when we pick this up
- Which advanced game comes first (my suggestion: Number Match for Kindergarten or Fact Match for Grade 1).
- How the website shows rewards per game (one quilt shared by the family of games, or one reward per game).
