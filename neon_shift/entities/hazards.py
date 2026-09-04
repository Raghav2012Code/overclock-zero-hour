"""Dynamic hazards: ground spikes, overhead beams, patrol drones."""

from __future__ import annotations

import math

import pygame

from neon_shift import config
from neon_shift.graphics import neon


class Hazard:
    kind = "hazard"

    def update(self, dt: float, speed: float, time: float) -> None:
        raise NotImplementedError

    @property
    def rect(self) -> pygame.Rect:
        raise NotImplementedError

    def draw(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

    @property
    def offscreen(self) -> bool:
        return self.rect.right < -80


class Spike(Hazard):
    """Ground spike cluster — JUMP over it."""

    kind = "spike"

    def __init__(self, x: float, count: int = 1) -> None:
        self.x = float(x)
        self.count = max(1, min(2, count))
        self.w = 34.0 * self.count + 8.0 * (self.count - 1)
        self.h = 44.0
        self._pulse = 0.0

    def update(self, dt: float, speed: float, time: float) -> None:
        self.x -= speed * dt
        self._pulse = time

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(config.GROUND_Y - self.h), int(self.w), int(self.h))

    def draw(self, surface: pygame.Surface) -> None:
        base_y = config.GROUND_Y
        glow = 0.6 + 0.4 * math.sin(self._pulse * 6.0)
        for i in range(self.count):
            sx = self.x + i * 42.0
            pts = [(sx, base_y), (sx + 17, base_y - self.h), (sx + 34, base_y)]
            # Halo layer then hot core.
            neon.glow_polygon(surface, pts, config.NEON_MAGENTA, alpha=int(70 + 40 * glow))
            pygame.draw.polygon(surface, (60, 8, 40), pts)
            pygame.draw.polygon(surface, config.NEON_MAGENTA, pts, 2)
            pygame.draw.line(surface, config.WHITE, (sx + 17, base_y - self.h), (sx + 17, base_y - 8), 2)
        # Warning strip on the track.
        neon.h_line(surface, self.x - 6, self.x + self.w + 6, base_y + 4, config.NEON_MAGENTA, 2)


class Beam(Hazard):
    """Overhead beam gate — SLIDE under it (low clearance)."""

    kind = "beam"

    def __init__(self, x: float) -> None:
        self.x = float(x)
        self.w = 40.0
        # Beam hangs from a gantry: lethal band sits above slide height
        # but below standing height, so sliding always clears it.
        self.top = config.GROUND_Y - 96.0
        self.bottom = config.GROUND_Y - 40.0
        self._pulse = 0.0

    def update(self, dt: float, speed: float, time: float) -> None:
        self.x -= speed * dt
        self._pulse = time

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.top), int(self.w), int(self.bottom - self.top))

    def draw(self, surface: pygame.Surface) -> None:
        r = self.rect
        # Gantry posts.
        post_c = (90, 40, 130)
        pygame.draw.rect(surface, post_c, (r.x - 6, self.top - 90, 8, (r.bottom - (self.top - 90)))))
        pygame.draw.rect(surface, post_c, (r.right - 2, self.top - 90, 8, (r.bottom - (self.top - 90)))))
        pygame.draw.rect(surface, (40, 18, 60), (r.x - 6, self.top - 96, r.width + 20, 12))
        flicker = 0.5 + 0.5 * math.sin(self._pulse * 14.0)
        core = (
            int(255),
            int(60 + 50 * flicker),
            int(120 + 60 * flicker),
        )
        neon.glow_rect(surface, r, config.NEON_MAGENTA, alpha=90)
        pygame.draw.rect(surface, (50, 8, 34), r)
        for i in range(3):
            yy = r.y + 8 + i * 14
            pygame.draw.line(surface, core, (r.x + 2, yy), (r.right - 2, yy), 3)
        pygame.draw.rect(surface, config.NEON_MAGENTA, r, 2)
        # "SLIDE" chevron hint on the track.
        cy = config.GROUND_Y - 14
        for k in range(2):
            xx = r.centerx - 14 + k * 14
            pygame.draw.lines(
                surface, config.NEON_CYAN, False,
                [(xx, cy - 8), (xx + 8, cy), (xx, cy + 8)], 2,
            )
            _ = flicker


class Drone(Hazard):
    """Oscillating patrol drone — time your jump or slide.

    ``mode`` controls the hover band:
    - ``sine``: mid-air sine sweep (jump over at low point / slide under at high point)
    - ``low``: fast low hover that must be jumped.
    """

    kind = "drone"

    def __init__(self, x: float, mode: str = "sine") -> None:
        self.x = float(x)
        self.mode = mode
        self.w = 44.0
        self.h = 30.0
        self.t = 0.0
        self.base_y = config.GROUND_Y - 110.0 if mode == "sine" else config.GROUND_Y - 52.0
        self.amplitude = 42.0 if mode == "sine" else 10.0
        self.frequency = 2.6 if mode == "sine" else 5.0
        self.phase = 0.0
        self.y = self.base_y

    def update(self, dt: float, speed: float, time: float) -> None:
        self.t += dt
        self.x -= speed * dt
        self.y = self.base_y + math.sin(self.t * self.frequency + self.phase) * self.amplitude

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), int(self.w), int(self.h))

    def draw(self, surface: pygame.Surface) -> None:
        r = self.rect
        cx, cy = r.centerx, r.centery
        # Rotor blur.
        rotor = int(10 + 6 * math.sin(self.t * 30.0))
        pygame.draw.ellipse(surface, (120, 240, 255),
                            (cx - rotor - 12, r.y - 10, (rotor + 12) * 2, 8), 1)
        # Patrol beam to the track (telegraphs position).
        neon.v_line(surface, cx, r.bottom, config.GROUND_Y, config.NEON_ORANGE, 1, alpha=90)
        # Hull.
        neon.glow_rect(surface, r.inflate(6, 6), config.NEON_ORANGE, alpha=70)
        pygame.draw.rect(surface, (45, 22, 8), r, border_radius=8)
        pygame.draw.rect(surface, config.NEON_ORANGE, r, 2, border_radius=8)
        # Eye: blinks magenta.
        blink = (math.sin(self.t * 5.0) > -0.85)
        eye_c = config.NEON_MAGENTA if blink else (60, 10, 30)
        pygame.draw.circle(surface, eye_c, (cx, cy), 7)
        pygame.draw.circle(surface, config.WHITE, (cx, cy), 3)
        # Side thrusters.
        pygame.draw.circle(surface, config.NEON_CYAN, (r.x - 2, cy), 3)
        pygame.draw.circle(surface, config.NEON_CYAN, (r.right + 2, cy), 3)
