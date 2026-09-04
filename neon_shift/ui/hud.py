"""Cyberpunk telemetry HUD: score, speed, cells, FPS + scanlines."""

from __future__ import annotations

import pygame

from neon_shift import config
from neon_shift.core.state import GameState
from neon_shift.graphics import neon


def _font(size: int, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont("consolas,couriernew,monospace", size, bold=bold)


class HUD:
    def __init__(self) -> None:
        self.f_big = _font(30, bold=True)
        self.f_med = _font(18, bold=True)
        self.f_small = _font(14)
        # Scanline overlay, built once.
        self.scanlines = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        for y in range(0, config.HEIGHT, 4):
            pygame.draw.line(self.scanlines, (0, 0, 0, 36), (0, y), (config.WIDTH, y), 1)
        # Vignette corners.
        vig = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(vig, (0, 0, 0, 0), vig.get_rect())
        self.vignette = vig

    def _panel(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        ghost = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        ghost.fill((8, 10, 26, 150))
        surface.blit(ghost, rect.topleft)
        pygame.draw.rect(surface, (0, 255, 255), rect, 1)
        pygame.draw.line(surface, config.NEON_MAGENTA, rect.topleft,
                         (rect.x + 26, rect.y), 3)

    def draw(self, surface: pygame.Surface, *, score: int, hi_score: int,
             speed: float, cells: int, fps: float, state: GameState,
             paused: bool, time: float) -> None:
        # Top-left telemetry panel.
        panel = pygame.Rect(10, 10, 250, 84)
        self._panel(surface, panel)
        neon.text_glow(surface, self.f_small, "// OVERCLOCK TELEMETRY", (20, 14), config.NEON_CYAN)
        neon.text_glow(surface, self.f_big, f"{score:06d}", (20, 30), config.WHITE,
                       glow_color=config.NEON_CYAN)
        hi_c = config.NEON_YELLOW if score >= hi_score and score > 0 else config.DIM
        self.f_small_render(surface, f"HI {hi_score:06d}", (20, 62), hi_c)
        self.f_small_render(surface, f"CELLS {cells:02d}", (150, 62), config.NEON_YELLOW)

        # Top-right speed gauge.
        gauge = pygame.Rect(config.WIDTH - 200, 10, 190, 84)
        self._panel(surface, gauge)
        neon.text_glow(surface, self.f_small, "VELOCITY", (config.WIDTH - 190, 14), config.NEON_MAGENTA)
        neon.text_glow(surface, self.f_med, f"{speed:4.0f} px/s", (config.WIDTH - 190, 32),
                       config.WHITE, glow_color=config.NEON_MAGENTA)
        # Speed bar.
        frac = (speed - config.BASE_SPEED) / max(1.0, config.MAX_SPEED - config.BASE_SPEED)
        bx, by, bw = config.WIDTH - 190, 58, 170
        pygame.draw.rect(surface, (30, 30, 60), (bx, by, bw, 10))
        pygame.draw.rect(surface, config.NEON_MAGENTA, (bx, by, int(bw * max(0.0, min(1.0, frac)))), 10)
        pygame.draw.rect(surface, config.WHITE, (bx, by, bw, 10), 1)
        self.f_small_render(surface, f"{fps:4.0f} FPS", (bx, 72), config.DIM)

        # Bottom control hints during play.
        if state == GameState.PLAYING and not paused:
            hint = "SPACE/W/UP jump  |  S/DOWN slide  |  P pause"
            img = self.f_small.render(hint, True, config.DIM)
            surface.blit(img, (config.WIDTH // 2 - img.get_width() // 2, config.HEIGHT - 24))

        # CRT overlays always on top (but below full-screen menus).
        surface.blit(self.scanlines, (0, 0))

    def f_small_render(self, surface, text, pos, color) -> None:
        img = self.f_small.render(text, True, color)
        surface.blit(img, pos)
