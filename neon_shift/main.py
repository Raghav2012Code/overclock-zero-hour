"""Overclock: Zero Hour — application entry point.

Run with either::

    python -m neon_shift.main
    python run.py
"""

from __future__ import annotations

import os
import sys


def _ensure_cwd_on_path() -> None:
    cwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if cwd not in sys.path:
        sys.path.insert(0, cwd)


def main() -> int:
    _ensure_cwd_on_path()
    import pygame

    from neon_shift import config
    from neon_shift.core.game import Game

    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass
    pygame.display.set_caption(f"{config.TITLE} v{config.VERSION}")
    surface = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
    try:
        game = Game(surface)
        game.run()
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
