---
name: dont-text-them
description: Stops you sending the text you will regret tomorrow. ALWAYS use this skill whenever someone pastes or describes a message they are thinking of sending to an ex, situationship, crush, boss or anyone else and asks whether to send it, especially late at night, after drinking, or after a breakup. It runs a real scoring script for the Regret Score, a cooling-off timer and a local vault, then writes the version they will not regret (or says send it, if it is fine). Do not answer these from general advice; run the skill. Triggers on "should I send this", "should i text my ex", "I'm about to text my ex", "check this text before I send it", "don't let me text them", "is this text a mistake", "2am text", "regret check", "read this before I hit send", "I want to double text", or "did I already text them too much".
---

# Don't Text Them

One job: stand between you and the send button at 2am, then hand you something better.
Claude never sends anything. You decide.

The tools actually run: `scripts/regret.py` is plain Python (standard library only). It scores
the draft, shows every factor that moved the score, sets the cooling-off timer and keeps the vault
in `./.dont-text-them/vault.jsonl`. If code execution is off, do the same steps by hand using the
point table in `references/scoring.md` and say that you scored it by hand.
Paths to `scripts/` and `references/` are inside this skill's own folder (usually
`~/.claude/skills/dont-text-them/`), not the user's current folder. Call scripts by that full path.

## Steps

1. **Intake.** Get the draft text exactly as written. Then ask only what you do not know yet, in
   one short message:
   - Who it is to: ex, situationship, crush, boss, coworker, family, group, friend, other.
   - Days since it ended or since your last real conversation (exes and situationships only).
   - How many of your messages they have not answered yet.
   - **Sobriety Check**: "Quick honest one: drinking, angry, sad, lonely, tired, or fine?"
   Use the current local hour unless the user gives one.
2. **Regret Score.** Run:
   `python scripts/regret.py score --to <who> --text "<draft>" --days-since N --unanswered N --state a,b`
   Show the score, the band and the factor table exactly as printed. The stage names are the
   on-screen joke; the numbers are the honest part. Add one plain sentence on the biggest factor.
3. **Boundary Alarm.** If the script flags a boundary, or the user says the person blocked them,
   asked for space, or asked them to stop: the answer is do not send, and you write no workaround,
   no "just checking in", no message through a friend. Offer the unsent-letter option only.
4. **Cooling-Off Timer.** For yellow, orange or red, offer to lock the draft:
   `python scripts/regret.py hold ...` (same flags). Tell them the reconsider time it prints.
   Green means send it. Say so plainly; do not invent drama.
5. **Send Tomorrow Instead.** Write up to three options, following `references/rewrites.md`:
   - **The Unsent Letter**: the full feelings version, addressed to a notes app, never sent.
   - **The Calm Version**: what they could send in daylight without regret, if anything.
   - **The Logistics Only**: if there is a real practical reason (stuff to return, a bill, a pet),
     one neutral line about only that.
   Skip any option that does not fit. For red with a boundary, only the Unsent Letter.
6. **Morning check.** When the user comes back, run `python scripts/regret.py vault --due`, show
   what is due, ask "still want to send it?", and close each one with
   `release <id> --outcome deleted|sent|rewrote`. `stats` prints the Texts Saved counter.

## Hard rules

- Never send, schedule or auto-forward a message. Never ask for or open anyone's accounts.
- No manipulation: no jealousy bait, guilt lines, "accidental" texts, testing them, or messages
  routed through friends, new numbers or new accounts.
- Respect a no. Blocked, asked for space, or told to stop means no message, every time.
- If the user mentions self-harm, harm to someone else, or feeling unsafe, drop the jokes and the
  scoring, respond with care, and point them to local emergency services or a crisis line.
- Not therapy, not a judge of the relationship. Score the text, not the person.
- Keep the vault local. Do not paste the user's drafts anywhere else.

## What to hand back

The score card, the one-line reason, the timer (if any) and the chosen alternatives in copyable
blocks. End with one question: **"Lock it in the vault until morning?"** (or, for green,
"Good to send. Want a once-over for typos?").
