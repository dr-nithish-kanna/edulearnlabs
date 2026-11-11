# Decisions log

## Revenue (decided 2026-11-11)
- Launch free, no ads. Build SEO traffic first.
- Turn on website-level, non-personalized ads at about 5k to 10k monthly visitors.
- Family subscription later, removes ads. Price TBD.
- Why changed from "ads from day 1": a new site has almost no traffic so ads earn about nothing, AdSense needs
  content and traffic to approve, and child-directed content limits ad earnings.

## Scope
- All grades in the taxonomy. MVP is 20 games, Pre-K to Grade 2.

## Name
- EduLearnLabs.

## Engine test (to run before committing)
Build one game, Addition for Grade 1, twice:
1. TypeScript + Phaser 3
2. Plain HTML, CSS, TypeScript
Optionally compare against an existing Unity build.
Measure: gzipped build size, first load time on throttled network and slow CPU, frames per second on a low-end
device, and how fast Claude Code can build and change it. Pick the lightest option that feels good.
Use Opus for the final decision.

## Open items
- Subscription price and payment provider (India, tax handling).
- Final engine choice after the test.
- Logo and visual style guide.
- Asset plan: Kenney packs, one itch.io pack, AI-generated icons, recolor and reuse, shared asset bank.
