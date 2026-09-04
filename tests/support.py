"""Shared headless-pygame helpers for the test suite.

Environment variables MUST be set before pygame is first imported, so
every test module imports this module (or replicates the two lines)
before any game import.
"""

from __future__ import annotations

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402  (env setup above must run first)

import config  # noqa: E402


def ensure_display() -> pygame.Surface:
    """Init pygame (idempotent) and return the main surface."""
    pygame.init()
    return pygame.display.set_mode((config.WIDTH, config.HEIGHT))


def make_game():
    """Build a Game bound to the headless display, key polling disabled."""
    from core.game import Game

    game = Game(ensure_display())
    # Detach real keyboard state: tests drive input explicitly.
    game._poll_held_keys = lambda: None  # noqa: SLF001
    return game
