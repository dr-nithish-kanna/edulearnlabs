# Universal game rules (copy into every game repo)

Source of truth: `planning/framework-spec.md` and `planning/decisions.md` in the main repo
(dr-nithish-kanna/edu-learn-labs). If this file and the spec disagree, the spec wins. Fix this file.

## Play
1. **Session length:** 2 to 5 minutes. Ends at `session.maxQuestions` (10 to 15) or `session.maxSeconds` (about 180),
   whichever comes first. Never endless, never autoplay into another game.
2. **One skill per game.** One micro-skill (a `skill` ID from the main repo's `content/skills.json`), one mechanic.
3. **Controls:** tap or click, Space or Enter, arrow keys, number keys 1 to 4. Large hit areas (at least 64 px).
   No precision timing, no fast reflexes.
4. **Drag and drop:** smooth and forgiving. Item lifts with a shadow, magnetic snap to targets, generous drop zones.
   Tap item then tap target must always work too. Use Pointer Events, never the HTML5 drag and drop API.
5. **Attempts:** wrong first try gives a gentle hint and a second try. Wrong again: a stronger hint (never the
   answer itself; for example dim a wrong choice or light up counting aids) until the child makes the final tap.
   The mascot says something kind ("Now you know it!"). No red X, no buzzer, no "Game Over". Decided 2026-11-12.
6. **Difficulty ramp:** start at the level the website suggests (level 1 for new players). 3 first-try correct in a
   row moves up one level, 2 wrong in a row moves down one level. Never jump more than one level.
7. **Golden rule:** if a 6 year old cannot understand the goal in 5 seconds, redesign it.

## Look, sound and feel ("juicy but fair")
8. **Visuals:** bright, saturated colors on the mascot, rewards and celebrations. Keep the area around the question
   calm and uncluttered. Decoration that is not the lesson goes at the edges, not next to the task.
9. **Feedback within 0.3 seconds:** visual (spring, squash and stretch, particle burst), audio, and a mascot reaction.
10. **Motion:** use ell-kit `juice` helpers (CSS transforms and Web Animations). Respect `prefers-reduced-motion` and
    the site's reduced-motion setting: swap big motion for simple fades.
11. **Audio:** every question is spoken. Sound on every tap. Rising pitch on correct answers in a row. Soft music,
    ducked under voice. Soft sounds only. Audio and music follow the website's toggles.
12. **UI density:** one question, 2 to 4 choices, the mascot, one progress indicator. Nothing else on the play area.
13. **Reading load:** ages 5 to 7 use words of 5 letters or fewer, icons and audio. Ages 8 to 12 use short sentences
    with optional narration.

## Rewards and engagement
14. **Allowed:** stars (1 for finishing, 2 at 70% first-try, 3 at 90%), mastery plant stages, stickers at fixed
    milestones (child chooses 1 of 3 designs), mascot outfits unlocked by mastery, varied praise lines, surprise
    celebrations at milestones, a happy ending screen with Play Again and Back to Games.
15. **Never:** streaks or anything that wilts or is lost when a child stops, random or mystery rewards, loot boxes,
    fake timers or countdowns, a mascot that guilts a child into staying, endless levels, leaderboards or comparing
    children, failure screens.

## Content
16. **Data-driven:** all content lives in `game.json` (levels with `items` or a `generator`). No questions in code.
17. **Stable IDs:** item IDs never change meaning (`q-3-4` is always 3 + 4). Missed item IDs are saved for practice.
18. **Planned distractors:** wrong choices reflect real mistakes (off by one, wrong operation) so a mistake tells us
    something.
19. **Validated at build time** with the mechanic's JSON Schema. The validator is not shipped to the browser.

## Website contract and safety
20. **Runs in an iframe** at `/play/<game-id>/`. Talks to the website only through ell-kit `host` messages:
    sends `GameReady`, `GameStarted`, `GameCompleted`, `GameExit`, `GameError`; receives `HostInit`, `HostSettings`,
    `HostPause`, `HostResume`. Check message origin.
21. **No storage in the game.** Never read or write localStorage, cookies or IndexedDB. The website saves progress.
22. **No personal data.** The game gets an avatar and color, never a profile ID, name or age.
23. **No money and no exits:** no ads, prices, upsells, external links, chat or popups. The website handles all of that.
24. **First screen is "Tap to start"** with the mascot. That tap unlocks audio on every browser.

## Performance
25. **Before Play** (shell code and first screen): 100 KB or less. Firm.
26. **Code:** ell-kit 15 KB brotli or less plus game code 15 KB brotli or less.
27. **After Play** (art, audio): about 1.5 MB by default, listed in `asset-manifest.json` so the website can preload it.
    Can grow when the game needs it and it is worth it. Explain why in the README with size and load time.
28. **Runs on old Chromebooks:** first load under 5 seconds on the throttled profile (4x CPU slowdown, about 1.6 Mbps,
    150 ms latency), 60 fps. Sprites 512 px max in atlases, audio mono 22 kHz MP3 at 48 to 64 kbps.
