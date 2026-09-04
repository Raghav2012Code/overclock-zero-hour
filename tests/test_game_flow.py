"""Game flow: states, input events, scoring, persistence, rendering."""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import tempfile  # noqa: E402
import unittest  # noqa: E402

import pygame  # noqa: E402

import config  # noqa: E402
import core.game as game_module  # noqa: E402
from core.state import GameState  # noqa: E402
from entities.hazards import Beam, Spike  # noqa: E402
from entities.pickups import EnergyCell  # noqa: E402
from tests.support import make_game  # noqa: E402

DT = 1.0 / 60.0


def key_event(kind: int, key: int) -> pygame.event.Event:
    return pygame.event.Event(kind, {"key": key})


class TestGameFlow(unittest.TestCase):
    def test_space_starts_run_from_menu(self):
        g = make_game()
        self.assertEqual(g.state, GameState.START)
        g.handle_event(key_event(pygame.KEYDOWN, pygame.K_SPACE))
        self.assertEqual(g.state, GameState.PLAYING)

    def test_jump_keydown_has_no_repeat_crash(self):
        # Regression: KEYDOWN carries no `repeat` attr; handler must not raise.
        g = make_game()
        g.start_run()
        g.handle_event(key_event(pygame.KEYDOWN, pygame.K_SPACE))
        g.handle_event(key_event(pygame.KEYUP, pygame.K_SPACE))

    def test_pause_toggles(self):
        g = make_game()
        g.start_run()
        g.handle_event(key_event(pygame.KEYDOWN, pygame.K_p))
        self.assertTrue(g.paused)
        g.handle_event(key_event(pygame.KEYDOWN, pygame.K_p))
        self.assertFalse(g.paused)

    def test_escape_quits(self):
        g = make_game()
        self.assertFalse(g.handle_event(key_event(pygame.KEYDOWN, pygame.K_ESCAPE)))
        self.assertFalse(g.handle_event(pygame.event.Event(pygame.QUIT)))

    def test_pickup_scores_bonus(self):
        g = make_game()
        g.start_run()
        g.cells = [EnergyCell(g.player.rect.centerx, g.player.rect.centery)]
        g.update(DT)
        self.assertEqual(g.cell_count, 1)
        self.assertGreaterEqual(g.score, config.CELL_BONUS)

    def test_spike_kills_and_restart_resets(self):
        g = make_game()
        g.start_run()
        g.hazards = [Spike(g.player.rect.x + 2, 1)]
        g.update(DT)
        self.assertEqual(g.state, GameState.GAME_OVER)
        g.start_run()
        self.assertEqual(g.state, GameState.PLAYING)
        self.assertEqual(g.score, 0.0)
        self.assertEqual(g.cell_count, 0)
        self.assertEqual(g.hazards, [])
        self.assertFalse(g.player.dead)

    def test_beam_kills_standing_but_not_sliding(self):
        g = make_game()
        g.start_run()
        g.hazards = [Beam(g.player.rect.x + 2)]
        g.slide_held = False
        g.update(DT)
        self.assertEqual(g.state, GameState.GAME_OVER)

        g.start_run()
        g.hazards = [Beam(g.player.rect.x + 2)]
        g.slide_held = True
        g.update(DT)
        self.assertEqual(g.state, GameState.PLAYING)

    def test_game_over_key_reboots(self):
        g = make_game()
        g.start_run()
        g.game_over()
        g.handle_event(key_event(pygame.KEYDOWN, pygame.K_r))
        self.assertEqual(g.state, GameState.PLAYING)

    def test_hiscore_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "hiscore.txt")
            old = game_module.HI_SCORE_FILE
            game_module.HI_SCORE_FILE = target
            try:
                self.assertEqual(game_module.load_hi_score(), 0)
                game_module.save_hi_score(1234)
                self.assertEqual(game_module.load_hi_score(), 1234)
                with open(target, "w", encoding="utf-8") as fh:
                    fh.write("not-a-number")
                self.assertEqual(game_module.load_hi_score(), 0)
            finally:
                game_module.HI_SCORE_FILE = old

    def test_render_does_not_mutate_simulation(self):
        g = make_game()
        g.start_run()
        g.hazards = [Spike(500, 2)]
        g.shake = 10.0
        before = (g.hazards[0].x, g.player.x, g.player.y)
        g.render()
        after = (g.hazards[0].x, g.player.x, g.player.y)
        self.assertEqual(before, after)

    def test_all_screens_render(self):
        g = make_game()
        g.update(DT)
        g.render()  # START
        g.start_run()
        g.update(DT)
        g.render()  # PLAYING
        g.game_over()
        g.render()  # GAME_OVER
        g.to_start()
        g.paused = True
        g.state = GameState.PLAYING
        g.render()  # PAUSED

    def test_survival_accumulates_score_and_speed(self):
        g = make_game()
        g.start_run()
        for _ in range(600):
            if g.state != GameState.PLAYING:
                break
            g.update(DT)
        self.assertGreater(g.elapsed, 0.0)
        self.assertGreaterEqual(g.speed, config.BASE_SPEED)


if __name__ == "__main__":
    unittest.main()
