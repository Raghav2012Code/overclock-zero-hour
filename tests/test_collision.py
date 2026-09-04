"""Collisions: forgiveness insets and hazard-specific lethality."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest  # noqa: E402

import pygame  # noqa: E402

import config  # noqa: E402
from core.collision import collides, forgiving_rect  # noqa: E402
from entities.hazards import Beam, Drone, Spike  # noqa: E402


class TestForgivingRect(unittest.TestCase):
    def test_shrinks_rect(self):
        r = pygame.Rect(0, 0, 40, 60)
        small = forgiving_rect(r)
        self.assertLess(small.width, r.width)
        self.assertLess(small.height, r.height)
        self.assertTrue(r.contains(small))

    def test_graze_does_not_collide(self):
        # 2px corner graze is forgiven by the insets.
        a = pygame.Rect(0, 0, 40, 60)
        b = pygame.Rect(38, 58, 40, 60)
        self.assertTrue(a.colliderect(b))
        self.assertFalse(collides(a, b))

    def test_solid_overlap_collides(self):
        a = pygame.Rect(0, 0, 40, 60)
        b = pygame.Rect(20, 20, 40, 60)
        self.assertTrue(collides(a, b))


class TestHazards(unittest.TestCase):
    def test_spike_sits_on_track(self):
        s = Spike(500, 2)
        self.assertEqual(s.rect.bottom, config.GROUND_Y)
        self.assertEqual(s.count, 2)

    def test_beam_clears_slide_but_kills_stand(self):
        from entities.player import Player

        p = Player()
        standing = p.rect
        beam = Beam(standing.x + 2)
        self.assertTrue(collides(standing, beam.rect))
        p.sliding = True
        self.assertFalse(collides(p.rect, beam.rect))

    def test_drone_oscillates(self):
        d = Drone(600, mode="sine")
        y0 = d.y
        d.update(0.25, 400.0, 0.0)
        d.update(0.25, 400.0, 0.25)
        self.assertNotAlmostEqual(d.y, y0, places=3)

    def test_hazards_scroll_with_world(self):
        s = Spike(500, 1)
        x0 = s.x
        s.update(0.5, 400.0, 0.0)
        self.assertAlmostEqual(s.x, x0 - 200.0)

    def test_offscreen_eventually(self):
        s = Spike(100, 1)
        for _ in range(120):
            s.update(1.0 / 60.0, 800.0, 0.0)
        self.assertTrue(s.offscreen)


if __name__ == "__main__":
    unittest.main()
