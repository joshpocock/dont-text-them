# Regret Score: the point table

Use this when code execution is off. `scripts/regret.py` implements exactly this table.

| Stage | Points | When |
|---|---|---|
| 2am Factor | +25 (ex, situationship, crush) or +10 (anyone else) | 00:00 to 04:59 |
| Late Night Factor | +10 or +3 | 22:00 to 23:59 |
| Still Up From Last Night Factor | +10 or +3 | 05:00 to 06:59 |
| Recipient Risk | ex +20, situationship +15, boss +10, crush +8, coworker +8, family +5, group +5, other +3, friend 0 | boss and coworker only count late at night (20:00 or later) |
| Double Text Detector | +12 per unanswered message, max +36 | |
| Sobriety Check | +20 | drinking |
| Mood Check | angry +15, sad +10, lonely +10, tired +5 | |
| Regret Phrases | +6 per phrase, max +30 | "miss you", "u up", "why didn't you", "i'm fine", "whatever", "closure", "one last thing", "hope you're happy", "you never", "you always", "can we talk", "just wanted to say" and similar |
| Feelings Density | +8 | three or more of: hate, love, hurt, sorry, never, always, forever, ruined |
| Essay Detector | +10 over 400 characters, +20 over 1,000 | |
| Bridge Burner | +10 per phrase, max +40 | "i quit", "i'm done", "why i bother", "never enough", "find someone else", "read your mind", "with all due respect", "per my last", "not my job", "sick of", "fed up", "you people" and similar rage-quit lines, to anyone |
| Caps Lock Rage | +10 | over 30% of words in capitals |
| Interrogation Mode | +5 | three or more question marks |
| Exclamation Overload | +5 | three or more exclamation marks |
| Over-Apology | +5 | "sorry" twice or more |

**Time-Since-Breakup Multiplier** (ex and situationship only), applied to the sum:
under 7 days x1.5, under 30 days x1.3, under 90 days x1.15, under a year x1.0, a year or more x0.9.
The total is capped at 100.

**Boundary Alarm**: "needed space", "asked me not to", "blocked me", "no contact", "stop texting"
and similar in the draft set the score to at least 95. The answer is do not send.

## Bands

| Score | Band | Verdict | Cooling-off |
|---|---|---|---|
| 0 to 24 | green | Send it, it's fine | none |
| 25 to 49 | yellow | Sleep on it (or at least 30 minutes) | 30 minutes |
| 50 to 74 | orange | Cooling-off: wait until morning | at least 8 hours, released at 10:00 |
| 75 to 100 | red | DO NOT TEXT THEM | at least 20 hours, released at 10:00 the day after |

The weights are a judgment call, not research. They are tuned so that an ordinary text to a
friend at any hour stays green and a 2am "miss you" to a recent ex with drinks involved goes red.
Change them in `RECIPIENT_POINTS`, `STATE_POINTS` and the phrase lists if your life differs.
