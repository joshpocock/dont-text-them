#!/usr/bin/env python3
"""Don't Text Them: regret scorer, cooling-off timer and the vault of saved texts.

Standard library only. Nothing here sends a message. It scores a draft, tells
you how long to wait, and keeps a local log so the morning version of you can
decide.

Usage:
  python regret.py score --to ex --text "u up?" [--hour 2] [--days-since 9]
                         [--unanswered 2] [--state drinking,sad] [--json]
  python regret.py hold  --to ex --text "..." [same options]   # score + save to the vault
  python regret.py vault [--due]                             # list held texts
  python regret.py release ID --outcome deleted|sent|rewrote # close one out
  python regret.py stats                                     # texts saved so far

Data lives in ./.dont-text-them/vault.jsonl (change with --dir).
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import uuid

RECIPIENT_POINTS = {
    "ex": 20, "situationship": 15, "crush": 8, "boss": 10, "coworker": 8,
    "family": 5, "group": 5, "friend": 0, "other": 3,
}
STATE_POINTS = {"drinking": 20, "angry": 15, "sad": 10, "lonely": 10, "tired": 5, "fine": 0}

# Phrases that tend to be regretted in daylight. Each hit adds points (capped).
RISK_PHRASES = [
    "miss you", "miss u", "u up", "you up", "are you awake", "why didn't you",
    "why did you", "we need to talk", "i'm fine", "im fine", "whatever",
    "closure", "one last thing", "hope you're happy", "hope ur happy",
    "i saw you", "who is she", "who is he", "you never", "you always",
    "i still love", "can we talk", "just wanted to say", "no offense but",
    "thanks for nothing", "do you even", "remember when", "last time i promise",
]
# Signs the other person already asked for distance. These override everything.
BOUNDARY_PHRASES = [
    "needed space", "need space", "needs space", "asked me not to", "told me not to",
    "blocked me", "said not to text", "said not to contact", "no contact", "leave them alone",
    "leave her alone", "leave him alone", "stop texting",
]
# Rage-quit lines that burn a bridge at work, with family or with friends.
BRIDGE_PHRASES = [
    "i quit", "i'm done", "im done", "why i bother", "never enough", "find someone else",
    "read your mind", "with all due respect", "per my last", "not my job", "sick of",
    "fed up", "you people", "screw this", "screw you", "f you", "fuck you", "fuck this",
    "good luck without me", "don't bother", "you'll regret",
]
EMOTION_WORDS = ["hate", "love", "hurt", "sorry", "never", "always", "forever", "ruined"]


def hour_points(hour, to):
    """Late hours only weigh heavily for texts with romantic or emotional stakes."""
    heavy = to in ("ex", "situationship", "crush")
    if 0 <= hour <= 4:
        return (25 if heavy else 10), "2am Factor"
    if hour in (22, 23):
        return (10 if heavy else 3), "Late Night Factor"
    if hour in (5, 6):
        return (10 if heavy else 3), "Still Up From Last Night Factor"
    return 0, None


def breakup_multiplier(to, days):
    if to not in ("ex", "situationship") or days is None:
        return 1.0
    if days < 7:
        return 1.5
    if days < 30:
        return 1.3
    if days < 90:
        return 1.15
    if days < 365:
        return 1.0
    return 0.9


def score(text, to="other", hour=None, days_since=None, unanswered=0, states=()):
    """Return a dict with the score (0-100), the band and every factor that moved it."""
    to = (to or "other").lower()
    if hour is None:
        hour = dt.datetime.now().hour
    factors = []
    raw = 0

    pts, label = hour_points(hour, to)
    if pts:
        raw += pts
        factors.append((label, pts, f"it is {hour:02d}:00"))

    rp = RECIPIENT_POINTS.get(to, 3)
    if to in ("boss", "coworker") and not (pts or hour >= 20):
        rp = 0  # texting your boss at 2pm is just work
    if rp:
        raw += rp
        factors.append(("Recipient Risk", rp, f"sending to: {to}"))

    if unanswered:
        up = min(36, 12 * int(unanswered))
        raw += up
        factors.append(("Double Text Detector", up, f"{unanswered} message(s) still unanswered"))

    for s in states:
        s = s.strip().lower()
        if s in STATE_POINTS and STATE_POINTS[s]:
            name = "Sobriety Check" if s == "drinking" else "Mood Check"
            raw += STATE_POINTS[s]
            factors.append((name, STATE_POINTS[s], f"you said: {s}"))

    low = text.lower()
    hits = [p for p in RISK_PHRASES if p in low]
    if hits:
        hp = min(30, 6 * len(hits))
        raw += hp
        factors.append(("Regret Phrases", hp, ", ".join(f'"{h}"' for h in hits)))

    burns = [p for p in BRIDGE_PHRASES if p in low]
    if burns:
        bp = min(40, 10 * len(burns))
        raw += bp
        factors.append(("Bridge Burner", bp, ", ".join(f'"{b}"' for b in burns)))

    emo = sum(len(re.findall(r"\b" + w + r"\b", low)) for w in EMOTION_WORDS)
    if emo >= 3:
        raw += 8
        factors.append(("Feelings Density", 8, f"{emo} heavy words"))

    n = len(text)
    if n > 1000:
        raw += 20
        factors.append(("Essay Detector", 20, f"{n} characters"))
    elif n > 400:
        raw += 10
        factors.append(("Essay Detector", 10, f"{n} characters"))

    words = re.findall(r"[A-Za-z]{2,}", text)
    caps = [w for w in words if w.isupper()]
    if words and len(caps) / len(words) > 0.3 and len(caps) >= 2:
        raw += 10
        factors.append(("Caps Lock Rage", 10, f"{len(caps)} words in capitals"))
    if text.count("?") >= 3:
        raw += 5
        factors.append(("Interrogation Mode", 5, f"{text.count('?')} question marks"))
    if text.count("!") >= 3:
        raw += 5
        factors.append(("Exclamation Overload", 5, f"{text.count('!')} exclamation marks"))
    if low.count("sorry") >= 2:
        raw += 5
        factors.append(("Over-Apology", 5, f"{low.count('sorry')} sorrys"))

    mult = breakup_multiplier(to, days_since)
    total = min(100, round(raw * mult))
    if mult != 1.0:
        factors.append(("Time-Since-Breakup Multiplier", f"x{mult}", f"{days_since} day(s) since it ended"))

    boundary = [p for p in BOUNDARY_PHRASES if p in low]
    if boundary:
        total = max(total, 95)
        factors.append(("Boundary Alarm", "min 95", "they asked for distance: " + ", ".join(f'"{b}"' for b in boundary)))

    if total >= 75:
        band, verdict, wait_h = "red", "DO NOT TEXT THEM", 20
    elif total >= 50:
        band, verdict, wait_h = "orange", "Cooling-off: wait until morning", 8
    elif total >= 25:
        band, verdict, wait_h = "yellow", "Sleep on it (or at least 30 minutes)", 0.5
    else:
        band, verdict, wait_h = "green", "Send it, it's fine", 0
    return {
        "score": total,
        "band": band,
        "verdict": verdict,
        "raw_points": raw,
        "multiplier": mult,
        "factors": [{"stage": f[0], "points": f[1], "why": f[2]} for f in factors],
        "cooldown_hours": wait_h,
        "boundary": bool(boundary),
    }


def release_time(now, wait_h):
    """Earliest sensible time to reconsider. Long waits land at 10:00, never at 3am."""
    if wait_h <= 0:
        return now
    if wait_h < 1:
        return now + dt.timedelta(hours=wait_h)
    target = now + dt.timedelta(hours=wait_h)
    ten = target.replace(hour=10, minute=0, second=0, microsecond=0)
    if ten < target:
        ten += dt.timedelta(days=1)
    return ten


def vault_path(d):
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "vault.jsonl")


def read_vault(d):
    p = vault_path(d)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write_vault(d, rows):
    with open(vault_path(d), "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")


def print_score(res):
    print(f"REGRET SCORE: {res['score']}/100  [{res['band'].upper()}]  {res['verdict']}")
    for f in res["factors"]:
        pts = f["points"] if isinstance(f["points"], str) else f"+{f['points']}"
        print(f"  {f['stage']:<32} {pts:>6}   {f['why']}")
    if not res["factors"]:
        print("  No risk factors found.")


def args_common(p):
    p.add_argument("--to", default="other", help="ex, situationship, crush, boss, coworker, family, group, friend, other")
    p.add_argument("--text", help="the draft message (or pipe it on stdin)")
    p.add_argument("--hour", type=int, help="hour of day 0-23 (default: now)")
    p.add_argument("--days-since", type=int, help="days since the breakup or last real conversation")
    p.add_argument("--unanswered", type=int, default=0, help="your messages they have not answered yet")
    p.add_argument("--state", default="", help="comma list: drinking, angry, sad, lonely, tired, fine")
    p.add_argument("--json", action="store_true")


def get_text(a):
    if a.text:
        return a.text
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()
    sys.exit("Give the draft with --text or on stdin.")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Don't Text Them: regret scorer and cooling-off vault")
    ap.add_argument("--dir", default=".dont-text-them", help="where the vault lives")
    sub = ap.add_subparsers(dest="cmd", required=True)
    args_common(sub.add_parser("score", help="score a draft"))
    args_common(sub.add_parser("hold", help="score a draft and lock it in the vault"))
    v = sub.add_parser("vault", help="list held texts")
    v.add_argument("--due", action="store_true", help="only texts whose cooling-off is over")
    r = sub.add_parser("release", help="close out a held text")
    r.add_argument("id")
    r.add_argument("--outcome", required=True, choices=["deleted", "sent", "rewrote"])
    sub.add_parser("stats", help="how many texts you did not send")
    a = ap.parse_args(argv)

    if a.cmd in ("score", "hold"):
        text = get_text(a)
        states = [s for s in a.state.split(",") if s.strip()]
        res = score(text, a.to, a.hour, a.days_since, a.unanswered, states)
        now = dt.datetime.now().replace(second=0, microsecond=0)
        if a.hour is not None:
            now = now.replace(hour=a.hour, minute=0)
        rel = release_time(now, res["cooldown_hours"])
        res["reconsider_at"] = rel.isoformat(timespec="minutes")
        if a.cmd == "hold":
            row = {"id": uuid.uuid4().hex[:6], "held_at": now.isoformat(timespec="minutes"),
                   "to": a.to, "text": text, "score": res["score"], "band": res["band"],
                   "reconsider_at": res["reconsider_at"], "outcome": None}
            rows = read_vault(a.dir)
            rows.append(row)
            write_vault(a.dir, rows)
            res["vault_id"] = row["id"]
        if a.json:
            print(json.dumps(res, indent=2, ensure_ascii=False))
        else:
            print_score(res)
            if res["cooldown_hours"]:
                print(f"COOLING-OFF TIMER: reconsider at {res['reconsider_at']}")
            if a.cmd == "hold":
                print(f"LOCKED IN THE VAULT as #{res['vault_id']}. Run `vault --due` in the morning.")
        return 0

    rows = read_vault(a.dir)
    if a.cmd == "vault":
        now = dt.datetime.now().isoformat(timespec="minutes")
        shown = [r for r in rows if r["outcome"] is None and (not a.due or r["reconsider_at"] <= now)]
        if not shown:
            print("Vault is empty." if not a.due else "Nothing is due yet. Go to sleep.")
        for r in shown:
            print(f"#{r['id']}  to {r['to']}  score {r['score']}  held {r['held_at']}  reconsider {r['reconsider_at']}")
            print(f"    \"{r['text']}\"")
        return 0
    if a.cmd == "release":
        for r in rows:
            if r["id"] == a.id:
                r["outcome"] = a.outcome
                r["closed_at"] = dt.datetime.now().isoformat(timespec="minutes")
                write_vault(a.dir, rows)
                print(f"#{a.id} closed: {a.outcome}")
                return 0
        sys.exit(f"No held text with id {a.id}")
    if a.cmd == "stats":
        deleted = sum(1 for r in rows if r["outcome"] == "deleted")
        rewrote = sum(1 for r in rows if r["outcome"] == "rewrote")
        sent = sum(1 for r in rows if r["outcome"] == "sent")
        open_ = sum(1 for r in rows if r["outcome"] is None)
        print(f"TEXTS SAVED: {deleted} deleted, {rewrote} rewritten calmly, {sent} sent anyway, {open_} still in the vault")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
