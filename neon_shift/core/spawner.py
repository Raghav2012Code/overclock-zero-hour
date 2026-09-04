"""Difficulty-scaled hazard / pickup spawner.

The spawner works in *distance space*: it tracks how far the world has
scrolled and emits the next pattern once the gap distance elapses. Gaps
shrink with difficulty but are clamped so patterns stay beatable at max
speed. Patterns never overlap vertically in an impossible way — each
pattern owns its airspace.
"""

from __future__ import annotations

import random

from neon_shift import config
from neon_shift.entities.hazards import Beam, Drone, Spike


class Spawner:
    """Emits hazards and energy-cell pickups ahead of the player."""

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        self.distance_since_spawn = 0.0
        self.next_gap = 520.0
        self.spawn_count = 0

    def reset(self, seed: int | None = None) -> None:
        if seed is not None:
            self.rng.seed(seed)
        self.distance_since_spawn = 0.0
        # First obstacle arrives late so the player can settle in.
        self.next_gap = 900.0
        self.spawn_count = 0

    # -- difficulty ------------------------------------------------------
    @staticmethod
    def difficulty(elapsed: float) -> float:
        """0.0 (start) -> 1.0 (fully ramped) over ~90 seconds."""
        return max(0.0, min(1.0, elapsed / 90.0))

    def _roll_gap(self, difficulty: float, speed: float) -> float:
        # Keep *reaction time* roughly constant as speed rises.
        span = config.SPAWN_MAX_GAP - config.SPAWN_MIN_GAP
        base = config.SPAWN_MAX_GAP - span * difficulty
        base = max(base, config.MIN_GAP_FLOOR)
        jitter = self.rng.uniform(-70.0, 110.0)
        # Faster scroll => wider pixel gap for the same time window.
        speed_factor = speed / config.BASE_SPEED
        return max(config.MIN_GAP_FLOOR, (base + jitter) * (0.7 + 0.3 * speed_factor))

    # -- patterns ---------------------------------------------------------
    def _pick_pattern(self, difficulty: float) -> str:
        pool = ["spike1", "cells", "beam", "spike1"]
        if difficulty > 0.15:
            pool += ["drone", "spike_cells"]
        if difficulty > 0.35:
            pool += ["spike2", "beam_cells", "drone_low"]
        if difficulty > 0.6:
            pool += ["spike2", "drone", "beam", "gauntlet"]
        return self.rng.choice(pool)

    def update(self, dt: float, speed: float, elapsed: float, world: object) -> None:
        """Advance distance clock; spawn due patterns into ``world``.

        ``world`` is duck-typed (the :class:`Game`) exposing
        ``hazards``, ``cells`` and ``difficulty``-independent helpers.
        Imported lazily to avoid a hard core->entities import cycle at
        module load; entities never import the spawner back.
        """
        from neon_shift.entities.pickups import EnergyCell

        self.distance_since_spawn += speed * dt
        if self.distance_since_spawn < self.next_gap:
            return
        self.distance_since_spawn = 0.0
        difficulty = self.difficulty(elapsed)
        self.next_gap = self._roll_gap(difficulty, speed)
        pattern = self._pick_pattern(difficulty)
        x = config.SPAWN_AHEAD
        self.spawn_count += 1

        if pattern == "spike1":
            world.hazards.append(Spike(x, 1))
        elif pattern == "spike2":
            world.hazards.append(Spike(x, 2))
        elif pattern == "beam":
            world.hazards.append(Beam(x))
        elif pattern == "drone":
            world.hazards.append(Drone(x, mode="sine"))
        elif pattern == "drone_low":
            world.hazards.append(Drone(x, mode="low"))
        elif pattern == "cells":
            for i in range(5):
                world.cells.append(
                    EnergyCell(x + i * 44.0, config.GROUND_Y - 120.0 - 38.0 * abs(2 - i))
                )
        elif pattern == "spike_cells":
            world.hazards.append(Spike(x, 1))
            for i in range(3):
                world.cells.append(EnergyCell(x + 8.0 + i * 40.0, config.GROUND_Y - 170.0))
        elif pattern == "beam_cells":
            world.hazards.append(Beam(x))
            for i in range(3):
                world.cells.append(EnergyCell(x + 10.0 + i * 40.0, config.GROUND_Y - 26.0))
        elif pattern == "gauntlet":
            world.hazards.append(Spike(x, 1))
            world.hazards.append(Beam(x + 260.0))
            for i in range(3):
                world.cells.append(EnergyCell(x + 300.0 + i * 40.0, config.GROUND_Y - 26.0))
