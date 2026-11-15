# Color pattern repeat (Kindergarten, logic): design plan

Status: 2026-11-15, DRAFT for owner critique. Owner picked "Color pattern repeat" (MVP number 18), attended session.
Ideas chosen: finish the string (1), copy the pattern as level 1 (2), bracelet collection (5), pattern is a tune (7),
shapes on every bead (locked), spider bead-maker in a cozy craft room (picked). Nothing is built yet.
Friendly title: **Bead Parlor** (default, see section 10). Keyword title and H1: **Pattern Games for Kindergarten**.
URL: `/logic-games/pattern-repeat-for-kindergarten`. Game id `pattern-repeat-k`, repo `dr-nithish-kanna/pattern-repeat-k`.
Skill `logic-memory.patterns.repeat`. Mechanic: `slot-build` generalized from letters to tokens (kit v0.6.0, Opus pass first).

## 1. The game in one sentence
A friendly spider is stringing bracelets for the children in the craft room. A bead string has gaps. The child puts the
right beads in the gaps so the pattern keeps going, and a finished bracelet joins their own collection.

Micro-skill: see the repeating unit in a sequence and continue it (early algebra thinking, ages 5 to 6).

## 2. Ideas considered (the discussion, grouped as in the playbook)
- **A. Child does the skill:** 1 finish the string (chosen), 2 copy the pattern (level 1 only), 3 spot the broken bead
  (later level, different skill), 4 shape and size patterns (later content, same mechanic).
- **B. Reward:** 5 bracelet collection (chosen), 6 growing ribbon (rejected: it ends and invites "one more").
- **C. Feel:** 7 pattern is a tune (chosen), 8 bead-maker character (chosen, as a spider).

## 3. Why this combination (honest critique)
- Gap filling is the right skill check. A child who can continue ABAB has seen the unit. Copying alone only proves matching.
- Trial and error is the known hole (same as Letter Workshop): with 2 colors a child can guess. Closed the same way: a wrong
  bead never counts as first try, and each wrong bead climbs the hint ladder. The child still always finishes and always gets the bracelet.
- **Color alone excludes color-blind children** (about 1 in 12 boys). Every color is paired with a shape, so the pattern can be
  read by shape alone. Test in a grayscale screenshot: every bead must still be tellable apart.
- The tune helps because the pattern becomes a repeating melody: a wrong bead sounds odd even though no buzzer plays.

## 4. A round (one bracelet)
1. The spider brings a string of beads with 1 to 3 gaps. The voice says "What comes next?" (no color names).
2. The tray shows a few beads. The child drags a bead into a gap or taps the bead then the gap, or uses the keyboard.
3. The right bead clicks in and plays its note, and stays. A wrong bead wobbles and hops back (no red, no buzzer).
4. When all gaps are filled, the pattern plays as a tune left to right, each bead lights in turn, the bracelet is tied,
   and it flies to the child's collection.
5. A session is 5 bracelets or about 180 seconds.

Hint ladder (hints only, never the answer), same rungs as slot-build:
- H1 Look: the first repeat unit pulses so the child can see where the pattern starts. Free.
- H2 Gap: the next gap to fill glows. Costs first try.
- H3 Beads: the beads still needed glow softly. Costs first try.

## 5. Levels (difficulty 1 to 5)
| Level | Pattern | Gaps | Tray |
|---|---|---|---|
| 1 | Copy: pattern shown above, build the same below (AB) | 4 slots, none given | exactly the needed beads plus 1 |
| 2 | Continue AB at the end | 1 | 2 colors, 1 spare |
| 3 | Continue ABB, AAB or ABC | 2 | 3 colors |
| 4 | Gaps in the middle as well as the end | 2 to 3 | 3 colors plus a look-alike shape |
| 5 | Longer units (ABCD, AABB) or size patterns | 3 | 4 colors |
Adapt rule like the other games: up after `upAfterCorrect` first-try bracelets, down after `downAfterWrong`.
Patterns are data (`game.json` items), never hardcoded. A pattern item is a unit string such as `"ABA"` plus a length,
and a level maps the letters to bead ids, so level 5 can reuse the generator.

## 6. Beads: color plus shape (locked)
Six beads for v1, each with a color, a shape and a note on the pentatonic scale (kit `src/pitch.ts`):
| Bead | Color | Shape |
|---|---|---|
| red | red | circle |
| blue | blue | square |
| yellow | yellow | triangle |
| green | green | star |
| purple | purple | diamond |
| orange | orange | heart |
Colors are chosen to stay apart under the common color-blind types (deuteranopia and protanopia). Do not put red and green
in the same level until shapes carry the difference (they do, but level 1 to 3 use red, blue, yellow only).
Tray planning rule: no two beads in one level share a shape or a very close color.

## 7. Reward (website owned)
**My bracelets:** one bracelet per finished string, shown as a small picture strip on a shelf. The website stores bracelet
patterns per profile and game as facts (own `v`, newer-schema guard, same as `walls` and `quilts`). The game receives
`HostInit.bracelets` (newest 64, oldest first) and reports `rewards` of kind `bracelet` (the pattern id and the beads).
A "My bracelets" parent page is a later follow-up, same as "My garden", "My word wall" and "My quilt".
A bracelet is kept even if it was not first try (effort is rewarded, like the word wall).

## 8. Kit work (Opus-sized, do not start on Sonnet)
Generalize `slot-build` from letters to tokens, as kit v0.6.0. A design pass doc `planning/token-slot-design.md` first.
Points to settle: replace the letter-specific parts (`letterPitch`, `LetterMistake`, "never in word order") with a token
interface; a "slot wants token T" rule that works for letters and beads with the golden files unchanged; the pattern
generator (unit plus length, given positions, middle gaps); mistake kinds for patterns (`wrong-in-unit`, `look-alike`
shape, `breaks-pattern`); validator rules for `game.json`; reward type `bracelet`; reduced motion; 667 x 375 layout.
Why Opus: every game depends on the kit, and Letter Workshop must keep working without changes.
Alternative if the generalization proves too wide: a thin `pattern-fill` runner that reuses `slot.ts` internals.
The design pass should compare both and recommend one.

## 9. Website work (Sonnet is fine)
`/logic-games/` already exists, so add the game page (300 to 600 words), a catalog entry in `src/data/games.json`,
`bracelets` store next to `quilts` in `src/scripts/progress.ts`, `HostInit.bracelets`, parent tip lines for the new
mistake kinds, smoke checks. The sitemap is generated.

## 10. Open questions for the owner (defaults used if no answer)
1. Title **Bead Parlor**. Alternative: "Spider's Bead Shop". Default: Bead Parlor.
2. Voice says only "What comes next?", never color names. Default: yes (reading load, and shape plus color both carry meaning).
3. Six beads in v1, growing to eight later. Default: six.
4. Level 4 look-alike shapes (circle and heart). Default: yes, only after the owner tries levels 1 to 3 on a tablet.
5. Spider named **Webb**? Default: a small friendly spider, name decided in the art preview.
6. Art preview first (`brand/pattern-repeat/index.html`), owner approves, then build. Default: yes.

## 11. Next steps (proposed order)
1. Owner critiques this doc and answers section 10 (or says "defaults").
2. Opus design pass for the token generalization (kit repo, then `planning/token-slot-design.md` here).
3. Static art preview in `brand/pattern-repeat/` (craft room, spider, six beads, grayscale check), owner approves.
4. Build bottom-up: kit reducer and tests, content, screen, browser tests, docs. Then game repo, sync, website, ship.
