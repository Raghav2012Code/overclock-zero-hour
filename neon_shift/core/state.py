"""Game state machine."""

from __future__ import annotations

from enum import Enum, auto


class GameState(Enum):
    """High-level screens of the game."""

    START = auto()
    PLAYING = auto()
    GAME_OVER = auto()
