# Don't Text Them

One Claude skill that stops you sending the text you will regret tomorrow. Free, MIT, no signup,
no API key, nothing to connect.

**It never sends anything. It never touches your phone or your accounts. You paste the draft,
Claude scores it, and you decide.**

Paste the message you are about to send. Claude gives it a Regret Score out of 100, shows exactly
why, locks it in a vault until morning if it needs to, and writes the version you will not regret.
If the text is fine, it tells you to send it.

## Install

**Claude Code, one paste.** Paste this into Claude Code:

```
Install the Don't Text Them skill: clone https://github.com/joshpocock/dont-text-them into ~/.claude/skills/dont-text-them, then confirm /dont-text-them works.
```

Or in a terminal:

```
git clone https://github.com/joshpocock/dont-text-them ~/.claude/skills/dont-text-them
```

Start a new Claude Code session and type `/dont-text-them`, then paste the text you're about to send.

**Claude.ai (website or app).** Turn on Settings, Capabilities, **Code execution and file
creation**. On this GitHub page click Code, Download ZIP. In Claude go to Customize, Skills, +,
Upload a skill, and pick the zip. Start a new chat and say "use the dont-text-them skill".

**Any chat, no install.** Copy the text of `SKILL.md` into a chat and paste your draft under it.
The scoring table in `references/scoring.md` lets Claude score it by hand.

## How it works

| Stage | What happens |
|---|---|
| Sobriety Check | One honest question about how you are doing right now |
| Regret Score | 0 to 100, with every factor shown: the 2am Factor, Recipient Risk, the Double Text Detector, Regret Phrases, the Bridge Burner, the Essay Detector, Caps Lock Rage |
| Time-Since-Breakup Multiplier | A recent breakup multiplies the score; a year later it shrinks it |
| Boundary Alarm | If they asked for space or blocked you, the answer is no, and Claude writes no workaround |
| Cooling-Off Timer | Locks the draft in a local vault until 10am |
| Send Tomorrow Instead | The Unsent Letter, the Calm Version, or Logistics Only |

| Score | Verdict |
|---|---|
| 0 to 24 | Send it, it's fine |
| 25 to 49 | Sleep on it (or at least 30 minutes) |
| 50 to 74 | Wait until morning |
| 75 to 100 | DO NOT TEXT THEM |

## One text, start to finish

A made-up draft, real tool output. The draft: "hey. i know it's late but i miss you. why didn't you answer my text last night? i'm
fine btw, just wanted to say i hope you're happy". To an ex, 2am, nine days after, one unanswered
text, drinking and sad.

```
REGRET SCORE: 100/100  [RED]  DO NOT TEXT THEM
  2am Factor                          +25   it is 02:00
  Recipient Risk                      +20   sending to: ex
  Double Text Detector                +12   1 message(s) still unanswered
  Sobriety Check                      +20   you said: drinking
  Mood Check                          +10   you said: sad
  Regret Phrases                      +30   "miss you", "why didn't you", "i'm fine", "hope you're happy", "just wanted to say"
  Time-Since-Breakup Multiplier      x1.3   9 day(s) since it ended
COOLING-OFF TIMER: reconsider at 2026-10-28T10:00
LOCKED IN THE VAULT as #36bc3f. Run `vault --due` in the morning.
```

The same tool on "landed safe, thanks for the ride" to a friend at 2am: 10/100, send it.

## The tool

`scripts/regret.py` is plain Python 3 with no installs.

```
python scripts/regret.py score --to ex --text "u up?" --hour 2 --days-since 9 --state drinking
python scripts/regret.py hold  --to ex --text "u up?"     # score it and lock it in the vault
python scripts/regret.py vault --due                       # the morning check
python scripts/regret.py release <id> --outcome deleted    # or sent, or rewrote
python scripts/regret.py stats                             # your Texts Saved counter
python -m unittest discover -s tests                       # 8 tests
```

The vault is a file in `.dont-text-them/` in the folder you run it from. It never leaves your
computer.

## Fine print

- The weights are a judgment call, not science. Change them in `scripts/regret.py`.
- Not therapy and not a verdict on your relationship. If you are struggling, talk to someone you
  trust or a local support line.
- If you feel unsafe, or someone else is, contact local emergency services.

## More free skills

Made by Josh Pocock. More at [strideaiacademy.com](https://strideaiacademy.com).

MIT licence.
