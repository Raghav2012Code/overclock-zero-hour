"""Pooled particle system: sparks, trails, bursts, landing dust."""

from __future__ import annotations

import math
import random

import pygame

import config


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "size", "color", "gravity", "drag")

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        size: float,
        color: tuple[int, int, int],
        gravity: float = 0.0,
        drag: float = 0.0,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.size = size
        self.color = color
        self.gravity = gravity
        self.drag = drag

    @property
    def alive(self) -> bool:
        return self.life > 0.0

    def update(self, dt: float) -> None:
        self.life -= dt
        if self.life <= 0.0:
            return
        if self.drag:
            damp = max(0.0, 1.0 - self.drag * dt)
            self.vx *= damp
            self.vy *= damp
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt


class ParticleSystem:
    """Single pooled emitter bank for all world effects."""

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.particles: list[Particle] = []

    def clear(self) -> None:
        self.particles.clear()

    # -- internal ---------------------------------------------------------
    def _push(self, p: Particle) -> None:
        if len(self.particles) >= config.PARTICLE_CAP:
            # Drop the oldest dead-ish particle to bound memory.
            self.particles.pop(0)
        self.particles.append(p)

    # -- public emitters ----------------------------------------------------
    def burst(
        self,
        x: float,
        y: float,
        color: tuple[int, int, int],
        count: int = 22,
        speed: float = 260.0,
        life: float = 0.6,
        size: float = 4.0,
        gravity: float = 500.0,
    ) -> None:
        for _ in range(count):
            ang = self.rng.uniform(0.0, math.tau)
            spd = self.rng.uniform(0.3, 1.0) * speed
            self._push(
                Particle(
                    x, y,
                    math.cos(ang) * spd, math.sin(ang) * spd,
                    self.rng.uniform(0.5, 1.0) * life,
                    self.rng.uniform(0.6, 1.3) * size,
                    color, gravity=gravity, drag=1.2,
                )
            )

    def trail(self, x: float, y: float, color: tuple[int, int, int], count: int = 1) -> None:
        for _ in range(count):
            self._push(
                Particle(
                    x + self.rng.uniform(-4, 4), y + self.rng.uniform(-6, 6),
                    self.rng.uniform(-90, -20), self.rng.uniform(-40, 40),
                    self.rng.uniform(0.2, 0.45), self.rng.uniform(2.0, 4.5),
                    color, drag=2.0,
                )
            )

    def land_dust(self, x: float, y: float, count: int = 10) -> None:
        for _ in range(count):
            self._push(
                Particle(
                    x + self.rng.uniform(-14, 14), y - 2.0,
                    self.rng.uniform(-160, 160), self.rng.uniform(-160, -20),
                    self.rng.uniform(0.25, 0.55), self.rng.uniform(2.0, 4.0),
                    config.NEON_CYAN, gravity=700.0, drag=1.5,
                )
            )

    def pickup_sparkle(self, x: float, y: float) -> None:
        self.burst(x, y, config.NEON_YELLOW, count=18, speed=220.0, life=0.5, size=3.5, gravity=120.0)

    def crash(self, x: float, y: float) -> None:
        self.burst(x, y, config.NEON_MAGENTA, count=46, speed=420.0, life=0.9, size=5.0)
        self.burst(x, y, config.WHITE, count=20, speed=300.0, life=0.6, size=3.5)

    # -- sim / draw ----------------------------------------------------------
    def update(self, dt: float) -> None:
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.alive]

    def draw(self, surface: pygame.Surface, offset: pygame.Vector2 | tuple[float, float]) -> None:
        ox, oy = float(offset[0]), float(offset[1])
        for p in self.particles:
            t = max(0.0, p.life / p.max_life)
            radius = max(1, int(p.size * t + 0.5))
            # Additive-style glow: outer faint halo + hot core.
            halo = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            c = p.color
            pygame.draw.circle(halo, (*c, int(70 * t)), (radius * 2, radius * 2), radius * 2)
            pygame.draw.circle(halo, (*c, int(200 * t)), (radius * 2, radius * 2), radius)
            surface.blit(halo, (p.x + ox - radius * 2, p.y + oy - radius * 2))
