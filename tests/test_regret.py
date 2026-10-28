import datetime as dt
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import regret  # noqa: E402


class RegretTests(unittest.TestCase):
    def test_harmless_text_is_green(self):
        r = regret.score("Running 10 min late, save me a seat", to="friend", hour=13)
        self.assertEqual(r["band"], "green")
        self.assertEqual(r["score"], 0)

    def test_2am_ex_text_is_red(self):
        r = regret.score("u up? i miss you", to="ex", hour=2, days_since=9,
                         unanswered=1, states=["drinking"])
        self.assertEqual(r["band"], "red")
        self.assertGreaterEqual(r["score"], 75)

    def test_friend_at_2am_with_harmless_text_is_green(self):
        r = regret.score("landed safe, thanks for the ride", to="friend", hour=2)
        self.assertEqual(r["band"], "green")

    def test_boundary_phrase_forces_red(self):
        r = regret.score("i know you said you needed space but hi", to="ex", hour=15, days_since=200)
        self.assertTrue(r["boundary"])
        self.assertGreaterEqual(r["score"], 95)

    def test_boss_at_noon_is_not_penalised(self):
        r = regret.score("Can we talk about the deadline?", to="boss", hour=12)
        self.assertLess(r["score"], 25)

    def test_late_rage_text_to_boss_is_not_green(self):
        r = regret.score("Honestly I don't know why I bother. I've done everything you asked "
                         "and it's never enough. Maybe find someone else who can read your mind.",
                         to="boss", hour=23)
        self.assertIn(r["band"], ("orange", "red"))
        self.assertIn("Bridge Burner", [f["stage"] for f in r["factors"]])

    def test_score_capped_at_100(self):
        r = regret.score("WHY DIDN'T YOU ANSWER??? I MISS YOU!!! " * 40, to="ex", hour=3,
                         days_since=2, unanswered=5, states=["drinking", "angry", "sad"])
        self.assertEqual(r["score"], 100)

    def test_long_waits_land_at_ten_am(self):
        now = dt.datetime(2026, 10, 27, 2, 0)
        self.assertEqual(regret.release_time(now, 8), dt.datetime(2026, 10, 27, 10, 0))
        self.assertEqual(regret.release_time(now, 20), dt.datetime(2026, 10, 28, 10, 0))

    def test_hold_and_release(self):
        with tempfile.TemporaryDirectory() as d:
            regret.main(["--dir", d, "hold", "--to", "ex", "--text", "miss you", "--hour", "2"])
            rows = regret.read_vault(d)
            self.assertEqual(len(rows), 1)
            regret.main(["--dir", d, "release", rows[0]["id"], "--outcome", "deleted"])
            self.assertEqual(regret.read_vault(d)[0]["outcome"], "deleted")


if __name__ == "__main__":
    unittest.main()
