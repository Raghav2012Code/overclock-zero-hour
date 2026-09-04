"""Spawner: difficulty curve, gap bounds, pattern variety, reset."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest  # noqa: E402
from types import SimpleNamespace  # noqa: E402

import config  # noqa: E402
from core.spawner import Spawner  # noqa: E402


def make_world():
    return SimpleNamespace(hazards=[], cells=[])


class TestSpawner(unittest.TestCase):
    def test_difficulty_ramps_zero_to_one(self):
        self.assertEqual(Spawner.difficulty(0.0), 0.0)
        self.assertEqual(Spawner.difficulty(200.0), 1.0)
        mid = Spawner.difficulty(45.0)
        self.assertGreater(mid, 0.0)
        self.assertLess(mid, 1.0)

    def test_gaps_stay_beatable(self):
        sp = Spawner(seed=7)
        for elapsed in (0.0, 30.0, 90.0, 200.0):
            for _ in range(50):
                gap = sp._roll_gap(Spawner.difficulty(elapsed), config.MAX_SPEED)
                self.assertGreaterEqual(gap, config.MIN_GAP_FLOOR)

    def test_emits_all_hazard_kinds_over_time(self):
        sp = Spawner(seed=42)
        kinds = set()
        for elapsed in range(0, 150):
            world = make_world()
            sp.distance_since_spawn = sp.next_gap
            sp.update(1.0 / 60.0, 600.0, float(elapsed), world)
            kinds.update(h.kind for h in world.hazards)
        self.assertGreaterEqual(kinds, {"spike", "beam", "drone"})

    def test_hazards_spawn_offscreen_right(self):
        sp = Spawner(seed=3)
        world = make_world()
        sp.distance_since_spawn = sp.next_gap
        sp.update(1.0 / 60.0, 400.0, 10.0, world)
        for h in world.hazards:
            self.assertGreater(h.rect.x, config.WIDTH - 200)

    def test_reset_gives_breathing_room(self):
        sp = Spawner(seed=1)
        sp.reset(seed=99)
        self.assertEqual(sp.spawn_count, 0)
        self.assertGreaterEqual(sp.next_gap, 800.0)


if __name__ == "__main__":
    unittest.main()
