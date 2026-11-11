# Universal game rules (copy into every game repo)

1. **Session length:** 2 to 5 minutes. End after 10 to 15 questions or 3 minutes. Never endless.
2. **One skill per game.** One micro-skill, one mechanic.
3. **Controls:** mouse or tap, Space or Enter, arrow keys, number keys 1 to 4. No precision timing, no fast reflexes,
   no physics-heavy dragging. Use large hit areas.
4. **Feedback:** within 0.3 seconds. Visual, audio and a character reaction. Soft sounds. No harsh buzzers or red X.
5. **UI density:** at most one question, 2 to 4 choices, one character, one progress indicator.
6. **Reading load:** ages 5 to 7 use words of 5 letters or fewer, icons and audio. Ages 8 to 12 use short sentences
   and optional narration. Support audio playback for questions.
7. **Difficulty ramp:** start easy, rise slowly, never spike. If a child fails twice in a row, ease off.
8. **Performance:** runs on old school PCs and Chromebooks. Small build, first load under 5 seconds, 60 fps.
   Sprites at most 512px, mono audio at about 22 kHz, short animations, sprite atlases, no heavy effects.
9. **Rewards:** stars, stickers, badges, unlocks. No streaks, rankings or loot boxes. Rewards are evidence of learning.
10. **Retry:** instant replay, big Play Again button. No "Game Over". Say "Let's try again".
11. **No money in games:** no ads, prices or upsells. Website handles all of that.
12. **Data-driven:** questions and levels live in JSON. Tag each game with grade, subject, topic, micro-skill, mechanic.
13. **Website contract:** game reports `GameStarted`, `GameCompleted` (accuracy tier, time) and reads nothing about the user.
    Progress is saved locally through the shared progress schema.
14. **Golden rule:** if a 6 year old cannot understand the goal in 5 seconds, redesign it.
