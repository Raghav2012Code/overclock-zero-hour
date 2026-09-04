"""Player physics: jump, variable jump cut, coyote time, buffering, slide."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest  # noqa: E402

import config  # noqa: E402
from entities.particles import ParticleSystem  # noqa: E402
from entities.player import Player  # noqa: E402

DT = 1.0 / 60.0


class TestJump(unittest.TestCase):
    def test_jump_launches_upward(self):
        p = Player()
        p.press_jump()
        p.update(DT, ParticleSystem())
        self.assertFalse(p.grounded)
        self.assertLess(p.vy, 0.0)

    def test_release_truncates_jump(self):
        p = Player()
        p.press_jump()
        p.update(DT, ParticleSystem())
        before = p.vy
        p.release_jump()
        self.assertGreater(p.vy, before)

    def test_coyote_time_allows_late_jump(self):
        p = Player()
        p.grounded = False
        p.coyote = 0.05
        p.press_jump()
        p.update(DT, ParticleSystem())
        self.assertLess(p.vy, 0.0)

    def test_expired_coyote_denies_jump(self):
        p = Player()
        p.grounded = False
        p.coyote = 0.0
        p.press_jump()
        p.update(DT, ParticleSystem(), slide_held=False)
        # Buffer is still pending but there is no ground/coyote: no launch.
        self.assertGreaterEqual(p.vy, 0.0)

    def test_buffered_jump_fires_on_landing(self):
        p = Player()
        p.grounded = False
        p.y = config.GROUND_Y - config.PLAYER_H - 4.0
        p.vy = 50.0
        p.press_jump()  # pressed mid-air, just before touchdown
        for _ in range(60):
            p.update(DT, ParticleSystem())
            if p.grounded:
                break
        self.assertTrue(p.grounded)

    def test_slide_cuts_hitbox(self):
        p = Player()
        standing = p.height
        p.update(DT, ParticleSystem(), slide_held=True)
        self.assertLess(p.height, standing)
        self.assertEqual(p.height, float(config.PLAYER_SLIDE_H))

    def test_landing_returns_to_track(self):
        p = Player()
        p.press_jump()
        ps = ParticleSystem()
        for _ in range(240):
            p.update(DT, ps)
            if p.grounded and p.vy == 0.0 and p.y == config.GROUND_Y - config.PLAYER_H:
                break
        self.assertTrue(p.grounded)
        self.assertEqual(p.y, config.GROUND_Y - config.PLAYER_H)

    def test_physics_is_frame_rate_independent(self):
        def simulate(dt: float, steps: int) -> float:
            p = Player()
            p.press_jump()
            ps = ParticleSystem()
            for _ in range(steps):
                p.update(dt, ps)
            return p.y

        y_fine = simulate(1.0 / 60.0, 60)
        y_coarse = simulate(1.0 / 30.0, 30)
        self.assertAlmostEqual(y_fine, y_coarse, delta=8.0)


if __name__ == "__main__":
    unittest.main()
