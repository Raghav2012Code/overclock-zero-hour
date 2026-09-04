"""Overclock: Zero Hour — application entry point.

Run with either::

    python main.py
    python run.py
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def main() -> int:
    logging.basicConfig(level=logging.WARNING)
    import pygame

    import config
    from core.game import Game

    pygame.init()
    try:
        pygame.mixer.init()
    except Exception as exc:
        logger.warning("mixer init failed, continuing silent: %s", exc)
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
