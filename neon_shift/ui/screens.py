"""Full-screen states: start, game over, pause."""

from __future__ import annotations

import math

import pygame

from neon_shift import config
from neon_shift.graphics import neon


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("consolas,couriernew,monospace", size, bold=bold)


class Screens:
    def __init__(self) -> None:
        self.f_title = _font(64, bold=True)
        self.f_sub = _font(22, bold=True)
        self.f_body = _font(17)
        self.f_small = _font(14)

    # -- helpers ---------------------------------------------------------------
    @staticmethod
    def _dim(surface: pygame.Surface, alpha: int = 150) -> None:
        veil = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        veil.fill((4, 4, 14, alpha))
        surface.blit(veil, (0, 0))

    def _blink(self, time: float, speed: float = 3.0) -> bool:
        return math.sin(time * speed) > -0.2

    # -- screens -----------------------------------------------------------------
    def draw_start(self, surface: pygame.Surface, time: float, hi_score: int) -> None:
        self._dim(surface, 120)
        cx = config.WIDTH // 2
        bob = math.sin(time * 2.0) * 6.0
        neon.text_glow(surface, self.f_title, "OVERCLOCK", (cx, 120 + bob),
                       config.NEON_CYAN, glow_color=config.NEON_CYAN, center=True)
        neon.text_glow(surface, self.f_title, "ZERO HOUR", (cx, 182 + bob),
                       config.NEON_MAGENTA, glow_color=config.NEON_MAGENTA, center=True)
        neon.text_glow(surface, self.f_sub, "// RETRO-CYBERPUNK ENDLESS RUNNER //",
                       (cx, 240), config.NEON_YELLOW, center=True)

        lines = [
            ("SPACE / UP / W", "JUMP  (release early = short hop)"),
            ("DOWN / S", "SLIDE  (dive-fast in mid-air)"),
            ("SPIKES", "jump them  |  BEAMS : slide  |  DRONES : time it"),
            ("CELLS", "+25 bonus score each"),
        ]
        y = 278
        for key, desc in lines:
            k = self.f_body.render(key, True, config.NEON_CYAN)
            d = self.f_body.render(f"  {desc}", True, config.WHITE)
            x0 = cx - (k.get_width() + d.get_width()) // 2
            surface.blit(k, (x0, y))
            surface.blit(d, (x0 + k.get_width(), y))
            y += 26

        if hi_score > 0:
            neon.text_glow(surface, self.f_body, f"BEST RUN  {hi_score:06d}",
                           (cx, y + 8), config.NEON_YELLOW, center=True)

        if self._blink(time):
            neon.text_glow(surface, self.f_sub, "PRESS SPACE TO JACK IN",
                           (cx, 452), config.WHITE, glow_color=config.NEON_CYAN, center=True)

    def draw_game_over(self, surface: pygame.Surface, time: float, score: int,
                       hi_score: int, cells: int, new_best: bool) -> None:
        self._dim(surface, 165)
        cx = config.WIDTH // 2
        glitch = int(math.sin(time * 30.0) * 3)
        neon.text_glow(surface, self.f_title, "FLATLINE", (cx + glitch, 130),
                       config.NEON_MAGENTA, glow_color=(255, 0, 80), center=True)
        neon.text_glow(surface, self.f_sub, "// SIGNAL LOST //", (cx, 190),
                       config.NEON_CYAN, center=True)
        if new_best:
            neon.text_glow(surface, self.f_sub, "** NEW BEST RUN **", (cx, 228),
                           config.NEON_YELLOW, center=True)

        stats = self.f_body.render(f"SCORE {score:06d}   BEST {hi_score:06d}   CELLS {cells:02d}",
                                   True, config.WHITE)
        surface.blit(stats, (cx - stats.get_width() // 2, 262))
        tip = self.f_small.render("coyote-time + jump-buffer are on: you can jump a hair late or early",
                                  True, config.DIM)
        surface.blit(tip, (cx - tip.get_width() // 2, 292))

        if self._blink(time, 2.4):
            neon.text_glow(surface, self.f_sub, "SPACE / R : REBOOT      M : MENU",
                           (cx, 350), config.WHITE, glow_color=config.NEON_CYAN, center=True)

    def draw_paused(self, surface: pygame.Surface) -> None:
        self._dim(surface, 150)
        neon.text_glow(surface, self.f_sub, "PAUSED  —  P TO RESUME",
                       (config.WIDTH // 2, config.HEIGHT // 2),
                       config.NEON_CYAN, center=True)
