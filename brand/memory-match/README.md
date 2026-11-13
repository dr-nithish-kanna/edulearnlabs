# Quilt Picnic art preview

Static preview for the Memory Match game (Pre-K and Kindergarten). Open `index.html` in a browser. It is one
self-contained file with no external requests. Rebuild it with `python3 build.py` (Hazel is copied from
`../mascot/owl.svg`, never redrawn).

Spec: `planning/memory-match-design.md`.

## Picture ids (these become the game's item ids)

ladybug, snail, bee, rabbit, fox, duck, hedgehog, mouse, apple, ball, star, cup, butterfly, fish, flower, kite

Each picture is a 100 x 100 viewBox with art kept inside 8 to 92 for headroom.

## Notes

- Scene is 960 x 600. Sky, hills, grass and cloth are drawn far past the box (gradients in `userSpaceOnUse`), so the
  game host should set `overflow: visible` on the scene svg. The preview page clips it.
- Board cell size is the largest square that fits the fixed board area: 150 px (2 x 2, capped), 116 px (3 x 4),
  about 86 px (4 x 4) at 960 x 600.
- Motion is transform and opacity only, with a `prefers-reduced-motion` version.
- Headings use a system rounded font in the preview to avoid external requests. The game ships subset Fredoka and Andika.
