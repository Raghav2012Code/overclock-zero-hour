"""Procedural sprite factory — all character art drawn in code.

Sprites are pre-rendered once at startup onto SRCALPHA surfaces with
neon rim-light, so per-frame cost is a single blit.
"""

from __future__ import annotations

import pygame

import config


def _canvas(w: int, h: int) -> pygame.Surface:
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _runner_base(pose: str) -> pygame.Surface:
    """Cyber-runner humanoid (~34x64) with visor + scarf. Poses: run1/run2/jump/fall/slide."""
    surf = _canvas(48, 72)
    cx = 24
    cyan, magenta, white = config.NEON_CYAN, config.NEON_MAGENTA, config.WHITE
    body = (30, 32, 60)
    # --- legs ---
    leg_c = (16, 20, 44)
    if pose == "run1":
        pygame.draw.line(surf, leg_c, (cx, 44), (cx - 10, 66), 6)
        pygame.draw.line(surf, cyan, (cx, 44), (cx - 4, 60), 5)
        pygame.draw.line(surf, leg_c, (cx, 44), (cx + 12, 58), 6)
        pygame.draw.line(surf, magenta, (cx, 44), (cx + 8, 52), 5)
    elif pose == "run2":
        pygame.draw.line(surf, leg_c, (cx, 44), (cx + 10, 66), 6)
        pygame.draw.line(surf, cyan, (cx, 44), (cx + 4, 60), 5)
        pygame.draw.line(surf, leg_c, (cx, 44), (cx - 12, 58), 6)
        pygame.draw.line(surf, magenta, (cx, 44), (cx - 8, 52), 5)
    elif pose in ("jump", "fall"):
        spread = 12 if pose == "jump" else 8
        lift = -6 if pose == "jump" else 2
        pygame.draw.line(surf, leg_c, (cx, 44), (cx - spread, 56 + lift), 6)
        pygame.draw.line(surf, leg_c, (cx, 44), (cx + spread, 56 + lift), 6)
        pygame.draw.line(surf, cyan, (cx, 44), (cx - spread, 56 + lift), 2)
        pygame.draw.line(surf, cyan, (cx, 44), (cx + spread, 56 + lift), 2)
    elif pose == "slide":
        surf = _canvas(64, 36)
        cx = 30
        # Low horizontal body: torso + extended legs + trailing sparks mount.
        pygame.draw.line(surf, leg_c, (cx - 6, 24), (cx + 26, 28), 7)
        pygame.draw.line(surf, cyan, (cx - 6, 24), (cx + 26, 28), 2)
        pygame.draw.ellipse(surf, body, (cx - 20, 10, 26, 16))
        pygame.draw.ellipse(surf, magenta, (cx - 20, 10, 26, 16), 2)
        pygame.draw.circle(surf, (20, 24, 48), (cx - 14, 12), 8)
        pygame.draw.line(surf, cyan, (cx - 20, 12), (cx - 8, 12), 3)  # visor
        pygame.draw.line(surf, magenta, (cx + 6, 16), (cx - 14, 22), 4)  # scarf
        return surf
    # --- torso ---
    pygame.draw.ellipse(surf, body, (cx - 9, 22, 18, 24))
    pygame.draw.ellipse(surf, cyan, (cx - 9, 22, 18, 24), 2)
    pygame.draw.line(surf, magenta, (cx - 9, 34), (cx + 9, 34), 2)  # chest coil
    # --- arms ---
    swing = {"run1": -8, "run2": 8, "jump": -12, "fall": 10}[pose]
    pygame.draw.line(surf, body, (cx, 26), (cx + swing, 40), 5)
    pygame.draw.line(surf, cyan, (cx, 26), (cx + swing, 40), 2)
    pygame.draw.line(surf, body, (cx, 26), (cx - swing, 38), 5)
    # --- head + visor ---
    pygame.draw.circle(surf, (20, 24, 48), (cx, 13), 9)
    pygame.draw.circle(surf, cyan, (cx, 13), 9, 2)
    pygame.draw.line(surf, magenta, (cx - 6, 12), (cx + 6, 12), 4)
    pygame.draw.circle(surf, white, (cx + 2, 12), 2)
    # --- scarf flutter ---
    pygame.draw.line(surf, magenta, (cx - 8, 20), (cx - 18, 16 + swing // 3), 4)
    return surf


def build_sprites() -> dict[str, pygame.Surface]:
    """Pre-render every sprite; called once at startup."""
    return {
        "player_run1": _runner_base("run1"),
        "player_run2": _runner_base("run2"),
        "player_jump": _runner_base("jump"),
        "player_fall": _runner_base("fall"),
        "player_slide": _runner_base("slide"),
    }
