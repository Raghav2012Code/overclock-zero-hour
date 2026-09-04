"""Multi-layer parallax retro-cyberpunk cityscape.

Layers (back -> front):
1. Vertical gradient sky + synthwave sun + twinkling stars
2. Far building silhouettes (0.15x scroll)
3. Near buildings with lit windows (0.35x scroll)
4. Antenna masts + scrolling marquee glow strip
5. Perspective grid floor rushing toward the viewer (1.0x scroll)

All art is procedural: pygame.draw + pre-rendered looping strips.
"""

from __future__ import annotations

import math
import random

import pygame

from neon_shift import config
from neon_shift.graphics import neon


class _BuildingStrip:
    """Pre-rendered, horizontally tileable building silhouette."""

    def __init__(self, width: int, height: int, base_y: int, seed: int,
                 color: tuple[int, int, int], window_color: tuple[int, int, int],
                 window_density: float, max_h: int) -> None:
        self.width = width
        self.rng = random.Random(seed)
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        x = 0
        while x < width:
            bw = self.rng.randint(50, 110)
            bh = self.rng.randint(max_h // 3, max_h)
            top = base_y - bh
            pygame.draw.rect(self.surface, color, (x, top, bw, bh))
            pygame.draw.rect(self.surface, window_color, (x, top, bw, 2))
            # Windows.
            for wy in range(top + 8, base_y - 6, 12):
                for wx in range(x + 5, x + bw - 5, 10):
                    if self.rng.random() < window_density:
                        pygame.draw.rect(self.surface, window_color, (wx, wy, 4, 6))
            # Antenna on some roofs.
            if self.rng.random() < 0.3:
                ax = x + bw // 2
                pygame.draw.line(self.surface, window_color, (ax, top), (ax, top - 14), 1)
                pygame.draw.circle(self.surface, (255, 60, 90), (ax, top - 15), 2)
            x += bw + self.rng.randint(6, 26)

    def draw(self, target: pygame.Surface, y: int, offset: float) -> None:
        x = -(offset % self.width)
        while x < target.get_width():
            target.blit(self.surface, (x, y - self.surface.get_height()))
            x += self.width


class ParallaxBackground:
    def __init__(self) -> None:
        self.scroll = 0.0
        self.time = 0.0
        rng = random.Random(1337)
        self.stars = [
            (rng.uniform(0, config.WIDTH), rng.uniform(0, 220), rng.uniform(0.5, 2.0), rng.uniform(0, 6.28))
            for _ in range(110)
        ]
        self.far = _BuildingStrip(640, 220, 220, seed=7,
                                  color=(22, 14, 44), window_color=(120, 60, 160),
                                  window_density=0.25, max_h=190)
        self.near = _BuildingStrip(760, 260, 260, seed=21,
                                   color=(32, 16, 58), window_color=(0, 220, 230),
                                   window_density=0.34, max_h=230)
        # Pre-render sky gradient.
        self.sky = pygame.Surface((config.WIDTH, config.GRID_HORIZON + 40))
        for y in range(self.sky.get_height()):
            t = y / max(1, self.sky.get_height() - 1)
            r = int(config.BG_TOP[0] + (config.BG_BOTTOM[0] - config.BG_TOP[0]) * t)
            g = int(config.BG_TOP[1] + (config.BG_BOTTOM[1] - config.BG_TOP[1]) * t)
            b = int(config.BG_TOP[2] + (config.BG_BOTTOM[2] - config.BG_TOP[2]) * t)
            pygame.draw.line(self.sky, (r, g, b), (0, y), (config.WIDTH, y))
        self.grid_offset = 0.0

    def update(self, dt: float, speed: float) -> None:
        self.time += dt
        self.scroll += speed * dt
        self.grid_offset = (self.grid_offset + speed * dt) % 48.0

    # -- pieces ---------------------------------------------------------------
    def _draw_sun(self, target: pygame.Surface) -> None:
        cx, cy, radius = config.WIDTH // 2, 250, 84
        # Halo.
        halo = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
        pygame.draw.circle(halo, (*config.NEON_MAGENTA, 40), (radius * 3 // 2, radius * 3 // 2), radius * 3 // 2)
        target.blit(halo, (cx - radius * 3 // 2, cy - radius * 3 // 2))
        # Striped synthwave disc (clip by drawing slats over it).
        pygame.draw.circle(target, (255, 80, 160), (cx, cy), radius)
        pygame.draw.circle(target, (255, 190, 60), (cx, cy), int(radius * 0.72))
        for i, sy in enumerate(range(cy + 6, cy + radius, 9)):
            w = int(radius * (0.35 + 0.65 * (sy - cy) / radius))
            pygame.draw.rect(target, config.BG_BOTTOM, (cx - w, sy, w * 2, 3 + i // 2))

    def _draw_stars(self, target: pygame.Surface) -> None:
        for x, y, s, ph in self.stars:
            tw = 0.4 + 0.6 * abs(math.sin(self.time * 1.7 + ph))
            v = int(140 + 110 * tw)
            pygame.draw.circle(target, (v, v, 255), (int(x), int(y)), max(1, int(s)))

    def _draw_grid_floor(self, target: pygame.Surface) -> None:
        horizon = config.GRID_HORIZON
        # Floor fill.
        pygame.draw.rect(target, config.TRACK, (0, horizon, config.WIDTH, config.HEIGHT - horizon))
        # Horizon glow.
        neon.h_line(target, 0, config.WIDTH, horizon, config.NEON_MAGENTA, 3)
        neon.h_line(target, 0, config.WIDTH, horizon + 3, config.NEON_CYAN, 1, alpha=120)
        # Vertical perspective rays rushing outward.
        for i in range(-12, 13):
            spread = i * 78 + (self.scroll * 0.02 % 78)
            pygame.draw.line(target, (60, 30, 110), (config.WIDTH / 2 + i * 30, horizon),
                             (config.WIDTH / 2 + spread, config.HEIGHT), 1)
        # Horizontal scan rows accelerating toward viewer.
        for k in range(8):
            t = ((k * 60.0 + self.grid_offset * 1.6) % 480.0) / 480.0
            y = horizon + t * t * (config.HEIGHT - horizon)
            alpha = int(40 + 150 * t)
            neon.h_line(target, 0, config.WIDTH, y, config.NEON_CYAN, 1, alpha=alpha)

    def _draw_track(self, target: pygame.Surface) -> None:
        gy = config.GROUND_Y
        pygame.draw.rect(target, (12, 14, 30), (0, gy, config.WIDTH, config.HEIGHT - gy))
        # Moving dashes sell the speed.
        dash_w, gap = 46, 30
        off = self.scroll % (dash_w + gap)
        x = -off
        while x < config.WIDTH:
            neon.h_line(target, x, x + dash_w, gy + 22, config.NEON_CYAN, 2, alpha=150)
            x += dash_w + gap
        # Side rail glow.
        neon.h_line(target, 0, config.WIDTH, gy + 1, config.NEON_CYAN, 2, alpha=200)

    # -- main -------------------------------------------------------------------
    def draw(self, target: pygame.Surface) -> None:
        target.blit(self.sky, (0, 0))
        self._draw_stars(target)
        self._draw_sun(target)
        self.far.draw(target, 300, self.scroll * 0.15)
        self.near.draw(target, 308, self.scroll * 0.35)
        self._draw_grid_floor(target)
        self._draw_track(target)
