"""Collectible energy cells: bonus score + particle bursts."""

from __future__ import annotations

import math

import pygame

import config
from graphics import neon


class EnergyCell:
    RADIUS = 11.0

    def __init__(self, x: float, y: float) -> None:
        self.x = float(x)
        self.y0 = float(y)
        self.y = float(y)
        self.t = 0.0
        self.taken = False
        # Deterministic phase from spawn x so lines shimmer out of sync.
        self.phase = (x * 0.05) % math.tau

    def update(self, dt: float, speed: float, time: float) -> None:
        self.t += dt
        self.x -= speed * dt
        self.y = self.y0 + math.sin(time * 4.0 + self.phase) * 6.0

    @property
    def rect(self) -> pygame.Rect:
        r = int(self.RADIUS * 1.6)
        return pygame.Rect(int(self.x - r), int(self.y - r), r * 2, r * 2)

    @property
    def offscreen(self) -> bool:
        return self.x < -40

    def draw(self, surface: pygame.Surface, ox: float = 0.0, oy: float = 0.0) -> None:
        x, y = self.x + ox, self.y + oy
        pulse = 0.6 + 0.4 * math.sin(self.t * 6.0 + self.phase)
        # Halo.
        halo_r = int(self.RADIUS + 8 + 4 * pulse)
        halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo, (*config.NEON_YELLOW, 60), (halo_r, halo_r), halo_r)
        pygame.draw.circle(halo, (*config.NEON_YELLOW, 110), (halo_r, halo_r), int(self.RADIUS + 3))
        surface.blit(halo, (x - halo_r, y - halo_r))
        # Rotating diamond core.
        w = self.RADIUS * (0.55 + 0.45 * abs(math.sin(self.t * 3.0 + self.phase)))
        pts = [
            (x, y - self.RADIUS),
            (x + w, y),
            (x, y + self.RADIUS),
            (x - w, y),
        ]
        pygame.draw.polygon(surface, (80, 60, 8), pts)
        pygame.draw.polygon(surface, config.NEON_YELLOW, pts, 2)
        pygame.draw.circle(surface, config.WHITE, (int(x), int(y)), 3)
        neon.v_line(surface, x, y - self.RADIUS - 4, y - self.RADIUS - 10,
                    config.NEON_YELLOW, 1, alpha=120)
