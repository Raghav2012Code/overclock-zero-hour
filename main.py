"""Overclock: Zero Hour — application entry point.

Run with either::

    python main.py
    python run.py
"""

from __future__ import annotations


def main() -> int:
    import pygame

    import config
    from core.game import Game

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
