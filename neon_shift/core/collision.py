"""Axis-aligned bounding-box collision helpers.

Hitboxes are deliberately shrunk ("forgiveness insets") so near-misses
feel fair — a standard technique in endless runners.
"""

from __future__ import annotations

import pygame


def aabb(a: pygame.Rect, b: pygame.Rect) -> bool:
    """Return True when two rects overlap."""
    return a.colliderect(b)


def forgiving_rect(rect: pygame.Rect, inset_x: float = 5.0, inset_y: float = 4.0) -> pygame.Rect:
    """Return a shrunk copy of ``rect`` used for fair player collisions."""
    ix = min(inset_x, rect.width / 2.0 - 1.0)
    iy = min(inset_y, rect.height / 2.0 - 1.0)
    ix = max(ix, 0.0)
    iy = max(iy, 0.0)
    return pygame.Rect(
        int(rect.x + ix),
        int(rect.y + iy),
        int(rect.width - 2 * ix),
        int(rect.height - 2 * iy),
    )


def collides(player_rect: pygame.Rect, hazard_rect: pygame.Rect) -> bool:
    """Forgiving player-vs-hazard overlap test."""
    return aabb(forgiving_rect(player_rect), forgiving_rect(hazard_rect, 3.0, 3.0))
